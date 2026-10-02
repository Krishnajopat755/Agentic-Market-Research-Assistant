.PHONY: demo-aapl test test-e2e lint typecheck format run-api

demo-aapl:
	.venv\Scripts\python.exe -m apps.orchestrator.cli demo-aapl

test:
	.venv\Scripts\pytest.exe -v tests/

test-e2e:
	.venv\Scripts\pytest.exe -v tests/e2e/

lint:
	.venv\Scripts\ruff.exe check src/ apps/ services/ tests/

format:
	.venv\Scripts\ruff.exe format src/ apps/ services/ tests/

typecheck:
	.venv\Scripts\mypy.exe src/ contracts/

run-api:
	.venv\Scripts\uvicorn.exe apps.api.main:app --host 0.0.0.0 --port 8000 --reload
