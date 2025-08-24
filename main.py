import os
from typing import AsyncIterable
import fastapi_poe as fp
from fastapi import FastAPI
from fastapi_poe import make_app

ACCESS = os.getenv("POE_ACCESS_KEY")

class PictureStorybookBot(fp.PoeBot):
    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(server_bot_dependencies={"Claude-3.5-Sonnet": 1})

    async def get_response(self, request: fp.QueryRequest) -> AsyncIterable[fp.PartialResponse]:
        try:
            content = request.query[-1].content.strip()
            
            if content.startswith("/ test"):
                yield fp.PartialResponse(text="🔄 デバッグ情報:\n")
                yield fp.PartialResponse(text=f"• Access key exists: {bool(request.access_key)}\n")
                yield fp.PartialResponse(text=f"• Access key length: {len(request.access_key) if request.access_key else 0}\n")
                yield fp.PartialResponse(text=f"• User ID: {request.user_id}\n")
                yield fp.PartialResponse(text="• Claude呼び出し開始...\n")
                
                try:
                    async for msg in fp.stream_request(
                        request, "Claude-3.5-Sonnet", request.access_key
                    ):
                        yield fp.PartialResponse(text=f"✅ 成功: {msg.text[:50]}...\n")
                        break
                        
                except Exception as e:
                    yield fp.PartialResponse(text=f"❌ Claude-3.5エラー: {type(e).__name__}: {str(e)}\n")
                    
                    # 別のボット名で試す
                    try:
                        yield fp.PartialResponse(text="• GPT-3.5-Turboで再試行...\n")
                        async for msg in fp.stream_request(
                            request, "GPT-3.5-Turbo", request.access_key
                        ):
                            yield fp.PartialResponse(text=f"✅ GPT成功: {msg.text[:50]}...\n")
                            break
                    except Exception as e2:
                        yield fp.PartialResponse(text=f"❌ GPT-3.5エラー: {type(e2).__name__}: {str(e2)}\n")
                    
            else:
                yield fp.PartialResponse(text="/ test でデバッグ実行してください")
                
        except Exception as e:
            yield fp.PartialResponse(text=f"外部エラー: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(PictureStorybookBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
