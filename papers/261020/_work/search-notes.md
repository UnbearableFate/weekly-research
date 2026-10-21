# Weekly paper search notes — 2026-10-20

## Scope and method

- Search window: 2026-10-14 through 2026-10-20 inclusive (Beijing reporting date 2026-10-20).
- Only the current user scope was applied: LLM optimizers, distributed learning, PEFT, and continual learning. The previous broad ML interests were not used.
- Manually checked Hugging Face Daily Papers for 2026-10-14, 10-15, 10-16, 10-19, and the current 10-20 page, plus the Hugging Face Trending Papers page. Exact-string checks included `Muon`, `LoRA`, `continual`, `distributed`, and `fine-tuning`; those searches are recall aids, not semantic exclusions.
- Checked official arXiv abstract pages for the papers below to verify titles, submission dates, categories, and abstract claims. HF counts are the snapshot displayed when checked, not counts gained during this week.
- The project discovery adapter subsequently scanned HF Daily for each date in the window, the HF Trending snapshot, and arXiv; it preserved the raw responses and per-item placement dates under `_work/sources/`. The 60 returned candidates were all semantically scored, then filtered by attention evidence and relevance. Script-observed vote counts below are cumulative snapshot counts, not weekly growth.
- No paper is accepted on keyword match alone. The next stage must read abstracts/full text, semantically score fit, and retain only candidates with a verifiable current attention signal. Weekend HF date pages were not available in this browser snapshot; arXiv Saturday/Sunday submissions were checked as leads but not treated as attention evidence.

## Candidates with directly observed HF attention

### Scaling Parameter-Efficient Fine-Tuning for Brain Encoding — arXiv:2610.26802

- HF Daily Papers, 2026-10-20: the discovery snapshot recorded 163 cumulative votes. A separate browser-rendered page snapshot displayed 154 and rank `#1`; counts varied between retrieval views, so use the timestamped raw discovery record for ranking and do not interpret either as weekly vote growth. HF page: <https://huggingface.co/papers/2610.26802>.
- Official arXiv: submitted 2026-10-19; `cs.LG`. The abstract describes PEFT/LoRA plus a lightweight readout for multimodal brain encoding, causal multi-timepoint feature extraction, adaptation up to 104B parameters, Qwen3-Omni, and a multi-LoRA kernel. Source: <https://arxiv.org/abs/2610.26802>.
- Semantic fit: direct PEFT methods and large multimodal pretrained backbones, though the task is neural response prediction rather than general LLM fine-tuning. Keep as a strong PEFT candidate if full-text review confirms the method details.

### Long-Horizon RL Needs Muon — arXiv:2610.20256

- HF Daily Papers, 2026-10-15: displayed with 29 on the daily page. This is a current-window attention signal, not a weekly increase count. HF page: <https://huggingface.co/papers/2610.20256> and date page: <https://huggingface.co/papers/date/2026-10-15>.
- Official arXiv: submitted 2026-10-14; `cs.LG`, `cs.AI`. The abstract describes an asynchronous single-rollout long-horizon agent training recipe combining Muon, token-averaged loss, truncated importance sampling, and length/tool-error penalties; it reports higher training success for the full recipe than baselines. Source: <https://arxiv.org/abs/2610.20256>.
- Semantic fit: an LLM/agent training application that studies an optimizer, but it is a combined training recipe rather than a new optimizer. Retain only if review finds the optimizer evidence substantial.

### Learning from Fleet Experience: A Collective Learning Paradigm for Robots — arXiv:2610.25736

- HF Daily Papers, 2026-10-20: 105 cumulative votes in the timestamped discovery snapshot. HF page: <https://huggingface.co/papers/2610.25736>.
- Official arXiv: submitted 2026-10-19. Source: <https://arxiv.org/abs/2610.25736>.
- Semantic fit: a direct distributed-learning system: fleet-shared experience, failure-guided retrieval fine-tuning, and fault-tolerant asynchronous training/policy distribution. The evaluated policy application is robotics, which is disclosed as the application domain.

### Beyond Domain-Routed Supervision: Cross-Teacher Guarding for Multi-Teacher On-Policy Distillation — arXiv:2610.13521

- HF Daily Papers, 2026-10-15: 250 cumulative votes in the timestamped discovery snapshot. It was posted 2026-10-09, so this is **resurfaced older work**, not a new paper of the week. HF page: <https://huggingface.co/papers/2610.13521>.
- Official arXiv source: <https://arxiv.org/abs/2610.13521>.
- Semantic fit: multi-teacher LLM distillation with an explicit gradient-projection mechanism over shared parameter updates. Kept as a narrowly relevant model-update method; full-text review must distinguish it from a general-purpose optimizer.

### Rethinking Projector Training in Multimodal LLMs — arXiv:2610.18598

- HF Daily Papers, 2026-10-15: 11 cumulative votes in the timestamped discovery snapshot. HF page: <https://huggingface.co/papers/2610.18598>.
- Official arXiv: submitted 2026-10-13. Source: <https://arxiv.org/abs/2610.18598>.
- Semantic fit: the paper studies projector training in multimodal LLMs and proposes training-free initialization from marginal feature statistics. It is relevant to efficient multimodal adaptation, but not conventional LoRA-style PEFT; this limitation must remain visible in the summary.

### PyTorch Distributed: Experiences on Accelerating Data Parallel Training — arXiv:2006.15704

- HF Trending snapshot observed 2026-10-20: 14 cumulative votes. This 2020 paper is **resurfaced older work**; it must not be described as newly published. HF page: <https://huggingface.co/papers/2006.15704>.
- Official arXiv source: <https://arxiv.org/abs/2006.15704>.
- Semantic fit: a core distributed data-parallel training system/performance study. The trending snapshot establishes current attention only at retrieval time; it does not prove that interest began during the week or rose by 14 votes.

## Recent arXiv leads without manually found HF attention evidence

These are discovery leads only. They are not eligible for the final set unless the automated/manual pass finds an in-window HF Daily or an unambiguous current Trending signal.

| Paper | Official arXiv evidence | Semantic note / current disposition |
|---|---|---|
| `PACT: NVFP4 Data-Flow LoRA Fine-Tuning on Consumer GPUs` (2610.25048) | Submitted 2026-10-18; `cs.LG`; <https://arxiv.org/abs/2610.25048> | Strong PEFT/LLM fine-tuning fit: NVFP4 frozen projections, activation-memory reduction, evaluation on RTX 5080. No HF Daily listing or attention count found in manual page checks. |
| `T-MUON: Tensorizing Muon via t-SVD for Large Language Model Pre-training` (2610.24938) | Submitted 2026-10-18; `cs.LG`; <https://arxiv.org/abs/2610.24938> | Strong LLM optimizer fit; proposes t-SVD/tensor-aware Muon and reports GPT-2/LLaMA-style evaluations. No HF attention signal found manually. |
| `How Does Muon Work in Private Deep Learning? Scalable Differentially Private Training via Orthogonalization` (2610.24736) | Submitted 2026-10-17; `cs.LG`; <https://arxiv.org/abs/2610.24736> | Optimizer and language-modeling relevance through DP-Muon; no HF attention signal found manually. |
| `Coordination-Free Workload Regularization for Variable-Cost Distributed Training` (2610.21162) | Submitted 2026-10-15; `cs.DC`, `cs.LG`; <https://arxiv.org/abs/2610.21162> | Strong distributed-training fit: Batch Cost Lookahead (BCL), no cross-rank metadata exchange; abstract reports lower estimated batch-cost variability and H200 speedups. No HF attention signal found manually. |
| `Muon Operates Beyond the Edge of Stability` (2610.24305) | Submitted 2026-10-16; `cs.LG`; <https://arxiv.org/abs/2610.24305> | Optimizer analysis, but abstract's experiments are on CIFAR-10 rather than LLM training. No HF attention signal found manually; weaker fit. |
| `DROD: Dual-Ratio Ordered Dropout for Federated Continual Learning on Heterogeneous Devices` (2610.25220) | Submitted 2026-10-18; `cs.LG`, `cs.DC`; <https://arxiv.org/abs/2610.25220> | Federated continual-learning fit, but experiments use ResNet-18 / Split-CIFAR-100 rather than LLMs. No HF attention signal found manually; lower priority for the user's focused interest set. |

## Older-paper reattention check

- HF Trending currently shows `Harness²: Recursive Agent Harnessing for an Open World`, published 2026-10-09, with 115 upvotes and 14k GitHub stars: <https://huggingface.co/papers/trending>. HF's description mentions continual harness-level learning. This is older than the reporting window and its topic is continual adaptation of agent harnesses, not clearly continual learning of model parameters. The page is a current trending snapshot, but does not expose a dated in-window feature event in the captured view; do not include unless the discover/review stage establishes that signal and judges the semantic fit sufficient.
- Searches also surfaced older PEFT/optimizer papers (including arXiv:2609.36659), but the direct dated HF Daily listing/reattention evidence inside 2026-10-14–20 was not established in the manual pass. Do not substitute them for recent work.

## Source coverage and limitations

- HF Daily source pages checked: <https://huggingface.co/papers>, <https://huggingface.co/papers/date/2026-10-14>, <https://huggingface.co/papers/date/2026-10-15>, <https://huggingface.co/papers/date/2026-10-16>, and <https://huggingface.co/papers/date/2026-10-19>. The current 10-20 page was accessible as `/papers`; a direct `/papers/date/2026-10-20` URL returned an access error. Direct HF paper-page opens sometimes failed in the browser tool, so the daily listing and arXiv page were used when available.
- The manual dated-page scan and exact-string finds were not exhaustive; the discovery adapter found additional Daily items (including 2610.25736, 2610.13521, and 2610.18598) from its preserved raw responses. Final items have date-stamped HF attention evidence and official arXiv metadata.
- arXiv metadata/abstract pages were accessible for the cited IDs. The final write-up must be based on downloaded original text, and should state `partial` if an original source cannot be retrieved or verified.
