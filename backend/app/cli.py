from __future__ import annotations

import argparse
import json
from typing import Any

from app.models import AssistantResponse, DocumentAnalysis, Overview, PromptEvaluation
from app.services import analyze_document, evaluate_prompt, get_overview, plan_assistant_reply


def main() -> None:
    parser = argparse.ArgumentParser(prog="cloud-ai-console")
    subparsers = parser.add_subparsers(dest="command", required=True)

    assistant_parser = subparsers.add_parser("assistant", help="Review a workflow prompt")
    assistant_parser.add_argument("--prompt", required=True)
    assistant_parser.add_argument("--workflow-id", default=None)

    document_parser = subparsers.add_parser("document", help="Analyze a note or document")
    document_parser.add_argument("--title", required=True)
    document_parser.add_argument("--content", required=True)

    prompt_parser = subparsers.add_parser("prompt", help="Evaluate a prompt")
    prompt_parser.add_argument("--prompt", required=True)

    subparsers.add_parser("overview", help="Print workspace overview")

    args = parser.parse_args()

    if args.command == "assistant":
        result = plan_assistant_reply(args.prompt, args.workflow_id)
    elif args.command == "document":
        result = analyze_document(args.title, args.content)
    elif args.command == "prompt":
        result = evaluate_prompt(args.prompt)
    else:
        result = get_overview()

    print(_dump_model(result))


def _dump_model(model: Overview | AssistantResponse | DocumentAnalysis | PromptEvaluation) -> str:
    payload: dict[str, Any] = model.model_dump()
    return json.dumps(payload, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
