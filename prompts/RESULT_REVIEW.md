# 结果复盘指令

请读取最新 State、运行时的 Experiment / Task 快照、results/ 记录、原始指标及实现报告。不要用实验运行后才修改的设计解释旧结果。

按以下顺序分析：

1. 实验有效性：实现、数据、划分、操纵、对照、预算和测量是否满足预定条件？偏离是否影响判定？
2. Facts：具体观察、效应量、不确定性、运行次数与失败情况；每项链接结果文件或原始产物。
3. Interpretation：按运行前判据区分 Supported / Refuted / Inconclusive / Invalid，写出适用范围与 Confidence；证据不足就保持不足。
4. Alternative explanations：哪些机制仍能解释结果？哪些结论尚不可识别？
5. Hypothesis / Idea / Experiment changes：是否需要修订、退役、复核、增加消融或设计新的区分实验？
6. 下一步：最有信息价值的研究动作；仅在规格明确时产生独立工程任务。

解释写入 analyses/ 的独立记录，不能覆盖 results/ 事实。按照讨论结束协议输出 Research Update 和精确 State Patch；未决定事项保持 Pending，不自动把解释写为确定事实。
