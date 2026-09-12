# Morning Light Desk Sentinel

Owner ✝️🧿🪬 · Assistant 3️⃣🧿5️⃣ · **elghaly / Wyndham Heaven**

> **Nebius×NVIDIA Global AI Hackathon:** see **[Morning Light Nebius Eyes](README-NEBIUS-EYES.md)** — dry bot Exam/card → structured desk readout via **Nebius Token Factory** + **NVIDIA Nemotron**. Quick run: `python -m desk_sentinel.nebius_eyes demo`

**Agents for Humans — Professional Agents track** · AWS Devpost · due Sep 14, 2026

A [Strands Agents SDK](https://strandsagents.com/) agent that quietly monitors **dry desk** status from mock JSON fixtures and **only notifies the human when a real decision is needed** — CLEAR go/no-go, SHORT market stance, or a genuine fault. Not a babysit dashboard.

## Problem

Solo desk operators cannot stare at dashboards all morning. Most status ticks are noise: SAFE HOLD dry states, routine pre-open checks, and benign drift. But missing a **CLEAR ready** window, a **SHORT regime** shift, or a **real execution fault** is costly.

Morning Light Desk Sentinel watches on your behalf and surfaces **decision-grade** moments only.

## Who it's for

- **Solo desk operators** running dry / paper lanes before live engagement
- Operators who want an agent **in the loop**, not another chart to babysit
- Teams exploring **Agents for Humans** — automation that respects human attention

## Why it matters

| State | Agent behavior |
| --- | --- |
| SAFE HOLD (dry) | **Silent** — keeps monitoring, no ping |
| CLEAR ready | **Notify** — go / no-go decision |
| SHORT market | **Notify** — engage or stand down |
| Real fault | **Notify** — critical operational alert |

All demo data is **mock JSON**. No Jupiter, Telegram, or trading keys are wired in.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the Strands tool loop and mermaid diagram.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional — defaults work for demo
```

### Run the demo (no cloud keys)

Default fixture — **SAFE HOLD dry** (agent stays silent):

```bash
python3 -m desk_sentinel demo
```

Run all bundled scenarios:

```bash
python3 -m desk_sentinel demo --all
```

Individual fixtures:

```bash
python3 -m desk_sentinel demo --fixture clear_ready.json
python3 -m desk_sentinel demo --fixture short_market.json
python3 -m desk_sentinel demo --fixture real_fault.json
```

Expected behavior:

- `safe_hold_dry.json` → silent watch, **no** notification banner
- `clear_ready.json` → go/no-go alert
- `short_market.json` → SHORT regime alert
- `real_fault.json` → critical fault alert

## Tools (Strands `@tool`)

| Tool | Purpose |
| --- | --- |
| `read_status` | Load mock desk JSON fixture |
| `decide_surface` | Classify silent vs notify + urgency |
| `notify_human` | Mock console alert (no Telegram) |

The **Strands agent loop** orchestrates these tools. In demo mode, a scripted `DemoModel` drives the same event loop without Bedrock/OpenAI credentials.

## Optional live models

Set in `.env`:

```bash
DESK_MODEL_MODE=openai   # requires OPENAI_API_KEY
DESK_MODEL_MODE=bedrock  # requires AWS credentials + model access
```

## Project layout

```
desk_sentinel/          # Python package
  tools/                # read_status, decide_surface, notify_human
  demo_model.py         # Keyless Strands model for local demo
  agent.py              # Agent factory + run_watch()
fixtures/               # Mock desk status JSON
```

## License

MIT — see [LICENSE](LICENSE).

## Hackathons

| Event | Entry | Docs |
| --- | --- | --- |
| **Nebius×NVIDIA Global AI Hackathon** | Morning Light Nebius Eyes | [README-NEBIUS-EYES.md](README-NEBIUS-EYES.md) |
| **AWS Devpost — Agents for Humans** | Morning Light Desk Sentinel | this README |

Repository: [Alarm2024/desk-sentinel](https://github.com/Alarm2024/desk-sentinel)
