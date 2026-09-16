import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("memory", SOURCE / "tools/research_memory.py")
memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        shutil.copytree(SOURCE, self.root, ignore=shutil.ignore_patterns(
            "exports", "__pycache__", ".git", "artifacts"))

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def snapshot(self):
        bundle, path = memory.export_context(self.root)
        return bundle, json.loads(path.read_text(encoding="utf-8"))

    def ready_task(self, experiment=False):
        info = memory.state_info(self.root)
        binding = "Experiment-ID: None\nExperiment-Revision: None\nExperiment-SHA256: None\n"
        if experiment:
            self.write("HYPOTHESES.md", "# Hypotheses\n\n## HYP-001\n\nA measurable claim.\n")
            exp = "Experiment-ID: EXP-001\nRevision: 1\nStatus: Ready\nHypothesis-ID: HYP-001\n"
            for heading in memory.EXP_SECTIONS:
                exp += f"\n## {heading}\n\nPredeclared concrete procedure for this test fixture.\n"
            path = self.write("experiments/EXP-001.md", exp)
            binding = ("Experiment-ID: EXP-001\nExperiment-Revision: 1\n"
                       f"Experiment-SHA256: {memory.digest(path.read_bytes())}\n")
        text = ("Task-ID: TASK-001\nRevision: 1\nStatus: Ready\n"
                f"State-Version: {info['state_version']}\n"
                f"State-SHA256: {info['state_sha256']}\n" + binding)
        for heading in memory.TASK_SECTIONS:
            body = "Concrete implementation acceptance evidence."
            if heading == "Context":
                body = "RESEARCH_STATE.md"
                if experiment:
                    body += "\nexperiments/EXP-001.md"
            elif heading in {"Scientific", "Experiment"} and not experiment:
                body = "N/A — document formatting maintenance has no scientific experiment."
            level = "###" if heading in {"Functional", "Scientific", "Regression"} else "##"
            text += f"\n{level} {heading}\n\n{body}\n"
        self.write("agent_tasks/TASK-001.md", text)
        return "agent_tasks/TASK-001.md"

    def test_initial_workspace_and_roundtrip(self):
        self.assertEqual(memory.validate(self.root), [])
        bundle, manifest = self.snapshot()
        memory.verify_manifest(self.root, manifest)
        self.assertIn("updates/UPD-20260916-001.md", manifest["files"])
        self.assertIn("RESEARCH_AGENT_PROTOCOL.md", manifest["files"])
        self.assertIn("BEGIN FILE: RESEARCH_STATE.md", bundle.read_text())
        self.assertNotIn("examples/WALKTHROUGH.md", manifest["files"])

    def test_same_version_changed_state_is_stale(self):
        _, manifest = self.snapshot()
        path = self.root / "RESEARCH_STATE.md"
        path.write_text(path.read_text() + "\nChanged constraint.\n")
        with self.assertRaisesRegex(memory.MemoryError, "state_sha256"):
            memory.verify_manifest(self.root, manifest)

    def test_changed_literature_without_state_change_is_stale(self):
        _, manifest = self.snapshot()
        path = self.root / "LITERATURE.md"
        path.write_text(path.read_text() + "\nNew evidence.\n")
        with self.assertRaisesRegex(memory.MemoryError, "LITERATURE"):
            memory.verify_manifest(self.root, manifest)

    def test_new_unlinked_result_is_detected(self):
        _, manifest = self.snapshot()
        self.write("results/RUN-20260916-001/RESULT.md", "# Measurement\n")
        with self.assertRaisesRegex(memory.MemoryError, "added, removed, or changed"):
            memory.verify_manifest(self.root, manifest)

    def test_unbundled_existing_record_change_is_detected(self):
        self.write("literature/LIT-999.md", "# Unselected evidence\n")
        _, manifest = self.snapshot()
        self.assertNotIn("literature/LIT-999.md", manifest["files"])
        self.write("literature/LIT-999.md", "# Corrected evidence\n")
        with self.assertRaisesRegex(memory.MemoryError, "research records"):
            memory.verify_manifest(self.root, manifest)

    def test_placeholder_and_draft_block_execution(self):
        name = self.ready_task()
        path = self.root / name
        original = path.read_text()
        path.write_text(original + "\nInput: TODO\n")
        with self.assertRaisesRegex(memory.MemoryError, "placeholder"):
            memory.validate_ready(self.root, name)
        path.write_text(original.replace("Status: Ready", "Status: Draft"))
        with self.assertRaisesRegex(memory.MemoryError, "not Ready"):
            memory.validate_ready(self.root, name)

    def test_nonexperimental_maintenance_can_be_ready(self):
        memory.validate_ready(self.root, self.ready_task())

    def test_task_state_drift_blocks_execution(self):
        name = self.ready_task()
        path = self.root / "RESEARCH_STATE.md"
        path.write_text(path.read_text() + "\nChanged constraint.\n")
        with self.assertRaisesRegex(memory.MemoryError, "State-SHA256"):
            memory.validate_ready(self.root, name)

    def test_silent_experiment_change_blocks_execution(self):
        name = self.ready_task(experiment=True)
        memory.validate_ready(self.root, name)
        path = self.root / "experiments/EXP-001.md"
        path.write_text(path.read_text().replace("## Metric", "## Metric\n\nNew definition."))
        with self.assertRaisesRegex(memory.MemoryError, "Experiment-SHA256"):
            memory.validate_ready(self.root, name)

    def test_missing_falsification_blocks_execution(self):
        name = self.ready_task(experiment=True)
        path = self.root / "experiments/EXP-001.md"
        path.write_text(path.read_text().replace("## Falsification", "## Unspecified"))
        with self.assertRaisesRegex(memory.MemoryError, "Falsification"):
            memory.validate_ready(self.root, name)

    def test_state_budget_and_hypothesis_limit(self):
        path = self.root / "RESEARCH_STATE.md"
        original = path.read_text()
        path.write_text(original + "\n" + "长" * 6001)
        self.assertTrue(any("6000" in error for error in memory.validate(self.root)))
        path.write_text(original.replace("## Active Hypotheses",
            "## Active Hypotheses\n\nHYP-001 HYP-002 HYP-003 HYP-004"))
        self.assertTrue(any("more than 3" in error for error in memory.validate(self.root)))

    def test_missing_link_is_reported(self):
        self.write("literature/LIT-001.md", "# Card\n\n[missing](absent.md)\n")
        self.assertTrue(any("missing linked file" in error for error in memory.validate(self.root)))

    def test_export_follows_selected_records_not_raw_data(self):
        self.write("literature/LIT-001.md", "# Card\n\n[follow](LIT-002.md)\n")
        self.write("literature/LIT-002.md", "# Evidence\n")
        self.write("artifacts/raw.csv", "private,large,data\n")
        bundle, path = memory.export_context(self.root, ["literature/LIT-001.md"])
        manifest = json.loads(path.read_text())
        self.assertIn("literature/LIT-002.md", manifest["files"])
        self.assertNotIn("artifacts/raw.csv", manifest["files"])
        self.assertNotIn("private,large,data", bundle.read_text())

    def test_path_escape_and_symlink_escape_are_rejected(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("outside workspace")
        for name in ("../outside.md", str(outside)):
            with self.assertRaisesRegex(memory.MemoryError, "escapes"):
                memory.export_context(self.root, [name])
        (self.root / "escape.md").symlink_to(outside)
        with self.assertRaisesRegex(memory.MemoryError, "escapes"):
            memory.export_context(self.root, ["escape.md"])

    def test_duplicate_or_blank_version_is_rejected(self):
        with self.assertRaises(memory.MemoryError):
            memory.field("State-Version: 1\nState-Version: 2\n", "State-Version")
        with self.assertRaises(memory.MemoryError):
            memory.field("State-Version:\nUpdated: today\n", "State-Version")

    def test_inbox_drafts_do_not_invalidate_baseline(self):
        _, manifest = self.snapshot()
        self.write("inbox/UPD-20260916-002.md", "# Draft\n\n[future](../experiments/EXP-001.md)\n")
        memory.verify_manifest(self.root, manifest)
        self.assertEqual(memory.validate(self.root), [])

    def test_unrelated_repository_docs_do_not_block_memory(self):
        self.write("src/vendor/README.md", "[external build file](missing.md)\n")
        self.assertEqual(memory.validate(self.root), [])

    def test_malformed_manifest_has_a_clear_error(self):
        with self.assertRaisesRegex(memory.MemoryError, "schema"):
            memory.verify_manifest(self.root, [])

    def test_two_exports_do_not_overwrite_each_other(self):
        first, _ = self.snapshot()
        second, _ = self.snapshot()
        self.assertNotEqual(first, second)
        self.assertTrue(first.is_file() and second.is_file())

    def test_cli_failure_has_no_traceback(self):
        with contextlib.redirect_stderr(io.StringIO()) as stderr:
            code = memory.main(["--root", str(self.root), "check", "--ready", "missing.md"])
        self.assertEqual(code, 1)
        self.assertIn("ERROR", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
