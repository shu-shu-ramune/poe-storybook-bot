import os
import fastapi_poe as fp
from fastapi import FastAPI

ACCESS = os.getenv("POE_ACCESS_KEY")

class EchoBot(fp.PoeBot):
    async def get_response(self, query: fp.QueryRequest):
        try:
            if hasattr(query, 'query') and query.query:
                content = query.query[-1].content
            else:
                content = "no content"
                
            if "ping" in content.lower():
                yield fp.PartialResponse(text="pong")
            elif "make" in content.lower():
                theme = content.replace("/make", "").replace("make", "").strip()
                yield fp.PartialResponse(text=f"絵本「{theme}」を生成中...")
                
                try:
                    # Poeの他のボットを呼び出す（正しい方法）
                    messages = [
                        fp.ProtocolMessage(
                            role="user", 
                            content=f"{theme}の絵本を5ページで作成してください。各ページには短い文章と場面の説明を含めてください。"
                        )
                    ]
                    
                    # Claude-3.5-Sonnetを呼び出し
                    async for partial in fp.stream_request(query, "Claude-3.5-Sonnet"):
                        yield partial
                        
                except Exception as e:
                    yield fp.PartialResponse(text=f"エラー: {str(e)}")
            else:
                yield fp.PartialResponse(text=f"received: {content}")
                
        except Exception as e:
            yield fp.PartialResponse(text=f"Error: {str(e)}")

app = FastAPI()
app.mount("/poe/", fp.make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
