# LoRA: Low-Rank Adaptation of Large Language Models

## Metadata and reading scope

**English.** Edward J. Hu et al., arXiv:2106.09685v2, first submitted 17 June 2021; published at ICLR 2022. Original: [arXiv](https://arxiv.org/abs/2106.09685), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, Problem Statement, Method, Practical Benefits and Limitations, Empirical Experiments, and References. This is the original low-rank adaptation method used by BrainLoRA.

**中文。** Edward J. Hu 等，arXiv:2106.09685v2，首次提交于 2021 年 6 月 17 日；发表于 ICLR 2022。原文：[arXiv](https://arxiv.org/abs/2106.09685)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、问题定义、方法、实际收益与局限、实验和参考文献。这是 BrainLoRA 使用的原始低秩适配方法。

## WHY / Core content / 核心内容

**English.** Full fine-tuning stores and updates a separate copy of every pretrained parameter for each downstream task. For very large models this creates substantial optimizer-state, memory, checkpoint and deployment costs. LoRA hypothesizes that task-specific changes to pretrained weights have low intrinsic rank. It freezes the pretrained matrix and learns a low-rank update, allowing many task adapters to share the original model. Unlike many adapter modules, the low-rank update can be merged into the weight matrix for inference, avoiding added sequential layers. The paper contributes a parameterization and empirical study, not a claim that every task’s ideal update is exactly low-rank.

**中文。** 全量微调需要为每项下游任务保存并更新每个预训练参数的副本。对超大模型，这会带来显著的优化器状态、显存、检查点和部署成本。LoRA 假设预训练权重的任务特定变化具有低内在秩。它冻结预训练矩阵，只学习一个低秩更新，使许多任务适配器可以共享原模型。与许多 adapter 模块不同，低秩更新可在推理时合并进权重矩阵，避免新增串行层。论文贡献的是一种参数化方法及其实证研究，并未声称每个任务的理想更新都严格低秩。

## HOW / Core method / 核心方法

**English.** For a pretrained weight matrix W₀ ∈ ℝᵈˣᵏ, LoRA constrains the update as ΔW = BA, where B ∈ ℝᵈˣʳ and A ∈ ℝʳˣᵏ, with r ≪ min(d,k). The forward operation is h = W₀x + BAx; W₀ stays frozen while A and B are trainable. A is initialized randomly and B to zero, so the adapter initially preserves the base model. The update is scaled by α/r. The authors mainly adapt attention projection matrices in Transformers. At deployment, W₀+BA can be materialized into one ordinary matrix; task switching then replaces the low-rank component. LoRA can be combined with standard optimizers such as Adam.

**中文。** 对预训练权重矩阵 W₀ ∈ ℝᵈˣᵏ，LoRA 将更新限制为 ΔW = BA，其中 B ∈ ℝᵈˣʳ、A ∈ ℝʳˣᵏ，且 r ≪ min(d,k)。前向计算为 h = W₀x + BAx；W₀ 冻结，只训练 A 和 B。A 随机初始化、B 初始化为零，因此适配器起始时保持基座模型不变。更新按 α/r 缩放。作者主要适配 Transformer 注意力投影矩阵。部署时可将 W₀+BA 实体化为普通矩阵；切换任务时只需替换低秩分量。LoRA 可与 Adam 等标准优化器结合。

## WHAT / Evidence / 实验证据

**English.** Experiments cover RoBERTa, DeBERTa, GPT-2 and GPT-3. On GPT-3 175B, the paper reports up to 10,000× fewer trainable parameters and a threefold reduction in GPU memory compared with Adam full fine-tuning (Abstract; §5.4 and Fig. 2). On GLUE, LoRA is competitive with or better than full fine-tuning across the tested RoBERTa and DeBERTa configurations (Table 2); on GPT-2 E2E NLG it is competitive with full fine-tuning and other adaptation baselines (Table 3). Results support the method across these NLP workloads, while remaining tied to the evaluated architectures, tasks, ranks and training recipes.

**中文。** 实验涵盖 RoBERTa、DeBERTa、GPT-2 和 GPT-3。对 GPT-3 175B，论文报告相较 Adam 全量微调，可将可训练参数最多减少 10,000 倍，并将 GPU 显存需求降至三分之一（摘要；§5.4 和图 2）。在 GLUE 上，LoRA 在所测 RoBERTa 与 DeBERTa 配置中与全量微调相当或更好（表 2）；在 GPT-2 E2E NLG 上，LoRA 与全量微调及其他适配基线具有竞争力（表 3）。结果支持其在这些 NLP 工作负载中的效果，但仍取决于被测架构、任务、秩和训练配方。

## Foundations / 基础关系

**English.** BrainLoRA inserts rank-16 LoRA modules into the attention layers of Qwen3-Omni (§4 of [Scaling Parameter-Efficient Fine-Tuning for Brain Encoding](../arxiv-2610.26802/summary.md); [original](../arxiv-2610.26802/original.pdf)). It inherits the frozen-base plus trainable low-rank update parameterization, then combines it with a neural readout and a multi-adapter training kernel. Brain-encoding setup and kernel are the newer paper’s contributions; the LoRA mechanism is not.

**中文。** BrainLoRA 在 Qwen3-Omni 注意力层中插入 rank-16 LoRA 模块（[《Scaling Parameter-Efficient Fine-Tuning for Brain Encoding》](../arxiv-2610.26802/summary.md)的 §4；[原文](../arxiv-2610.26802/original.pdf)）。它继承冻结基座加可训练低秩更新的参数化，再与神经 readout 和多适配器训练内核结合。脑编码设置和内核是新论文的贡献；LoRA 机制本身不是。

## Limitations / 局限

**English.** The original experiments mainly adapt selected attention matrices and study a finite set of NLP tasks. Low rank constrains the update and may require higher rank or different target modules for harder tasks. Merging weights removes added inference depth, but batching examples that use different adapters is not straightforward (§4, Practical Benefits and Limitations). Reader inference: later PEFT variants may change implementation trade-offs, but they do not invalidate this original mechanism. The summary is AI-assisted and covers the listed sections.

**中文。** 原始实验主要适配选定注意力矩阵，并研究有限数量的 NLP 任务。低秩会限制更新，复杂任务可能需要更高秩或不同目标模块。合并权重可避免额外推理深度，但让一个批次中的样本使用不同适配器并不简单（§4“实际收益与局限”）。读者推断：后续 PEFT 变体可能改变实现取舍，但不改变这一原始机制。本摘要由 AI 辅助生成，覆盖列明章节。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:2106.09685](https://arxiv.org/abs/2106.09685). Archived PDF and extracted text are the source material.

**中文。** 主要来源：[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)。归档 PDF 和提取文本为资料来源。
