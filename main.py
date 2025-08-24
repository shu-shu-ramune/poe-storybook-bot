import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        # 入ってきた内容を Render のログに出す（デバッグ用）
        try:
            print(">> RAW:", query, flush=True)
            if hasattr(query, "model_dump"):
                print(">> DUMP:", query.model_dump(), flush=True)
        except Exception:
            pass

        # ★ 疎通確認のため必ず pong を返す
        yield self.text_event("pong 🏓")

app = FastAPI()
# URL は /poe/ にマウント（末尾スラッシュ必須）
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
