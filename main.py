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
        # 本文テキストを取得
        text = to_plain_text(query.query).strip()
        # もしスラッシュコマンド扱いなら metadata.command を使う
        if not text and getattr(query, "metadata", None):
            cmd = getattr(query.metadata, "command", "")
            if cmd:
                text = cmd

        t = (text or "").strip().lower()

        if t in ("ping", "/ping"):
            yield self.text_event("pong 🏓")
            return

        yield self.text_event(f"📥 受け取り: {t or '(empty)'}")

app = FastAPI()
# 末尾スラッシュ付きでマウント（Poe 側のURLも /poe/ に合わせる）
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
