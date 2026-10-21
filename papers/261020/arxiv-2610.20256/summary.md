# Long-Horizon RL Needs Muon

## Metadata and reading scope

**English.** Kai Ruan et al., arXiv:2610.20256v1, submitted 14 October 2026 (cs.LG). HF Daily placement was 15 October; the discovery record observed 30 cumulative votes. The manuscript labels itself “Work in progress.” Original: [arXiv page](https://arxiv.org/abs/2610.20256), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, Related Work, Muon-based optimization method, outcome/reward and importance-correction methods, experimental setup/results, conclusion, and references.

**中文。** Kai Ruan 等，arXiv:2610.20256v1，2026 年 10 月 14 日提交（cs.LG）。HF Daily 排位日期为 10 月 15 日；发现记录观测到累计 30 票。稿件自称“Work in progress”。原文：[arXiv 页面](https://arxiv.org/abs/2610.20256)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、相关工作、Muon 优化方法、结果奖励与重要性修正方法、实验设置和结果、结论及参考文献。

## WHY / Core content / 核心内容

**English.** Long-horizon software agents receive sparse terminal feedback, generate trajectories of different lengths, and collect rollouts asynchronously while the policy changes. The authors study whether Muon can work within a single-rollout asynchronous policy-optimization recipe for repository issue resolution. This is an empirical optimization study, not a new standalone RL objective: it compares Adam and Muon within SPO, then combines Muon with SPO++, token-averaged loss, truncated importance sampling, and length/tool-error reward shaping. The claimed result is that the full recipe reaches higher training success in the evaluated runs than the SPO baselines. Because several recipe components change together in the main comparison, the paper does not isolate the contribution of Muon to that overall gain.

**中文。** 长时程软件智能体得到稀疏的终局反馈，轨迹长度不一，并在策略持续变化时异步收集 rollout。作者研究 Muon 能否用于面向代码仓库 issue 修复的单 rollout 异步策略优化配方。这是一项经验性优化研究，而非新的独立 RL 目标：论文先在 SPO 中比较 Adam 与 Muon，再将 Muon 与 SPO++、token 平均损失、截断重要性采样以及长度/工具错误奖励塑形组合。论文声称完整配方在所测训练运行中比 SPO 基线取得更高成功率。由于主要对照同时改变了多个配方组件，论文没有单独识别 Muon 对总体增益的贡献。

## HOW / Core method / 核心方法

**English.** Each issue produces one agent rollout while asynchronous training updates continue. The final patch receives a binary reward based on passing all fail-to-pass and pass-to-pass tests. Tool errors can receive a −0.5 penalty; an overlong turn incurs a length penalty that reaches −0.5 past 2,048 tokens, subject to a trajectory cap. SPO++ standardizes advantages over valid action tokens. The learner applies truncated importance sampling with cap C=2 to correct for mismatch between sampling and pre-update policies, then uses token-mean policy loss. For matrix hidden-layer parameters, Muon applies approximate Newton–Schulz orthogonalization to a momentum update; embeddings, output head, normalization and vector parameters use AdamW. The paper’s local spectral-norm interpretation characterizes a direction proportional to −UVᵀ for a compact SVD of the gradient; it is not a proof that this combined RL recipe is generally superior.

**中文。** 每个 issue 只产生一条 agent rollout，同时异步训练持续更新策略。最终补丁若通过全部 fail-to-pass 与 pass-to-pass 测试，则获得二值奖励。工具错误可获 −0.5 惩罚；超过 2,048 token 的过长轮次会产生长度惩罚，但轨迹总惩罚有上限。SPO++ 对有效动作 token 的优势做标准化。学习器采用上限 C=2 的截断重要性采样，修正采样策略与更新前策略之间的偏差，然后使用 token 平均的策略损失。对隐藏层矩阵参数，Muon 对动量更新施加近似 Newton–Schulz 正交化；embedding、输出头、归一化参数和向量参数仍用 AdamW。论文的局部谱范数解释将更新方向刻画为梯度紧致 SVD 下与 −UVᵀ 成比例的方向；这并不能证明该组合 RL 配方普遍更优。

## WHAT / Evidence / 实验证据

**English.** Experiments use repository issue-resolution tasks from R2E-Gym with the Claude Code harness version 2.1.118 and two model families, MiniCPM5-2B and Qwen3.5-4B (§4.1). Runs collect their own trajectories asynchronously; matched comparisons use the same seed, and the paper summarizes selected runs and late-training success. The full SPO++ + Muon recipe is reported above the SPO + Adam and SPO + Muon baselines later in training for both model families (§4.2, Fig. 3; recipe component results in Figs. 4–5). Several Adam configurations collapse in the displayed selected runs (Figs. 4–5). Ablations show that removing reward penalties or changing token/sequence averaging changes success substantially, and that outcomes vary across seeds when length penalties are absent (§4.2, Figs. 4–5). These results support further investigation of the full recipe, but are limited by selected runs, two models, one software-repair setting, and jointly changed components.

**中文。** 实验使用 R2E-Gym 的代码仓库 issue 修复任务，搭配 Claude Code harness 2.1.118 和两个模型族：MiniCPM5-2B 与 Qwen3.5-4B（§4.1）。各运行异步收集自身轨迹；匹配对照使用相同随机种子，论文汇总的是挑选出的运行及训练后段成功率。两种模型的完整 SPO++ + Muon 配方在后期训练阶段均高于 SPO + Adam 和 SPO + Muon 基线（§4.2，图 3；配方组件结果见图 4–5）。图示的若干 Adam 配置出现崩溃（图 4–5）。消融结果显示，移除奖励惩罚或改变 token/sequence 平均方式会显著改变成功率；没有长度惩罚时，结果会随随机种子变化（§4.2，图 4–5）。这些结果支持进一步研究完整配方，但受限于选定运行、两种模型、单一软件修复场景以及多组件同时改变。

## Foundations / 基础关系

**English.** The paper explicitly says its recipe follows SPO++ for standardizing advantages over valid tokens and cites Ruan et al., [SPO++: Stream-Aligned Policy Optimization for Asynchronous Agentic RL](../arxiv-2608.24870/summary.md) ([original](../arxiv-2608.24870/original.pdf)). It adapts that single-rollout asynchronous policy-learning base to repository repair, then studies Muon and additional reward/importance-correction components. The paper’s Muon reference is Keller Jordan et al.’s author technical blog, [Muon: An optimizer for hidden layers in neural networks](https://kellerjordan.github.io/posts/muon/); this is not a registered paper foundation in this run.

**中文。** 论文明确称其配方沿用 SPO++ 对有效 token 优势进行标准化，并引用 Ruan 等人的[SPO++: Stream-Aligned Policy Optimization for Asynchronous Agentic RL](../arxiv-2608.24870/summary.md)（[原文](../arxiv-2608.24870/original.pdf)）。本文将这一单 rollout 异步策略学习基础用于代码仓库修复，再研究 Muon 以及额外的奖励/重要性修正组件。论文对 Muon 的引用是 Keller Jordan 等人的作者技术博客[《Muon: An optimizer for hidden layers in neural networks》](https://kellerjordan.github.io/posts/muon/)；本次未将其登记为论文型基础文献。

## Limitations / 局限

**English.** The manuscript marks itself as work in progress. It covers two model families and one execution-based software-repair environment; it reports selected training runs rather than a broad seed distribution. The conclusion attributes the main gain to the combined recipe, and the authors note that component effects interact. Therefore the title’s “Needs Muon” should be read as a motivating empirical result in this setup, not a general theorem or settled optimizer recommendation. Additional evidence would need controlled comparisons that vary only the optimizer and broader tasks/models. Summary covers the sections listed above; no claim of human reading is made.

**中文。** 稿件标注为进行中的工作。评测涵盖两个模型族和一个基于执行反馈的软件修复环境；报告的是挑选的训练运行，而非广泛的随机种子分布。结论把主要增益归于组合配方，作者也指出各组件效果相互影响。因此标题中的“Needs Muon”应理解为该设置下的经验性动机结果，而不是普遍定理或已确立的优化器建议。进一步证据需要只改变优化器的受控对照，以及更广泛的任务和模型。本摘要覆盖上述列明章节，不声称由人类阅读。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:2610.20256](https://arxiv.org/abs/2610.20256). HF Daily attention date and cumulative vote observation are recorded in `../_work/`. This is an AI-assisted summary of the archived PDF and extracted text.

**中文。** 主要来源：[arXiv:2610.20256](https://arxiv.org/abs/2610.20256)。HF Daily 关注日期和累计票数观测记录于 `../_work/`。本摘要由 AI 辅助阅读归档 PDF 与提取文本后生成。
