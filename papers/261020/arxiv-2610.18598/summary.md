# Rethinking Projector Training in Multimodal LLMs (PORTAL)

## Metadata and reading scope

**English.** PORTAL is an arXiv preprint posted 13 October 2026 and a NeurIPS 2026 camera-ready paper. HF Daily placement was 15 October, with 11 cumulative votes observed in the archived record. It is included as an adjacent efficient projector-adaptation contribution; it is not a conventional LoRA-style PEFT method. Original: [arXiv](https://arxiv.org/abs/2610.18598), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, Related Work, projector analysis and construction, Experiments, Limitations, and References.

**中文。** PORTAL 是 2026 年 10 月 13 日发布的 arXiv 预印本，也是 NeurIPS 2026 camera-ready 论文。HF Daily 排位日期为 10 月 15 日，归档记录观测到累计 11 票。本文作为高效投影器适配的相邻贡献纳入；它不是传统 LoRA 式 PEFT 方法。原文：[arXiv](https://arxiv.org/abs/2610.18598)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、相关工作、投影器分析与构造、实验、局限和参考文献。

## WHY / Core content / 核心内容

**English.** Standard multimodal LLM training first aligns a vision-language projector on paired image-caption data, then instruction-tunes the model. This can consume substantial alignment data and compute. PORTAL argues that a useful projector can be initialized without paired image-text supervision by matching the marginal feature distributions of the vision and language modalities. The authors first observe that projector alignment gains saturate with relatively small subsets and that multiple projectors trained on different data can lie in a region where their weights interpolate well. PORTAL then derives an affine projector from Gaussian optimal transport. It targets the Stage-I projector initialization step; it does not remove the need for Stage-II multimodal instruction tuning.

**中文。** 标准多模态 LLM 训练先用成对图像-文本数据对齐视觉-语言投影器，再对模型进行指令微调。该流程可能消耗大量对齐数据和计算。PORTAL 认为，可以不依赖成对图文监督，而通过匹配视觉与语言模态的边缘特征分布来初始化有用的投影器。作者先观察到投影器对齐收益在相对较小的数据子集上趋于饱和，并且用不同数据训练的多个投影器可能处于权重可良好插值的区域。随后 PORTAL 从 Gaussian 最优传输推导仿射投影器。它针对 Stage-I 投影器初始化，并未省去 Stage-II 多模态指令微调。

## HOW / Core method / 核心方法

**English.** For image and text feature samples, PORTAL estimates means and covariance matrices, then projects both modalities into a shared top-k principal-component subspace (k=512 in the default configuration). It uses the closed-form Gaussian Bures–Wasserstein optimal-transport map to transform source statistics toward target statistics. In the two-layer LLaVA-style MLP, the resulting affine map is implemented as a linear first layer with a matching bias, while the second layer is initialized to the identity with zero bias. No image-caption pairs or projector gradient updates are needed for this initialization. The construction uses marginal Gaussian moments and a shared PCA basis; it is a distribution-matching initializer, not a learned semantic correspondence model. Standard Stage-II training can follow, and the initializer can also serve as a warm start for a reduced paired-data alignment budget.

**中文。** 对图像和文本特征样本，PORTAL 估计均值与协方差矩阵，再将两个模态投影到共享的 top-k 主成分子空间（默认 k=512）。它使用 Gaussian Bures–Wasserstein 最优传输的闭式映射，将源统计量变换到目标统计量。在两层 LLaVA 风格 MLP 中，所得仿射映射由带对应偏置的第一层线性变换实现，第二层初始化为单位映射且偏置为零。该初始化不需要图像-文本配对，也无需对投影器执行梯度更新。该构造依赖边缘 Gaussian 矩和共享 PCA 基，是分布匹配初始化器，而非学习语义对应关系的模型。之后可继续标准 Stage-II 训练，也可将其作为减少成对数据对齐预算的 warm start。

## WHAT / Evidence / 实验证据

**English.** The main benchmark spans seven vision-encoder/LLM configurations and sixteen evaluation benchmarks (§5, Table 1). PORTAL matches or exceeds the conventional trained-projector baseline in three of seven configurations and reaches 98% of its average performance across the other four (Abstract; §5.1, Table 1). In the Vicuna 1.5 7B/CLIP compute study, approximately 4,000 alignment captions after PORTAL initialization reach the 558,000-caption trained baseline, at about 135× fewer projector-alignment FLOPs (§5.2, Fig. 4). The paper also reports that PORTAL remains effective under larger Stage-II instruction tuning and on POPE hallucination evaluation (Appendix E.3–E.4, Tables 12–13). These results cover a two-layer projector and the evaluated vision-language configurations; they do not establish that Gaussian marginal matching replaces paired alignment in all architectures or tasks.

**中文。** 主要基准涵盖七种视觉编码器/LLM 配置和十六个评测基准（§5，表 1）。PORTAL 在七种配置中的三种达到或超过传统训练投影器基线；其余四种的平均表现达到基线的 98%（摘要；§5.1，表 1）。在 Vicuna 1.5 7B/CLIP 计算实验中，PORTAL 初始化后使用约 4,000 条对齐 caption，即达到使用 558,000 条 caption 训练的基线，投影器对齐 FLOPs 约减少 135 倍（§5.2，图 4）。论文还报告 PORTAL 在更大规模 Stage-II 指令微调及 POPE 幻觉评测中仍有效（附录 E.3–E.4，表 12–13）。这些结果针对两层投影器和被测视觉语言配置，尚未证明 Gaussian 边缘分布匹配能在所有架构或任务中取代成对对齐。

## Foundations / 基础关系

**English.** The mathematical construction uses the Gaussian Bures–Wasserstein optimal-transport map, supported by Bhatia, Jain and Lim, [On the Bures–Wasserstein Distance Between Positive Definite Matrices](../arxiv-1712.01504/summary.md) ([original](../arxiv-1712.01504/original.pdf)). The paper also identifies CORAL as the closest unpaired statistical-alignment approach and explicitly says PORTAL “extends this idea” to multimodal projector alignment (§2). The corresponding foundation is Sun and Saenko’s [Deep CORAL: Correlation Alignment for Deep Domain Adaptation](../arxiv-1607.01719/summary.md) ([original](../arxiv-1607.01719/original.pdf)). PORTAL changes the construction to a shared-subspace closed-form Gaussian OT projector.

**中文。** 数学构造使用 Gaussian Bures–Wasserstein 最优传输映射，其基础文献为 Bhatia、Jain 和 Lim 的[《On the Bures–Wasserstein Distance Between Positive Definite Matrices》](../arxiv-1712.01504/summary.md)（[原文](../arxiv-1712.01504/original.pdf)）。论文还将 CORAL 称为最接近的无配对统计对齐方法，并明确说 PORTAL 将该思路“扩展”到多模态投影器对齐（§2）。对应基础文献为 Sun 和 Saenko 的[《Deep CORAL: Correlation Alignment for Deep Domain Adaptation》](../arxiv-1607.01719/summary.md)（[原文](../arxiv-1607.01719/original.pdf)）。PORTAL 将构造改为共享子空间中的闭式 Gaussian OT 投影器。

## Limitations / 局限

**English.** The empirical analysis centers on the LLaVA 1.5 two-layer MLP projector. The method matches Gaussian means and covariances but omits higher-order structure; the authors note residual gaps concentrated in OCR and Chart cases, where character-level spatial structure may matter. The vision encoder remains frozen in the reported experiments, the benchmark suite inherits its existing biases, and audio/video alignment is not evaluated (Limitations). The authors describe this as an existence proof rather than a finished construction. Reader inference: the fit may change for resampler or cross-attention projectors and when both modalities are updated. This summary is AI-assisted and based on the listed full-text sections.

**中文。** 实证分析集中于 LLaVA 1.5 两层 MLP 投影器。该方法匹配 Gaussian 均值与协方差，但忽略更高阶结构；作者指出残余差距集中于 OCR 和 Chart 场景，字符级空间结构可能对此重要。报告实验冻结视觉编码器，基准集继承既有偏差，且未评测音频/视频对齐（局限部分）。作者将其称为存在性证明，而非完整构造。读者推断：在 resampler 或 cross-attention 投影器上，以及同时更新两种模态时，拟合效果可能不同。本摘要由 AI 辅助生成，基于上述全文章节。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:2610.18598](https://arxiv.org/abs/2610.18598). HF Daily attention date and observed cumulative votes are preserved in `../_work/`. The archived PDF and extracted text are the reading sources.

**中文。** 主要来源：[arXiv:2610.18598](https://arxiv.org/abs/2610.18598)。HF Daily 关注日期和观测到的累计票数保存在 `../_work/`。归档 PDF 和提取文本为阅读资料。
