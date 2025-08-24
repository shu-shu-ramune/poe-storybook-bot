import os
import asyncio
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest
import fastapi_poe as fp

ACCESS = os.getenv("POE_ACCESS_KEY")
POE_API_KEY = os.getenv("POE_API_KEY")

class EchoBot(PoeBot):
    async def call_other_bot(self, prompt, bot_name="Claude-3-Haiku"):
        """Poe内の他のボットを呼び出す"""
        try:
            # ProtocolMessageを作成
            messages = [
                fp.ProtocolMessage(role="user", content=prompt)
            ]
            
            # Poe内蔵のBot Query APIを使用
            response_text = ""
            async for partial in fp.get_bot_response(
                messages=messages,
                bot_name=bot_name,
                api_key=POE_API_KEY
            ):
                if hasattr(partial, 'text') and partial.text:
                    response_text += partial.text
            
            return response_text
            
        except Exception as e:
            return f"Bot呼び出しエラー: {str(e)}"

    async def get_response(self, query: QueryRequest):
        try:
            if hasattr(query, 'query') and query.query:
                if isinstance(query.query, list) and len(query.query) > 0:
                    content = query.query[-1].content
                else:
                    content = str(query.query)
            else:
                content = "no content"
                
            content = content.strip()
            
            if "ping" in content.lower():
                yield self.text_event("pong")
                
            elif content.startswith("/ test"):
                yield self.text_event("🟢 Poe Bot Query API テスト開始...")
                
                # Poe内蔵APIでClaude呼び出し
                result = await self.call_other_bot("Hello! Please respond briefly.")
                yield self.text_event(f"Claude応答: {result}")
                
            elif content.startswith("/ make"):
                theme = content.replace("/ make", "").strip()
                if not theme:
                    yield self.text_event("テーマを指定してください。例: / make 猫の冒険")
                    return
                    
                yield self.text_event(f"絵本「{theme}」を生成中...")
                
                # 絵本生成プロンプト
                story_prompt = f"""
                テーマ「{theme}」で、子供向けの短い絵本を作ってください。
                以下の形式で出力してください：

                タイトル: [絵本のタイトル]

                ページ1: [最初のページの文章]
                ページ2: [2番目のページの文章]  
                ページ3: [3番目のページの文章]
                ページ4: [最後のページの文章]

                各ページは1-2文程度の短い文章にしてください。
                """
                
                # Claude呼び出しで絵本生成
                story = await self.call_other_bot(story_prompt, "Claude-3-Haiku")
                yield self.text_event(story)
                
            else:
                yield self.text_event(f"received: {content}")
                
        except Exception as e:
            yield self.text_event(f"Error: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
