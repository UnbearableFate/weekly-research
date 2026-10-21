# STRAP: Robot Sub-Trajectory Retrieval for Augmented Policy Learning

## Metadata and reading scope

**English.** Marius Memmel, Jacob Berg, Bingqing Chen, Abhishek Gupta, and Jonathan Francis. arXiv:2412.15182, first submitted 19 December 2024; the archived v2 is dated 18 August 2025. Published as an ICLR 2025 conference paper. Primary sources: [arXiv record and versions](https://arxiv.org/abs/2412.15182), [ICLR/OpenReview PDF](https://openreview.net/pdf?id=MXNoOqBNLZ). Read: abstract, Introduction, §§2–6, and experimental tables in Appendix A.

**中文。** Marius Memmel、Jacob Berg、Bingqing Chen、Abhishek Gupta 和 Jonathan Francis。arXiv:2412.15182，首版提交于 2024 年 12 月 19 日；归档 v2 日期为 2025 年 8 月 18 日。发表于 ICLR 2025。主要来源：[arXiv 记录和版本](https://arxiv.org/abs/2412.15182)、[ICLR/OpenReview PDF](https://openreview.net/pdf?id=MXNoOqBNLZ)。已读：摘要、引言、§§2–6 及附录 A 的实验表格。

## WHY / Core content / 核心内容

**English.** A broad offline robotics corpus can improve average multi-task performance while still transferring poorly to a particular target task. Collecting enough demonstrations for each new task is expensive, and retrieving only whole trajectories or isolated states misses reusable actions embedded inside otherwise unrelated tasks. STRAP studies few-shot imitation learning at deployment: given a small set of target-task demonstrations, find useful sub-trajectories in a larger offline corpus and train a task-specific policy on the combined data. The paper’s core idea is to use semantically useful visual features and temporally aligned sub-sequence retrieval to reuse low-level behavior across tasks.

**中文。** 大规模离线机器人数据可提升多任务平均表现，但迁移到某个具体目标任务时仍可能效果不佳。为每个新任务收集足够示范成本很高，而只检索完整轨迹或单个状态会漏掉嵌在其他任务中的可复用动作片段。STRAP 研究部署阶段的小样本模仿学习：给定少量目标任务示范，从更大的离线语料中寻找有用子轨迹，并用合并数据训练专用策略。核心思路是结合具有语义信息的视觉特征与时间对齐的子序列检索，在不同任务之间复用低层行为。

## HOW / Core method / 核心方法

**English.** STRAP assumes that the prior corpus contains expert trajectories and matches the target embodiment, though tasks and scenes may differ (§4.1). It automatically segments only the small target demonstrations, using low end-effector velocity as a motion-transition heuristic (§4.2). A vision foundation model such as DINOv2 or CLIP embeds image frames; frame-level L2 distances form a visual cost matrix (§4.3, Eq. 2). S-DTW then aligns each target chunk to a variable-length subsequence in the larger prior trajectories, allowing the match to begin and end inside a reference trajectory (§3.1; §4.4). The method retrieves the lowest-cost matches, distributed uniformly across target chunks, retains their language instructions, and combines them with the target demonstrations. A language-conditioned behavior-cloning policy is trained on this augmented set (§4.5, Algorithm 1). STRAP is a data-retrieval and policy-training procedure; it does not propose a new optimizer or parameter-efficient update rule.

**中文。** STRAP 假设先验语料含有专家轨迹，且与目标任务使用相同机器人本体，但任务和场景可以不同（§4.1）。它只自动切分少量目标示范，并用末端执行器低速状态作为动作片段转折的启发式信号（§4.2）。DINOv2 或 CLIP 等视觉基础模型将图像帧嵌入特征空间；帧级 L2 距离构成视觉代价矩阵（§4.3，式 2）。随后 S-DTW 将每个目标片段对齐到较大先验轨迹中的可变长度子序列，匹配可以从参考轨迹内部开始和结束（§3.1、§4.4）。方法按代价选取低成本匹配，并在目标片段间均匀分配，保留对应语言指令后与目标示范合并。最终使用语言条件行为克隆策略在增强数据集上训练（§4.5，算法 1）。STRAP 是数据检索与策略训练流程，并未提出新优化器或参数高效更新规则。

## WHAT / Evidence / 实验证据

**English.** In LIBERO-10 simulation, STRAP uses five target demonstrations and 4,500 prior trajectories. With task-tuned K, it reaches 58.1% ± 32.0 average success across the benchmark, compared with 51.7% ± 35.7 for fine-tuning from the prior corpus (Table 1, §5.1–5.2); the authors report that STRAP is 6.4 percentage points higher. With fixed K=100, DINOv2 STRAP scores 45.6% ± 32.6, illustrating that retrieval quantity matters and the best K is task-dependent (Table 1; §5.2). In the real DROID-Kitchen evaluation, STRAP’s normalized partial/full success scores for Table, Sink, and Stove are 36.36, 61.36, and 57.12 in the Kitchen setting, and 56.81, 63.04, and 45.45 with the larger Kitchen+DROID prior corpus; the corresponding behavior-cloning scores are 12.50, 10.00, and 14.28 in both settings (Table 2, §5.2). In the separate Franka Pen-in-Cup experiment, STRAP obtains 100% pick and 100% place success on the OOD condition, while BC obtains 0% for both; on the base condition STRAP scores 100%/90% versus BC’s 100%/100% (Appendix A.2.1, Table 4). These evaluations support retrieval augmentation in the tested settings, not across arbitrary robots or tasks.

**中文。** 在 LIBERO-10 仿真中，STRAP 使用 5 条目标示范和 4,500 条先验轨迹。按任务调节 K 时，它在基准上的平均成功率为 58.1% ± 32.0，而从先验语料微调的结果为 51.7% ± 35.7（§5.1–5.2，表 1）；作者报告 STRAP 高 6.4 个百分点。固定 K=100 时，DINOv2 版本 STRAP 为 45.6% ± 32.6，说明检索数量会影响结果，最佳 K 取决于任务（§5.2，表 1）。在真实 DROID-Kitchen 评测中，STRAP 在 Kitchen 场景下 Table、Sink、Stove 三项任务的归一化部分/完整成功分数为 36.36、61.36、57.12；使用更大的 Kitchen+DROID 先验语料时为 56.81、63.04、45.45。对应行为克隆在两种设置下均为 12.50、10.00、14.28（§5.2，表 2）。在另一个 Franka Pen-in-Cup 实验中，STRAP 在 OOD 条件下的抓取和放置成功率为 100% 和 100%，BC 两项均为 0%；在基础条件下 STRAP 为 100%/90%，BC 为 100%/100%（附录 A.2.1，表 4）。这些评测支持检索增强在所测设置中的作用，不能证明其适用于任意机器人或任务。

## Foundations / 基础关系

**English.** The later [Learning from Fleet Experience: A Collective Learning Paradigm for Robots](../arxiv-2610.25736/summary.md) directly cites STRAP as reference [27] for the slope-constrained S-DTW used in FERT retrieval: “using slope-constrained subsequence dynamic time warping (S-DTW) [27]” (§3.1.3, Step 3: Failure-guided retrieval; see the [original](../arxiv-2610.25736/original.pdf)). FERT inherits STRAP’s temporal alignment of a query segment to a subsequence of a longer stored trajectory. Fleet CEL adds failure-context query construction, a shared successful-experience buffer across robots, and retrieval priorities; those extensions are not STRAP’s method. Within STRAP, S-DTW is an established time-series alignment method (§3.1), and pretrained visual encoders supply frame features (§4.3); STRAP’s contribution is their use for cross-task sub-trajectory retrieval and retrieval-augmented policy training.

**中文。** 后续论文[Learning from Fleet Experience: A Collective Learning Paradigm for Robots](../arxiv-2610.25736/summary.md) 将 STRAP 作为参考文献 [27]，直接引用其带斜率约束的 S-DTW 用于 FERT 检索：“using slope-constrained subsequence dynamic time warping (S-DTW) [27]”（§3.1.3，第 3 步：Failure-guided retrieval；见[原文](../arxiv-2610.25736/original.pdf)）。FERT 继承了 STRAP 将查询片段与较长存储轨迹中的子序列进行时间对齐的方法。Fleet CEL 新增失败上下文查询构造、机器人间共享的成功经验库和检索优先级；这些扩展不属于 STRAP。STRAP 内部将 S-DTW 作为已有时间序列对齐方法（§3.1），并用预训练视觉编码器提取帧特征（§4.3）；其贡献是将二者用于跨任务子轨迹检索和检索增强策略训练。

## Limitations / 局限

**English.** The setup assumes expert prior demonstrations from the same embodiment, which limits direct use across heterogeneous robot bodies (§4.1). Automatic target segmentation relies on a low-velocity heuristic and may produce imperfect chunks (§4.2). The best retrieval count K varies by task (§5.2), and matching can return duplicate or semantically misleading segments; language conditioning is used to reduce negative transfer (§4.4–4.5). Evaluation covers LIBERO-10 and two specific real-world settings with few target demonstrations; robustness on broader, less curated deployments remains unestablished. These are scope limits supported by the paper’s stated assumptions and experiments, with the generalization concern an inference from that coverage.

**中文。** 方法假设先验数据为同一机器人本体采集的专家示范，这限制了它直接迁移到异构机器人本体（§4.1）。目标轨迹自动切分依赖低速启发式，片段边界可能不准确（§4.2）。最佳检索数量 K 因任务而异（§5.2），检索也可能返回重复或语义误导的片段；作者使用语言条件训练来降低负迁移（§4.4–4.5）。评测覆盖 LIBERO-10 和两个特定真实场景，且目标示范数量较少；其在更广泛、较少筛选的部署中的鲁棒性尚未得到验证。这些是由论文明确假设和实验覆盖范围支持的限制，其中泛化问题是根据该覆盖范围作出的推断。

## Sources and disclosure / 来源与说明

**English.** Primary sources: [arXiv:2412.15182](https://arxiv.org/abs/2412.15182) and the [ICLR/OpenReview conference PDF](https://openreview.net/pdf?id=MXNoOqBNLZ). The full paper and extracted text are archived as `original.pdf` and `original.txt`. This bilingual note is AI-assisted and was checked against those sources.

**中文。** 主要来源：[arXiv:2412.15182](https://arxiv.org/abs/2412.15182) 和 [ICLR/OpenReview 会议论文 PDF](https://openreview.net/pdf?id=MXNoOqBNLZ)。全文和提取文本归档为 `original.pdf` 与 `original.txt`。本双语摘要由 AI 辅助生成，并已对照上述来源核查。
