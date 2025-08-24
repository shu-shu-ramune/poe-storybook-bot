import os
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest
import fastapi_poe as fp

ACCESS = os.getenv("POE_ACCESS_KEY")
POE_API_KEY = os.getenv("POE_API_KEY")

class EchoBot(PoeBot):
    async def call_claude(self, prompt):
        """Claude-3.5-Sonnetを呼び出す"""
        try:
            messages = [fp.ProtocolMessage(role="user", content=prompt)]
            
            response_text = ""
            async for partial in fp.get_bot_response(
                messages=messages,
                bot_name="Claude-3.5-Sonnet",  # 公式ドキュメント通り
                api_key=POE_API_KEY
            ):
                if hasattr(partial, 'text') and partial.text:
                    response_text += partial.text
            
            return response_text if response_text else "応答が空でした"
            
        except Exception as e:
            return f"エラー: {str(e)}"

    async def get_response(self, query: QueryRequest):
        try:
            content = query.query[-1].content.strip()
            
            if "ping" in content.lower():
                yield self.text_event("pong")
                
            elif content.startswith("/ test"):
                yield self.text_event("🟢 Claude-3.5-Sonnet テスト...")
                result = await self.call_claude("Hello! Please respond briefly in Japanese.")
                yield self.text_event(f"Claude応答: {result}")
                
            elif content.startswith("/ make"):
                theme = content.replace("/ make", "").strip()
                if not theme:
                    yield self.text_event("テーマを指定してください。例: / make 猫の冒険")
                    return
                    
                yield self.text_event(f"📚 絵本「{theme}」を生成中...")
                
                story_prompt = f"""
子供向けの絵本を日本語で作成してください。

テーマ: {theme}

以下の形式で出力してください：

**タイトル: [絵本のタイトル]**

**ページ1:**
[最初のページの文章（1-2文）]

**ページ2:**
[2番目のページの文章（1-2文）]

**ページ3:**
[3番目のページの文章（1-2文）]

**ページ4:**
[最後のページの文章（1-2文）]

各ページは子供が理解しやすい簡単な文章にしてください。
                """
                
                story = await self.call_claude(story_prompt)
                yield self.text_event(story)
                
            else:
                yield self.text_event(f"受信: {content}\n\n利用可能なコマンド:\n- `/ test` : Claudeテスト\n- `/ make [テーマ]` : 絵本作成")
                
        except Exception as e:
            yield self.text_event(f"エラー: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(EchoBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
