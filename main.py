import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        # シンプルに query の内容をすべて文字列として扱う
        raw_text = str(query.query).lower()
        
        if "ping" in raw_text:
            yield self.text_event("pong 🏓")
        else:
            yield self.text_event(f"受信: {raw_text}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
