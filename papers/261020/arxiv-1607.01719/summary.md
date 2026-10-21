# Deep CORAL: Correlation Alignment for Deep Domain Adaptation

## Metadata and reading scope

**English.** Baochen Sun and Kate Saenko, arXiv:1607.01719v1, submitted 6 July 2016. Original: [arXiv](https://arxiv.org/abs/1607.01719), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, Related Work, Deep CORAL method, Experiments, and Conclusion. PORTAL explicitly says it extends CORAL’s moment-alignment idea to multimodal projector alignment.

**中文。** Baochen Sun 和 Kate Saenko，arXiv:1607.01719v1，2016 年 7 月 6 日提交。原文：[arXiv](https://arxiv.org/abs/1607.01719)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、相关工作、Deep CORAL 方法、实验和结论。PORTAL 明确表示其将 CORAL 的矩对齐思想扩展到多模态投影器对齐。

## WHY / Core content / 核心内容

**English.** A classifier trained on a labeled source domain can perform poorly when the target domain is unlabeled and has a shifted feature distribution. CORAL aligns source and target second-order statistics through a linear transformation. Deep CORAL integrates that idea into a deep network with a differentiable covariance-alignment loss, allowing feature representations to adapt jointly with the task classifier. It is an unsupervised domain adaptation objective: source labels supervise the task, while unlabeled target examples shape feature correlations. The central contribution is a simple end-to-end correlation loss that can be attached to deep layers.

**中文。** 在有标签源域训练的分类器，面对无标签且特征分布偏移的目标域时可能表现不佳。CORAL 通过线性变换对齐源域与目标域的二阶统计量。Deep CORAL 将这一思想集成到深度网络中，使用可微协方差对齐损失，使特征表示与任务分类器联合适配。它是一种无监督领域适应目标：源域标签监督任务，目标域无标签样本则约束特征相关性。其核心贡献是可附加到深层特征上的简单端到端相关性损失。

## HOW / Core method / 核心方法

**English.** For source feature matrix Dˢ and target feature matrix Dᵗ at a layer, the method computes sample covariance matrices Cˢ and Cᵗ. The CORAL loss is ℓCORAL = (1/(4d²))‖Cˢ−Cᵗ‖²F, where d is the feature dimension (§3.1, Eq. 1). A standard source classification loss is combined with this covariance penalty. In the reported architecture the same CNN processes source and target examples with shared parameters, and the CORAL loss is applied at a selected layer; other layers can be used as well. The target examples need no labels, and covariance estimates are computed from minibatches.

**中文。** 对某一层的源域特征矩阵 Dˢ 和目标域特征矩阵 Dᵗ，方法计算样本协方差 Cˢ、Cᵗ。CORAL 损失定义为 ℓCORAL = (1/(4d²))‖Cˢ−Cᵗ‖²F，其中 d 是特征维度（§3.1，式 1）。标准源域分类损失与该协方差惩罚相加。报告架构使用共享参数的同一 CNN 处理源域和目标域样本，并在选定层施加 CORAL 损失；也可选择其他层。目标域样本无需标签，协方差由 minibatch 估计。

## WHAT / Evidence / 实验证据

**English.** The experiments use BVLC Reference CaffeNet with CORAL loss at the final `fc8` classifier layer on all six Office source-to-target shifts (§4). Deep CORAL obtains a 72.1% average accuracy, compared with 70.1% for the source-only CNN and 71.3% for DAN; it is best on three of six individual shifts (Table 1). Figure 2 diagnoses the A→W shift by plotting source/target accuracy, training losses and covariance distance during optimization. The paper says other layers and architectures should be straightforward to support, but does not evaluate those variants. Results therefore support covariance alignment in this benchmark and implementation, not a claim that matching second moments is sufficient for every domain shift.

**中文。** 实验使用 BVLC Reference CaffeNet，在 Office 六种源域到目标域迁移上将 CORAL 损失施加于最后的 `fc8` 分类层（§4）。Deep CORAL 平均准确率为 72.1%，仅源域 CNN 为 70.1%，DAN 为 71.3%；在六个单独迁移中的三个上取得最佳成绩（表 1）。图 2 针对 A→W 迁移，展示训练期间源/目标准确率、训练损失及协方差距离的变化。论文称其他层和架构也可支持，但没有评测这些变体。因此，结果支持该基准与实现中的协方差对齐，并不代表匹配二阶统计量足以处理所有领域偏移。

## Foundations / 基础关系

**English.** PORTAL calls CORAL the closest prior unpaired statistical-alignment method and explicitly states that it extends the idea to multimodal alignment (§2 of [PORTAL](../arxiv-2610.18598/summary.md); [original](../arxiv-2610.18598/original.pdf)). Deep CORAL aligns learned feature covariance distributions with a differentiable loss; PORTAL instead constructs a closed-form affine projector from Gaussian statistics in a shared principal subspace. The relationship is explicit conceptual inspiration, with a different initialization mechanism and target setting.

**中文。** PORTAL 将 CORAL 称为最接近的既有无配对统计对齐方法，并明确说明它将该思路扩展到多模态对齐（[PORTAL](../arxiv-2610.18598/summary.md)的 §2；[原文](../arxiv-2610.18598/original.pdf)）。Deep CORAL 用可微损失对齐学习到的特征协方差分布；PORTAL 则在共享主成分子空间中，根据 Gaussian 统计量构造闭式仿射投影器。二者是明确的概念启发，但构造机制和目标场景不同。

## Limitations / 局限

**English.** The authors evaluate one architecture, BVLC Reference CaffeNet, with CORAL applied at `fc8` on the Office benchmark. The paper does not test whether the same gains transfer to other layers or network architectures, although it describes that extension as straightforward. CORAL aligns covariance and cannot by itself guarantee that source and target class-conditional distributions match; it also requires unlabeled target samples during adaptation. Reader inference: with small batches or high-dimensional activations, covariance estimates may be noisy or expensive. Summary covers the listed full-text sections and is AI-assisted.

**中文。** 作者只在 Office 基准上评测一种架构 BVLC Reference CaffeNet，并将 CORAL 施加于 `fc8`。论文没有测试相同收益能否迁移到其他层或网络架构，尽管作者称扩展并不困难。CORAL 对齐协方差，本身无法保证源域与目标域的类条件分布相同；适应时也需要无标签目标样本。读者推断：batch 较小或激活维度较高时，协方差估计可能噪声较大或计算开销较高。本摘要覆盖列明全文章节，由 AI 辅助生成。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:1607.01719](https://arxiv.org/abs/1607.01719). Archived PDF and extracted text are the source material.

**中文。** 主要来源：[arXiv:1607.01719](https://arxiv.org/abs/1607.01719)。归档 PDF 和提取文本为资料来源。
