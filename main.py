import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        text = (query.query or "").strip()
        if text.lower().startswith("/ping") or text.lower() == "ping":
            yield self.text_event("pong 🏓")
        else:
            yield self.text_event(f"🧪 受け取り: {text}")

# FastAPI アプリ
app = FastAPI()

# Poe用のサブアプリを /poe にマウント
poe_app = make_app(EchoBot(), access_key=ACCESS)
app.mount("/poe", poe_app)

@app.get("/")
def health():
    return {"ok": True}
