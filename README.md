# Telex Code Helper (Python)

A simple Telex.im AI agent written in Python + Flask. It explains Python code, formats snippets and can run very small safe Python snippets for demo.

## Run locally
1. python -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. export TELEX_API_KEY=...
5. python telex_agent.py
6. ngrok http 5000

## Webhook
Point your Mastra/Telex workflow node to `https://<ngrok>.ngrok.io/webhook`.

## Commands (as a user message)
- `explain: <python code>` — returns an explanation (uses LLM if OPENAI_API_KEY set)
- `format: <code>` — returns code in a triple-backtick block
- `run: <python code>` — runs small snippet (demo only)

## Security & production
Do not run untrusted code using this demo in production. Use proper sandboxing.
