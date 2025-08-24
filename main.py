from fastapi import FastAPI, Request, HTTPException
import os

app = FastAPI()
ACCESS = os.getenv("POE_ACCESS_KEY")

@app.get("/")
def health():
    return {"ok": True}

@app.post("/poe")
async def poe_handler(req: Request):
    auth = req.headers.get("authorization", "")
    if not ACCESS or auth != f"Bearer {ACCESS}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await req.json()
    text = (body.get("message", {}).get("content") or "").strip()

    if text.lower().startswith("/ping"):
        return {"text": "pong 🏓"}

    return {"text": f"🧪 受け取り: {text}"}
