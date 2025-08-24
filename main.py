import os
from typing import AsyncIterable
import fastapi_poe as fp
from fastapi import FastAPI
from fastapi_poe import make_app

ACCESS = os.getenv("POE_ACCESS_KEY")

class PictureStorybookBot(fp.PoeBot):
    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        # 正しい依存関係の宣言
        return fp.SettingsResponse(
            server_bot_dependencies={
                "GPT-4o": 2,  # ツール呼び出しで往復するため2回
                "Claude-3-Opus": 2,
                "Claude-3-Sonnet": 2,
                "GPT-3.5-Turbo": 1
            }
        )

    async def get_response(self, request: fp.QueryRequest) -> AsyncIterable[fp.PartialResponse]:
        content = request.query[-1].content.strip()
        
        if content.startswith("/ test"):
            yield fp.PartialResponse(text="🔄 設定同期後テスト...\n\n")
            
            try:
                # GPT-4oで試す
                async for msg in fp.stream_request(request, "GPT-4o", request.access_key):
                    yield fp.PartialResponse(text=f"✅ **GPT-4o成功**: {msg.text[:100]}...\n")
                    break
            except Exception as e:
                yield fp.PartialResponse(text=f"❌ GPT-4o: {str(e)}\n")
        else:
            yield fp.PartialResponse(text="/ test で設定同期後テストを実行")

app = FastAPI()

# 重要：bot_nameとaccess_keyを指定して自動同期
app.mount("/poe/", make_app(
    PictureStorybookBot(), 
    access_key=ACCESS,
    bot_name="PictureStorybook"  # あなたのボット名
))

@app.get("/")
def health():
    return {"ok": True}
