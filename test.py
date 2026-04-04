import json
with open("workflows/feedback-listener-workflow.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for node in data.get("nodes", []):
    if "Basic LLM Chain" in node.get("name", "") or "Agent" in node.get("name", "") or "Gemini" in node.get("name", ""):
        print("NODE:", node.get("name"))
        params = node.get("parameters", {})
        print(json.dumps(params, indent=2))
