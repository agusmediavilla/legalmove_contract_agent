.PHONY: install test run-saas

install:
	python -m pip install -r requirements.txt

test:
	pytest -q

run-saas:
	python -m src.main data/test_contracts/caso_3_saas/documento_3__original.jpg data/test_contracts/caso_3_saas/documento_3__enmienda.jpg --output sample_outputs/run_saas.json
