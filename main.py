import os
import fastapi_poe as fp
from fastapi import FastAPI

ACCESS = os.getenv("POE_ACCESS_KEY")

class PictureStorybook(fp.PoeBot):
    async def get_response(self, query: fp.QueryRequest):
        try:
            # 最後のメッセージを取得
            if query.query:
                content = query.query[-1].content
            else:
                content = ""
                
            if "ping" in content.lower():
                yield fp.PartialResponse(text="pong")
                
            elif "/make" in content or "作って" in content or "生成" in content:
                # テーマを抽出
                theme = content.replace("/make", "").replace("作って", "").replace("生成", "").strip()
                if not theme:
                    theme = "冒険"
                
                yield fp.PartialResponse(text=f"📚 絵本「{theme}」を生成中...\n\n")
                
                # プロンプトを作成
                prompt = f"""
                「{theme}」をテーマにした子供向けの絵本を5ページで作成してください。
                
                各ページには：
                1. ページ番号
                2. 短い物語文（2-3文）
                3. 【場面】として、そのページの絵の描写
                
                を含めてください。温かみのある内容でお願いします。
                """
                
                # Claude-3.5-Sonnetを呼び出し
                async for partial in fp.stream_request(
                    query, 
                    "Claude-3.5-Sonnet",
                    query.api_key  # QueryRequestからapi_keyを使用
                ):
                    yield partial
                    
            else:
                # ヘルプメッセージ
                yield fp.PartialResponse(text="""
                📖 PictureStorybookボットへようこそ！
                
                使い方：
                • 「/make [テーマ]」 - 絵本を生成します
                • 例: "/make 海の冒険"、"/make 宇宙の旅"
                • 「ping」 - 接続テスト
                
                どんなテーマの絵本を作りましょうか？
                """)
                
        except Exception as e:
            yield fp.ErrorResponse(
                text=f"エラーが発生しました: {str(e)}",
                allow_retry=True
            )

app = FastAPI()
app.mount("/", fp.make_app(PictureStorybook(), access_key=ACCESS))

@app.get("/health")
def health():
    return {"status": "healthy", "bot": "PictureStorybook"}
