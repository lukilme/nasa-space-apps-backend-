from fastapi import FastAPI
import httpx
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware 
from typing import Optional
import os
import asyncio
import json

app = FastAPI()

origins = [
    "http://127.0.0.1:8000", 
    "http://localhost:8000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"],    
)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama_core:11434")

async def llm_token_generator(prompt: str):
    tokens = ["Olá", ", ", "isso ", "é ", "um ", "teste", "."]
    print(prompt)
    for t in tokens:
        await asyncio.sleep(0.15)  
        print(t)
        yield f"data: {json.dumps({'type':'token','text':t})}\n\n"
    yield f"data: {json.dumps({'type':'done'})}\n\n"

@app.get("/v1/ask")
async def ask(prompt: str):
    return StreamingResponse(llm_token_generator(prompt),
                             media_type="text/event-stream")

@app.post("/ask")
async def ask(request: Request, question: Optional[str] = Query(None)):
    print(question)
    if not question:
        try:
            body = await request.json()
            question = body.get("question")
        except:
            query_params = request.query_params
            question = query_params.get("question")
    
    if not question:
        raise HTTPException(status_code=400, detail="'question' parameter is required")

    async def event_stream():
        try:
            async with httpx.AsyncClient(timeout=60.0) as client: 
                async with client.stream(
                    "POST",
                    f"{OLLAMA_HOST}/api/generate",
                    json={"model": "llama3", "prompt": "in portuguese "+question, "stream": True}
                ) as resp:
                    print(f"Response status: {resp.status_code}")
                    
                    if resp.status_code != 200:
                        error_msg = f"Ollama API returned status {resp.status_code}"
                        yield f"data: {json.dumps({'type': 'token', 'text': error_msg})}\n\n"
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                        return
                    
                    async for line in resp.aiter_lines():
                        if line.strip():
                            print(f"Received line: {line}")
                            try:
                                ollama_data = json.loads(line)
                                print(f"Ollama response: {ollama_data}")
                                
                                if "response" in ollama_data and ollama_data["response"]:
                                    yield f"data: {json.dumps({'type': 'token', 'text': ollama_data['response']})}\n\n"
                                
                                if ollama_data.get("done", False):
                                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                                    break
                                    
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON: {e}, line: {line}")
                                yield f"data: {json.dumps({'type': 'token', 'text': f'Parsing error: {line}'})}\n\n"
                        
        except httpx.TimeoutException:
            error_msg = "Timeout connecting to Ollama"
            print(f"Error: {error_msg}")
            yield f"data: {json.dumps({'type': 'token', 'text': error_msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except httpx.ConnectError:
            error_msg = "Could not connect to Ollama. Please check if it's running."
            print(f"Error: {error_msg}")
            yield f"data: {json.dumps({'type': 'token', 'text': error_msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            error_msg = f"Streaming error: {str(e)}"
            print(f"Error: {error_msg}")
            yield f"data: {json.dumps({'type': 'token', 'text': error_msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream", 
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_HOST}/api/version")
            if response.status_code == 200:
                return {"status": "ok", "ollama": "connected"}
            else:
                return {"status": "error", "ollama": "not responding"}
    except Exception as e:
        return {"status": "error", "ollama": f"connection failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)