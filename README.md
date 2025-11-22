# 共起語抽出API（ValueSERP対応版 - 最終版）

MeCabを使った形態素解析による真の共起語抽出APIです。

## 特徴

### ✅ 1位〜15位の通常検索結果のみを取得

- AI Overviewは**除外**
- オーガニック検索結果（1位〜15位）のみを対象
- 既存の共起語抽出ロジック（スクレイピング→MeCab形態素解析→共起語抽出）はそのまま

### ✅ 日本語検索の最適化

- `google_domain`、`gl`、`hl`パラメータの明示的設定
- 日本語クエリに最適化されたパラメータ構成
- 9ヶ国の国別設定に対応

### ✅ 複数API対応

- **Ahrefs API**: 既存のAhrefs SERP Overview API
- **ValueSERP API**: リアルタイムGoogle検索結果取得API
- **ハイブリッドモード**: Ahrefsを優先し、失敗時にValueSERPにフォールバック（推奨）

## 環境変数

以下の環境変数を設定してください。

```bash
AHREFS_API_KEY=your_ahrefs_api_key_here
VALUESERP_API_KEY=your_valueserp_api_key_here
```

- `AHREFS_API_KEY`: Ahrefs APIキー（オプション）
- `VALUESERP_API_KEY`: ValueSERP APIキー（オプション）

※ 少なくとも1つのAPIキーが必要です。両方設定すると、ハイブリッドモードが利用できます。

## APIエンドポイント

### ヘルスチェック

```bash
GET /health
```

レスポンス例:

```json
{
  "status": "ok",
  "mecab_available": true,
  "ahrefs_api_configured": true,
  "valueserp_api_configured": true
}
```

### 共起語抽出

```bash
POST /extract
Content-Type: application/json

{
  "keyword": "検索キーワード",
  "country": "jp",
  "top_pages": 10,
  "top_words": 50,
  "use_api": "hybrid"
}
```

#### パラメータ

- `keyword` (必須): 検索キーワード
- `country` (オプション): 国コード（デフォルト: "jp"）
  - 対応国: `jp`, `us`, `uk`, `ca`, `au`, `de`, `fr`, `kr`, `cn`
- `top_pages` (オプション): 取得する上位ページ数（デフォルト: 10、最大15推奨）
- `top_words` (オプション): 抽出する共起語数（デフォルト: 50）
- `use_api` (オプション): 使用するAPI（デフォルト: "hybrid"）
  - `"ahrefs"`: Ahrefs APIのみ使用
  - `"valueserp"`: ValueSERP APIのみ使用
  - `"hybrid"`: Ahrefsを優先し、失敗時にValueSERPを使用（推奨）

#### レスポンス例

```json
{
  "keyword": "検索キーワード",
  "cooccurrence_words": ["共起語1", "共起語2", "共起語3", ...],
  "cooccurrence_string": "共起語1, 共起語2, 共起語3, ...",
  "analyzed_pages": 10,
  "top_urls": ["https://example.com/1", "https://example.com/2", ...],
  "mecab_used": true,
  "api_used": "valueserp"
}
```

## 使用例

### cURLでのリクエスト

```bash
curl -X POST https://your-app.onrender.com/extract \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "共起語抽出",
    "country": "jp",
    "top_pages": 10,
    "top_words": 50,
    "use_api": "hybrid"
  }'
```

### Pythonでのリクエスト

```python
import requests

url = "https://your-app.onrender.com/extract"
data = {
    "keyword": "共起語抽出",
    "country": "jp",
    "top_pages": 10,
    "top_words": 50,
    "use_api": "hybrid"
}

response = requests.post(url, json=data)
result = response.json()

print("共起語:", result["cooccurrence_string"])
print("使用API:", result["api_used"])
```

### n8nでの使用

n8nのHTTPリクエストノードで以下のように設定します。

- **Method**: POST
- **URL**: `https://your-app.onrender.com/extract`
- **Body Content Type**: JSON
- **Body**:

```json
{
  "keyword": "{{ $json.keyword }}",
  "country": "jp",
  "top_pages": 10,
  "top_words": 50,
  "use_api": "hybrid"
}
```

## デプロイ方法

### Renderへのデプロイ

1. GitHubリポジトリにコードをプッシュ
2. Renderで新しいWebサービスを作成
3. 環境変数を設定
   - `AHREFS_API_KEY`（オプション）
   - `VALUESERP_API_KEY`（オプション）
4. デプロイ

### ローカルでの実行

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# MeCabのインストール（Ubuntu/Debian）
sudo apt-get install mecab libmecab-dev mecab-ipadic-utf8

# 環境変数の設定
export AHREFS_API_KEY="your_ahrefs_api_key"
export VALUESERP_API_KEY="your_valueserp_api_key"

# サーバーの起動
python app.py
```

## ValueSERP APIキーの取得方法

詳細な手順は、同梱の`valueserp_setup_guide.md`をご参照ください。

### 簡易手順

1. [ValueSERP公式サイト](https://www.valueserp.com/)でアカウント作成
2. ダッシュボードにログイン
3. 画面右上に表示されている**API Key**をコピー
4. Renderの環境変数に`VALUESERP_API_KEY`として設定

## 対応国一覧

| 国コード | 国名 | Google Domain | 言語 |
|---------|------|---------------|------|
| `jp` | 日本 | google.co.jp | 日本語 |
| `us` | 米国 | google.com | 英語 |
| `uk` | 英国 | google.co.uk | 英語 |
| `ca` | カナダ | google.ca | 英語 |
| `au` | オーストラリア | google.com.au | 英語 |
| `de` | ドイツ | google.de | ドイツ語 |
| `fr` | フランス | google.fr | フランス語 |
| `kr` | 韓国 | google.co.kr | 韓国語 |
| `cn` | 中国 | google.com.hk | 中国語 |

## 変更点のまとめ

### 旧バージョンからの変更点

| 項目 | 旧バージョン | 最終版 |
|-----|------------|--------|
| AI Overview | 対応 | **除外**（通常の検索結果のみ） |
| 日本語検索 | `location`のみ設定 | `google_domain`、`gl`、`hl`も明示的に設定 |
| 対応国数 | 13ヶ国（マッピングなし） | 9ヶ国（最適化された設定） |
| 取得範囲 | 1位〜10位 | **1位〜15位**（パラメータで調整可能） |

### 共起語抽出ロジック

**変更なし**。以下のフローはそのままです。

1. SERP APIで上位ページURL取得（ValueSERPまたはAhrefs）
2. 各ページをスクレイピング
3. MeCabで形態素解析
4. 共起語を抽出

## コスト情報

### ValueSERP API

- **基本料金**: $0.002/検索（25kプラン、年契約）
- **AI Overview除外**: 追加料金なし
- **月間1,000検索**: 約$2（従量課金）または$50/月（25kプラン）

### Ahrefs API

- 既存のクレジット消費
- データベースにないキーワードは0件

### ハイブリッドモード（推奨）

- Ahrefsで結果が得られる場合: Ahrefsクレジットのみ消費
- Ahrefsで結果が0件の場合: ValueSERPクレジットを消費
- **コスト効率が最も高い**

## トラブルシューティング

### 問題: ValueSERP APIでエラーが発生する

**確認事項:**
- APIキーが正しく設定されているか
- APIの利用制限に達していないか
- ネットワーク接続が正常か

### 問題: 検索結果が0件

**確認事項:**
- キーワードが正しいか
- 国コードが適切か
- Renderのログを確認

### 問題: デプロイが失敗する

**確認事項:**
- `requirements.txt`に必要なパッケージが含まれているか
- Pythonのバージョンが互換性があるか

## ライセンス

MIT License

## お問い合わせ

ご質問やご要望がございましたら、GitHubのIssuesまでお願いします。
