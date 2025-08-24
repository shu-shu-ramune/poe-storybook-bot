import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

def to_plain_text(q) -> str:
    """query.query が str / list どちらでもテキストだけ連結して返す"""
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

def stringify(obj) -> str:
    """最後の保険として安全に文字列化"""
    try:
        if isinstance(obj, str):
            return obj
        if isinstance(obj, list):
            return " ".join([stringify(x) for x in obj])
        if isinstance(obj, dict):
            return " ".join([f"{k}:{stringify(v)}" for k, v in obj.items()])
        return str(obj)
    except Exception:
        return ""

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        # デバッグ（Render Logsで確認可）
        try:
            print("==== RAW ====", query, flush=True)
            if hasattr(query, "model_dump"):
                print("==== DUMP keys ====", list(query.model_dump().keys()), flush=True)
        except Exception:
            pass

        # 1) 普通の本文
        text = to_plain_text(getattr(query, "query", "")).strip()
        # 2) /ping などコマンド経路
        if not text:
            cmd = deep_find_command(query)
            if isinstance(cmd, str) and cmd:
                text = cmd
        # 3) それでも空なら stringify で保険
        if not text:
            text = stringify(getattr(query, "query", "")).strip()

        t = (text or "").strip().lower()

        if t in ("ping", "/ping"):
            yield self.text_event("pong 🏓")
            return

        yield self.text_event(f"📥 受け取り: {t or '(empty)'}")

app = FastAPI()
# Poe 側のURLも https://<host>/poe/（末尾スラッシュ必須）に合わせる
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
