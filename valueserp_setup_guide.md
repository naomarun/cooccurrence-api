# ValueSERP APIキー取得・設定ガイド

## 1. ValueSERPアカウントの作成

### ステップ1: 公式サイトにアクセス

[ValueSERP公式サイト](https://www.valueserp.com/)にアクセスします。

または、直接サインアップページ: https://app.valueserp.com/signup

### ステップ2: アカウント登録

1. **Sign Up**ボタンをクリック
2. 以下の情報を入力:
   - **Name**: お名前
   - **Email**: メールアドレス
   - **Password**: パスワード（8文字以上推奨）
3. **Create Account**をクリック

### ステップ3: メール認証

1. 登録したメールアドレスに確認メールが届きます
2. メール内の**Verify Email**リンクをクリック
3. アカウントが有効化されます

## 2. APIキーの取得

### ステップ1: ダッシュボードにログイン

1. [ValueSERPログインページ](https://app.valueserp.com/login)にアクセス
2. メールアドレスとパスワードを入力してログイン

### ステップ2: APIキーを確認

ログイン後、画面右上に**API Key**が表示されています。

**スクリーンショットの例:**
```
API Key: ●●●●●●●●●●●●●●●●●●●●●●●●
```

この文字列があなたの**APIキー**です。

### ステップ3: APIキーをコピー

1. APIキーの右側にある**コピーアイコン**をクリック
2. APIキーがクリップボードにコピーされます

**重要:** APIキーは秘密情報です。他人と共有しないでください。

## 3. API Playgroundでテスト（オプション）

APIキーが正しく動作するか、API Playgroundでテストできます。

### ステップ1: API Playgroundにアクセス

左側のメニューから**API Playground**をクリックします。

### ステップ2: テスト検索を実行

スクリーンショットの設定例を参考に、以下のように設定します。

**基本設定:**
- **Search Type**: Google Web Search
- **Search (q)**: テストしたいキーワード（例: `keyword here`）
- **Location**: `98146, Washington, United States`（または任意のロケーション）
- **Google Domain**: `Japan - jp`（日本の検索結果を取得する場合）
- **Google Country**: `Japan - jp`
- **Google UI Language**: `Japanese`

**AI Overview設定:**
- **Google AI Overview**: `include_ai_overview`
- **Include AI Overview**: `false`（AI Overviewを除外する場合）

### ステップ3: リクエストを送信

右上の**Send API Request**ボタンをクリックします。

### ステップ4: 結果を確認

右側の**Results**タブに、JSON形式でレスポンスが表示されます。

**確認ポイント:**
- `"request_info"`: `"success": true`になっているか
- `"organic_results"`: 検索結果が配列で返されているか

## 4. Renderでの環境変数設定

### ステップ1: Renderダッシュボードにアクセス

1. [Render Dashboard](https://dashboard.render.com/)にログイン
2. 該当のWebサービスを選択

### ステップ2: 環境変数を追加

1. 左側のメニューから**Environment**タブをクリック
2. **Add Environment Variable**ボタンをクリック
3. 以下の情報を入力:
   - **Key**: `VALUESERP_API_KEY`
   - **Value**: ValueSERPからコピーしたAPIキー
4. **Save Changes**をクリック

### ステップ3: 再デプロイ

環境変数を追加すると、Renderが自動的に再デプロイを開始します。

デプロイが完了するまで数分待ちます。

## 5. 動作確認

### ステップ1: ヘルスチェック

以下のコマンドで、APIキーが正しく設定されているか確認します。

```bash
curl https://your-app.onrender.com/health
```

**期待される応答:**
```json
{
  "status": "ok",
  "mecab_available": true,
  "ahrefs_api_configured": true,
  "valueserp_api_configured": true
}
```

`"valueserp_api_configured": true`になっていればOKです。

### ステップ2: テストリクエスト

実際に共起語抽出をテストします。

```bash
curl -X POST https://your-app.onrender.com/extract \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "テストキーワード",
    "country": "jp",
    "top_pages": 10,
    "top_words": 50,
    "use_api": "valueserp"
  }'
```

**期待される応答:**
```json
{
  "keyword": "テストキーワード",
  "cooccurrence_words": ["共起語1", "共起語2", ...],
  "cooccurrence_string": "共起語1, 共起語2, ...",
  "analyzed_pages": 10,
  "top_urls": ["https://...", ...],
  "mecab_used": true,
  "api_used": "valueserp"
}
```

`"api_used": "valueserp"`になっていれば、ValueSERP APIが正しく使用されています。

## 6. プラン選択とクレジット管理

### 無料トライアル

新規アカウントには、通常**無料クレジット**が付与されます。

### 有料プラン

無料クレジットを使い切った後は、以下のプランから選択できます。

| プラン | 月額料金 | 検索数/月 | 単価 |
|--------|---------|----------|------|
| 従量課金 | $0〜 | 使った分だけ | $0.002〜0.003/検索 |
| 25k | $50（年契約） | 25,000 | $0.002/検索 |
| 100k | $180（年契約） | 100,000 | $0.0018/検索 |

### クレジット残高の確認

ダッシュボードの右上に、現在のクレジット残高が表示されます。

## 7. トラブルシューティング

### 問題1: APIキーが表示されない

**解決策:**
- メール認証が完了しているか確認
- ログアウトして再度ログイン
- ブラウザのキャッシュをクリア

### 問題2: API Playgroundでエラーが発生

**確認事項:**
- APIキーが正しくコピーされているか
- クレジット残高があるか
- パラメータが正しく設定されているか

### 問題3: Renderで環境変数が反映されない

**解決策:**
- 環境変数を保存後、手動で再デプロイを実行
- 環境変数名が`VALUESERP_API_KEY`と完全に一致しているか確認
- APIキーに余分なスペースが含まれていないか確認

### 問題4: `valueserp_api_configured: false`と表示される

**原因:**
- 環境変数が設定されていない
- 環境変数名が間違っている
- Renderの再デプロイが完了していない

**解決策:**
1. Renderの環境変数を再確認
2. 手動で再デプロイを実行
3. デプロイ完了後、再度ヘルスチェックを実行

## 8. セキュリティのベストプラクティス

### APIキーの管理

- **絶対にGitHubにコミットしない**: `.env`ファイルや環境変数で管理
- **定期的にローテーション**: セキュリティ上、定期的にAPIキーを再生成
- **アクセス制限**: 必要な人だけがAPIキーにアクセスできるようにする

### 使用量の監視

- ダッシュボードで定期的に使用量を確認
- 予期せぬ大量リクエストがないかチェック
- 必要に応じてレート制限を設定

## まとめ

1. ✅ ValueSERPアカウントを作成
2. ✅ ダッシュボードからAPIキーをコピー
3. ✅ API Playgroundでテスト（オプション）
4. ✅ Renderの環境変数に`VALUESERP_API_KEY`を設定
5. ✅ ヘルスチェックで動作確認
6. ✅ テストリクエストで共起語抽出を確認

これで、ValueSERP APIを使った共起語抽出が利用可能になります！

ご不明な点がございましたら、お気軽にお問い合わせください。
