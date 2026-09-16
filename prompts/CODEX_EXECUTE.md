# Codex 执行指令

请执行我指定的 agent_tasks/TASK-XXX.md。

先读取 RESEARCH_STATE.md 与 TASK 的 Context，核对 State 版本和 SHA256、实验 Revision、输入、约束和资源预算，并运行 check --ready。如果仅因无关 State 变更导致过期，核对依赖后留下重新绑定记录；研究含义冲突时暂停相关部分，说明原因，不自行猜测。

按任务完成 implementation → testing → debugging → 规定的 experiment / ablation execution。规格明确且已授权的工作直接完成。只有缺少阻塞性信息才澄清，继续不依赖它的工作。

不改变假设、主要指标、成功阈值、对照、划分或预算。发现需要改变研究设计的问题，记录在报告中供下一轮讨论。

交付代码、合适的测试、配置、实验事实和 Implementation Report。每次实验使用唯一 RUN ID，保存设计快照、State / Task / Experiment 指纹、代码与数据版本、环境、命令、种子、全部尝试、日志与指标。

结果事实写入 results/，解释写入 analyses/；未运行写 Not run，部分完成写 Partial。Task Done 不要求假设被支持。按 Functional / Scientific / Regression 分别给出验收证据，再把结果与未决问题交回研究讨论。
