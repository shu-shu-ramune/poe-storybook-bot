import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

def to_plain_text(q) -> str:
    """Poeのqueryは str または Content(list) のことがある。安全に文字列化。"""
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
        # テキストをまず通常の query から取得
        text = to_plain_text(query.query).strip().lower()

        # もし空なら metadata.command を見る
        if not text and getattr(query, "metadata", None):
            cmd = getattr(query.metadata, "command", "")
            if cmd:
                text = cmd.lower()

        if text in ("ping", "/ping"):
            yield self.text_event("pong 🏓")
        else:
            yield self.text_event(f"📥 受け取り: {text or '(empty)'}")

app = FastAPI()
# 末尾スラッシュ付きでマウント（Poe 側のURLも /poe/ に合わせる）
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
