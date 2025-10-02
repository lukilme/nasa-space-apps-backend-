import httpx
import json
import sys

url = "http://localhost:8082/ask"
payload = {"question": "Qual a cor do pikachu?"}
headers = {"Accept": "text/event-stream", "Content-Type": "application/json"}

with httpx.stream("POST", url, json=payload, headers=headers, timeout=None) as resp:
    if resp.status_code != 200:
        print("Erro HTTP:", resp.status_code, resp.text)
        raise SystemExit(1)

    buffer = []  
    for raw in resp.iter_lines():
        if not raw:
            continue

        line = raw.decode() if isinstance(raw, bytes) else raw

        if line.startswith("data:"):
            payload_str = line[len("data:"):].strip()
        else:
            payload_str = line.strip()

        try:
            obj = json.loads(payload_str)
        except json.JSONDecodeError:
            print(payload_str, end="", flush=True)
            continue

        t = obj.get("type")
        if t == "token":
            text = obj.get("text", "")

            print(text, end="", flush=True)
            buffer.append(text)
        elif t == "done" or obj.get("done") is True:
            print() 
            break
        else:
 
            print(f"\n[evento:{t}] {obj}\n", flush=True)
