# On the Bures-Wasserstein Distance Between Positive Definite Matrices

## Metadata and reading scope

**English.** Rajendra Bhatia, Tanvi Jain and Yongdo Lim, arXiv:1712.01504v1, submitted 5 December 2017; published in Expositiones Mathematicae in 2019. Original: [arXiv](https://arxiv.org/abs/1712.01504), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, Variational Principles, Bures–Wasserstein metric properties, matrix means/barycentres, and References. PORTAL cites this work for the Bures–Wasserstein mathematics behind its Gaussian transport projector.

**中文。** Rajendra Bhatia、Tanvi Jain 和 Yongdo Lim，arXiv:1712.01504v1，2017 年 12 月 5 日提交；2019 年发表于 Expositiones Mathematicae。原文：[arXiv](https://arxiv.org/abs/1712.01504)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、变分原理、Bures–Wasserstein 度量性质、矩阵均值/重心和参考文献。PORTAL 引用该文作为 Gaussian 传输投影器所用 Bures–Wasserstein 数学基础。

## WHY / Core content / 核心内容

**English.** The paper studies a metric on positive semidefinite/definite matrices that appears in optimal transport, statistics, quantum information and Riemannian geometry. For covariance matrices, the Bures–Wasserstein distance provides a geometry-aware measure of distributional difference that accounts for both matrix scale and orientation. The authors organize matrix-analysis results and variational characterizations, and develop means and barycentres under this metric. It is a mathematical foundations paper, not a machine-learning algorithm or empirical model evaluation.

**中文。** 论文研究正半定/正定矩阵上的一种度量，它出现在最优传输、统计学、量子信息和黎曼几何中。对协方差矩阵而言，Bures–Wasserstein 距离提供一种考虑矩阵尺度和方向的几何分布差异度量。作者整理矩阵分析结果和变分刻画，并发展该度量下的均值与重心理论。这是一篇数学基础论文，不是机器学习算法或经验模型评测。

## HOW / Core method / 核心方法

**English.** For positive matrices A and B, the squared distance is d²(A,B)=tr(A)+tr(B)−2tr((A¹ᐟ²BA¹ᐟ²)¹ᐟ²) (§1, Eq. 1). Theorem 1 gives an equivalent factor-space characterization: minimize the Frobenius distance between matrix square-root factors over unitary rotations (§2, Eq. 3). The minimizing rotation is determined by the polar decomposition. The paper uses this representation to connect the metric to Procrustes alignment and develops variational forms for fidelity and matrix means. These facts support optimal-transport constructions between Gaussian distributions whose covariance matrices are positive definite.

**中文。** 对正矩阵 A、B，平方距离为 d²(A,B)=tr(A)+tr(B)−2tr((A¹ᐟ²BA¹ᐟ²)¹ᐟ²)（§1，式 1）。定理 1 给出等价的因子空间刻画：在酉旋转上最小化矩阵平方根因子之间的 Frobenius 距离（§2，式 3）。最优旋转由极分解确定。论文利用该表示将度量与 Procrustes 对齐联系起来，并发展 fidelity 和矩阵均值的变分形式。这些结果可支持协方差矩阵正定的 Gaussian 分布之间的最优传输构造。

## WHAT / Evidence / 实验证据

**English.** This is a theoretical matrix-analysis paper and does not report model benchmarks. Its evidence consists of proofs and equivalent characterizations of the distance, its metric properties, variational principles, and barycentre constructions (§§2–5). PORTAL uses the cited Bures–Wasserstein closed-form Gaussian transport construction to derive its affine projector parameters (§2 and §4.1 of [PORTAL](../arxiv-2610.18598/summary.md); [original](../arxiv-2610.18598/original.pdf)). The empirical validation belongs to PORTAL, not this mathematical source.

**中文。** 这是一篇矩阵分析理论论文，不报告模型基准。其论证证据由距离的证明与等价刻画、度量性质、变分原理和重心构造组成（§§2–5）。PORTAL 使用其引用的 Bures–Wasserstein Gaussian 传输闭式构造推导仿射投影器参数（[PORTAL](../arxiv-2610.18598/summary.md)的 §2 和 §4.1；[原文](../arxiv-2610.18598/original.pdf)）。经验验证属于 PORTAL，而非这篇数学基础文献。

## Foundations / 基础关系

**English.** PORTAL explicitly says its projector construction exploits the Bures–Wasserstein covariance map (§2, §4.1). This paper supplies the matrix-geometric distance and polar-factor characterization; PORTAL specializes Gaussian optimal transport to source/target modality feature statistics in a shared PCA subspace. That application is a use of the mathematical construction, not a result established by Bhatia et al.

**中文。** PORTAL 明确说明其投影器构造利用 Bures–Wasserstein 协方差映射（§2、§4.1）。本文提供矩阵几何距离及极因子刻画；PORTAL 将 Gaussian 最优传输特化到共享 PCA 子空间中的源/目标模态特征统计量。该应用是对数学构造的使用，并非 Bhatia 等人在原文中建立的结果。

## Limitations / 局限

**English.** The paper’s framework concerns positive (semi)definite matrices and matrix geometry. Applying it to empirical feature distributions requires choices about covariance estimation, rank, regularization and distributional assumptions. It does not establish that Gaussian moment matching is sufficient for multimodal semantic alignment. Reader inference: singular empirical covariances may require restricting to a positive subspace or regularization. Summary covers the listed mathematical sections and is AI-assisted.

**中文。** 论文框架针对正（半）定矩阵和矩阵几何。将其用于经验特征分布时，需要选择协方差估计、秩、正则化和分布假设。它没有证明 Gaussian 矩匹配足以实现多模态语义对齐。读者推断：奇异经验协方差可能需要限制到正定子空间或进行正则化。本摘要覆盖列明数学章节，由 AI 辅助生成。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:1712.01504](https://arxiv.org/abs/1712.01504). Archived PDF and extracted text are the source material.

**中文。** 主要来源：[arXiv:1712.01504](https://arxiv.org/abs/1712.01504)。归档 PDF 和提取文本为资料来源。
