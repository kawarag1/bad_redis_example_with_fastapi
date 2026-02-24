dev:
	uv run uvicorn main:app --reload --port 8000

kill:
	taskkill /f /im python.exe