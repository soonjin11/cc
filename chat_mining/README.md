# Chat Mining: 客服诊断行为挖掘

从客服聊天记录中**提炼"问诊"过程**（望闻问切）而非仅抽取"药方"（解决方案）。

## 目录结构

```
chat_mining/
├── schema/
│   └── annotation_schema.md       # v0.1 标注 schema：turn-level dialogue acts + session-level 字段
├── samples/
│   └── annotated_samples.json     # 10 个手工标注样本（覆盖 8 个 category）
├── scripts/
│   ├── annotate_batch.py          # LLM 批量标注全量 806 个 session
│   └── aggregate_report.py        # 聚合标注产物生成 markdown 报表
└── reports/
    └── sample_report.md           # 用 10 样本跑出的演示报表
```

## 工作流

### 1. Schema 设计 (已完成 v0.1)
见 `schema/annotation_schema.md`。两层标注：
- **Turn-level**：每条 Agent 消息打 dialogue act 标签（`clarify_symptom` / `request_artifact` / `verify` / `hypothesize` / `confirm_finding` / `instruct` / ...）
- **Session-level**：`initial_symptom`、`info_requested[]`、`hypotheses[]`、`root_cause`、`solution`、`diagnosis_quality`、`reusable_assets`

核心理念：把 reason 字段里"是否给了链接/方案"那种偏向**药方**的判断，**改为评估问诊过程**：客服是否澄清了症状、索取了关键信息、提出并核实了假设。

### 2. 抽样验证 (已完成 10 个)
手工标注 10 个跨 category 的 session，验证 schema 字段是否覆盖：
- 修正型问诊 (idx=167，资源不足)
- 关键词反射 (idx=263，module purge)
- 服务端/客户端隔离 (idx=669，gateway)
- 边界 decline + workaround (idx=65，国际带宽)
- 流程类咨询 (idx=81，活动 token)
- 纯交易/模板 (idx=162，购买)
- 等等

### 3. 批量标注 (待跑)

```bash
export ANTHROPIC_API_KEY=...
python chat_mining/scripts/annotate_batch.py \
    --input  /path/to/chat_20260402_judged.json \
    --output chat_mining/reports/annotated_full.jsonl \
    --model  claude-sonnet-4-6 \
    --max-workers 8
```

特性：
- prompt cache 复用 schema 部分，省 token
- 失败重试 + 指数退避
- 按 session_id 续跑（jsonl 增量写入）
- 总量 ~806，预计 1–2 小时单机跑完

### 4. 聚合报表

```bash
python chat_mining/scripts/aggregate_report.py \
    --input chat_mining/reports/annotated_full.jsonl \
    --out   chat_mining/reports/full_report.md
```

每个 category 输出：
- 症状分布
- 必索取信息 top-K（如 HPC 类：作业号、报错；网络类：region、URL）
- 诊断质量评分均值与分布
- 高频好做法 / 高频反模式
- 决策分支目录（一句话流程图）
- 触发短语索引（用户口语 → 症状归类）

### 5. 后续可做

- **反模式案例库**：抽 score≤2 的会话做培训反例
- **决策树合成**：把同症状下多个 decision_branch 合成完整流程图（FSM）
- **Agent 评估**：用 must_ask + decision_branch 当评分卡，回测每个客服个体表现
- **训练 RAG/agent**：trigger_phrases 当用户意图入口，must_ask 当工具调用清单
- **跨日趋势**：当数据集扩展到多个日期文件时，监控诊断质量随时间变化

## 与原 judgment 字段的关系

原数据 `judgment="valuable"` + `reason` 字段评判的是**是否给了具体方案/链接**，与"问诊质量"是两个维度：
- 一个会话可以 valuable（最终给了方案）但 `diagnosis_quality.score=2`（直接甩链接没问诊）
- 我们的 schema 显式区分这两层，便于针对**问诊能力**单独训练和复盘

## Schema 演进

v0.1 是初版。在跑全量 806 之前可能还要根据更多样本调整：
- 是否需要拆分 `request_artifact` 为更细的子类（视觉证据 vs 数值证据 vs 系统状态）
- 是否需要 turn-level 的 `user_act` 标签（用户在反馈、抱怨、跟进、确认）
- `symptom_normalized` 枚举是否够用（HPC 类目前都被压成"环境配置类"，可能需要二级标签）

建议跑完前 50 个之后人工 review 一轮再决定是否升 v0.2。
