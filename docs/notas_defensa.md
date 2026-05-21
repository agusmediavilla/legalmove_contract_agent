# Notas para defensa

## Problema

LegalMove necesita comparar contratos originales contra enmiendas. La comparación manual consume tiempo y puede tener errores, especialmente cuando hay muchos documentos.

## Solución

El pipeline recibe dos imágenes, extrae texto con GPT-4o Vision, usa dos agentes y devuelve un JSON validado.

## Por qué dos agentes

Separé el proceso en dos pasos:

1. contextualización: entender secciones y correspondencias;
2. extracción: detectar cambios puntuales.

Esto hace más fácil explicar el razonamiento y revisar la traza en Langfuse.

## Qué mostrar en vivo

1. Ejecutar caso consultoría.
2. Abrir el JSON generado.
3. Ejecutar otro caso, por ejemplo SaaS.
4. Abrir Langfuse y mostrar `contract-analysis`.
5. Mostrar los spans de parsing, contextualización y extracción.

## Comando principal

```powershell
python -m src.main data/test_contracts/caso_2_consultoria/documento_2__original.jpg data/test_contracts/caso_2_consultoria/documento_2__enmienda.jpg --output sample_outputs/run_consultoria.json
```

## Puntos técnicos

- GPT-4o Vision: porque el input son imágenes.
- LangChain: para separar los agentes y sus prompts.
- Pydantic: para validar la estructura final.
- Langfuse: para revisar trazas, inputs, outputs y tiempos.
