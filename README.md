# LegalMove - Comparador de Contratos

Proyecto en Python para comparar un contrato original contra una enmienda/adenda usando modelos multimodales y agentes especializados.

La idea del trabajo es automatizar una tarea típica de compliance/legal: leer dos documentos escaneados, entender qué secciones se corresponden y devolver un JSON con las cláusulas modificadas.

## Qué hace

El programa recibe dos imágenes:

1. contrato original
2. contrato actualizado o enmienda

Luego ejecuta este flujo:

```text
Imagen original + imagen enmienda
        ↓
Parsing multimodal con GPT-4o
        ↓
Agente de contextualización
        ↓
Agente de extracción de cambios
        ↓
Validación Pydantic
        ↓
JSON final + trazabilidad en Langfuse
```

La salida tiene este formato:

```json
{
  "sections_changed": ["3. Honorarios", "4. Entregables"],
  "topics_touched": ["Honorarios", "Entregables"],
  "summary_of_the_change": "Resumen de los cambios encontrados entre ambos documentos."
}
```

## Estructura del proyecto

```text
legalmove_contract_agent/
├─ src/
│  ├─ main.py
│  ├─ image_parser.py
│  ├─ models.py
│  ├─ observability.py
│  └─ agents/
│     ├─ contextualization_agent.py
│     └─ extraction_agent.py
├─ data/test_contracts/
│  ├─ caso_1_software/
│  ├─ caso_2_consultoria/
│  ├─ caso_3_saas/
│  ├─ expected_changes.json
│  └─ README.md
├─ sample_outputs/
├─ tests/
├─ docs/
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ Makefile
└─ README.md
```

## Requisitos

Recomiendo usar Python 3.11 o 3.12. Con Python 3.14 algunas dependencias pueden intentar compilarse localmente y fallar en Windows.

## Instalación

En Windows PowerShell:

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

En Linux/Mac:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Después completar el archivo `.env`:

```env
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

El archivo `.env` no se sube al repositorio. Queda ignorado en `.gitignore`.

## Uso

Ejemplo con el caso de consultoría:

```powershell
python -m src.main data/test_contracts/caso_2_consultoria/documento_2__original.jpg data/test_contracts/caso_2_consultoria/documento_2__enmienda.jpg --output sample_outputs/run_consultoria.json
```

Ejemplo con el caso SaaS:

```powershell
python -m src.main data/test_contracts/caso_3_saas/documento_3__original.jpg data/test_contracts/caso_3_saas/documento_3__enmienda.jpg --output sample_outputs/run_saas.json
```

Ejemplo con el caso de licencia de software:

```powershell
python -m src.main data/test_contracts/caso_1_software/documento_1__original.jpg data/test_contracts/caso_1_software/documento_1__enmienda.jpg --output sample_outputs/run_software.json
```

## Componentes principales

### `src/image_parser.py`

Valida la imagen, la convierte a base64 y llama al modelo multimodal para extraer el texto del documento manteniendo estructura, secciones, montos, fechas y porcentajes.

### `src/agents/contextualization_agent.py`

Este agente arma el contexto comparado. Identifica las secciones del contrato original y de la enmienda, y genera un mapa para que el siguiente agente pueda comparar con más precisión.

### `src/agents/extraction_agent.py`

Este agente toma el contexto y los textos parseados. Su tarea es detectar modificaciones, adiciones y eliminaciones. La respuesta se fuerza al modelo `ContractChangeOutput`.

### `src/models.py`

Define el contrato de salida con Pydantic:

```python
sections_changed: List[str]
topics_touched: List[str]
summary_of_the_change: str
```

### `src/observability.py`

Centraliza la integración con Langfuse. Si las credenciales están configuradas, crea una traza raíz llamada `contract-analysis` y spans para cada etapa:

```text
contract-analysis
├─ parse_original_contract
├─ parse_amendment_contract
├─ contextualization_agent
└─ extraction_agent
```

Si las variables de Langfuse no están cargadas, el flujo sigue funcionando en modo local para no bloquear la ejecución.

## Casos de prueba

Incluí tres pares de documentos para probar el pipeline:

| Caso | Tipo de contrato | Cambios principales |
|---|---|---|
| 1 | Licencia de software | plazo, pago, soporte, terminación y protección de datos |
| 2 | Consultoría | alcance, duración, honorarios, entregables y propiedad intelectual |
| 3 | SaaS | precio, disponibilidad y soporte |

Los cambios esperados están en:

```text
data/test_contracts/expected_changes.json
```

## Tests

```powershell
pytest -q
```

Los tests verifican principalmente:

- schema de Pydantic
- validaciones básicas de imagen
- contrato mínimo de salida del pipeline

No hacen llamadas reales a OpenAI ni Langfuse.

## Decisiones de diseño

- Separé el flujo en dos agentes para no mezclar contexto con extracción. Primero se entiende el documento y después se extraen los cambios.
- Usé GPT-4o Vision porque la entrada son imágenes, no texto plano.
- Validé la salida con Pydantic para que el resultado pueda ser consumido por otro sistema sin depender de texto libre.
- Agregué Langfuse para poder revisar cada etapa del pipeline durante la defensa.
- Dejé fallback no-op en observabilidad para poder ejecutar el proyecto aunque Langfuse no esté configurado.

## Comandos útiles

```powershell
# instalar dependencias
pip install -r requirements.txt

# correr tests
pytest -q

# ejecutar caso de consultoría
python -m src.main data/test_contracts/caso_2_consultoria/documento_2__original.jpg data/test_contracts/caso_2_consultoria/documento_2__enmienda.jpg --output sample_outputs/run_consultoria.json
```
