import os
from typing import AsyncIterable
import fastapi_poe as fp
from fastapi import FastAPI
from fastapi_poe import make_app, PoeBot, QueryRequest

ACCESS = os.getenv("POE_ACCESS_KEY")

class PictureStorybookBot(fp.PoeBot):
    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        """ボットの依存関係を宣言"""
        return fp.SettingsResponse(server_bot_dependencies={"Claude-3.5-Sonnet": 1})

    async def get_response(self, request: fp.QueryRequest) -> AsyncIterable[fp.PartialResponse]:
        try:
            content = request.query[-1].content.strip()
            
            if "ping" in content.lower():
                yield fp.PartialResponse(text="pong")
                
            elif content.startswith("/ test"):
                yield fp.PartialResponse(text="🔄 Claude-3.5-Sonnet テスト中...")
                
                # 正しい方法でボットを呼び出し
                async for msg in fp.stream_request(
                    request, "Claude-3.5-Sonnet", request.access_key
                ):
                    yield msg
                    
            elif content.startswith("/ make"):
                theme = content.replace("/ make", "").strip()
                if not theme:
                    yield fp.PartialResponse(text="テーマを指定してください。例: / make 猫の冒険")
                    return
                    
                yield fp.PartialResponse(text=f"📚 絵本「{theme}」を生成中...")
                
                # 絵本生成のプロンプトを作成
                story_prompt = f"""
テーマ「{theme}」で、子供向けの短い絵本を日本語で作ってください。

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
                
                # 新しいリクエストを作成
                new_query = request.query.copy()
                new_query[-1] = fp.ProtocolMessage(role="user", content=story_prompt)
                new_request = fp.QueryRequest(
                    query=new_query,
                    user_id=request.user_id,
                    conversation_id=request.conversation_id,
                    message_id=request.message_id,
                    access_key=request.access_key
                )
                
                # Claude-3.5-Sonnetで絵本を生成
                async for msg in fp.stream_request(
                    new_request, "Claude-3.5-Sonnet", request.access_key
                ):
                    yield msg
                    
            else:
                yield fp.PartialResponse(text=f"受信: {content}\n\n利用可能なコマンド:\n- `/ test` : Claude-3.5-Sonnetテスト\n- `/ make [テーマ]` : 絵本作成")
                
        except Exception as e:
            yield fp.PartialResponse(text=f"エラー: {str(e)}")

app = FastAPI()
app.mount("/poe/", make_app(PictureStorybookBot(), access_key=ACCESS))

@app.get("/")
def health():
    return {"ok": True}
