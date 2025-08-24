import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

class EchoBot(PoeBot):
    async def get_response(self, query: QueryRequest):
        # query.query を文字列化して content= の部分を抽出
        raw_text = str(query.query)
        
        # content='...' の部分を抽出
        import re
        content_matches = re.findall(r"content='([^']*)'", raw_text)
        
        if content_matches:
            # 最後のユーザーメッセージの content を使用
            user_content = content_matches[-1].lower().strip()
        else:
            user_content = ""
        
        if user_content in ("ping", "/ping"):
            yield self.text_event("pong 🏓")
        else:
            yield self.text_event(f"受信: {user_content or raw_text[:100]}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
