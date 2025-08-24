import os
from typing import AsyncIterable
import fastapi_poe as fp
from fastapi import FastAPI
from fastapi_poe import make_app

ACCESS = os.getenv("POE_ACCESS_KEY")

class PictureStorybookBot(fp.PoeBot):
    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(server_bot_dependencies={"Claude-3-Opus": 1})

    async def get_response(self, request: fp.QueryRequest) -> AsyncIterable[fp.PartialResponse]:
        content = request.query[-1].content.strip()
        
        if content.startswith("/ test"):
            # 複数のボット名をテスト
            bot_names = [
                "Claude-3-Opus",
                "Claude-3-Sonnet", 
                "Claude-3-Haiku",
                "GPT-4",
                "GPT-3.5-Turbo",
                "Gemini-Pro"
            ]
            
            yield fp.PartialResponse(text="🔄 利用可能ボット検索中...\n\n")
            
            for bot_name in bot_names:
                try:
                    async for msg in fp.stream_request(request, bot_name, request.access_key):
                        yield fp.PartialResponse(text=f"✅ **{bot_name}**: 成功！\n")
                        yield fp.PartialResponse(text=f"応答: {msg.text[:100]}...\n\n")
                        break
                except Exception as e:
                    yield fp.PartialResponse(text=f"❌ **{bot_name}**: {str(e)}\n\n")
        else:
            yield fp.PartialResponse(text="/ test で利用可能ボットを検索します")

app = FastAPI()
app.mount("/poe/", make_app(PictureStorybookBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
