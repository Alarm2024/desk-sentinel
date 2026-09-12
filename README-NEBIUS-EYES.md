# Morning Light Nebius Eyes

**Nebius×NVIDIA Global AI Hackathon** · Track: **Best Apps and Agents** / **Coding and Agentic Engineering**

Owner ✝️🧿🪬 · Bot 3️⃣🧿5️⃣ · **elghaly / Wyndham Heaven**

A minimal honest dry-desk tool: paste a **dry bot Exam/card** text block and get a structured readout:

**Test result · Signal · Problem · Needs · Alarms · Recommend**

Powered by **[Nebius Token Factory](https://nebius.com/services/token-factory)** with an **NVIDIA Nemotron** open model. No live trading. No CLEAR+/go. English only. Mock fixtures included.

## Hackathon compliance

| Requirement | How |
| --- | --- |
| Nebius Token Factory / AI Cloud | OpenAI-compatible client → `https://api.tokenfactory.nebius.com/v1/` |
| NVIDIA open-source model | Default `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` (Nemotron family) |
| Public repo + license | MIT — [LICENSE](LICENSE) |
| Working demo + README | CLI, web UI, offline demo mode |
| No secrets in repo | `.env.example` only — set `NEBIUS_API_KEY` locally |

### $25 Nebius credits (Devpost)

Use activation code **`NEBIUS-DEVPOST-GLOBAL26`** on the hackathon credits form linked from [Devpost](https://nebius-global-ai-hackathon.devpost.com/) to claim **$25** in Nebius Token Factory credits.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add NEBIUS_API_KEY for live Nemotron
```

### Demo (no API key)

```bash
python -m desk_sentinel.nebius_eyes demo
python -m desk_sentinel.nebius_eyes analyze --fixture safe_hold_dry.txt
python -m desk_sentinel.nebius_eyes analyze --fixture bridge_fault.txt
```

### Live Nemotron via Token Factory

```bash
export NEBIUS_API_KEY=your_key_here
# optional: export NEBIUS_MODEL=nvidia/Nemotron-3_5-Lightning
python -m desk_sentinel.nebius_eyes analyze --fixture short_market.txt --mode live
python -m desk_sentinel.nebius_eyes models   # list NVIDIA models on your project
```

### Web UI

```bash
python -m desk_sentinel.nebius_eyes serve
# open http://127.0.0.1:8787/
```

Static fallback (browser-only demo rules): open [nebius-eyes.html](nebius-eyes.html) — use `serve` for live Nemotron.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `NEBIUS_API_KEY` | — | Token Factory API key (never commit) |
| `NEBIUS_BASE_URL` | `https://api.tokenfactory.nebius.com/v1/` | OpenAI-compatible base URL |
| `NEBIUS_MODEL` | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | NVIDIA model ID on Token Factory |
| `NEBIUS_EYES_MODE` | `auto` | `auto` · `demo` · `live` |

To pick another Nemotron variant, run `python -m desk_sentinel.nebius_eyes models` and set `NEBIUS_MODEL` to any listed `nvidia/…` ID.

## Sample output

```
✝️🧿🪬

Morning Light Nebius Eyes
────────────────────────────────
Test result · PASS — SAFE HOLD dry watch
Signal · Neutral regime · stable liquidity · pre-open session
Problem · None — routine dry holding pattern
Needs · Continue silent watch · no operator action
Alarms · NONE
Recommend · Keep monitoring. Re-pulse exam card on next tick.

Mode: demo (offline rules) · set NEBIUS_API_KEY for NVIDIA via Token Factory

3️⃣🧿5️⃣
```

## Project layout

```
desk_sentinel/nebius_eyes/   # CLI, analyzer, Nebius client
fixtures/exam_cards/         # Dry bot exam/card text fixtures
nebius-eyes.html             # Web UI (works with serve)
```

## Related

This repo also ships **Morning Light Desk Sentinel** (Strands agent, AWS Agents for Humans track). See [README.md](README.md).

## License

MIT — see [LICENSE](LICENSE).
