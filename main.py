import os
from typing import AsyncIterable
import fastapi_poe as fp
from fastapi import FastAPI
from fastapi_poe import make_app

ACCESS = os.getenv("POE_ACCESS_KEY")

class PictureStorybookBot(fp.PoeBot):
    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(
            server_bot_dependencies={
                "GPT-4o": 2,
                "Claude-3-Opus": 2
            }
        )

    async def get_response(self, request: fp.QueryRequest) -> AsyncIterable[fp.PartialResponse]:
        content = request.query[-1].content.strip()
        
        if content.startswith("/ sync"):
            try:
                # 手動同期を実行
                yield fp.PartialResponse(text="🔄 手動同期実行中...\n")
                await fp.sync_bot_settings("PictureStorybook", ACCESS)  # ←正確なボット名に変更
                yield fp.PartialResponse(text="✅ 同期完了\n")
            except Exception as e:
                yield fp.PartialResponse(text=f"❌ 同期エラー: {str(e)}\n")
                
        elif content.startswith("/ test"):
            try:
                async for msg in fp.stream_request(request, "GPT-4o", request.access_key):
                    yield fp.PartialResponse(text=f"✅ 成功: {msg.text[:100]}...\n")
                    break
            except Exception as e:
                yield fp.PartialResponse(text=f"❌ エラー: {str(e)}\n")
        else:
            yield fp.PartialResponse(text="/ sync で手動同期、/ test でテスト")

app = FastAPI()
app.mount("/poe/", make_app(PictureStorybookBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
