# Research workspace instructions

适用于科研任务。维护本工作流文档与工具时，按用户要求实施并验证，无需虚构科学任务。

1. 第一入口是 RESEARCH_STATE.md。科研工程执行还须读取指定 agent_tasks/TASK-XXX.md 的全部 Context，按需读取 RESEARCH_AGENT_PROTOCOL.md。聊天历史和 Idea Pool 不是已采用规格。
2. 先运行 python3 tools/research_memory.py check；执行科研任务前运行 check --ready agent_tasks/TASK-XXX.md，并人工核对科学条件。
3. 区分 Memory 同步与工程执行。明确要求同步时按 prompts/MEMORY_SYNC.md 操作；工程执行不得静默改变假设、指标、阈值、对照、数据划分或研究决策。
4. 规格明确、已授权的实施和运行直接推进。仅因阻塞性信息缺失或研究含义冲突请求澄清，同时继续独立工作。
5. 记录真实命令、结果、失败和未运行事项。每个实验保存设计、代码、数据、配置、种子和日志；事实写 results/，解释写 analyses/。
6. 用 reports/ 交接。任务完成不依赖假设被支持；负结果按既定判据记录。不得改规则或隐藏运行尝试以迎合预期。
7. State 只做有依据的局部修改，通过 Update 留痕。已应用 Update、旧决策正文和原始运行事实不静默覆盖。
8. 工具改动运行 python3 -m unittest discover -s tests -v；文档改动运行结构与引用检查。
