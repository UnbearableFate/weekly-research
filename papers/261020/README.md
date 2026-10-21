# Weekly research papers — 2026-10-20

## Scope and selection

检索窗口为 **2026-10-14 至 2026-10-20（含首尾）**。仅使用用户指定的研究范围：**LLM 优化器、分布式学习、PEFT、持续学习**；不沿用旧的宽泛 ML 兴趣。执行配置记录为 native `spawn_agent`，`gpt-6-luna / xhigh`（[`execution.json`](execution.json)）。

Discovery adapter 返回 241 条匹配记录，构成 60 篇候选池；逐篇阅读题目和摘要并按 0–4 相关度评分后，6 篇同时满足语义相关性和本周可核实 HF 关注证据。配置上限为 10 篇，本期不为凑数保留泛相关论文。60 篇候选中，4 篇评分为 4，2 篇评分为 3。排名按相关度和抓取时观测到的 HF 累计票数排序；累计票数是快照值，不是本周新增票数。

在本次有界检索和语义筛选的候选中，没有直接匹配持续学习范围且同时满足本周关注证据的论文入选；这仅描述当前来源与候选池，不代表更广泛文献中不存在相关工作。

| Rank | Paper and archived files | Publication / version date | HF attention evidence observed | Fit |
|---:|---|---|---|---|
| 1 | [Scaling Parameter-Efficient Fine-Tuning for Brain Encoding — summary](arxiv-2610.26802/summary.md) · [original PDF](arxiv-2610.26802/original.pdf) | arXiv v1, 2026-10-19 | HF Daily 2026-10-20, 163 cumulative votes in timestamped discovery response | PEFT/LoRA on multimodal pretrained backbones; application is brain encoding rather than ordinary LLM fine-tuning |
| 2 | [Learning from Fleet Experience: A Collective Learning Paradigm for Robots — summary](arxiv-2610.25736/summary.md) · [original PDF](arxiv-2610.25736/original.pdf) | arXiv v1, 2026-10-19 | HF Daily 2026-10-20, 105 cumulative votes | Direct distributed and asynchronous fleet learning; robotics application |
| 3 | [Long-Horizon RL Needs Muon — summary](arxiv-2610.20256/summary.md) · [original PDF](arxiv-2610.20256/original.pdf) | arXiv v1, 2026-10-14; marked work in progress | HF Daily 2026-10-15, 30 cumulative votes | Direct study of an optimizer in asynchronous language-model agent training; combined recipe, not an isolated Muon result |
| 4 | [PyTorch Distributed: Experiences on Accelerating Data Parallel Training — summary](arxiv-2006.15704/summary.md) · [original PDF](arxiv-2006.15704/original.pdf) | arXiv v1, 2020-06-28 | HF Trending snapshot 2026-10-20, 14 cumulative votes | Distributed data-parallel systems paper; **resurfaced older work**, not new publication |
| 5 | [Beyond Domain-Routed Supervision: Cross-Teacher Guarding for Multi-Teacher On-Policy Distillation — summary](arxiv-2610.13521/summary.md) · [original PDF](arxiv-2610.13521/original.pdf) | v1 2026-10-09; v2 revision 2026-10-17 | HF Daily 2026-10-15, 250 cumulative votes | **Resurfaced older work**; a concrete shared-parameter gradient-update method for multi-teacher LLM training |
| 6 | [Rethinking Projector Training in Multimodal LLMs (PORTAL) — summary](arxiv-2610.18598/summary.md) · [original PDF](arxiv-2610.18598/original.pdf) | arXiv v1, 2026-10-13; NeurIPS 2026 camera-ready | HF Daily 2026-10-15, 11 cumulative votes | **Resurfaced older work**; adjacent efficient projector initialization, not conventional LoRA-style PEFT |

关注日期与论文发布日期分别记录；三篇首版早于检索窗口的作品（DDP、ROAD、PORTAL）本周重新受到关注，其中 ROAD 的 v2 修订在窗口内。BrainLoRA 的票数存在抓取视图差异：本次排序采用带时间戳的 API 原始响应（163），另一个浏览器页面快照显示 154；两者都只是观测到的累计票数，不表示周增量。来源线索、候选排除和抓取限制见 [`_work/search-notes.md`](_work/search-notes.md)。

## WHY / HOW / WHAT comparison

| Paper | WHY — problem | HOW — contribution | WHAT — evidence and limits |
|---|---|---|---|
| BrainLoRA | Neural-response data is limited; frozen backbones cannot specialize, while full fine-tuning is costly. | Rank-16 LoRA plus a neural readout; causal single-pass feature extraction and a fused multi-LoRA kernel. | Nine backbones; about 350× lower feature-extraction cost (§4, Fig. 2); at 32 adapters, 29.8× faster step than sequential runs (§5.5, Fig. 5a); 261-model ensemble scores in §5.5/Table 1. Benchmark- and validation-selection-specific. |
| Fleet CEL | Human corrective actions do not scale with a deployed robot fleet. | Failure contexts retrieve successful action segments (FERT), while FATS handles asynchronous fleet execution and faults. | Five real-world tasks, 120 trials each, 93.3–99.2% success (§4.2, Fig. 5); phone packaging rises from 79.2% to 98.3% with 96 robots (§4.3, Fig. 6). Humans still annotate outcomes and reset scenes. |
| Long-Horizon Muon | Sparse terminal rewards and variable-length asynchronous rollouts complicate long-horizon agent optimization. | Single-rollout recipe combining Muon, SPO++, token-mean loss, importance correction and auxiliary penalties. | Full recipe exceeds SPO baselines later in selected runs for two model families (§4.2, Fig. 3); components change together, so Muon’s isolated effect is not established. |
| PyTorch DDP | Scaling data-parallel training requires overlapping communication with backward computation. | DDP buckets ready gradients and overlaps asynchronous all-reduce; bucket sizes and sync-skipping require workload tuning. | Near-linear scaling to 256 GPUs under appropriate configuration (Abstract, §5.3); historical 2020 implementation and cluster results. This is not a current performance measurement. |
| ROAD MOPD | Multi-teacher domain distillation can conflict on shared student parameters. | Agreement-gated token rewards plus target-gradient projection constrained by auxiliary-teacher feedback (Eqs. 4–9). Auxiliary gradients guide the constraint and are not separate updates. | Across four paired settings, gains of 0.72–2.89 points over strongest multi-domain baselines (§4.2, Table 1); three-domain Qwen3-4B average 52.89 vs. 51.71 (Table 3). v1 predates the window; v2 is in-window. |
| PORTAL | Conventional projector alignment uses paired image-caption data and gradient-based training. | Closed-form Gaussian Bures–Wasserstein transport projector in a shared PCA subspace. | Exceeds trained baseline in 3/7 configurations and averages 98% of baseline in the other four (§5.1, Table 1); about 135× fewer alignment FLOPs at roughly 4k captions (§5.2, Fig. 4). Adjacent efficient adaptation contribution. |

## Methodological foundations and verified relations

All relation records have direct source excerpts and section/equation locators. Reader-inferred links are identified as inferences, and a bibliography entry alone was not used as evidence.

| Recent paper → foundation | Relationship and evidence locator | Foundation note and original |
|---|---|---|
| DDP → PyTorch | `method_dependency`: DDP names the PyTorch `DistributedDataParallel` module in §3. | [PyTorch summary](arxiv-1912.01703/summary.md) · [original](arxiv-1912.01703/original.pdf) |
| BrainLoRA → LoRA | `based_on`: BrainLoRA says it inserts rank-16 LoRA in attention layers, §4. | [LoRA summary](arxiv-2106.09685/summary.md) · [original](arxiv-2106.09685/original.pdf) |
| Long-Horizon → SPO++ | `based_on`: explicitly follows SPO++ token-normalization recipe, §3.1. | [SPO++ summary](arxiv-2608.24870/summary.md) · [original](arxiv-2608.24870/original.pdf) |
| Fleet CEL → STRAP | `based_on`: Fleet §3.1.3, Step 3 explicitly cites STRAP [27] for slope-constrained S-DTW; FERT inherits sub-trajectory temporal alignment and adds failure-context queries and fleet priorities. | [STRAP summary](arxiv-2412.15182/summary.md) · [original](arxiv-2412.15182/original.pdf) |
| Fleet CEL → RLinf | `method_dependency`: FATS explicitly states its implementation is on RLinf, §3.2. | [RLinf summary](arxiv-2509.15965/summary.md) · [original](arxiv-2509.15965/original.pdf) |
| ROAD → GKD / OPD | `based_on`: §2.1 describes teacher feedback on student-generated trajectories. | [GKD summary](arxiv-2306.13649/summary.md) · [original](arxiv-2306.13649/original.pdf) |
| ROAD → PCGrad | `method_dependency` inference from shared projection geometry, §3.3/Eqs. 7–9; the authors call PCGrad related and compare it, but do not claim inspiration or derivation. | [PCGrad summary](arxiv-2001.06782/summary.md) · [original](arxiv-2001.06782/original.pdf) |
| PORTAL → Bures–Wasserstein | `method_dependency`: PORTAL derives projector parameters from the Gaussian optimal-transport map, §§2, 4.1. | [Bhatia–Jain–Lim summary](arxiv-1712.01504/summary.md) · [original](arxiv-1712.01504/original.pdf) |
| PORTAL → Deep CORAL | `inspired_by`: PORTAL explicitly says it extends the CORAL idea to multimodal projector alignment, §2. | [Deep CORAL summary](arxiv-1607.01719/summary.md) · [original](arxiv-1607.01719/original.pdf) |

The included set contains **6 recent selections + 9 direct foundations** (15 papers, each with a bilingual summary and archived original PDF/text). During this first trial, seven foundation originals already fetched earlier in the same run were reused from the local paper catalog/cache; Bures–Wasserstein and STRAP were downloaded during the run. The six selected recent originals were also downloaded during this run; none of these files came from a prior weekly run. The initially considered LLaVA paper (arXiv:2304.08485) was withdrawn from the foundation role after review; its cached PDF remains as background material. SOP is also retained with its finished note and original as broader systems context, but its foundation role was withdrawn in favor of STRAP’s direct method evidence. Neither cached background paper is counted in the 15-paper included set.

## Source health and run files

- Discovery returned HTTP 200 for seven HF Daily date endpoints (14–20 October), the HF Trending endpoint and the arXiv API: **9 healthy sources, 0 failed sources**. The bounded search covered at most 100 records per HF endpoint and 500 newest arXiv records; it is not an exhaustive global search.
- The source adapter returned 241 matches and retained the 60-paper candidate pool, all raw source responses, per-paper attention dates, and scoring records under [`_work/`](_work/). HF API snapshots provide dated placement evidence. The manual browser scan could not view the 17–18 October Daily pages, so those dates rely on the healthy adapter snapshots.
- All selected and foundation papers have archived PDFs and extracted full text, and each summary records its reading scope. There were no source download failures. The excluded LLaVA cache is retained only as background material.
- The dated search notes document manual queries, source limitations and unselected leads. [`run.json`](run.json) and [`execution.json`](execution.json) preserve the run and model-selection metadata.

## Completion

The required recent and foundation papers, bilingual summaries, verified relations and this overview are registered. The final post-revision `finalize --date 2026-10-20` run returned **complete**, produced [`manifest.json`](manifest.json), verified archived-file hashes, and reported an empty `problems` list.
