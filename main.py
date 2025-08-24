import os
import json
import httpx
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")
POE_API_KEY = os.getenv("POE_API_KEY")

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        try:
            if hasattr(query, 'query') and query.query:
                if isinstance(query.query, list) and len(query.query) > 0:
                    content = query.query[-1].content
                else:
                    content = str(query.query)
            else:
                content = "no content"
                
            if "ping" in content.lower():
                yield self.text_event("pong")
            elif "make" in content.lower():
                theme = content.replace("/make", "").replace("make", "").strip()
                yield self.text_event(f"絵本「{theme}」を生成中...")
                
                if not POE_API_KEY:
                    yield self.text_event("エラー: POE_API_KEYが設定されていません")
                else:
                    yield self.text_event("テスト: API呼び出しをスキップしました")
            else:
                yield self.text_event(f"received: {content}")
                
        except Exception as e:
            yield self.text_event(f"Error: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
