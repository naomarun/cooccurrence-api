# 共起語抽出API

MeCabを使った形態素解析による真の共起語抽出APIサーバー

## 機能

- Ahrefs APIで上位ランキングページを取得
- Webスクレイピングでコンテンツを収集
- MeCabによる日本語形態素解析
- 共起語の抽出と頻度分析

## エンドポイント

### GET /health
ヘルスチェック

### POST /extract
共起語抽出

**リクエスト:**
```json
{
  "keyword": "SEO対策",
  "country": "jp",
  "top_pages": 10,
  "top_words": 50
}
```

**レスポンス:**
```json
{
  "keyword": "SEO対策",
  "cooccurrence_words": ["検索エンジン", "上位表示", ...],
  "cooccurrence_string": "検索エンジン, 上位表示, ...",
  "analyzed_pages": 8,
  "top_urls": ["https://...", ...],
  "mecab_used": true
}
```

## 環境変数

- `AHREFS_API_KEY`: Ahrefs APIキー（必須）

## デプロイ (Render)

1. GitHubリポジトリを作成
2. Renderで新しいWeb Serviceを作成
3. 環境変数 `AHREFS_API_KEY` を設定
4. デプロイ

## ローカル実行

```bash
pip install -r requirements.txt
export AHREFS_API_KEY="your_api_key"
python app.py
```
