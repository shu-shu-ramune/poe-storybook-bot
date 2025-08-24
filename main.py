import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        raw_text = str(query.query).lower()
        
        # 厳密に ping だけを判定
        if raw_text == "ping" or "ping" in raw_text and len(raw_text.strip()) <= 10:
            yield self.text_event("pong 🏓")
        else:
            yield self.text_event(f"受信: {raw_text}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
