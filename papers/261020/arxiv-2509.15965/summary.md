# RLinf: Flexible and Efficient Large-scale Reinforcement Learning via Macro-to-Micro Flow Transformation

## Metadata and reading scope

**English.** Chao Yu et al., arXiv:2509.15965; the 2026 revision is published at USENIX OSDI 2026. Original: [arXiv](https://arxiv.org/abs/2509.15965), [USENIX OSDI 2026](https://www.usenix.org/conference/osdi26/presentation/yu-chao), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, M2Flow design, workflow interface, evaluation, and conclusion. The paper is a distributed RL runtime dependency explicitly named by Fleet’s FATS implementation.

**中文。** Chao Yu 等，arXiv:2509.15965；2026 年修订版发表于 USENIX OSDI 2026。原文：[arXiv](https://arxiv.org/abs/2509.15965)、[USENIX OSDI 2026](https://www.usenix.org/conference/osdi26/presentation/yu-chao)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、M2Flow 设计、工作流接口、评测和结论。该论文是 Fleet 的 FATS 实现明确采用的分布式 RL 运行时依赖。

## WHY / Core content / 核心内容

**English.** Reinforcement-learning workloads combine rollout generation, environment simulation, inference and training, whose compute and memory needs differ. Fixed execution modes can leave GPUs idle: collocation creates resource contention, while disaggregated pipelines can waste capacity or suffer synchronization bubbles. RLinf proposes M2Flow, a system design that preserves a simple imperative RL workflow while transforming it into a flexible micro-execution flow. Its contribution is a general execution and scheduling runtime for large-scale RL, covering language-model reasoning and embodied RL, rather than a new policy-learning objective.

**中文。** 强化学习工作负载组合 rollout 生成、环境模拟、推理和训练，各阶段的计算与显存需求不同。固定执行模式可能导致 GPU 空闲：共置会造成资源争用，分离式流水线则可能浪费资源或产生同步气泡。RLinf 提出 M2Flow，在保留简单命令式 RL 工作流的同时，将其转换为灵活的微执行流。其贡献是面向大规模 RL 的通用执行与调度运行时，涵盖语言模型推理和具身 RL，而非新的策略学习目标。

## HOW / Core method / 核心方法

**English.** Users express a macro-level workflow in a procedural interface. RL components become workers that communicate through adaptive channels and can be spatially placed on accelerators, temporally time-multiplexed, or pipelined at different granularities. A profiling-guided scheduler measures worker behavior and selects execution modes. Elastic pipelining controls how rollout and training batches overlap; context switching permits workers to share accelerators over time. RLinf supports collocated, disaggregated spatial, temporal and hybrid modes, along with workload-specific parallelism. This separation lets applications retain their high-level program structure while the runtime changes lower-level execution.

**中文。** 用户通过过程式接口表达宏观工作流。RL 组件转化为可通过自适应通道通信的 worker，并可在加速器上空间分配、按时间复用或以不同粒度流水执行。基于 profiling 的调度器测量 worker 行为并选择执行模式。弹性流水线控制 rollout 和训练 batch 的重叠程度；上下文切换允许 worker 随时间共享加速器。RLinf 支持共置、空间分离、时间复用和混合模式，以及适合具体工作负载的并行配置。该分离使应用保留高层程序结构，同时由运行时调整底层执行。

## WHAT / Evidence / 实验证据

**English.** Evaluation spans four model families/scales, two RL algorithms, several GPU-cluster sizes, and both reasoning and embodied workloads (§5). For math-reasoning RL, RLinf reports 1.07×–1.70× throughput over veRL and Slime across evaluated settings (Abstract; §5.1, Figs. 8–13). For embodied tasks, it reports 1.05×–2.43× over SimpleVLA-RL on LIBERO, and up to 1.87× among execution modes on ManiSkill (Abstract; §5.1.2, Figs. 14–15). Its scheduler identifies a suitable execution mode in 0.0007 seconds to 5.98 seconds across 8–1024 GPU clusters (Abstract). These are system throughput results under stated model, batch, sequence and hardware configurations, not improvements in policy quality caused by a new optimizer.

**中文。** 评测涵盖四类模型及规模、两种 RL 算法、多种 GPU 集群规模，并包含推理和具身工作负载（§5）。在数学推理 RL 上，RLinf 在被测设置中报告相较 veRL 和 Slime 达到 1.07×–1.70× 吞吐（摘要；§5.1，图 8–13）。在具身任务上，LIBERO 的吞吐相较 SimpleVLA-RL 达到 1.05×–2.43×，ManiSkill 执行模式之间最高达到 1.87×（摘要；§5.1.2，图 14–15）。其调度器在 8–1024 GPU 集群上的模式选择耗时为 0.0007–5.98 秒（摘要）。这些是规定模型、batch、序列长度和硬件条件下的系统吞吐结果，并非新优化器带来的策略质量提升。

## Foundations / 基础关系

**English.** Fleet’s paper explicitly states that FATS is implemented on RLinf (§3.2 of [Learning from Fleet Experience](../arxiv-2610.25736/summary.md); [original](../arxiv-2610.25736/original.pdf)). RLinf supplies the worker orchestration and distributed execution substrate. Fleet’s FERT algorithm and robotics-specific fault-management design are separate contributions; the dependency is runtime/system implementation, not a claim that RLinf supplies CEL’s learning objective.

**中文。** Fleet 论文明确说明 FATS 构建于 RLinf 之上（[《Learning from Fleet Experience》](../arxiv-2610.25736/summary.md)的 §3.2；[原文](../arxiv-2610.25736/original.pdf)）。RLinf 提供 worker 编排和分布式执行底座。Fleet 的 FERT 算法和机器人特定故障管理设计是独立贡献；该依赖指运行时/系统实现，并非称 RLinf 提供 CEL 学习目标。

## Limitations / 局限

**English.** Performance depends on runtime profiles, model and simulator behavior, memory pressure, hardware layout and parallelism choices. The paper’s large search space means the reported best mode is workload-specific. Most comparisons are throughput-focused and cannot by themselves establish better task reward or sample efficiency. Reader inference: profile-guided decisions may need refresh when workloads change. Summary covers the listed full-text sections and is AI-assisted.

**中文。** 性能取决于运行时 profile、模型和模拟器行为、显存压力、硬件布局及并行配置。论文所面对的配置空间较大，因此报告的最佳模式具有工作负载特异性。多数对比关注吞吐，单凭这些结果不能证明任务奖励或样本效率更高。读者推断：工作负载变化时可能需要刷新 profile。摘要覆盖列明全文章节，由 AI 辅助生成。

## Sources and disclosure / 来源与说明

**English.** Primary sources: [arXiv:2509.15965](https://arxiv.org/abs/2509.15965) and the [USENIX OSDI 2026 paper page](https://www.usenix.org/conference/osdi26/presentation/yu-chao). Archived PDF and extracted text are the reading sources.

**中文。** 主要来源：[arXiv:2509.15965](https://arxiv.org/abs/2509.15965) 和 [USENIX OSDI 2026 论文页面](https://www.usenix.org/conference/osdi26/presentation/yu-chao)。归档 PDF 和提取文本为阅读资料。
