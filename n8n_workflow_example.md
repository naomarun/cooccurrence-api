# n8nワークフロー設定例

## 基本的なワークフロー構成

```
[トリガー] → [HTTPリクエスト] → [データ処理] → [出力]
```

## HTTPリクエストノードの設定

### 設定1: 基本的な共起語抽出（AI Overviewなし）

**ノード名**: 共起語抽出API呼び出し

**設定項目:**
- **Method**: POST
- **URL**: `https://your-app.onrender.com/extract`
- **Authentication**: None
- **Send Headers**: Yes
  - **Name**: `Content-Type`
  - **Value**: `application/json`
- **Send Body**: Yes
- **Body Content Type**: JSON
- **Specify Body**: Using Fields
- **Fields to Send**:
  - `keyword`: `{{ $json.keyword }}`
  - `country`: `jp`
  - `top_pages`: `10`
  - `top_words`: `50`
  - `use_api`: `hybrid`
  - `include_ai_overview`: `false`

### 設定2: AI Overview含む共起語抽出

**ノード名**: 共起語抽出API呼び出し（AI Overview含む）

**設定項目:**
- **Method**: POST
- **URL**: `https://your-app.onrender.com/extract`
- **Authentication**: None
- **Send Headers**: Yes
  - **Name**: `Content-Type`
  - **Value**: `application/json`
- **Send Body**: Yes
- **Body Content Type**: JSON
- **Specify Body**: Using JSON
- **JSON**:

```json
{
  "keyword": "{{ $json.keyword }}",
  "country": "jp",
  "top_pages": 10,
  "top_words": 50,
  "use_api": "hybrid",
  "include_ai_overview": true
}
```

## レスポンスデータの処理

### 共起語の取得

HTTPリクエストノードの後に**Set**ノードを追加して、必要なデータを抽出します。

**Setノードの設定:**
- **Keep Only Set**: Yes
- **Values to Set**:
  - **Name**: `keyword`
    - **Value**: `{{ $json.keyword }}`
  - **Name**: `cooccurrence_words`
    - **Value**: `{{ $json.cooccurrence_words }}`
  - **Name**: `cooccurrence_string`
    - **Value**: `{{ $json.cooccurrence_string }}`
  - **Name**: `analyzed_pages`
    - **Value**: `{{ $json.analyzed_pages }}`
  - **Name**: `api_used`
    - **Value**: `{{ $json.api_used }}`

### AI Overview情報の取得（オプション）

AI Overviewを含める場合、以下のフィールドも追加します。

**追加のValues to Set:**
- **Name**: `ai_overview_included`
  - **Value**: `{{ $json.ai_overview_included }}`
- **Name**: `ai_overview_text`
  - **Value**: `{{ $json.ai_overview?.text || "" }}`
- **Name**: `ai_overview_position`
  - **Value**: `{{ $json.ai_overview?.position || null }}`

## 実践的なワークフロー例

### 例1: スプレッドシートから複数キーワードの共起語を一括抽出

```
[Google Sheets] → [Loop Over Items] → [HTTPリクエスト] → [Set] → [Google Sheets書き込み]
```

**Google Sheetsノード（読み込み）:**
- **Operation**: Read
- **Sheet**: キーワードリスト
- **Range**: A2:A100

**HTTPリクエストノード:**
- URL: `https://your-app.onrender.com/extract`
- Body:
```json
{
  "keyword": "{{ $json['キーワード'] }}",
  "country": "jp",
  "top_pages": 10,
  "top_words": 50,
  "use_api": "hybrid",
  "include_ai_overview": false
}
```

**Setノード:**
- `keyword`: `{{ $json.keyword }}`
- `cooccurrence_string`: `{{ $json.cooccurrence_string }}`
- `analyzed_pages`: `{{ $json.analyzed_pages }}`

**Google Sheetsノード（書き込み）:**
- **Operation**: Append
- **Sheet**: 共起語結果
- **Columns**:
  - キーワード: `{{ $json.keyword }}`
  - 共起語: `{{ $json.cooccurrence_string }}`
  - 分析ページ数: `{{ $json.analyzed_pages }}`

### 例2: AI Overview付きの詳細分析

```
[Webhook] → [HTTPリクエスト] → [IF] → [Set] → [Slack通知]
```

**Webhookノード:**
- **HTTP Method**: POST
- **Path**: `/analyze-keyword`

**HTTPリクエストノード:**
- URL: `https://your-app.onrender.com/extract`
- Body:
```json
{
  "keyword": "{{ $json.body.keyword }}",
  "country": "{{ $json.body.country || 'jp' }}",
  "top_pages": 10,
  "top_words": 50,
  "use_api": "hybrid",
  "include_ai_overview": true
}
```

**IFノード:**
- **Condition**: `{{ $json.ai_overview_included }} === true`

**Setノード（True分岐）:**
- `message`: `キーワード「{{ $json.keyword }}」の分析完了\n共起語: {{ $json.cooccurrence_string }}\n\nAI Overview:\n{{ $json.ai_overview.text }}`

**Setノード（False分岐）:**
- `message`: `キーワード「{{ $json.keyword }}」の分析完了\n共起語: {{ $json.cooccurrence_string }}\n\n※AI Overviewなし`

**Slackノード:**
- **Channel**: #seo-analysis
- **Text**: `{{ $json.message }}`

## エラーハンドリング

### HTTPリクエストノードのエラー設定

**Error Workflow Settings:**
- **Continue On Fail**: Yes
- **Retry On Fail**: Yes
- **Max Tries**: 3
- **Wait Between Tries**: 5000 (5秒)

### エラー時の処理

HTTPリクエストノードの後に**IF**ノードを追加して、エラーをチェックします。

**IFノード:**
- **Condition**: `{{ $json.error }} !== undefined`

**True分岐（エラー時）:**
- **Setノード**:
  - `error_message`: `{{ $json.error }}`
  - `keyword`: `{{ $json.keyword }}`
- **Slack通知**: エラーメッセージを送信

**False分岐（成功時）:**
- 通常の処理を続行

## パフォーマンス最適化

### バッチ処理の設定

大量のキーワードを処理する場合、**Split In Batches**ノードを使用します。

```
[データソース] → [Split In Batches] → [HTTPリクエスト] → [Wait] → [集約]
```

**Split In Batchesノード:**
- **Batch Size**: 10
- **Options**: Reset

**Waitノード:**
- **Amount**: 2
- **Unit**: Seconds

これにより、APIレート制限を回避できます。

## まとめ

- **基本設定**: `use_api=hybrid`、`include_ai_overview=false`
- **詳細分析**: `include_ai_overview=true`（コスト+1クレジット）
- **エラーハンドリング**: 必ず設定する
- **バッチ処理**: 大量データ処理時は適切な待機時間を設定

ご不明な点がございましたら、お気軽にお問い合わせください。
