import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

def to_plain_text(q) -> str:
    """PoeのQueryは str または Content(list) のことがあるので安全に文字列化"""
    if isinstance(q, str):
        return q
    if isinstance(q, list):
        parts = []
        for c in q:
            # dictでもオブジェクトでも text パートだけ拾う
            t = None
            if isinstance(c, dict):
                if c.get("type") == "text":
                    t = c.get("text", "")
            else:
                # fastapi_poe.types.Content の場合
                if getattr(c, "type", "") == "text":
                    t = getattr(c, "text", "")
            if t:
                parts.append(t)
        return "".join(parts)
    return ""

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        text = to_plain_text(query.query).strip().lower()

        if text in ("ping", "/ping"):
            yield self.text_event("pong 🏓")
        else:
            yield self.text_event(f"📥 受け取り: {text or '(empty)'}")
            
app = FastAPI()
app.mount("/poe", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
