## [Beyond Domain-Routed Supervision: Cross-Teacher Guarding for Multi-Teacher On-Policy Distillation](Beyond%20Domain-Routed%20Supervision%20-%20Cross-Teacher%20Guarding%20for%20Multi-Teacher%20On-Policy%20Distillation.pdf)

上传日期：2026-10-09

**WHY (EN):** Multi-teacher LLM distillation can let one domain's updates damage another when their gradients conflict.

**HOW (EN):** ROAD MOPD uses auxiliary teachers on the same student trajectories: agreement adjusts token credit, while a projection reduces conflicting target-gradient components under a minimum target-gradient norm constraint.

**WHY（中文）：** 多教师蒸馏中，不同领域的梯度冲突会让一种能力的更新损害另一种能力。

**HOW（中文）：** ROAD MOPD 在同一学生轨迹上查询辅助教师，用教师一致性调节 token 信用分配，并在保留目标梯度范数的约束下移除冲突分量。

## [Learning from Fleet Experience: A Collective Learning Paradigm for Robots](Learning%20from%20Fleet%20Experience%20-%20A%20Collective%20Learning%20Paradigm%20for%20Robots.pdf)

上传日期：2026-10-19

**WHY (EN):** Robot fleets need to improve shared policies from deployment experience without depending on continual expert corrections.

**HOW (EN):** FERT uses failures to retrieve relevant successful action segments across the fleet and prioritize replay; FATS asynchronously collects experience, trains policies, and distributes updates despite interruptions.

**WHY（中文）：** 机器人群需要从部署经验中改进共享策略，同时减少对专家持续纠正的依赖。

**HOW（中文）：** FERT 根据失败检索群体中相关的成功动作片段并提高其回放优先级；FATS 异步收集经验、训练策略并分发更新，以应对设备中断。

## [Long-Horizon RL Needs Muon](Long-Horizon%20RL%20Needs%20Muon.pdf)

上传日期：2026-10-14

**WHY (EN):** Long-horizon LLM agents face sparse rewards, variable-length trajectories, and policy lag during asynchronous training.

**HOW (EN):** The paper evaluates a combined single-rollout asynchronous SPO++ recipe: Muon updates hidden weight matrices, while token-mean losses, truncated importance weights, and length/tool-error penalties address trajectory scale and rollout lag.

**WHY（中文）：** 长程 LLM 智能体面对稀疏奖励、轨迹长度不一和异步训练中的策略滞后。

**HOW（中文）：** 论文评估单轨迹异步 SPO++ 组合方案：Muon 更新隐藏层权重矩阵，token 均值损失、截断重要性权重及长度/工具错误惩罚处理轨迹尺度和策略滞后。

## [PyTorch Distributed: Experiences on Accelerating Data Parallel Training](PyTorch%20Distributed%20-%20Experiences%20on%20Accelerating%20Data%20Parallel%20Training.pdf)

上传日期：2020-06-28

**WHY (EN):** In data-parallel training, gradient communication can bottleneck throughput when it waits for computation to finish.

**HOW (EN):** PyTorch DDP reduces ready gradient buckets with AllReduce during backpropagation and supports skipped synchronization during local gradient accumulation.

**WHY（中文）：** 数据并行训练中，等待计算结束后再通信梯度会限制吞吐。

**HOW（中文）：** PyTorch DDP 将就绪梯度分桶，在反向传播期间用 AllReduce 同步；本地累积梯度时还可跳过同步。

## [Scaling Parameter-Efficient Fine-Tuning for Brain Encoding](Scaling%20Parameter-Efficient%20Fine-Tuning%20for%20Brain%20Encoding.pdf)

上传日期：2026-10-19

**WHY (EN):** Adapting huge multimodal backbones to scarce neural recordings is costly, while training only a readout leaves their representations fixed.

**HOW (EN):** The method freezes the backbone and trains LoRA adapters with a lightweight readout; one causal pass extracts features for many timepoints, and a batched multi-LoRA kernel scales independent adapters on the shared backbone.

**WHY（中文）：** 稀缺神经记录难以支撑大型多模态骨干的全量微调，而仅训练读出层无法调整骨干表征。

**HOW（中文）：** 该方法冻结骨干，用 LoRA 与轻量读出层进行训练；单次因果前向可提取多个时点特征，批量 multi-LoRA 内核则在共享骨干上扩展独立适配器。

## [Rethinking Projector Training in Multimodal LLMs](Rethinking%20Projector%20Training%20in%20Multimodal%20LLMs.pdf)

上传日期：2026-10-13

**WHY (EN):** Multimodal LLMs often spend paired-data and optimization budget on projector alignment that appears to need only coarse matching.

**HOW (EN):** PORTAL estimates vision and language feature Gaussians and computes a closed-form optimal-transport map on a shared principal subspace, replacing the initial projector-training stage; joint multimodal training still follows.

**WHY（中文）：** 多模态 LLM 的投影器对齐可能只需粗粒度匹配，却常消耗成对数据和优化预算。

**HOW（中文）：** PORTAL 估计视觉与语言特征的高斯分布，在共享主成分子空间上计算闭式最优传输映射，替代初始投影器训练阶段；之后仍进行联合多模态训练。
