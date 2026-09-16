# 完整讨论结束指令

本次 Research Discussion 结束。不要做普通聊天总结。

请读取本次上下文中的协议、State-Version、State SHA256 和文件清单，按 templates/RESEARCH_UPDATE.md 生成本次 Research Update。

要求：

1. 只保留对未来研究有持久价值的变化；未变内容写 No change。
2. 区分 Fact、Evidence、Hypothesis、Interpretation、Decision、Open Question、Speculation；不将推测写成事实。
3. 每项重要命题注明 Evidence、Scope 和 Confidence 及理由；缺证据直说。文献提供独立 LIT 卡与索引变更，注明原文阅读范围。
4. 明确 Hypothesis 的 Previous / New / Reason、证据支持与反证；删除改为退役或替代，保留历史。
5. Idea 留在 Pool，选中或拒绝都记录原因；拒绝需区分科学反驳、工程成本、重复和优先级。
6. 实验采用可证伪结构；支持、反驳、结论不足、实验无效分别给出判据。执行前固定指标、对照、重复方案和停止条件。
7. 未明确决定的事项保持 Pending，不能修改已有决策；已明确授权的变化不再要求逐项重复确认。
8. State 只输出精确局部补丁：Target、Operation、Before 原文、After、Reason、References。基线或原文不可见时写 Needs rebase，不编造 Before。
9. 有具体工程需求时另输出独立 agent_tasks/TASK-XXX.md，采用任务模板。输入、命令或必要验收不明确时为 Draft；没有需求则 Next Agent Task: None。
10. Task 的 Scientific acceptance 检查实验是否忠实执行、可复核，不要求结果支持假设。
11. 输出受影响文件列表，各文件分开并标注路径。已有文件仅给增量，新文件可以完整输出。不要生成完整的新 RESEARCH_STATE.md。
12. 指明这些草稿先保存到 inbox/，正式目标路径保持不变，待本地基线验证后再落盘。
13. 使用已有 ID，新增 ID 先检查清单；未掌握全量编号时标明临时编号由合并者分配。基线版本与指纹从清单原样复制，禁止猜算。

严格保留十个区块：
Session → New Insights → Hypothesis Changes → Idea Changes → Experimental Changes → Decisions → Rejected / Invalidated → Open Questions → Agent Tasks → State Update。

State Update 末尾给出当前只读投影：
Current Research Direction / Current Hypothesis / Current Experiment / Open Questions / Next Research Action / Next Agent Task。

除非已通过工具成功写入并验证，否则整份输出标为“待落盘”，不要声称 Memory 已更新。这个指令生成研究变化及任务，不执行工程实现。
