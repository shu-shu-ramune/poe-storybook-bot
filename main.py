import os
import httpx
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")
POE_API_KEY = os.getenv("POE_API_KEY")

class EchoBot(PoeBot):
    async def call_poe_api(self, prompt):
        """Poe APIを呼び出す"""
        try:
            headers = {
                "Authorization": f"Bearer {POE_API_KEY}",
                "Content-Type": "application/json"
            }
            
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
                
                return f"Status: {response.status_code}\nResponse: {response.text[:300]}..."
                
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
                
            content = content.strip()
            
            if "ping" in content.lower():
                yield self.text_event("pong")
            elif content.startswith("/ test"):
                yield self.text_event("🟢 API呼び出しテスト開始...")
                result = await self.call_poe_api("Hello!")
                yield self.text_event(result)
            elif content.startswith("/ make"):
                theme = content.replace("/ make", "").strip()
                yield self.text_event(f"絵本「{theme}」を生成中...")
                yield self.text_event("(まだ実装中...)")
            else:
                yield self.text_event(f"received: {content}")
                
        except Exception as e:
            yield self.text_event(f"Error: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
