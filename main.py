import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest
from fastapi_poe.types import Settings, Command

ACCESS = os.getenv("POE_ACCESS_KEY")
BOT_NAME = os.getenv("POE_BOT_NAME")  # ← 追加

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
    async def get_settings(self) -> Settings:
        # ここで /ping コマンドをPoe側に宣言して同期
        return Settings(
            # ほかはデフォルトでOK。必要に応じて調整
            commands=[Command(name="ping", display_name="ping", description="health check")]
        )

    async def get_response(self, query: QueryRequest):
        # デバッグ（Render Logs で確認できる）
        print(">> query.query=", query.query,
              " meta.command=",
              getattr(getattr(query, "metadata", None), "command", None),
              flush=True)

        text = to_plain_text(query.query).strip().lower()

        # スラッシュコマンドは metadata.command に入る
        if not text and getattr(query, "metadata", None):
            cmd = getattr(query.metadata, "command", "")
            if cmd:
                text = cmd.lower()

        if text in ("ping", "/ping"):
            yield self.text_event("pong 🏓")
            return

        yield self.text_event(f"📥 受け取り: {text or '(empty)'}")

app = FastAPI()
# bot_name を渡すと、起動時に Settings をPoeへ自動同期してくれる
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS, bot_name=BOT_NAME))

@app.get("/")
def health():
    return {"ok": True}
