from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


CONTEXTUALIZATION_SYSTEM_PROMPT = """
Eres un agente legal de contextualización. Tu única tarea es construir un mapa comparado
entre un contrato original y su enmienda. No extraigas todavía una lista final de cambios.

Debes identificar:
1. Tipo de contrato y partes.
2. Secciones del contrato original.
3. Secciones de la enmienda o versión actualizada.
4. Correspondencia entre secciones equivalentes.
5. Secciones nuevas, omitidas o con posible renumeración.
6. Propósito legal o comercial de cada bloque.

Devuelve texto estructurado en español, con encabezados claros y referencias a números de cláusula.
""".strip()


class ContextualizationAgent:
    def __init__(self, model: str = "gpt-4o", temperature: float = 0) -> None:
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CONTEXTUALIZATION_SYSTEM_PROMPT),
                (
                    "human",
                    "Contrato original:\n{original_text}\n\nEnmienda o versión actualizada:\n{amendment_text}",
                ),
            ]
        )
        self.chain = self.prompt | self.llm

    def run(self, original_text: str, amendment_text: str) -> str:
        response = self.chain.invoke(
            {"original_text": original_text, "amendment_text": amendment_text}
        )
        return response.content.strip()
