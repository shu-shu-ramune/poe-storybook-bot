import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest
import fastapi_poe as fp

ACCESS = os.getenv("POE_ACCESS_KEY")
POE_API_KEY = os.getenv("POE_API_KEY")

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        try:
            content = query.query[-1].content.strip()
            
            if "ping" in content.lower():
                yield self.text_event("pong")
                
            elif content.startswith("/ test"):
                yield self.text_event("🔄 ボット名テスト開始...")
                
                # 最も基本的なボット名から順番にテスト
                basic_bots = [
                    "Assistant",
                    "ChatGPT", 
                    "Claude-3-Haiku",
                    "Claude-3-Sonnet",
                    "GPT-3.5-Turbo",
                    "Sage"
                ]
                
                for bot_name in basic_bots:
                    try:
                        yield self.text_event(f"テスト中: {bot_name}")
                        
                        messages = [fp.ProtocolMessage(role="user", content="Hi")]
                        
                        async for partial in fp.get_bot_response(
                            messages=messages,
                            bot_name=bot_name,
                            api_key=POE_API_KEY
                        ):
                            if hasattr(partial, 'text') and partial.text:
                                yield self.text_event(f"✅ 成功! {bot_name}: {partial.text[:30]}...")
                                return
                        
                    except Exception as e:
                        error_msg = str(e)
                        yield self.text_event(f"❌ {bot_name}: {error_msg[:50]}...")
                        
                        # 特定のエラーを詳しく確認
                        if "not found" in error_msg.lower():
                            yield self.text_event(f"→ ボット {bot_name} は存在しません")
                        elif "permission" in error_msg.lower():
                            yield self.text_event(f"→ {bot_name} の権限がありません")
                        elif "quota" in error_msg.lower():
                            yield self.text_event(f"→ {bot_name} のクォータ不足")
                        
                yield self.text_event("❌ すべてのボットでエラーが発生しました")
                
            elif content.startswith("/ simple"):
                # 最もシンプルなテスト
                yield self.text_event("シンプルテスト: Assistant呼び出し...")
                
                try:
                    messages = [fp.ProtocolMessage(role="user", content="Hello")]
                    
                    async for partial in fp.get_bot_response(
                        messages=messages,
                        bot_name="Assistant",
                        api_key=POE_API_KEY
                    ):
                        yield self.text_event(f"応答: {partial}")
                        
                except Exception as e:
                    yield self.text_event(f"詳細エラー: {e}")
                    yield self.text_event(f"エラータイプ: {type(e).__name__}")
                
            else:
                yield self.text_event(f"受信: {content}\n\nコマンド:\n- `/ test` : ボット名テスト\n- `/ simple` : シンプルテスト")
                
        except Exception as e:
            yield self.text_event(f"全体エラー: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
