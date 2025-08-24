import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

def to_plain_text(q) -> str:
    """query は str or Content(list)。テキストだけ連結して返す"""
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

def find_command_anywhere(obj):
    """obj 内を深く探索して 'command' を含むキー/属性の文字列を拾う"""
    seen = set()
    def _walk(x):
        if id(x) in seen:
            return None
        seen.add(id(x))
        # 文字列なら不要
        if isinstance(x, str):
            return None
        # dict: まずキー名に command を含むものを優先
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(k, str) and "command" in k.lower() and isinstance(v, str) and v:
                    return v
            for v in x.values():
                r = _walk(v)
                if r: return r
            return None
        # list/tuple
        if isinstance(x, (list, tuple)):
            for v in x:
                r = _walk(v)
                if r: return r
            return None
        # オブジェクト: __dict__ 相当を走査
        for k in dir(x):
            if k.startswith("_"):  # 内部属性はスキップ
                continue
            try:
                v = getattr(x, k)
            except Exception:
                continue
            if isinstance(k, str) and "command" in k.lower() and isinstance(v, str) and v:
                return v
            r = _walk(v)
            if r: return r
        return None
    try:
        return _walk(obj)
    except Exception:
        return None

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        # デバッグ: そのままログへ（Render Logs で確認）
        try:
            print(">> RAW query:", query, flush=True)
            if hasattr(query, "model_dump"):
                print(">> DUMP keys:", list(query.model_dump().keys()), flush=True)
        except Exception:
            pass

        text = to_plain_text(getattr(query, "query", "")).strip()

        # 本文が空なら、オブジェクト全体から command らしき文字列を探索
        if not text:
            cmd = find_command_anywhere(query)
            if isinstance(cmd, str) and cmd:
                text = cmd

        t = (text or "").strip().lower()

        if t in ("ping", "/ping"):
            yield self.text_event("pong 🏓")
            return

        yield self.text_event(f"📥 受け取り: {t or '(empty)'}")

app = FastAPI()
# リダイレクト回避のため末尾スラッシュ。Poe 側URLも /poe/ に統一
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
