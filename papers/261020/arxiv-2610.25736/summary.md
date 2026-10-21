# Learning from Fleet Experience: A Collective Learning Paradigm for Robots

## Metadata and reading scope

**English.** Chao Yu et al., arXiv:2610.25736v1, submitted 19 October 2026. HF Daily placement: 20 October 2026, with 105 cumulative votes observed in the archived response. This is a robotics learning and distributed-systems paper, included as a relevant adjacent example of fleet-scale asynchronous learning rather than an LLM method. Original: [arXiv](https://arxiv.org/abs/2610.25736), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, Collective Experience Learning and FERT/FATS methods, Experiments, Related Work, Conclusion, and References.

**中文。** Chao Yu 等，arXiv:2610.25736v1，2026 年 10 月 19 日提交。HF Daily 排位日期为 2026 年 10 月 20 日；归档响应观测到累计 105 票。这是一篇机器人学习与分布式系统论文，作为群体异步学习的相邻案例纳入，不属于 LLM 方法。原文：[arXiv](https://arxiv.org/abs/2610.25736)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、群体经验学习与 FERT/FATS 方法、实验、相关工作、结论和参考文献。

## WHY / Core content / 核心内容

**English.** Robot policies can improve from deployment, but conventional online robot learning often needs teleoperators to intervene when execution fails. Such supervision is difficult to scale with the number of robots. The paper proposes Collective Experience Learning (CEL): deployed robots share execution outcomes and trajectory data to improve a common policy. Its central learning procedure, Failure-guided Experience Retrieval Fine-Tuning (FERT), treats failure observations as retrieval queries into a fleet-wide store of successful experience. It then trains on retrieved successful action segments without collecting additional expert demonstrations or corrective actions. A separate fault-tolerant asynchronous training system (FATS) coordinates robots, data and policy updates despite slow workers and local interruptions. The contribution combines a retrieval-based policy-learning method with system support for a large robot fleet.

**中文。** 机器人策略可从部署运行中改进，但传统在线机器人学习通常需要遥操作员在执行失败时介入。这类监督难以随机器人数量扩展。论文提出群体经验学习（Collective Experience Learning，CEL）：部署中的机器人共享执行结果和轨迹数据，以改进共同策略。核心学习过程 FERT（Failure-guided Experience Retrieval Fine-Tuning）把失败观察作为查询，从全群体共享的成功经验库中检索相关经验，再使用检索到的成功动作片段训练策略，而无需收集额外专家示范或纠正动作。独立的容错异步训练系统 FATS 在工作进程变慢或局部中断时协调机器人、数据与策略更新。论文贡献将基于检索的策略学习方法与大规模机器人群系统支持结合起来。

## HOW / Core method / 核心方法

**English.** FERT first collects autonomous episodes asynchronously and labels outcomes as success or failure. A frozen visual encoder and proprioceptive features represent the scene and robot state. For a failed episode, the system retrieves temporally relevant segments from successful trajectories using a slope-constrained subsequence dynamic time-warping distance. Retrieved successful actions become supervision; overlapping action chunks receive priorities and are sampled for fine-tuning. The paper defines a priority-weighted negative log-likelihood fitting objective over successful chunks (Eqs. 12–13), but its flow-based policy does not explicitly evaluate action likelihoods: it uses the base policy’s conditional flow-matching loss as a tractable surrogate (App. F, Eq. 43). Failed actions are not targets, and the system does not learn a critic or value estimate from them. Humans still provide binary outcome labels and reset the scene; “without corrective actions” refers to the absence of additional expert action corrections during this learning phase. FATS separates the real-time interaction data plane from the experience and control plane, and uses SwarmLink and HotSwarm for asynchronous communication, worker recovery and policy distribution. The implementation is built on RLinf.

**中文。** FERT 首先异步收集自主运行轨迹，并标注成败。冻结的视觉编码器与本体感知特征用于表示场景和机器人状态。对失败轨迹，系统通过带斜率约束的子序列动态时间规整距离，从成功轨迹中检索时间上相关的片段。检索到的成功动作作为监督；重叠动作块按优先级采样用于微调。论文对成功动作块定义了按优先级加权的负对数似然拟合目标（式 12–13），但其 flow-based 策略不显式计算动作似然，而采用基座策略的条件流匹配损失作为可计算替代（附录 F，式 43）。失败动作不作为训练目标，系统也不从中学习 critic 或 value estimate。人类仍提供二值结果标注并重置场景；“无需纠正动作”指该学习阶段不再额外收集专家动作纠正。FATS 将实时交互数据平面与经验、控制平面分离，通过 SwarmLink 和 HotSwarm 支持异步通信、工作进程恢复和策略分发。其实现构建于 RLinf 之上。

## WHAT / Evidence / 实验证据

**English.** The evaluation uses five real-world manipulation tasks on AgiBot G2 robots. Each task reports 120 held-out trials on robots excluded from experience collection. FERT reaches 93.3–99.2% task success in the main results (§4.2, Fig. 5; detailed counts in App. F, Table 11). For multi-stage phone packaging, increasing the training fleet to 96 robots improves success from 79.2% to 98.3% (§4.2, Fig. 5 and §4.3, Fig. 6). Across the five tasks, FERT improves average success from 81.0% for the initialized multi-robot HG-DAgger policies to 97.3% (Table 3). The system evaluation also records 30 fault incidents across 22 robots during the 96-robot run (§4.5.1, Fig. 8), while fleet-level collection continued. These results show performance in the tested platform and tasks; they do not establish generality to other robot types or task distributions.

**中文。** 评测使用 AgiBot G2 机器人执行五项真实操作任务。每项任务报告 120 次留出测试，这些测试机器人未参与经验收集。FERT 在主要结果中达到 93.3%–99.2% 的任务成功率（§4.2，图 5；详细计数见附录 F，表 11）。对多阶段手机包装任务，将训练群体扩大到 96 台机器人后，成功率从 79.2% 提升到 98.3%（§4.2，图 5 和 §4.3，图 6）。五项任务的平均成功率从初始化多机器人 HG-DAgger 策略的 81.0% 提升到 FERT 的 97.3%（表 3）。系统评测还记录了 96 机器人运行期间 22 台机器人上的 30 起故障事件（§4.5.1，图 8），群体级数据收集仍在继续。这些结果证明了在被测平台和任务上的效果，尚不能证明对其他机器人类型或任务分布的普遍性。

## Foundations / 基础关系

**English.** The direct retrieval-method foundation is [STRAP: Robot Sub-Trajectory Retrieval for Augmented Policy Learning](../arxiv-2412.15182/summary.md) ([original](../arxiv-2412.15182/original.pdf)). Fleet §3.1.3, Step 3, explicitly cites STRAP [27] for “using slope-constrained subsequence dynamic time warping (S-DTW)”; FERT inherits its temporal alignment of a query segment to a subsequence in a longer trajectory. Fleet adds failure-context queries, a fleet-wide successful-experience buffer, and retrieval priorities. It also explicitly states that FATS is implemented on [RLinf](../arxiv-2509.15965/summary.md) ([original](../arxiv-2509.15965/original.pdf)) (§3.2), a concrete distributed-runtime dependency. [SOP](../arxiv-2601.03044/summary.md) ([original](../arxiv-2601.03044/original.pdf)) remains broader systems-direction context in §§5.2, 5.4, but is not counted as a core foundation.

**中文。** 直接的检索方法基础是[STRAP: Robot Sub-Trajectory Retrieval for Augmented Policy Learning](../arxiv-2412.15182/summary.md)（[原文](../arxiv-2412.15182/original.pdf)）。Fleet §3.1.3 第 3 步明确引用 STRAP [27] 来实现“using slope-constrained subsequence dynamic time warping (S-DTW)”；FERT 继承了将查询片段与较长轨迹中的子序列进行时间对齐的方法。Fleet 新增失败上下文查询、全群体共享的成功经验库和检索优先级。论文还明确说明 FATS 构建于[RLinf](../arxiv-2509.15965/summary.md)（[原文](../arxiv-2509.15965/original.pdf)）之上（§3.2），这是具体的分布式运行时依赖。[SOP](../arxiv-2601.03044/summary.md)（[原文](../arxiv-2601.03044/original.pdf)）仍是 §§5.2、5.4 中较宽泛的系统方向背景，但不计作核心基础。

## Limitations / 局限

**English.** The authors evaluate five tasks on one robot platform, with the largest fleet experiment limited to phone packaging. FERT still depends on human binary outcome annotation and scene resets, so “without corrective actions” does not mean fully unsupervised operation. Generalization to heterogeneous robot fleets, broader task distributions, extended deployments and policy changes under real deployment drift remains open (§6). Reader inference: retrieval quality also depends on the representation and successful-trajectory coverage; failure contexts with no matching experience may not benefit. This summary covers the sections listed above and is based on AI-assisted reading of the archived full text and PDF.

**中文。** 作者在单一机器人平台上评测五项任务，最大规模群体实验集中于手机包装。FERT 仍依赖人类二值结果标注和场景重置，因此“无需纠正动作”不等于完全无监督运行。对异构机器人群、更广泛任务分布、长期部署以及部署漂移下策略变更的泛化仍待研究（§6）。读者推断：检索质量也取决于表示方式和成功轨迹覆盖率；若失败上下文找不到匹配经验，方法可能无法受益。本摘要覆盖上述列明章节，基于 AI 辅助阅读归档全文和 PDF 生成。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:2610.25736](https://arxiv.org/abs/2610.25736). HF Daily attention date and observed cumulative votes are preserved in `../_work/`. This summary is AI-assisted; the original PDF and extracted text are the source material.

**中文。** 主要来源：[arXiv:2610.25736](https://arxiv.org/abs/2610.25736)。HF Daily 关注日期和观测到的累计票数保存在 `../_work/`。本摘要由 AI 辅助生成；原始 PDF 和提取文本为资料来源。
