"""
Batch annotation of customer-service chat sessions.

Default backend: SiliconFlow (OpenAI-compatible) with DeepSeek-V3.
Switchable to any OpenAI-compatible provider via --base-url.

Input:  raw chat JSON (list of sessions, see dataset structure)
Output: annotated JSONL (one annotation per line, schema v0.1)

Run:
    export SILICONFLOW_API_KEY=...
    python annotate_batch.py \
        --input  /path/to/chat_20260402_judged.json \
        --output ./annotated_full.jsonl \
        --model  deepseek-ai/DeepSeek-V3 \
        --max-workers 8

Resumes by skipping session_ids already present in the output JSONL.
"""
from __future__ import annotations
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from openai import OpenAI, APIError

SCHEMA_PROMPT = """You are an analyst extracting *diagnostic-process* signals from a customer-service chat. Output ONE JSON object conforming to the schema below. Do NOT wrap with markdown fences.

Schema:
{
  "session_id": str,
  "category": str,
  "is_diagnostic": bool,        // true if Agent did real clarify/verify/hypothesize work
  "is_transactional": bool,     // true if pure purchase/approval/template flow
  "initial_symptom": str,       // user's first concrete complaint (<=50 chars, original phrasing)
  "symptom_normalized": str,    // one of: 资源/容量类|环境配置类|连接/网络类|性能/卡顿类|报错/异常类|权限/账号类|计费/订单类|操作不会用类|数据/IO类|产品咨询类
  "turns": [                    // merged-by-semantic-unit, agent turns labeled
    {"i": int, "role": "User"|"Agent", "act"?: str, "excerpt": str(<=120)}
  ],
  "info_requested": [{"type": str, "raw": str}],   // type ∈ job_id|screenshot|error_log|command_output|version|account|region|package_name|code_snippet|artifact_check
  "hypotheses": [{"raw": str, "verdict": "confirmed"|"rejected"|"untested"|"partially_confirmed"}],
  "root_cause": str|null,
  "solution": str|null,
  "diagnosis_quality": {
    "score": 1|2|3|4|5|null,    // 5=one-shot accurate; 1=wrong/dropped; null if non-diagnostic
    "rationale": str,
    "patterns_good": [str],
    "patterns_bad": [str]
  },
  "reusable_assets": {
    "trigger_phrases": [str],
    "must_ask": [str],
    "decision_branch": str|null,
    "notes"?: str
  }
}

Dialogue act labels (for turns[].act, Agent only): greet | clarify_symptom | request_artifact | request_repro | hypothesize | verify | confirm_finding | instruct | educate | handoff | decline | closing | boilerplate. Combine with '+' if needed.

Rules:
- Merge consecutive Agent fragments into one logical turn before labeling.
- For pure transactional sessions (auto-purchase/approval), set is_diagnostic=false, is_transactional=true, score=null.
- initial_symptom must be the user's FIRST substantive complaint, not greetings.
- Strings in Chinese OK. Output strict JSON only.
"""

def build_user_prompt(session: dict) -> str:
    sid = session.get("sessionId", "")
    cat = session.get("category", "")
    msgs = session.get("messages", [])
    lines = [f"session_id: {sid}", f"category: {cat}", "messages:"]
    for i, m in enumerate(msgs):
        c = (m.get("content") or "").replace("\n", " / ")
        lines.append(f"  [{i:02d}][{m.get('role')}] {c[:500]}")
    return "\n".join(lines)


def annotate_session(client: OpenAI, model: str, session: dict, retries: int = 3) -> dict:
    user = build_user_prompt(session)
    last_err = None
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                max_tokens=4096,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SCHEMA_PROMPT},
                    {"role": "user", "content": user},
                ],
            )
            text = (resp.choices[0].message.content or "").strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:].strip()
            obj = json.loads(text)
            obj["_session_id"] = session.get("sessionId")
            obj["_category"] = session.get("category")
            return obj
        except (APIError, json.JSONDecodeError) as e:
            last_err = e
            time.sleep(2 ** attempt)
    return {
        "_session_id": session.get("sessionId"),
        "_error": f"{type(last_err).__name__}: {last_err}",
    }


def load_done(out_path: Path) -> set[str]:
    if not out_path.exists():
        return set()
    done = set()
    with out_path.open() as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("_session_id"):
                    done.add(obj["_session_id"])
            except json.JSONDecodeError:
                pass
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V3")
    ap.add_argument("--base-url", default="https://api.siliconflow.cn/v1")
    ap.add_argument("--api-key-env", default="SILICONFLOW_API_KEY",
                    help="env var holding the API key")
    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="0 = all")
    args = ap.parse_args()

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        sys.exit(f"error: env var {args.api_key_env} not set")
    client = OpenAI(api_key=api_key, base_url=args.base_url)
    sessions = json.loads(Path(args.input).read_text())
    out_path = Path(args.output)
    done = load_done(out_path)

    todo = [s for s in sessions if s.get("sessionId") not in done]
    if args.limit:
        todo = todo[: args.limit]
    print(f"total={len(sessions)} done={len(done)} todo={len(todo)}", file=sys.stderr)

    with out_path.open("a") as out, ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(annotate_session, client, args.model, s): s for s in todo}
        for n, fut in enumerate(as_completed(futures), 1):
            obj = fut.result()
            out.write(json.dumps(obj, ensure_ascii=False) + "\n")
            out.flush()
            if n % 20 == 0:
                print(f"  progress {n}/{len(todo)}", file=sys.stderr)


if __name__ == "__main__":
    main()
