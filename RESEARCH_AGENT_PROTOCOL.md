# Research Agent Protocol v1.0

## 1. 六条不变规则

1. 聊天可以发散，State 必须收敛。
2. Idea 可以很多，Active Hypothesis 默认不超过 3 个。
3. 结论必须和 Evidence 分离。
4. 实验结果必须和 Interpretation 分离。
5. Research Decision 必须留下历史记录。
6. Agent 执行当前明确的 State 和 Task，不猜测研究意图。

State 是当前采用的研究认识与行动依据，不是对科学真理的担保。它可以包含明确标注的假设、不确定性和已确定的工程约束。“正在检验 H1”不表示“H1 成立”。

## 2. 知识类型与证据

| 类型 | 含义 | 必须说明 |
| --- | --- | --- |
| Fact | 明确条件下核验的观察 | 范围、测量方式、时间、来源 |
| Evidence | 支持或反驳命题的材料 | 论文具体位置、日志、数据、代码版本 |
| Hypothesis | 可被实验削弱或否定的命题 | 操作定义、支持条件、反驳条件 |
| Interpretation | 从观察到机制或结论的推理 | 依赖证据、竞争解释、局限 |
| Decision | 当前选择做什么 | 原因、取舍、依据、替代关系 |
| Open Question | 尚缺答案的问题 | 未解决原因、解决方法、阻塞事项 |
| Speculation | 尚未充分支持的猜想 | 留在 Idea Pool，不提升为事实 |

重要命题注明 Type、Evidence、Confidence 与 Scope。Confidence 使用 Low / Medium / High 并说明理由；它不是校准后的概率，也不能代替证据。

无证据写 `Evidence: None — 待验证`。文献区分全文已核验、仅摘要、二手描述和未核验；不得编造引用、DOI、页码或数值。“作者报告 X”不等于“我们复现了 X”。预算和偏好可以成为决策依据，无需伪装成科学证据。

## 3. 权威副本、ID 与历史

本地 Memory 是权威副本。讨论开始读取最新上下文的 State-Version、State SHA256 和文件清单，承认未提供文件不可见。聊天记忆不能替代文件现状。

ID：`UPD-YYYYMMDD-NNN`、`INS-NNN`、`IDEA-NNN`、`LIT-NNN`、`HYP-NNN`、`EXP-NNN`、`DEC-NNN`、`Q-NNN`、`TASK-NNN`；运行用 `RUN-YYYYMMDD-NNN`。同一对象修订保持 ID，增加 Revision；命题操作定义或适用范围发生本质变化时建立新 ID，并关联旧命题。编号不重复复用；并行草稿由维护者在合并时去重。

State 保存当前投影，Updates 保存变化事件，专题文件保存详细记录。已应用的 Update、决策正文和运行事实不静默覆盖。纠错写新 Update，说明原记录与修正原因；决策用新 DEC 替代旧 DEC，索引可更新当前状态，旧正文保留。

Idea 被拒绝不等于 Hypothesis 被实验证伪。Reject 可源于成本、重复、不可识别或优先级，须写明类别、范围和重新考虑的条件。假设“删除”改为 Superseded / Retired，实验“删除”改为 Cancelled，不能擦除历史。

## 4. State 预算

目标约 1–3 页。Markdown 页数取决于排版；工程近似预算是最多 6,000 个非空白字符、180 行、3 个 Active Hypothesis。实际打印布局仍需人工检查。

只保留研究问题与范围、关键事实、活动假设、当前实验、有效决策与约束、关键问题、下一研究动作和下一工程任务。尽量一行加链接，不嵌入文献笔记、聊天或长实验表。

Idea 经明确 Decision 选中后才进入当前方向或变成 HYP / EXP。超限时将历史与细节移出 State，保留适用条件、重要反证和链接，不以压缩为理由删除负面证据。

## 5. Discussion → Update → Memory

结束讨论只产出变更，使用 [Update 模板](templates/RESEARCH_UPDATE.md) 的十个区块；无变化写 `No change`。新增文献在 Insights 关联独立文献卡，未决问题明确写入 `OPEN_QUESTIONS.md`。

State Update 给出简短的当前投影，以及精确 State Patch：Target、Operation、Before、After、Reason、References。没有 State 变化就写 `No state change`；当前投影不是重写 State 的指令。

Memory 维护者按顺序执行：

传入的 Update 与文件草稿先放在 inbox/，基线核对前不写入正式记忆目录。

1. 读取 State 与相关专题记录；在修改前运行 `verify-base`。任何基线差异都须基于最新文件重做相关变更，不强行覆盖。已 Applied 的 Update 不重复应用。
2. 区分明确决定与建议：已授权变化直接落地；建议保持 Pending。只在缺失信息会影响研究选择时澄清，常规整理不需反复批准。
3. 核对 Before、Evidence 和 ID，进行局部编辑，并同步相关专题记录和独立文件。不能只更新 State、丢失详细依据。
4. State 内容变化才把 State-Version 加 1，并更新 Updated、Last-Update；只更新专题笔记时 State 版本不变，但必须重新导出清单。Update 记录 From / To 版本。
5. Task 绑定合并后的 State 版本和 SHA256，Context 列出实际依赖。避免循环哈希：State 只引用任务路径 / ID，Task 在 State 定稿后填写其指纹。
6. 运行 `check` 与相关 `--ready`，将 Update 标记 Applied，填写 Applied-At、文件清单及实际 From / To。以一个 Git 提交或完整版本备份保存这组变化，一致性恢复前不启动工程任务。
7. 导出新快照。若写入中断，核对工作区差异及 Applied 状态，补齐或回退这组修改后再执行。辅助工具不提供跨文件原子事务或自动冲突合并。

Update“生成”不等于“应用”。没有写入能力的 GPT 输出标注为待落盘，不宣称已改本地文件。

## 6. 生命周期与执行条件

- Idea：Captured → Selected / Parked / Rejected；重新开放须记录理由。
- Hypothesis：Proposed → Active → Supported / Refuted / Inconclusive / Retired / Superseded。Supported 仅在注明范围内成立；新证据以新的评估事件修正状态。
- Experiment：Draft → Ready → Running → Completed / Failed / Cancelled。执行前保存设计快照和哈希；操纵、样本、指标、阈值或分析规则变化须增加 Revision。事后分析标为 Exploratory。
- Task：Draft → Ready → InProgress → Done / Blocked / Cancelled。缺少执行必要的输入、命令、预算或验收条件时保持 Draft；未知科学结果本身不阻塞执行。
- Update：Draft → Applied / Rejected / Superseded。已 Applied 的 Update 中可以包含仍为 Pending 的建议，只要未提升为有效决策。

Ready Task 必须有 Objective、Context、Implementation、Constraints、Expected Behavior、Acceptance Criteria、Tests、Experiment、Deliverables。Functional / Scientific / Regression 分别验收。纯工程维护可写 `Experiment-ID: None` 并明确科学验收与实验不适用的理由，不编造实验凑模板。

## 7. 实验最低要求

每个实验明确 Question、Hypothesis、Manipulation、Control、Metric、Expected、Falsification、Alternative Explanation。

执行前还须固定：数据与划分版本、独立实验单位、种子或抽样方案、重复次数及理由、baseline、公平资源预算、主要指标和方向、最小相关效应、聚合与不确定性方法、排除规则、停止条件、命令及结果路径。非量化项目给出可核验的判据，不机械套用显著性检验。

支持、反驳、结论不足分别有操作性规则。不显著或单次失败不自动等于反驳；测量或实现失效归为 Invalid，先修复有效性。不在观察结果后修改阈值、筛选最优种子或更换主要指标。

Ablation 每行说明移除/替换因素、保持不变的项目、检验机制、预期差异和竞争解释；比较多个变体时说明选择与多重比较策略。

## 8. 执行、结果与反馈

Agent 先读 State，再读 TASK Context 和实验。冲突时只暂停受影响部分并说明，继续无冲突且已授权的工作。不根据 brainstorming 扩大任务范围。

任务边界内的实现、测试、调试、消融和维护可直接推进；不得静默修改假设、主要指标、对照、划分、决策、阈值或预算。需要改变研究含义的发现写入报告和待讨论的 Update 建议。

Task 绑定设计指纹后，不为标记进度而随手修改设计文件；运行状态写到 RUN。改变设计文件的任何内容会改变哈希，须核对影响并重新绑定任务，旧 RUN 保留旧快照。

每个 RUN 保存 State / Task / Experiment 版本、设计快照、代码提交及 dirty diff、环境、数据指纹、配置、命令、种子、起止时间、退出码、全部尝试、原始日志与指标位置及 SHA256。大文件可放外部存储，但要记录稳定 URI 与内容校验值。

`results/` 只保存观察、有效性检查和运行事实；`analyses/` 保存机制解释与假设评估。报告不能替代原始数据。解析错误的修正保留原日志和旧版本并写纠错依据。

Task Done 表示工程交付和规定实验执行符合规格，不要求假设被支持。负结果和结论不足也可以是合格交付。未运行或未完成明确写 Not run / Partial，不宣称成功。

GPT 复盘先判断实验有效性，再按预先规则评估 Supported / Refuted / Inconclusive / Invalid，列出替代解释并产生 Update。State 只采用经决定的结论与动作。
