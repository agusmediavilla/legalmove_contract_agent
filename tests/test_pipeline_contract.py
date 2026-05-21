from src.models import ContractChangeOutput


def test_expected_saas_payload_has_required_changes():
    payload = ContractChangeOutput.model_validate(
        {
            "sections_changed": ["3. Precio", "4. Disponibilidad del Servicio", "5. Soporte"],
            "topics_touched": ["precio", "nivel de servicio/SLA", "soporte"],
            "summary_of_the_change": "Precio 1200 a 1250, disponibilidad 99,5 a 99,9 y soporte con tickets.",
        }
    )
    assert "3. Precio" in payload.sections_changed
    assert any("soporte" in t for t in payload.topics_touched)
