import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        # 生の中身をログへ（Render Logsで必ず見える）
        try:
            print(">> RAW:", query, flush=True)
            if hasattr(query, "model_dump"):
                print(">> DUMP:", query.model_dump(), flush=True)
        except Exception:
            pass

        # ★ まずは必ず返す（疎通が最優先）
        yield self.text_event("pong 🏓")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
