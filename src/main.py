from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent
from src.image_parser import parse_contract_image
from src.models import ContractChangeOutput
from src.observability import LangfuseTracer


def run_pipeline(
    original_image_path: str,
    amendment_image_path: str,
    *,
    model: str = "gpt-4o",
) -> ContractChangeOutput:
    tracer = LangfuseTracer(name="contract-analysis")

    with tracer.span(
        "parse_original_contract",
        input_data={"image_path": original_image_path},
        metadata={"model": model},
    ) as span:
        original_text = parse_contract_image(original_image_path, model=model)
        span.update(output=original_text)

    with tracer.span(
        "parse_amendment_contract",
        input_data={"image_path": amendment_image_path},
        metadata={"model": model},
    ) as span:
        amendment_text = parse_contract_image(amendment_image_path, model=model)
        span.update(output=amendment_text)

    contextualization_agent = ContextualizationAgent(model=model)
    with tracer.span(
        "contextualization_agent",
        input_data={"original_text": original_text, "amendment_text": amendment_text},
        metadata={"agent": "ContextualizationAgent"},
    ) as span:
        context_map = contextualization_agent.run(original_text, amendment_text)
        span.update(output=context_map)

    extraction_agent = ExtractionAgent(model=model)
    with tracer.span(
        "extraction_agent",
        input_data={
            "context_map": context_map,
            "original_text": original_text,
            "amendment_text": amendment_text,
        },
        metadata={"agent": "ExtractionAgent", "schema": "ContractChangeOutput"},
    ) as span:
        result = extraction_agent.run(
            context_map=context_map,
            original_text=original_text,
            amendment_text=amendment_text,
        )
        validated = ContractChangeOutput.model_validate(result)
        span.update(output=validated.model_dump())

    tracer.flush()
    return validated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LegalMove - agente autónomo de comparación de contratos"
    )
    parser.add_argument("original_image", help="Path JPEG/PNG del contrato original")
    parser.add_argument("amendment_image", help="Path JPEG/PNG de la enmienda/adenda")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o"))
    parser.add_argument("--output", "-o", help="Archivo JSON de salida opcional")
    return parser


def main() -> None:
    load_dotenv()
    args = build_parser().parse_args()
    result = run_pipeline(args.original_image, args.amendment_image, model=args.model)
    payload = result.model_dump()
    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(json_text + "\n", encoding="utf-8")
    print(json_text)


if __name__ == "__main__":
    main()
