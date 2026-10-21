# Gradient Surgery for Multi-Task Learning

## Metadata and reading scope

**English.** Tianhe Yu et al., arXiv:2001.06782v4, originally submitted 19 January 2020; published at NeurIPS 2020. Original: [arXiv](https://arxiv.org/abs/2001.06782), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, Multi-Task Optimization, PCGrad Update Rule, Practical Applications, Experiments, and Conclusion. ROAD MOPD compares against PCGrad and uses a related projection mechanism, but does not claim to derive from it.

**中文。** Tianhe Yu 等，arXiv:2001.06782v4，最初提交于 2020 年 1 月 19 日；发表于 NeurIPS 2020。原文：[arXiv](https://arxiv.org/abs/2001.06782)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、多任务优化、PCGrad 更新规则、实际应用、实验和结论。ROAD MOPD 与 PCGrad 进行比较并采用相关投影机制，但未声称由 PCGrad 推导而来。

## WHY / Core content / 核心内容

**English.** In multi-task learning, gradients from different tasks can interfere. The paper’s “tragic triad” describes when conflict is especially harmful: gradients point in opposing directions, one task’s gradient dominates in magnitude, and the loss landscape has high curvature. Simple averaging may then harm a weaker task even if aggregate loss decreases. PCGrad is a first-order gradient modification that projects away components of one task’s gradient that conflict with another, while leaving non-conflicting pairs unchanged. The method targets simultaneous multi-task optimization and can be combined with standard optimizers.

**中文。** 多任务学习中，不同任务的梯度可能相互干扰。论文提出的“悲剧三元组”描述了冲突特别有害的条件：梯度方向相反、某一任务梯度幅度占优、损失曲面曲率较高。即使总体损失下降，简单平均也可能损害较弱任务。PCGrad 是一阶梯度修改方法：投影掉一个任务梯度中与另一个任务冲突的分量，而不改变不冲突的任务梯度。该方法面向同时进行的多任务优化，可与标准优化器结合。

## HOW / Core method / 核心方法

**English.** For each task i, PCGrad computes gradient gᵢ. It processes other tasks j in random order. If gᵢ·gⱼ<0, it replaces gᵢ with gᵢ−(gᵢ·gⱼ/‖gⱼ‖²)gⱼ, which removes the component pointing against task j’s gradient. The operation is repeated across other tasks, then the modified task gradients are summed and passed to SGD, Adam or another gradient-based optimizer (§3, Algorithm 1). The method does not solve a quadratic program and does not add trainable parameters. Its order of pairwise projections matters in principle, so the authors use random task ordering.

**中文。** 对每个任务 i，PCGrad 计算梯度 gᵢ，再按随机顺序处理其他任务 j。若 gᵢ·gⱼ<0，则将 gᵢ 替换为 gᵢ−(gᵢ·gⱼ/‖gⱼ‖²)gⱼ，从而移除指向任务 j 反方向的分量。该操作对其他任务重复执行，最后将修改后的任务梯度求和并交给 SGD、Adam 或其他基于梯度的优化器（§3，算法 1）。该方法不求解二次规划，也不增加可训练参数。成对投影的顺序在原理上会产生影响，因此作者随机排列任务。

## WHAT / Evidence / 实验证据

**English.** Experiments span multi-task supervised learning, multi-task reinforcement learning and goal-conditioned RL (§5). On NYUv2, combining PCGrad with MTAN produces the best scores in eight of nine task metrics in the reported comparison (Table 1; §5.1). On CIFAR-100, combining PCGrad with routing networks reaches 77.5% test accuracy versus 74.7% for routing networks with the listed weighting method (Table 2). On CelebA, average error across 40 attributes is 8.69 versus 8.95 for the comparison method (Table 3). Multi-task RL curves show improved success and data efficiency on MT10/MT50 (Fig. 3). These results span several settings but do not imply every task conflict benefits from projection; the paper’s own two-task theory permits a degenerate opposing-gradient case.

**中文。** 实验涵盖多任务监督学习、多任务强化学习和目标条件 RL（§5）。在 NYUv2 上，将 PCGrad 与 MTAN 结合，在报告的比较中九项任务指标有八项取得最佳分数（§5.1，表 1）。在 CIFAR-100 上，PCGrad 与 routing networks 结合达到 77.5% 测试准确率，而表列权重方法下的 routing networks 为 74.7%（表 2）。在 CelebA 上，跨 40 个属性的平均错误率为 8.69，对比方法为 8.95（表 3）。多任务 RL 曲线显示 MT10/MT50 上成功率和数据效率有所提高（图 3）。这些结果覆盖多个设置，但不意味着每种任务冲突都适合投影；论文的双任务理论也允许出现退化的完全相反梯度情形。

## Foundations / 基础关系

**English.** ROAD MOPD describes PCGrad as a related approach and compares projection behavior (§3.3, Fig. 4 of [ROAD MOPD](../arxiv-2610.13521/summary.md); [original](../arxiv-2610.13521/original.pdf)). The relationship is recorded as a method-dependency inference because ROAD’s preventive projection shares a geometric mechanism with PCGrad. ROAD changes the construction: it uses the target-domain gradient and same-trajectory auxiliary teacher gradient, adds a minimum retained-norm condition, and applies a single update. ROAD’s authors do not state that their method is inspired by PCGrad.

**中文。** ROAD MOPD 将 PCGrad 称为相关方法并比较投影行为（[ROAD MOPD](../arxiv-2610.13521/summary.md)的 §3.3、图 4；[原文](../arxiv-2610.13521/original.pdf)）。该关系被记录为方法依赖推断，因为 ROAD 的预防性投影与 PCGrad 共享几何机制。ROAD 改变了构造：使用目标领域梯度和同轨迹辅助教师梯度，增加最小范数保留条件，并执行一次更新。ROAD 作者没有表示其方法受 PCGrad 启发。

## Limitations / 局限

**English.** PCGrad requires multiple task gradients at each update, which adds computation and memory compared with simply aggregating gradients. Sequential projections are order-dependent. The paper’s theory includes a pathological two-task case where directly opposing gradients can yield a zero update, and its empirical results cover selected task suites rather than all multi-objective problems. Reader inference: deciding what constitutes a “task” and which parameters are shared affects the gradients being projected. Summary covers the listed sections and is AI-assisted.

**中文。** 与简单聚合梯度相比，PCGrad 每次更新都需要多个任务梯度，因此增加计算和显存开销。连续投影依赖任务处理顺序。论文理论中存在退化的双任务情形：梯度完全相反时可能得到零更新；实验只涵盖选定任务集，而非所有多目标问题。读者推断：如何定义“任务”以及哪些参数共享，会影响被投影的梯度。本摘要覆盖列明章节，由 AI 辅助生成。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:2001.06782](https://arxiv.org/abs/2001.06782). Archived PDF and extracted text are the source material.

**中文。** 主要来源：[arXiv:2001.06782](https://arxiv.org/abs/2001.06782)。归档 PDF 和提取文本为资料来源。
