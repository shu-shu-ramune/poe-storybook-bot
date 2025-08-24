import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

def stringify(obj) -> str:
    """オブジェクト全体を安全に文字列化"""
    try:
        if isinstance(obj, str):
            return obj
        if isinstance(obj, list):
            return " ".join([stringify(x) for x in obj])
        if isinstance(obj, dict):
            return " ".join([f"{k}:{stringify(v)}" for k, v in obj.items()])
        return str(obj)
    except Exception as e:
        return f"<error {e}>"

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        # まずログ出力して何が来てるか可視化
        try:
            print("==== RAW QUERY ====", flush=True)
            print(query, flush=True)
            if hasattr(query, "model_dump"):
                print("==== MODEL_DUMP ====", flush=True)
                print(query.model_dump(), flush=True)
        except Exception as e:
            print("Log error:", e, flush=True)

        # 文字列化してテキストにまとめる
        text = stringify(getattr(query, "query", "")).strip().lower()

        if "ping" in text:
            yield self.text_event("pong 🏓")
        else:
            yield self.text_event(f"📥 受け取り: {text or '(empty)'}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
