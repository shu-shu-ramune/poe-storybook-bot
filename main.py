import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

def to_plain_text(q) -> str:
    if isinstance(q, str):
        return q
    if isinstance(q, list):
        parts = []
        for c in q:
            if isinstance(c, dict) and c.get("type") == "text":
                parts.append(c.get("text", ""))
            else:
                if getattr(c, "type", "") == "text":
                    parts.append(getattr(c, "text", ""))
        return "".join(parts)
    return ""

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        # デバッグ（RenderのLogsに出る）
        print(">> query.query=", query.query,
              " meta.command=",
              getattr(getattr(query, "metadata", None), "command", None),
              flush=True)

        # まず通常テキスト
        text = to_plain_text(query.query).strip()

        # 空なら /command を拾う
        if not text and getattr(query, "metadata", None):
            cmd = getattr(query.metadata, "command", "")
            if cmd:
                text = cmd

        t = (text or "").strip().lower()

        if t in ("ping", "/ping"):
            yield self.text_event("pong 🏓")
        else:
            yield self.text_event(f"📥 受け取り: {t or '(empty)'}")

app = FastAPI()
# Poe 側のURLが /poe/ ならこちらに合わせる（どちらかに統一）
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
