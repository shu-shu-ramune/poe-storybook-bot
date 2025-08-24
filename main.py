import os
import fastapi_poe as fp
from fastapi import FastAPI

ACCESS = os.getenv("POE_ACCESS_KEY")

class PictureStorybook(fp.PoeBot):
    async def get_response(self, query: fp.QueryRequest):
        try:
            content = query.query[-1].content if query.query else ""
            
            if "test" in content.lower():
                # 基本的な応答テスト
                yield fp.PartialResponse(text="✅ ボットは正常に動作しています")
                yield fp.PartialResponse(text=f"\n📝 受信メッセージ: {content}")
                yield fp.PartialResponse(text=f"\n🆔 ユーザーID: {query.user_id}")
                
            elif "simple" in content.lower():
                # シンプルなfp.stream_requestテスト
                yield fp.PartialResponse(text="🤖 Claude-3-Haikuを呼び出し中...\n")
                
                try:
                    async for partial in fp.stream_request(query, "Claude-3-Haiku"):
                        yield partial
                except Exception as e:
                    yield fp.PartialResponse(text=f"❌ エラー: {str(e)}")
                    
            else:
                yield fp.PartialResponse(text="""
                🔧 デバッグモード
                
                • 「test」 - 基本動作確認
                • 「simple」 - シンプルなボット呼び出しテスト
                """)
                
        except Exception as e:
            yield fp.PartialResponse(text=f"❌ 予期しないエラー: {str(e)}")

app = FastAPI()
app.mount("/", fp.make_app(PictureStorybook(), access_key=ACCESS))
