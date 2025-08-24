import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

def to_plain_text(q) -> str:
    """query.query が str / list のどちらでもテキストだけ連結して返す"""
    if isinstance(q, str):
        return q
    if isinstance(q, list):
        parts = []
        for c in q:
            # dict（webhook生）/ Contentオブジェクト の両対応
            if isinstance(c, dict) and c.get("type") == "text":
                parts.append(c.get("text", ""))
            elif hasattr(c, "type") and getattr(c, "type", "") == "text":
                parts.append(getattr(c, "text", ""))
        return "".join(parts)
    return ""

def deep_find_command(obj):
    """オブジェクト全体を探索して 'command' っぽい文字列を拾う（/ping対策）"""
    seen = set()
    def walk(x):
        if id(x) in seen:
            return None
        seen.add(id(x))
        if isinstance(x, str):
            return None
        if isinstance(x, dict):
            # key に command を含む項目を優先
            for k, v in x.items():
                if isinstance(k, str) and "command" in k.lower() and isinstance(v, str) and v:
                    return v
            for v in x.values():
                r = walk(v)
                if r: return r
            return None
        if isinstance(x, (list, tuple)):
            for v in x:
                r = walk(v)
                if r: return r
            return None
        # オブジェクト属性を走査
        for k in dir(x):
            if k.startswith("_"):
                continue
            try:
                v = getattr(x, k)
            except Exception:
                continue
            if isinstance(k, str) and "command" in k.lower() and isinstance(v, str) and v:
                return v
            r = walk(v)
            if r: return r
        return None
    try:
        return walk(obj)
    except Exception:
        return None

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        # 必要ならログ確認（Render Logs で見える）
        try:
            print(">> RAW:", query, flush=True)
            if hasattr(query, "model_dump"):
                print(">> DUMP keys:", list(query.model_dump().keys()), flush=True)
        except Exception:
            pass

        # まず本文を取り出す
        text = to_plain_text(getattr(query, "query", "")).strip()

        # 本文が空なら、オブジェクト全体から command を探索（/ping対策）
        if not text:
            cmd = deep_find_command(query)
            if isinstance(cmd, str) and cmd:
                text = cmd

        t = (text or "").strip().lower()

        if t in ("ping", "/ping"):
            yield self.text_event("pong 🏓")
            return

        yield self.text_event(f"📥 受け取り: {t or '(empty)'}")

app = FastAPI()
# URL は /poe/ にマウント（Poe 側のサーバーURLも末尾 /poe/ に合わせる）
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
