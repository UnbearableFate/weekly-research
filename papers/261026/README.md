## [Learning from Fleet Experience: A Collective Learning Paradigm for Robots](Learning%20from%20Fleet%20Experience%20-%20A%20Collective%20Learning%20Paradigm%20for%20Robots.pdf)

上传日期：2026-10-19

**WHY (EN):** Robots can improve after deployment, but relying on human corrections for every failure limits fleet-scale learning.

**HOW (EN):** FERT retrieves successful trajectory segments using failure contexts and prioritizes their actions for supervised policy updates; FATS asynchronously coordinates robot experience collection, training, and policy rollout.

**WHY（中文）：** 機器人可從部署經驗中改進，但若每次失敗都仰賴人工糾正，機隊擴展便難以帶動持續學習。

**HOW（中文）：** FERT 以失敗情境檢索成功軌跡片段，優先用其動作監督策略更新；FATS 非同步協調經驗收集、訓練與策略分發。

## [PyTorch Distributed: Experiences on Accelerating Data Parallel Training](PyTorch%20Distributed%20-%20Experiences%20on%20Accelerating%20Data%20Parallel%20Training.pdf)

上传日期：2020-06-28

**WHY (EN):** Data-parallel training wastes time when gradient communication cannot overlap with the backward pass.

**HOW (EN):** PyTorch DDP groups gradients into buckets and uses autograd hooks to launch asynchronous AllReduce when each bucket is ready, overlapping communication with remaining computation.

**WHY（中文）：** 資料平行訓練若梯度通訊無法與反向傳播重疊，便會浪費計算時間。

**HOW（中文）：** PyTorch DDP 將梯度分桶，並由自動微分鉤子在分桶就緒時啟動非同步 AllReduce，讓通訊與後續計算重疊。

## [Scaling Parameter-Efficient Fine-Tuning for Brain Encoding](Scaling%20Parameter-Efficient%20Fine-Tuning%20for%20Brain%20Encoding.pdf)

上传日期：2026-10-19

**WHY (EN):** Frozen readouts cannot specialize large backbones, while full fine-tuning is costly when neural data is scarce.

**HOW (EN):** A causal single-pass feature path encodes all time points together; rank-16 LoRA adapters and lightweight readouts adapt the backbone, while a fused multi-LoRA kernel trains many adapters jointly.

**WHY（中文）：** 只訓練讀出層無法使大型骨幹充分特化，而神經資料稀少時，全量微調的成本又很高。

**HOW（中文）：** 因果式單次前向路徑同時編碼各時間點；模型以 rank-16 LoRA 與輕量讀出層適配骨幹，並用融合式 multi-LoRA 核心共同訓練多組適配器。

## [Memory-Centric Continual Learning for AI Agents](Memory-Centric%20Continual%20Learning%20for%20AI%20Agents.pdf)

上传日期：2026-10-21

**WHY (EN):** Agent memory can retain information without preserving useful behavior when tasks change or experiences interfere.

**HOW (EN):** MCCL models continual learning as coupled memory-state and feedback-updated management-policy loops, and specifies stateful-versus-reset tests for behavioral retention, adaptation, and transfer.

**WHY（中文）：** 代理記憶可能留住資訊，卻未必能在任務變動或經驗互相干擾時維持有效行為。

**HOW（中文）：** MCCL 將持續學習描述為記憶狀態迴圈與回饋更新的管理策略迴圈，並提出以保留狀態對照重置狀態來測量保留、適應與遷移。

## [Ultralytics YOLO26: Unified Real-Time End-to-End Vision Models](Ultralytics%20YOLO26%20-%20Unified%20Real-Time%20End-to-End%20Vision%20Models.pdf)

上传日期：2026-06-02

**WHY (EN):** Long training schedules make real-time detector development expensive.

**HOW (EN):** YOLO26 uses MuSGD, which mixes Muon’s orthogonalized momentum updates with momentum SGD for matrix-valued weights while retaining SGD for biases and normalization parameters.

**WHY（中文）：** 即時物件偵測器往往需要漫長訓練，使開發成本偏高。

**HOW（中文）：** YOLO26 採用 MuSGD：對矩陣權重混合 Muon 正交化動量更新與動量 SGD，對偏置與正規化參數則保留 SGD。

## [Evaluating Agentic Capabilities Before Post-Training: An End-to-End Approach](Evaluating%20Agentic%20Capabilities%20Before%20Post-Training%20-%20An%20End-to-End%20Approach.pdf)

上传日期：2026-10-14

**WHY (EN):** Static proxies reveal little about how interactive agent capabilities emerge during language-model pretraining.

**HOW (EN):** ASAP adapts completion-style base models to agent scaffolds using short verified trajectory prefixes and minimal recovery rules, then analyzes step-level behavior across pretraining checkpoints.

**WHY（中文）：** 靜態代理任務難以呈現互動式代理能力如何在語言模型預訓練中形成。

**HOW（中文）：** ASAP 以經核實的短軌跡前綴和精簡復原規則，將補全文本式基礎模型接入代理框架，再比較不同預訓練檢查點的逐步行為。

## [Deep Fusion Memory: A Chunk-Level Parametric Memory for Large Language Models](Deep%20Fusion%20Memory%20-%20A%20Chunk-Level%20Parametric%20Memory%20for%20Large%20Language%20Models.pdf)

上传日期：2026-10-18

**WHY (EN):** Continued pretraining can overwrite prior knowledge, while online retrieval adds cost when language models acquire domain information.

**HOW (EN):** DFM trains chunk-level memory predictors and gated cross-attention modules against retrieval-derived targets while freezing the backbone, fusing predicted memory into decoder states without retrieval at inference.

**WHY（中文）：** 持續預訓練可能覆寫既有知識，而線上檢索會增加語言模型取得領域資訊時的成本。

**HOW（中文）：** DFM 凍結骨幹，以檢索所得目標訓練區塊級記憶預測器與閘控交叉注意力模組，將預測記憶融合進解碼器狀態，推論時無須檢索。

## [Policy Is Not Capability: Some Safety Benchmarks Measure Which Definition of "Unsafe" You Trained On](Policy%20Is%20Not%20Capability%20-%20Some%20Safety%20Benchmarks%20Measure%20Which%20Definition%20of%20-%20Unsafe%20-%20You%20Trained%20On.pdf)

上传日期：2026-10-18

**WHY (EN):** Guardrail benchmark scores can reflect the label policy learned during training rather than detection capability alone.

**HOW (EN):** Across ten training arms, the study varies how two label policies enter supervised training, distillation, and head-only calibration while holding architecture and optimizer family fixed, tracing their effects on evaluation.

**WHY（中文）：** 安全護欄的基準分數可能反映訓練時學到的標註政策，而不只是偵測能力。

**HOW（中文）：** 研究比較十種訓練設定，改變兩種標註政策進入監督訓練、蒸餾與僅訓練輸出頭的方式，並固定架構和最佳化器家族來追蹤評測變化。

## [Answering in the User's Variety: Calibrated Accommodation Pairs for Post-Training](Answering%20in%20the%20User%27s%20Variety%20-%20Calibrated%20Accommodation%20Pairs%20for%20Post-Training.pdf)

上传日期：2026-10-20

**WHY (EN):** Post-training can standardize replies while favoring some dialect features, and output audits miss stage-specific preferences.

**HOW (EN):** Content-matched prompts diagnose SFT, DPO, and RL updates; calibrated accommodation pairs encode DPO preferences that distinguish user-matched feature density from over-accommodation and dialect imposition.

**WHY（中文）：** 後訓練可能使回覆趨於標準化並偏好某些方言特徵，單看輸出難以辨認各階段的偏好。

**HOW（中文）：** 研究以內容相同的提示診斷 SFT、DPO 與 RL 更新；校準式語言調適偏好組則用 DPO 區分貼合使用者特徵密度、過度調適與強加方言。

## [TokenGate: Adapting LLMs for Fast and Memory-Efficient Prefill with Learned Token Pruning](TokenGate%20-%20Adapting%20LLMs%20for%20Fast%20and%20Memory-Efficient%20Prefill%20with%20Learned%20Token%20Pruning.pdf)

上传日期：2026-10-19

**WHY (EN):** Long prompts waste prefill compute and KV memory when every token passes through each decoder layer.

**HOW (EN):** A learned gate keeps the top-K tokens at an intermediate layer; token-gated attention carries their importance scores into later layers, enabling end-to-end adaptation of the gate and model.

**WHY（中文）：** 長提示中的每個詞元都經過所有解碼器層，造成預填充計算與 KV 記憶體浪費。

**HOW（中文）：** 學習式閘門在中間層保留 top-K 詞元；詞元閘控注意力將重要性分數帶入後續層，讓閘門與模型可端到端適配。
