import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        try:
            # 最も基本的な方法で内容を取得
            if hasattr(query, 'query') and query.query:
                if isinstance(query.query, list) and len(query.query) > 0:
                    last_msg = query.query[-1]
                    if hasattr(last_msg, 'content'):
                        content = last_msg.content
                    else:
                        content = str(last_msg)
                else:
                    content = str(query.query)
            else:
                content = "no content"
                
            if "ping" in content.lower():
                yield self.text_event("pong")
            else:
                yield self.text_event(f"received: {content}")
                
        except Exception as e:
            yield self.text_event(f"Error: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
