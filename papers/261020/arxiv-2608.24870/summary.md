# SPO++: Stream-Aligned Policy Optimization for Asynchronous Agentic RL

## Metadata and reading scope

**English.** Kai Ruan et al., arXiv:2608.24870v1, submitted 25 August 2026; the paper labels itself a work in progress. It is cited as the single-rollout policy-optimization basis of Long-Horizon RL Needs Muon. Original: [arXiv](https://arxiv.org/abs/2608.24870), [PDF](original.pdf), extracted text (original.txt). Read: Abstract, Introduction, Methods, Experiments, Limitations, Conclusion, and References.

**中文。** Kai Ruan 等，arXiv:2608.24870v1，2026 年 8 月 25 日提交；论文标注为进行中的工作。它被《Long-Horizon RL Needs Muon》引用为单 rollout 策略优化基础。原文：[arXiv](https://arxiv.org/abs/2608.24870)、[PDF](original.pdf)、提取文本（original.txt）。已读：摘要、引言、方法、实验、局限、结论和参考文献。

## WHY / Core content / 核心内容

**English.** Group-relative policy optimization waits for sibling trajectories for the same prompt, which is inefficient when agent rollouts are long and variable. Single-stream Policy Optimization (SPO) removes this dependency through persistent prompt-level outcome estimates, but SPO’s trajectory-level advantage normalization is mismatched with an actor loss averaged over action tokens. Variable response lengths can therefore change the effective centering seen by the optimizer. SPO++ targets two consistency problems in asynchronous learning: prompt evidence should be ordered by the policy snapshot that generated it, and advantage normalization should use the same action-token measure as the loss.

**中文。** Group-relative policy optimization 需要等待同一提示的多条并行轨迹；当智能体 rollout 很长且时长不一时，这会降低效率。单流策略优化 SPO 通过持久化 prompt 级结果估计消除了该依赖，但其轨迹级优势标准化与按动作 token 求平均的 actor loss 不匹配。因此，回答长度变化可能改变优化器实际看到的中心化方式。SPO++ 针对异步学习中的两个一致性问题：prompt 证据应按生成它的策略快照排序；优势标准化应使用与损失相同的动作 token 测度。

## HOW / Core method / 核心方法

**English.** SPO maintains persistent success/failure evidence per repeatable prompt and computes a scalar terminal-outcome advantage from the prompt baseline. SPO++ freezes that baseline at rollout dispatch and attaches returned outcomes to the policy-event coordinate of the generating snapshot, making the evidence update independent of receipt order for a fixed visible history. It also normalizes trajectory advantages weighted by valid action-token counts: the mean and variance are computed under token mass, then each trajectory’s normalized scalar is broadcast to its action tokens. The single-rollout dependency and terminal reward remain unchanged. The method is critic-free and retains trajectory-level credit while aligning the normalization measure to the token-mean actor objective.

**中文。** SPO 为每个可重复提示维护成功/失败证据，并根据提示基线计算标量终局优势。SPO++ 在 rollout 派发时冻结该基线，并将返回结果关联到生成它的策略快照事件坐标；在可见历史固定时，证据更新不再依赖结果接收顺序。它还按有效动作 token 数加权标准化轨迹优势：均值和方差按 token 总量计算，再把每条轨迹的标准化标量广播到其动作 token。单 rollout 依赖和终局奖励保持不变。该方法无需 critic，保留轨迹级信用，同时使标准化测度与 token 平均 actor 目标一致。

## WHAT / Evidence / 实验证据

**English.** The paper evaluates Qwen3.5-0.8B and 2B on ALFWorld and Qwen3.5-0.8B on Math-TIR, with matched runs and fixed online-trajectory budgets (§3.1). SPO++ improves normalized reward-curve area in all three settings; paired gains are +19.00±8.95, +15.92±10.25 and +2.50±1.64 points, respectively (Table 1). Final-five-step reward gains are also positive on average. A matched ablation isolates action-token-measure normalization and finds a +10.70±3.98-point composite improvement on short-horizon ALFWorld (Table 2, §3.3). The full comparison changes event-time tracking, retention and Dual-Clip jointly, so its end-to-end gain cannot be attributed to normalization alone. The authors note the limited model scale and task coverage (§5).

**中文。** 论文在 ALFWorld 上评测 Qwen3.5-0.8B 与 2B，在 Math-TIR 上评测 Qwen3.5-0.8B，并使用匹配运行和固定在线轨迹预算（§3.1）。SPO++ 在三个设置中均提高归一化奖励曲线面积；配对增益分别为 +19.00±8.95、+15.92±10.25 和 +2.50±1.64 个百分点（表 1）。最后五步平均奖励也均为正增益。匹配消融单独测试动作 token 测度标准化，在短时程 ALFWorld 上发现 +10.70±3.98 个百分点的综合指标改善（§3.3，表 2）。完整对照同时改变事件时间跟踪、保留率和 Dual-Clip，因此不能把端到端增益单独归于标准化。作者指出模型规模和任务覆盖有限（§5）。

## Foundations / 基础关系

**English.** Long-Horizon RL Needs Muon explicitly says its recipe follows SPO++ for standardizing advantages over valid action tokens (§3.1 of [Long-Horizon RL Needs Muon](../arxiv-2610.20256/summary.md); [original](../arxiv-2610.20256/original.pdf)). That paper retains the single-rollout asynchronous setup, then adds Muon for matrix parameters, importance correction and auxiliary penalties. SPO++ provides the normalization and stream-aligned policy framework; the optimizer comparison and task-specific recipe are new.

**中文。** 《Long-Horizon RL Needs Muon》明确说明其配方沿用 SPO++ 对有效动作 token 优势进行标准化（[《Long-Horizon RL Needs Muon》](../arxiv-2610.20256/summary.md)的 §3.1；[原文](../arxiv-2610.20256/original.pdf)）。该论文保留单 rollout 异步设置，再为矩阵参数加入 Muon、重要性修正和辅助惩罚。SPO++ 提供标准化和流对齐策略框架；优化器比较与任务特定配方是新贡献。

## Limitations / 局限

**English.** Experiments use small Qwen3.5 models, limited training budgets, ALFWorld and one Math-TIR setup. The full end-to-end comparison changes multiple components, while the normalization ablation isolates the measure but not the individual effects of centering and batch scaling. Persistent values require repeatable prompt identities and offline initialization; first-finished collection can favor shorter trajectories. The sparse terminal reward still creates a cold-start problem (§5). This is a 2026 preprint marked work in progress. Summary is AI-assisted and covers the listed sections.

**中文。** 实验使用小型 Qwen3.5 模型、有限训练预算、ALFWorld 和一种 Math-TIR 设置。完整端到端对照同时改变多个组件；标准化消融虽然隔离了测度，但未分别拆解中心化和批次缩放的效果。持久化价值需要可重复的 prompt 标识及离线初始化；先完成的轨迹收集可能偏向较短轨迹。稀疏终局奖励仍带来冷启动问题（§5）。这是一篇标注为进行中工作的 2026 年预印本。本摘要由 AI 辅助生成，覆盖列明章节。

## Sources and disclosure / 来源与说明

**English.** Primary source: [arXiv:2608.24870](https://arxiv.org/abs/2608.24870). Archived PDF and extracted text are the source material.

**中文。** 主要来源：[arXiv:2608.24870](https://arxiv.org/abs/2608.24870)。归档 PDF 和提取文本为资料来源。
