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
                                headers={
                                    "Authorization": f"Bearer {POE_API_KEY}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "model": "Claude-3.5-Sonnet",  # 正しいモデル名
                                    "messages": [{"role": "user", "content": f"{theme}の絵本を5ページで作成してください。各ページには短い文章と場面の説明を含めてください。"}],
                                    "max_tokens": 2000,
                                    "temperature": 0.7
                                },
                                timeout=60.0
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                story = result["choices"][0]["message"]["content"]
                                yield self.text_event(f"完成！\n\n{story}")
                            else:
                                error_text = response.text if response.text else "不明なエラー"
                                yield self.text_event(f"API エラー: {response.status_code}\n詳細: {error_text}")
                                
                    except httpx.TimeoutException:
                        yield self.text_event("タイムアウトエラー: リクエストが時間切れになりました")
                    except httpx.RequestError as e:
                        yield self.text_event(f"リクエストエラー: {str(e)}")
                    except Exception as e:
                        yield self.text_event(f"予期しないエラー: {str(e)}")
            else:
                yield self.text_event(f"received: {content}")
                
        except Exception as e:
            yield self.text_event(f"Error: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
