import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest
import fastapi_poe as fp

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
                
            content = content.strip()
            
            if "ping" in content.lower():
                yield self.text_event("pong")
                
            elif content.startswith("/ test"):
                yield self.text_event("🟢 基本テスト開始...")
                
                # 環境変数確認
                access_status = "設定済み" if ACCESS else "未設定"
                api_status = "設定済み" if POE_API_KEY else "未設定"
                
                yield self.text_event(f"ACCESS_KEY: {access_status}")
                yield self.text_event(f"POE_API_KEY: {api_status}")
                
                if POE_API_KEY:
                    yield self.text_event(f"API Key長さ: {len(POE_API_KEY)}")
                    yield self.text_event(f"API Key先頭: {POE_API_KEY[:8]}...")
                
                # 簡単なBot Query APIテスト
                try:
                    yield self.text_event("🔄 Claude呼び出し開始...")
                    
                    messages = [fp.ProtocolMessage(role="user", content="Hi")]
                    
                    response_count = 0
                    async for partial in fp.get_bot_response(
                        messages=messages,
                        bot_name="Claude-3.5-Sonnet",
                        api_key=POE_API_KEY
                    ):
                        response_count += 1
                        if hasattr(partial, 'text') and partial.text:
                            yield self.text_event(f"応答{response_count}: {partial.text[:50]}...")
                            break
                    
                    if response_count == 0:
                        yield self.text_event("❌ 応答なし")
                        
                except Exception as e:
                    yield self.text_event(f"❌ Bot Query API エラー: {str(e)}")
                
            elif content.startswith("/ make"):
                yield self.text_event("🚧 まだ実装中です")
                
            else:
                yield self.text_event(f"受信: {content}")
                
        except Exception as e:
            yield self.text_event(f"全体エラー: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
