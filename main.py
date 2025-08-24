import os
import fastapi_poe as fp
from fastapi import FastAPI

ACCESS = os.getenv("POE_ACCESS_KEY")

class PictureStorybook(fp.PoeBot):
    async def get_response(self, query: fp.QueryRequest):
        # 最もシンプルな応答
        yield fp.PartialResponse(text="Hello! ボットが動いています。")

# アプリの作成
app = fp.make_app(PictureStorybook(), access_key=ACCESS)
