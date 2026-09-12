"""CLI for Morning Light Nebius Eyes."""

from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from desk_sentinel.config import FIXTURES_DIR, get_settings
from desk_sentinel.nebius_eyes.analyzer import analyze_exam_card, format_report
from desk_sentinel.nebius_eyes.client import get_nebius_config, list_models

EXAM_CARDS_DIR = FIXTURES_DIR / "exam_cards"
REPO_ROOT = FIXTURES_DIR.parent


def _load_text(source: str) -> str:
    path = Path(source)
    if not path.is_absolute() and not path.exists():
        candidate = EXAM_CARDS_DIR / source
        if candidate.exists():
            path = candidate
    if path.exists():
        return path.read_text(encoding="utf-8")
    return source


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nebius-eyes",
        description=(
            "Morning Light Nebius Eyes — dry bot Exam/card → "
            "Test result · Signal · Problem · Needs · Alarms · Recommend"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze exam/card text")
    analyze.add_argument("--text", help="Inline exam card text")
    analyze.add_argument("--fixture", help="Fixture file under fixtures/exam_cards/")
    analyze.add_argument(
        "--mode",
        choices=["auto", "demo", "live"],
        default="auto",
        help="auto=live when NEBIUS_API_KEY set, else demo (default)",
    )
    analyze.add_argument("--json", action="store_true", help="Emit JSON instead of report")

    sub.add_parser("models", help="List Nebius Token Factory models (requires API key)")

    serve = sub.add_parser("serve", help="Local web UI + /api/analyze")
    serve.add_argument("--port", type=int, default=8787)
    serve.add_argument("--host", default="127.0.0.1")

    demo_all = sub.add_parser("demo", help="Run all bundled exam card fixtures")
    demo_all.add_argument(
        "--mode",
        choices=["auto", "demo", "live"],
        default="demo",
        help="Default demo uses offline rules (default: demo)",
    )

    return parser


def _model_note(mode: str) -> str:
    cfg = get_nebius_config()
    if mode == "demo" or not cfg["api_key"]:
        return "Mode: demo (offline rules) · set NEBIUS_API_KEY for NVIDIA via Token Factory"
    return f"Mode: live · model {cfg['model']} · {cfg['base_url']}"


def cmd_analyze(args: argparse.Namespace) -> int:
    if args.text:
        card = args.text
    elif args.fixture:
        card = _load_text(args.fixture)
    else:
        card = _load_text("safe_hold_dry.txt")

    fields = analyze_exam_card(card, mode=args.mode)
    if args.json:
        print(json.dumps(fields, indent=2))
    else:
        print(format_report(fields, model_note=_model_note(args.mode)))
    return 0


def cmd_models() -> int:
    try:
        models = list_models()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    nvidia = [m for m in models if "nvidia" in m["id"].lower() or "nemotron" in m["id"].lower()]
    print(f"Total models: {len(models)} · NVIDIA/Nemotron: {len(nvidia)}\n")
    for item in nvidia[:20]:
        print(f"  {item['id']}")
    if len(nvidia) > 20:
        print(f"  … and {len(nvidia) - 20} more")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    settings = get_settings()
    fixtures = sorted(EXAM_CARDS_DIR.glob("*.txt"))
    if not fixtures:
        print("No exam card fixtures found.", file=sys.stderr)
        return 1

    print(f"Owner {settings.owner_sign} · Bot {settings.assistant_sign}")
    print(f"Running {len(fixtures)} exam cards in {args.mode} mode\n")

    for path in fixtures:
        print(f"=== {path.name} ===")
        fields = analyze_exam_card(path.read_text(encoding="utf-8"), mode=args.mode)
        print(format_report(fields, model_note=_model_note(args.mode)))
        print()
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    html_path = REPO_ROOT / "nebius-eyes.html"

    class Handler(BaseHTTPRequestHandler):
        def _cors(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            if self.path in ("/", "/index.html"):
                body = html_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self._cors()
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_error(404)

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/api/analyze":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return

            text = payload.get("text", "")
            mode = payload.get("mode", "auto")
            fields = analyze_exam_card(text, mode=mode)
            body = json.dumps(
                {
                    "fields": fields,
                    "report": format_report(fields, model_note=_model_note(mode)),
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *log_args: object) -> None:
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % log_args))

    server = HTTPServer((args.host, args.port), Handler)
    print(f"Morning Light Nebius Eyes → http://{args.host}:{args.port}/")
    print("POST /api/analyze with {\"text\": \"...\", \"mode\": \"auto|demo|live\"}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        return cmd_analyze(args)
    if args.command == "models":
        return cmd_models()
    if args.command == "demo":
        return cmd_demo(args)
    if args.command == "serve":
        return cmd_serve(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
