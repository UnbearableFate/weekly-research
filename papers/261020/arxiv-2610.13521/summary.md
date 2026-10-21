# Beyond Domain-Routed Supervision: Cross-Teacher Guarding for Multi-Teacher On-Policy Distillation

## Metadata and reading scope

**English.** The paper is arXiv:2610.13521v2, with v2 submitted 17 October 2026; v1 first appeared 9 October, outside the 14–20 October publication window. It was surfaced in HF Daily on 15 October with 250 cumulative votes observed. Mark it as **resurfaced older work**, not a newly published paper. The manuscript bears a “Paper Under Review” notice. Original: [arXiv](https://arxiv.org/abs/2610.13521), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, Related Work, Method, Experiments, Analysis, Limitations, and References.

**中文。** 本文为 arXiv:2610.13521v2，v2 于 2026 年 10 月 17 日提交；v1 首次发布于 10 月 9 日，早于 10 月 14–20 日的发表窗口。它于 10 月 15 日进入 HF Daily，归档时观测到累计 250 票。应标记为**本周重新受到关注的旧作**，而非新发表论文。稿件带有“Paper Under Review”标记。原文：[arXiv](https://arxiv.org/abs/2610.13521)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、相关工作、方法、实验、分析、局限和参考文献。

## WHY / Core content / 核心内容

**English.** Multi-domain on-policy distillation routes each domain’s student trajectories to a specialized teacher, but this does not prevent shared-parameter updates from harming another domain. ROAD MOPD uses auxiliary teachers as cross-domain critics on the same target-domain student trajectories. Agreement between the routed target-domain teacher and an auxiliary teacher, measured relative to a frozen reference, gates token-level reward. A second mechanism projects the target-domain update away from components that locally conflict with auxiliary feedback while retaining target-gradient norm. The auxiliary teacher guides a constraint; it is not given a separate optimizer update. ROAD is a concrete shared-parameter optimization method for multi-teacher LLM training, evaluated across Math, Code and Medical domains.

**中文。** 多领域 on-policy 蒸馏会将每个领域的学生轨迹路由给专门教师，但这并不能防止共享参数更新损害其他领域。ROAD MOPD 在相同的目标领域学生轨迹上使用辅助教师作为跨领域 critic。路由的目标领域教师与辅助教师相对冻结参考模型的一致性会门控 token 级奖励。第二种机制将目标领域更新中与辅助反馈局部冲突的分量投影掉，同时保留目标梯度范数。辅助教师用于提供约束，不会执行单独的优化器更新。ROAD 是一种面向多教师 LLM 训练的具体共享参数优化方法，实验覆盖 Math、Code 和 Medical 领域。

## HOW / Core method / 核心方法

**English.** For a target domain d, its routed teacher Tᵣ is the target-domain teacher; an auxiliary teacher Tₐ comes from another domain. Both teachers and a frozen reference score the same student-generated tokens. The agreement is sₜ=tanh((ℓᵣₜ−ℓrefₜ)/τ)·tanh((ℓₐₜ−ℓrefₜ)/τ), and λₜ=clip(1+ρg sₜ, λmin, λmax) modulates the routed teacher’s token reward (Eqs. 4–5). For gradient correction, the target gradient g=∇Lᵃᵍʳ_d comes from the agreement-modulated loss; the auxiliary gradient g′=∇L′d→a comes from plain OPD with the auxiliary teacher on the same stored domain-d trajectories (Eq. 6). If ⟨g,g′⟩<0, full projection is gfull=g−(⟨g,g′⟩/‖g′‖²)g′. ROAD selects a partial projection between g and gfull that minimizes local conflict subject to ‖g̃‖≥m‖g‖ (Eqs. 7–9). Only projected target-domain gradients are aggregated, clipped and sent to one AdamW update; auxiliary gradients are never applied separately. The paired-domain configuration uses m=0.6 (App. B.3).

**中文。** 对目标领域 d，路由教师 Tᵣ 就是该目标领域的教师；辅助教师 Tₐ 来自另一领域。两位教师与冻结参考模型对相同的学生生成 token 打分。一致性为 sₜ=tanh((ℓᵣₜ−ℓrefₜ)/τ)·tanh((ℓₐₜ−ℓrefₜ)/τ)，并由 λₜ=clip(1+ρg sₜ, λmin, λmax) 调节路由教师的 token 奖励（式 4–5）。梯度修正时，目标梯度 g=∇Lᵃᵍʳ_d 来自一致性调制损失；辅助梯度 g′=∇L′d→a 则是在相同领域 d 存储轨迹上，使用辅助教师执行普通 OPD 得到（式 6）。若 ⟨g,g′⟩<0，完整投影为 gfull=g−(⟨g,g′⟩/‖g′‖²)g′。ROAD 在 g 与 gfull 之间选择部分投影，使局部冲突最小且满足 ‖g̃‖≥m‖g‖（式 7–9）。它只聚合投影后的目标领域梯度，裁剪后交给一次 AdamW 更新；辅助梯度不会单独应用。成对领域配置中 m=0.6（附录 B.3）。

## WHAT / Evidence / 实验证据

**English.** The experiments train Qwen3-4B and Qwen3-1.7B students on combinations of Math, Code and Medical data and evaluate eleven benchmarks (§4.1). Across four paired-domain/model settings, ROAD MOPD has the highest two-domain average among the compared multi-domain methods, exceeding each strongest overall baseline by 0.72–2.89 points (§4.2, Table 1). In the three-domain Qwen3-4B setting it reaches an average of 52.89 versus 51.71 for CaMOPD (Table 3). For the smaller student, reported Medical gains are 3.88 and 5.17 points in the two Medical pairings (§4.2). The analyses indicate both adaptive reward and preventive projection contribute (§4.3, Table 4), and comparisons against PCGrad show different behavior under the paper’s preventive constraint (Fig. 4). The findings are bounded by the evaluated teachers, domains, checkpoints and benchmark suite; they do not establish performance for arbitrary domain mixtures.

**中文。** 实验使用 Qwen3-4B 与 Qwen3-1.7B 学生，在 Math、Code、Medical 数据组合上训练，并评估 11 个基准（§4.1）。在四种成对领域/模型设置中，ROAD MOPD 的双领域平均分在被比较的多领域方法中最高，超过每种设置下最强总体基线 0.72–2.89 分（§4.2，表 1）。在 Qwen3-4B 三领域设置中，其平均分为 52.89，CaMOPD 为 51.71（表 3）。对较小学生模型，两个 Medical 配对设置报告的医学领域增益为 3.88 和 5.17 分（§4.2）。分析显示自适应奖励和预防性投影均有贡献（§4.3，表 4）；与 PCGrad 的比较展示了其在论文所提预防性约束下的不同表现（图 4）。结果仅适用于被测教师、领域、检查点和基准集，尚未证明任意领域组合上的效果。

## Foundations / 基础关系

**English.** ROAD’s on-policy teacher feedback follows the student-trajectory distillation setup in [Generalized Knowledge Distillation](../arxiv-2306.13649/summary.md) ([original](../arxiv-2306.13649/original.pdf)); the present paper adds cross-teacher reward modulation and a preventive gradient constraint. Its projection mechanism cites [Gradient Surgery for Multi-Task Learning](../arxiv-2001.06782/summary.md) ([original](../arxiv-2001.06782/original.pdf)). The relation to PCGrad is recorded as a method-dependency inference from the shared gradient-projection mechanism: ROAD’s authors call PCGrad a related approach and compare against it, but do not claim that ROAD is inspired by or derived from PCGrad.

**中文。** ROAD 的 on-policy 教师反馈沿用[《Generalized Knowledge Distillation》](../arxiv-2306.13649/summary.md)（[原文](../arxiv-2306.13649/original.pdf)）中的学生轨迹蒸馏设置；本文增加跨教师奖励调节和预防性梯度约束。其投影机制引用了[《Gradient Surgery for Multi-Task Learning》](../arxiv-2001.06782/summary.md)（[原文](../arxiv-2001.06782/original.pdf)）。PCGrad 关系被记录为基于共享梯度投影机制的方法依赖推断：ROAD 作者将 PCGrad 称为相关方法并进行比较，但未声称 ROAD 受其启发或由其推导而来。

## Limitations / 局限

**English.** The authors identify teacher scoring and gradient processing as additional training overhead, and the joint evaluation covers at most three domains; broader teacher pools and more domains are future work. Some comparisons use selected checkpoints and report benchmark averages, so they do not establish robustness to different prompt mixtures, teacher quality or optimization settings. The authors state that projection constraints are local statements about the same-trajectory auxiliary loss, not guarantees of auxiliary-domain performance after an optimizer step (§3.3). Reader inference: the choice of target domain, auxiliary teacher and norm floor can alter the trade-off. This summary is AI-assisted and covers the sections listed above.

**中文。** 作者指出，教师打分和梯度处理会增加训练开销；联合评估最多覆盖三个领域，更多领域和更广教师集合留待未来工作。部分比较使用挑选后的检查点并报告基准平均分，因此不能证明对其他提示混合、教师质量或优化设置具有稳健性。作者说明，投影约束只描述同轨迹辅助损失上的局部性质，并不保证优化器更新后的辅助领域表现（§3.3）。读者推断：目标领域、辅助教师和范数下限的选择会改变权衡。本摘要由 AI 辅助生成，覆盖上述列明章节。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:2610.13521](https://arxiv.org/abs/2610.13521). The v2 revision date and HF Daily attention evidence are retained in `../_work/`. Archived PDF and extracted text are the reading sources.

**中文。** 主要来源：[arXiv:2610.13521](https://arxiv.org/abs/2610.13521)。v2 修订日期与 HF Daily 关注证据保存在 `../_work/`。归档 PDF 和提取文本为阅读资料。
