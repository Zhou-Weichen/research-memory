# 本地 Memory 同步指令

请作为 Memory 维护者，将我提供的 Research Update 和独立文档草稿合并进当前研究工作区。本次只同步 Memory，不启动科研工程任务。

先将传入草稿放在 inbox/，保留其目标路径；不要在核对基线前写入正式研究目录。

1. 先读 RESEARCH_STATE.md、协议、目标文件及更新 ID。已 Applied 的同 ID 不重复应用。
2. 在修改前，使用该讨论上下文对应的 manifest 文件运行 verify-base，并核对 Update 的 Base-State-Version 和 Base-State-SHA256。没有本地 manifest 时使用上下文内嵌的清单恢复它，不补造指纹。
3. 基线冲突时读取最新文件并重做受影响变更；不能静默采用旧 State。必要的研究选择冲突再澄清，独立且明确的工作继续。
4. 核对 Before → After，分开已决定与 Pending。按局部操作更新相关记忆索引和记录，保留历史，不把全部 Update 塞入 State。
5. State 内容变化时版本加 1，更新 Updated / Last-Update；没有变化时保持版本。任务绑定最终 State 指纹，实验引用正确 Revision。避免 State 和 Task 内容哈希循环。
6. 新工程任务保存到 agent_tasks/，Ready 所需条件不全就留 Draft。论文、结果或假设的真实性不能只由格式检查决定。
7. 运行 check 和相关 check --ready。填写 Update 的 Applied-At、Applied-State-Version、Applied files，再检查一次。所有关联文件一致后保存同一版本提交或备份。
8. 运行 export 导出新讨论上下文。报告实际应用项、仍 Pending 的项、冲突、最新版本与文件路径。

不要重写没有变化的内容；不把“已生成草稿”说成“已落盘”。
