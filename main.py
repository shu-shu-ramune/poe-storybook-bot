import os
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
                
            # スペースを除去
            content = content.strip()
            
            # デバッグ出力
            yield self.text_event(f"Debug: '{content}' (length: {len(content)})")
            
            if "ping" in content.lower():
                yield self.text_event("pong")
            elif content.startswith("/test"):
                yield self.text_event("🟢 /test コマンド認識成功！")
                api_status = "設定済み" if POE_API_KEY else "未設定"
                yield self.text_event(f"API Key: {api_status}")
            elif content.startswith("/make"):
                yield self.text_event("🟢 /make コマンド認識成功！")
            else:
                yield self.text_event(f"received: {content}")
                
        except Exception as e:
            yield self.text_event(f"Error: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
