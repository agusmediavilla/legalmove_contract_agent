import pytest
from pydantic import ValidationError

from src.models import ContractChangeOutput


def test_contract_change_output_validates_required_schema():
    payload = {
        "sections_changed": ["3. Precio"],
        "topics_touched": ["precio"],
        "summary_of_the_change": "Aumenta el precio mensual.",
    }
    obj = ContractChangeOutput.model_validate(payload)
    assert obj.sections_changed == ["3. Precio"]


def test_contract_change_output_rejects_extra_fields():
    with pytest.raises(ValidationError):
        ContractChangeOutput.model_validate(
            {
                "sections_changed": [],
                "topics_touched": [],
                "summary_of_the_change": "Sin cambios.",
                "unexpected": True,
            }
        )
