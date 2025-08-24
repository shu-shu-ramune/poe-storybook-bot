import os
import json
import httpx
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
                
            if "ping" in content.lower():
                yield self.text_event("pong")



            elif "make" in content.lower():
    theme = content.replace("/make", "").replace("make", "").strip()
    yield self.text_event(f"絵本「{theme}」を生成中...")
    
    if not POE_API_KEY:
        yield self.text_event("エラー: POE_API_KEYが設定されていません")
    else:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.poe.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {POE_API_KEY}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": f"{theme}の絵本を5ページで作成してください"}]
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    story = result["choices"][0]["message"]["content"]
                    yield self.text_event(f"完成！\n\n{story}")
                else:
                    yield self.text_event(f"API エラー: {response.status_code}")
                    
        except Exception as e:
            yield self.text_event(f"エラー: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
