# On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes

## Metadata and reading scope

**English.** Rishabh Agarwal et al., arXiv:2306.13649v3, first submitted 23 June 2023; published at ICLR 2024. Original: [arXiv](https://arxiv.org/abs/2306.13649), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, Problem Setup, Generalized Knowledge Distillation method, Experiments, and Conclusion. ROAD MOPD uses its on-policy student-trajectory distillation setup.

**中文。** Rishabh Agarwal 等，arXiv:2306.13649v3，首次提交于 2023 年 6 月 23 日；发表于 ICLR 2024。原文：[arXiv](https://arxiv.org/abs/2306.13649)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、问题定义、Generalized Knowledge Distillation 方法、实验和结论。ROAD MOPD 使用其 on-policy 学生轨迹蒸馏设置。

## WHY / Core content / 核心内容

**English.** Standard distillation for autoregressive language models often trains on fixed ground-truth or teacher-generated sequences. At inference, however, the student follows its own token distribution; errors alter later contexts, creating a training–inference distribution mismatch. Generalized Knowledge Distillation (GKD) lets the student generate its own sequences and asks the teacher to provide token-level distribution feedback on those contexts. This transfers on-policy imitation-learning ideas to language-model distillation. GKD also allows a choice of divergence, making it possible to adapt the objective when a smaller student cannot represent the teacher’s full distribution.

**中文。** 自回归语言模型的标准蒸馏通常在固定的真实序列或教师生成序列上训练。但推理时学生沿自身 token 分布生成；错误会改变后续上下文，形成训练—推理分布不匹配。Generalized Knowledge Distillation（GKD）让学生自行生成序列，并要求教师在这些上下文中提供 token 级分布反馈。这将 on-policy 模仿学习思想迁移到语言模型蒸馏。GKD 还允许选择散度，因此当较小学生无法表达教师完整分布时，可调整目标函数。

## HOW / Core method / 核心方法

**English.** Given an input prompt, the student samples an output trajectory. At each prefix, the teacher evaluates next-token probabilities, and the student minimizes a divergence between teacher and student distributions over the visited tokens. GKD unifies on-policy and fixed-data training by mixing student-generated samples with an optional dataset of ground-truth or teacher-generated sequences using a student-data fraction λ. The divergence D can be forward KL, reverse KL or generalized Jensen–Shannon divergence. The sampling process is treated as data collection; gradients update the student on the resulting sequence without differentiating through its sampling distribution. This is an optimization objective for distillation, not an RL reward function.

**中文。** 给定输入提示后，学生采样生成一条回答轨迹。对每个前缀，教师计算下一个 token 的概率，学生则最小化所访问 token 上教师与学生分布之间的散度。GKD 通过 student-data fraction λ，将学生生成样本与可选的真实目标或教师生成序列混合，统一 on-policy 和固定数据训练。散度 D 可选 forward KL、reverse KL 或广义 Jensen–Shannon 散度。采样过程被视为数据收集；随后在所得序列上更新学生参数，不对采样分布反向传播。这是蒸馏优化目标，而不是 RL 奖励函数。

## WHAT / Evidence / 实验证据

**English.** The paper evaluates T5 student sizes on summarization, machine translation and arithmetic reasoning, and also studies instruction tuning and combination with RL fine-tuning (§4). Figure 1 compares student sizes and distillation methods: averaged over model sizes, on-policy GKD yields 2.1×, 1.7× and 1.9× the performance improvements over the initial student achieved by baseline KD methods on summarization, translation and reasoning, respectively (Abstract; Fig. 1). Task-agnostic distillation reports absolute accuracy gains of 2 points on BBH and 1 point on MMLU (Abstract; Fig. 10). The best divergence varies by task, and conclusions depend on the tested T5 models and datasets.

**中文。** 论文评测不同规模的 T5 学生在摘要、机器翻译和算术推理上的表现，也研究指令微调和与 RL 微调结合（§4）。图 1 比较不同学生规模和蒸馏方法：按模型规模平均，on-policy GKD 在摘要、翻译和推理上的性能增量分别达到基线 KD 方法相对初始学生增量的 2.1 倍、1.7 倍和 1.9 倍（摘要；图 1）。任务无关蒸馏在 BBH 和 MMLU 上分别报告 2 和 1 个百分点的绝对准确率提升（摘要；图 10）。最佳散度因任务而异，结论受限于所测 T5 模型与数据集。

## Foundations / 基础关系

**English.** ROAD MOPD uses the same core supervision setting: the student generates trajectories and the teacher provides feedback on them. In §2.1 of [ROAD MOPD](../arxiv-2610.13521/summary.md) ([original](../arxiv-2610.13521/original.pdf)), this on-policy distillation approach is cited as the direct basis. ROAD adds cross-teacher agreement for credit assignment and a preventive projection constraint over training gradients; those additions are not part of GKD.

**中文。** ROAD MOPD 使用相同的核心监督设置：学生生成轨迹，教师在这些轨迹上提供反馈。[ROAD MOPD](../arxiv-2610.13521/summary.md)（[原文](../arxiv-2610.13521/original.pdf)）的 §2.1 将此 on-policy 蒸馏方法作为直接基础。ROAD 增加跨教师一致性信用分配和训练梯度上的预防性投影约束；这些新增机制不属于 GKD。

## Limitations / 局限

**English.** On-policy teacher queries add inference cost, and results depend on the student’s sampling policy, prompt distribution, teacher quality and divergence. GKD samples from student states but does not backpropagate through sampling; the method therefore relies on iterative retraining rather than an exact gradient through trajectory generation. The paper’s main task-specific experiments use T5 families and do not establish scaling behavior for today’s largest LLMs. Summary covers the listed sections and is AI-assisted.

**中文。** On-policy 教师查询会增加推理成本，结果取决于学生采样策略、提示分布、教师质量和散度选择。GKD 从学生状态采样，但不穿过采样过程反向传播；因此它依赖迭代重新训练，而非对轨迹生成求精确梯度。论文主要任务实验使用 T5 模型族，未证明其在当前最大规模 LLM 上的扩展行为。本摘要覆盖列明章节，由 AI 辅助生成。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:2306.13649](https://arxiv.org/abs/2306.13649). Archived PDF and extracted text are the source material.

**中文。** 主要来源：[arXiv:2306.13649](https://arxiv.org/abs/2306.13649)。归档 PDF 和提取文本为资料来源。
