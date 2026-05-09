# 客服会话诊断行为标注 Schema v0.1

目标：从客服聊天记录中提炼"问诊"行为（望、闻、问、切），而非仅抽取"药方"。
针对单条 session 的 messages 序列，输出两层标注：
1. **turn-level**：每条 Agent 消息打一个 dialogue act 标签
2. **session-level**：整个会话的诊断结构化字段

---

## 1. Turn-level Dialogue Act 标签集

只对 `role == "Agent"` 的消息打标。一条消息只打一个主标签（必要时可加副标签）。

| 标签 | 含义 | 触发示例 |
|---|---|---|
| `greet` | 问候、寒暄、安抚 | "老师您好"、"您客气了" |
| `clarify_symptom` | 追问症状/现象细节 | "是什么现象呢？"、"具体什么报错？" |
| `request_artifact` | 索取定位所需具体信息或物料 | "麻烦提供作业号"、"截图发我看下"、"什么版本" |
| `request_repro` | 请用户重现/再试一次以观察 | "您再点一下试试"、"重新提交看下" |
| `hypothesize` | 提出假设/初步判断 | "可能是CPU资源不足"、"看着像 glibc 问题" |
| `verify` | 主动核查（看后台、查日志、登账号查） | "我这边看下"、"我登账号查一下" |
| `confirm_finding` | 通报核查结果（结论性陈述） | "确认了下，是资源不够" |
| `instruct` | 给出操作步骤/命令/链接（开药方） | "执行 pip install ..."、文档链接 |
| `educate` | 背景知识科普（不是直接解法） | "DCU都需要适配"、"集群节点用ib通信" |
| `handoff` | 转交他人/排期/挂单 | "明天上午给您反馈"、"@业务老师" |
| `decline` | 表明能力边界/拒绝 | "我这边操作不了"、"目前不提供国际带宽" |
| `closing` | 收尾 | "有问题随时沟通" |
| `boilerplate` | 模板化声明（购买协议、审批通过等，无诊断价值） | 商品声明、审批模板 |

副标签（可选，作为 list）：
- `tone:reassuring` 安抚情绪
- `tone:apology` 道歉
- `escalation` 表示升级到二线/业务

---

## 2. Session-level 结构化字段

```json
{
  "session_id": "...",
  "category": "AI计算服务",
  "is_diagnostic": true,
  "is_transactional": false,
  "initial_symptom": "明明有卡但是开机一直失败显示没卡",
  "symptom_normalized": "资源/容量类-创建实例失败",
  "diagnostic_phase": {
    "start_turn": 0,
    "end_turn": 11,
    "turn_count": 12,
    "agent_diagnostic_turns": 5
  },
  "info_requested": [
    {"type": "screenshot", "raw": "点击查看详情呢"},
    {"type": "artifact_check", "raw": "我这边看下"}
  ],
  "hypotheses": [
    {"raw": "可能是卡了显示问题或网络原因创建慢", "verdict": "rejected"},
    {"raw": "CPU资源不够导致显示有卡但提交不成功", "verdict": "confirmed"}
  ],
  "root_cause": "CPU资源不足（即使GPU显示有余量）",
  "solution": "等待资源释放或更换区域",
  "diagnosis_quality": {
    "score": 4,
    "rationale": "首假设错误（怪到网络），但客服主动复核并修正到真根因；用户教育到位",
    "patterns_good": ["主动核查 verify→confirm_finding", "修正初判"],
    "patterns_bad": ["首问'点击查看详情'过于含糊"]
  },
  "reusable_assets": {
    "trigger_phrases": ["有卡但创建失败", "显示没卡"],
    "must_ask": ["报错截图/详情", "实例规格"],
    "decision_branch": "GPU充足但创建失败 → 看CPU余量 → 资源池整体紧张？ → 建议等待或换区"
  }
}
```

### 字段说明

- **is_diagnostic**：是否包含真正的诊断过程（有澄清/验证/假设）。模板化购买/安装服务通常 false。
- **is_transactional**：是否仅为交易/审批流程类（购买、退款、审批）。
- **initial_symptom**：用户最早一条非寒暄消息的核心诉求（原文，不超 50 字）。
- **symptom_normalized**：用枚举词归类，便于聚合：
  - `资源/容量类` `环境配置类` `连接/网络类` `性能/卡顿类` `报错/异常类` `权限/账号类` `计费/订单类` `操作不会用类` `数据/IO类` `产品咨询类`
- **info_requested**：客服索取的信息条目，type 取自固定集合：
  - `job_id` `screenshot` `error_log` `command_output` `version` `account` `region` `package_name` `code_snippet` `artifact_check`(指客服自己去后台查)
- **hypotheses[].verdict**：`confirmed` / `rejected` / `untested`
- **diagnosis_quality.score**：1–5 分主观评估
  - 5 = 一次性命中根因，问诊精准
  - 4 = 略有绕弯但及时修正
  - 3 = 多次绕弯最终定位
  - 2 = 没真正诊断，直接给文档；用户后续仍困惑
  - 1 = 诊断错误或不了了之
- **reusable_assets.trigger_phrases**：用户可能用来描述同类问题的口语表达
- **reusable_assets.must_ask**：处理此类问题必须索取的信息字段
- **reusable_assets.decision_branch**：一句话流程图

---

## 3. 标注流程约定

1. 只标注 `judgment == "valuable"` 的会话（本数据集全部）
2. 短会话（messages < 4）默认 `is_diagnostic=false`，仍要填 `symptom_normalized` 和 `solution`
3. 当 session 包含多个独立子问题（如 idx=162 同时购买 FLUENT 和 WORKBENCH），按主问题标注，副问题在 notes 提及
4. 客服的发送消息常被切成多条短消息（"老师"+"麻烦提供作业号"+"在作业管理"），打标时按**语义单元**合并为一个 turn 再标 act
