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
            elif "make" in content.lower() and ("海" in content or "冒険" in content or len(content.split()) >= 2):
                theme = content.replace("/make", "").replace("make", "").strip()
                yield self.text_event(f"絵本「{theme}」を生成中...")
                
                # 実際の生成処理
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "https://api.poe.com/v1/chat/completions",
                            headers={"Authorization": f"Bearer {POE_API_KEY}"},
                            json={
                                "model": "gemini-1.5-pro",
                                "messages": [{"role": "user", "content": f"{theme}というテーマで5ページの絵本を作って"}],
                                "max_tokens": 1000
                            }
                        )
                        result = response.json()
                        story = result["choices"][0]["message"]["content"]
                        yield self.text_event(f"完成！\n\n{story}")
                except Exception as e:
                    yield self.text_event(f"生成エラー: {str(e)}")
            else:
                yield self.text_event(f"received: {content}")
                
        except Exception as e:
            yield self.text_event(f"Error: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
