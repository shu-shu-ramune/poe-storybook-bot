import os
import json
import httpx
import asyncio
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")
POE_API_KEY = os.getenv("POE_API_KEY")

class EchoBot(PoeBot):
    async def simple_poe_call(self, prompt):
        """最もシンプルなPoe API呼び出し"""
        try:
            headers = {
                "Authorization": f"Bearer {POE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # 最もシンプルなペイロード
            payload = {
                "query": prompt,
                "bot": "Claude-3-Haiku"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.poe.com/bot/chat",
                    headers=headers,
                    json=payload
                )
                
                return f"Status: {response.status_code}, Response: {response.text[:200]}..."
                
        except Exception as e:
            return f"Error: {str(e)}"

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
                
            elif content.startswith("/test"):
                yield self.text_event("API テスト開始...")
                
                # デバッグ情報
                api_key_status = "設定済み" if POE_API_KEY else "未設定"
                yield self.text_event(f"API Key: {api_key_status}")
                
                if POE_API_KEY:
                    # 実際のAPI呼び出しテスト
                    result = await self.simple_poe_call("Hello, how are you?")
                    yield self.text_event(f"API結果: {result}")
                
            elif content.startswith("/make"):
                theme = content.replace("/make", "").strip()
                yield self.text_event(f"絵本「{theme}」を生成中...")
                yield self.text_event("(API実装テスト中...)")
                
            else:
                yield self.text_event(f"received: {content}")
                
        except Exception as e:
            yield self.text_event(f"Error: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
