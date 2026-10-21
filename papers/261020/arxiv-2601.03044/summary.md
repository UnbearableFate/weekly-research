# SOP: A Scalable Online Post-Training System for Vision-Language-Action Models

## Metadata and reading scope

**English.** Mingjie Pan et al., arXiv:2601.03044v1, submitted 6 January 2026. Original: [arXiv](https://arxiv.org/abs/2601.03044), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, system design, post-training workflow, evaluation, discussion/conclusion, and References. SOP is relevant as a fleet-learning systems precedent; the citing CEL paper does not claim to inherit its learning algorithm.

**中文。** Mingjie Pan 等，arXiv:2601.03044v1，2026 年 1 月 6 日提交。原文：[arXiv](https://arxiv.org/abs/2601.03044)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、系统设计、后训练流程、评测、讨论/结论和参考文献。SOP 是群体学习系统方向的先例；引用它的 CEL 论文并未声称继承其学习算法。

## WHY / Core content / 核心内容

**English.** Generalist vision-language-action policies can recognize many tasks but still lack deployment-specific proficiency. Offline datasets become stale as robot behavior shifts, while one-robot data collection limits diversity and speed. SOP introduces a closed-loop system for online, distributed, multi-task post-training of VLA models in the physical world. A fleet shares on-policy experience and optional human intervention with a centralized learner, then receives policy updates asynchronously. The paper’s focus is system orchestration that couples deployment and learning; it is intentionally agnostic to the post-training algorithm and demonstrates the system with both interactive imitation learning and reinforcement learning.

**中文。** 通用视觉-语言-动作策略能够识别多种任务，但在具体部署场景中仍可能缺少熟练度。离线数据会随机器人行为变化而过时，单机器人采集又限制了数据多样性和速度。SOP 提出在真实物理环境中对 VLA 模型进行在线、分布式、多任务后训练的闭环系统。机器人群向中心化学习器共享 on-policy 经验和可选的人类干预信号，再异步接收策略更新。论文关注连接部署与学习的系统编排；它刻意不限定后训练算法，并分别以交互模仿学习和强化学习展示系统。

## HOW / Core method / 核心方法

**English.** Robot actors execute a shared policy across several tasks, stream trajectories and intervention signals, and receive new checkpoints at safe boundaries such as between episodes. The centralized learner maintains task-partitioned buffers containing online and offline data. A task-balanced adaptive sampler keeps tasks represented while adjusting the online/offline ratio based on recent losses (§IV-C). Policy publication is asynchronous and actor/learner resources can scale independently. The system instantiates HG-DAgger for human corrective actions and RECAP for reinforcement learning; SOP itself does not prescribe their objectives. The result is a collect–train–deploy loop that reduces the delay between deployed-policy failures and learning updates.

**中文。** 机器人 actor 在多项任务上执行共享策略，持续上传轨迹和干预信号，并在 episode 间等安全边界接收新检查点。中心化学习器维护按任务划分的缓冲区，包含在线与离线数据。任务均衡的自适应采样器保持不同任务的覆盖，同时根据近期损失调整在线/离线数据比例（§IV-C）。策略异步发布，actor 和 learner 资源可独立扩展。系统分别实例化使用人类纠正动作的 HG-DAgger 和强化学习方法 RECAP；SOP 本身不规定两者的目标函数。系统由此形成采集—训练—部署闭环，缩短部署策略失败与学习更新之间的延迟。

## WHAT / Evidence / 实验证据

**English.** Experiments use ten dual-arm manipulators across three real-world manipulation task families (§V). The abstract reports that post-training can be completed within hours and that increasing the fleet reduces wall-clock time to a target performance approximately proportionally. With SOP, HG-DAgger and RECAP often achieve at least 2× success-rate improvements over their non-SOP counterparts; the paper reports near-linear fleet scaling and sustained laundry-folding and box-assembly runs exceeding 36 hours (Abstract; §V, Fig. 4). These are specific to the evaluated robot fleet, algorithms and tasks; the paper does not establish the same gains for arbitrary VLA models or deployments.

**中文。** 实验使用十台双臂操作机器人，涵盖三类真实操作任务（§V）。摘要报告，后训练可在数小时内完成；扩大机器人群体大致可按比例缩短达到目标性能所需的墙钟时间。使用 SOP 后，HG-DAgger 和 RECAP 相较各自非 SOP 版本经常达到至少 2 倍成功率提升；论文报告了近线性群体扩展，以及超过 36 小时持续运行的衣物折叠和箱体组装任务（摘要；§V，图 4）。结果仅适用于被测机器人群、算法和任务，不能证明任意 VLA 模型或部署都能获得相同增益。

## Foundations / 基础关系

**English.** The later paper [Learning from Fleet Experience: A Collective Learning Paradigm for Robots](../arxiv-2610.25736/summary.md) ([original](../arxiv-2610.25736/original.pdf)) discusses SOP as a fleet-scale learning and distributed-systems direction precursor (§5.2, §5.4). This link is an explicitly marked reader inference: CEL does not say it inherits SOP’s algorithm. SOP provides a systems comparison—fleet actors, shared experience, centralized learning and policy return—while CEL’s FERT and FATS are separately defined contributions.

**中文。** 后续论文[《Learning from Fleet Experience: A Collective Learning Paradigm for Robots》](../arxiv-2610.25736/summary.md)（[原文](../arxiv-2610.25736/original.pdf)）在 §5.2、§5.4 将 SOP 作为群体规模学习与分布式系统方向先例讨论。该关系明确标注为读者推断：CEL 并未称其继承 SOP 算法。SOP 提供系统对照——群体 actor、共享经验、中心学习和策略回传；CEL 的 FERT 和 FATS 则是独立定义的贡献。

## Limitations / 局限

**English.** SOP demonstrates only two post-training algorithms and three task families on the studied robot fleet. Its results depend on real-world hardware, task-specific interaction and safety procedures. The paper’s broad claim is architectural, but throughput and learning gains are deployment-specific. Reader inference: centralized learning and shared-policy updates may require additional safeguards when robot embodiments, action spaces or network conditions differ. The summary covers the listed sections and is AI-assisted.

**中文。** SOP 只在所研究机器人群的三类任务上展示两种后训练算法。其结果依赖真实硬件、任务特定交互和安全流程。论文的广义主张是系统架构，但吞吐和学习增益取决于具体部署。读者推断：当机器人形态、动作空间或网络条件不同时，中心化学习和共享策略更新可能需要额外保护机制。本摘要覆盖列明章节，由 AI 辅助生成。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:2601.03044](https://arxiv.org/abs/2601.03044). The original PDF and extracted text are the reading sources.

**中文。** 主要来源：[arXiv:2601.03044](https://arxiv.org/abs/2601.03044)。原始 PDF 和提取文本为阅读资料。
