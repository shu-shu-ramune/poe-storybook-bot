import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

def _extract_text_unit(x) -> str:
    """Message/Content/dict/str から1ユニットのテキストを抽出"""
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        # dictのときは content / text 優先で拾う
        if "content" in x and isinstance(x["content"], str):
            return x["content"]
        if x.get("type") == "text" and isinstance(x.get("text"), str):
            return x["text"]
        if "text" in x and isinstance(x["text"], str):
            return x["text"]
        return ""
    # オブジェクト: .content / .text を順に見る
    for attr in ("content", "text"):
        if hasattr(x, attr):
            v = getattr(x, attr)
            if isinstance(v, str):
                return v
    return ""

def to_plain_text(q) -> str:
    """query.query が str / list / dict / Message のどれでも安全に連結"""
    if isinstance(q, str):
        return q
    if isinstance(q, list):
        return "".join(_extract_text_unit(u) for u in q)
    if isinstance(q, dict):
        return _extract_text_unit(q)
    # Messageオブジェクト1個で来るケース
    return _extract_text_unit(q)

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        # 必要最小限のログだけ（型確認用）
        try:
            q = getattr(query, "query", None)
            print(">> type(query.query)=", type(q), " len=", (len(q) if isinstance(q, list) else "n/a"), flush=True)
        except Exception:
            pass

        text = to_plain_text(getattr(query, "query", "")).strip()
        t = (text or "").lower()

        if t in ("ping", "/ping"):
            yield self.text_event("pong 🏓")
            return

        yield self.text_event(f"📥 受け取り: {text or '(empty)'}")

app = FastAPI()
# Poe 側のサーバーURLも必ず末尾スラッシュ /poe/ に合わせてください
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
