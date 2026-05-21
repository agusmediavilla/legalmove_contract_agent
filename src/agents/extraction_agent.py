from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.models import ContractChangeOutput


EXTRACTION_SYSTEM_PROMPT = """
Eres un agente legal de extracción de diferencias. Recibes un mapa contextual y los textos
completos del contrato original y de la enmienda. Tu responsabilidad exclusiva es identificar
los cambios introducidos por la enmienda.

Criterios:
- Distingue modificaciones, adiciones y eliminaciones.
- Incluye cambios comerciales: precio, honorarios, plazos, SLA, soporte, terminación.
- Incluye cambios legales: confidencialidad, propiedad intelectual, protección de datos,
  legislación aplicable, alcance de licencia o servicio.
- No incluyas cláusulas idénticas salvo para explicar que no cambiaron cuando sea necesario.
- El resultado debe cumplir exactamente el schema Pydantic ContractChangeOutput.
- Redacta el resumen de forma precisa, útil para Compliance y sin inventar información.
""".strip()


class ExtractionAgent:
    def __init__(self, model: str = "gpt-4o", temperature: float = 0) -> None:
        base_llm = ChatOpenAI(model=model, temperature=temperature)
        self.llm = base_llm.with_structured_output(ContractChangeOutput)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EXTRACTION_SYSTEM_PROMPT),
                (
                    "human",
                    "Mapa contextual:\n{context_map}\n\nContrato original:\n{original_text}\n\nEnmienda:\n{amendment_text}",
                ),
            ]
        )
        self.chain = self.prompt | self.llm

    def run(
        self,
        *,
        context_map: str,
        original_text: str,
        amendment_text: str,
    ) -> ContractChangeOutput:
        result = self.chain.invoke(
            {
                "context_map": context_map,
                "original_text": original_text,
                "amendment_text": amendment_text,
            }
        )
        if isinstance(result, ContractChangeOutput):
            return result
        return ContractChangeOutput.model_validate(result)
