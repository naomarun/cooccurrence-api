#!/usr/bin/env python3
"""
共起語抽出APIサーバー（ValueSERP対応版 - 最終版）
MeCabを使った形態素解析による真の共起語抽出
日本語検索最適化、AI Overviewは除外
"""

import os
import requests
import time
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urlencode
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import MeCab

app = Flask(__name__)
CORS(app)

# 環境変数から取得
AHREFS_API_KEY = os.environ.get("AHREFS_API_KEY", "")
VALUESERP_API_KEY = os.environ.get("VALUESERP_API_KEY", "")

# MeCabの初期化
try:
    mecab = MeCab.Tagger("-Owakati")
    print("✅ MeCab初期化成功")
except Exception as e:
    print(f"⚠️  MeCab初期化エラー: {e}")
    mecab = None


# 国別設定
COUNTRY_CONFIG = {
    'jp': {
        'location': 'Japan',
        'google_domain': 'google.co.jp',
        'gl': 'jp',
        'hl': 'ja'
    },
    'us': {
        'location': 'United States',
        'google_domain': 'google.com',
        'gl': 'us',
        'hl': 'en'
    },
    'uk': {
        'location': 'United Kingdom',
        'google_domain': 'google.co.uk',
        'gl': 'uk',
        'hl': 'en'
    },
    'ca': {
        'location': 'Canada',
        'google_domain': 'google.ca',
        'gl': 'ca',
        'hl': 'en'
    },
    'au': {
        'location': 'Australia',
        'google_domain': 'google.com.au',
        'gl': 'au',
        'hl': 'en'
    },
    'de': {
        'location': 'Germany',
        'google_domain': 'google.de',
        'gl': 'de',
        'hl': 'de'
    },
    'fr': {
        'location': 'France',
        'google_domain': 'google.fr',
        'gl': 'fr',
        'hl': 'fr'
    },
    'kr': {
        'location': 'South Korea',
        'google_domain': 'google.co.kr',
        'gl': 'kr',
        'hl': 'ko'
    },
    'cn': {
        'location': 'China',
        'google_domain': 'google.com.hk',
        'gl': 'cn',
        'hl': 'zh-CN'
    }
}


def get_top_ranking_pages_valueserp(keyword, country="jp", limit=10):
    """ValueSERP APIで上位ランキングページを取得（日本語最適化、AI Overview除外）"""
    print(f"🔍 ValueSERP APIで上位ページを取得中: {keyword}")
    
    # 国別設定を取得
    config = COUNTRY_CONFIG.get(country, COUNTRY_CONFIG['jp'])
    
    params = {
        'api_key': VALUESERP_API_KEY,
        'q': keyword,
        'location': config['location'],
        'google_domain': config['google_domain'],
        'gl': config['gl'],
        'hl': config['hl'],
        'output': 'json',
        'num': limit,
        'include_ai_overview': 'false'  # AI Overviewは明示的に除外
    }
    
    try:
        print(f"📤 リクエストパラメータ: {json.dumps({k: v for k, v in params.items() if k != 'api_key'}, ensure_ascii=False)}")
        
        response = requests.get('https://api.valueserp.com/search', params=params, timeout=60)
        
        print(f"📥 ステータスコード: {response.status_code}")
        
        response.raise_for_status()
        
        data = response.json()
        
        # デバッグ情報を出力
        print(f"📊 レスポンスキー: {list(data.keys())}")
        
        top_urls = []
        
        # ValueSERPのレスポンス構造を確認
        if data.get('request_info', {}).get('success') == True:
            if 'organic_results' in data:
                print(f"📊 organic_results配列の長さ: {len(data['organic_results'])}")
                
                for i, result in enumerate(data['organic_results'], 1):
                    if 'link' in result:
                        top_urls.append(result['link'])
                        print(f"  {i}位: {result['link']}")
                        if len(top_urls) >= limit:
                            break
            else:
                print("⚠️  'organic_results'キーがレスポンスに存在しません")
        else:
            print(f"⚠️  APIリクエストが失敗しました: {data.get('request_info', {}).get('message', '不明なエラー')}")
        
        print(f"✅ 上位ページ取得完了: {len(top_urls)}件")
        
        if len(top_urls) == 0:
            print(f"⚠️  警告: キーワード「{keyword}」の検索結果が0件でした")
        
        return top_urls
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️  ValueSERP API リクエストエラー: {e}")
        return []
    except Exception as e:
        print(f"⚠️  予期せぬエラー: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_top_ranking_pages(keyword, country="jp", limit=10):
    """Ahrefs APIで上位ランキングページを取得"""
    print(f"🔍 Ahrefs APIで上位ページを取得中: {keyword}")
    
    url = "https://api.ahrefs.com/v3/serp-overview/serp-overview"
    
    headers = {
        "Authorization": f"Bearer {AHREFS_API_KEY}",
        "Accept": "application/json"
    }
    
    params = {
        "keyword": keyword,
        "country": country,
        "select": "position,url,title,type",
        "top_positions": limit
    }
    
    try:
        full_url = f"{url}?{urlencode(params)}"
        
        print(f"📤 リクエストURL: {full_url}")
        
        response = requests.get(full_url, headers=headers, timeout=30)
        
        print(f"📥 ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            top_urls = []
            if 'positions' in data:
                for result in data['positions']:
                    if 'url' in result and result['url'] is not None:
                        result_types = result.get('type', [])
                        if isinstance(result_types, str):
                            result_types = [result_types]
                        
                        # AI Overviewを除外
                        if result_types == ['ai_overview']:
                            continue
                        
                        top_urls.append(result['url'])
                        if len(top_urls) >= limit:
                            break
            
            print(f"✅ 上位ページ取得完了: {len(top_urls)}件")
            return top_urls
        
        else:
            print(f"⚠️  Ahrefs API エラー: {response.status_code}")
            print(f"レスポンス: {response.text}")
            return []
    
    except Exception as e:
        print(f"⚠️  上位ページ取得エラー: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_top_ranking_pages_hybrid(keyword, country="jp", limit=10):
    """Ahrefsを優先し、失敗時にValueSERPにフォールバックする"""
    
    # 1. まずAhrefs APIを試す（APIキーが設定されている場合のみ）
    if AHREFS_API_KEY:
        print("🔍 Ahrefs APIで試行中...")
        ahrefs_urls = get_top_ranking_pages(keyword, country, limit)
        
        if ahrefs_urls:
            print("✅ Ahrefs APIで取得成功")
            return ahrefs_urls, 'ahrefs'
    
    # 2. Ahrefsで失敗した場合、またはAPIキーがない場合、ValueSERP APIを呼び出す
    if VALUESERP_API_KEY:
        print("⚠️  Ahrefsで結果なし、またはAPIキー未設定。ValueSERPにフォールバックします...")
        valueserp_urls = get_top_ranking_pages_valueserp(keyword, country, limit)
        return valueserp_urls, 'valueserp'
    
    print("⚠️  エラー: AhrefsとValueSERPの両方のAPIキーが設定されていません")
    return [], 'none'


def scrape_page_content(url, timeout=10):
    """指定URLのページコンテンツをスクレイピング"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        main_content = (
            soup.find('article') or 
            soup.find('main') or 
            soup.find('div', class_=re.compile(r'content|article|post', re.I)) or
            soup.find('body')
        )
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            return text
        
        return ""
    
    except Exception as e:
        print(f"  ⚠️  スクレイピングエラー ({url}): {e}")
        return ""


def extract_cooccurrence_with_mecab(texts, keyword, top_n=50):
    """MeCabを使った共起語抽出"""
    print(f"📊 MeCabで共起語を抽出中...")
    
    if not mecab:
        print("⚠️  MeCabが利用できません。簡易抽出を使用します。")
        return extract_cooccurrence_simple(texts, keyword, top_n)
    
    combined_text = ' '.join(texts)
    
    # MeCabで形態素解析
    try:
        parsed = mecab.parse(combined_text)
        words = parsed.split()
    except Exception as e:
        print(f"⚠️  MeCab解析エラー: {e}")
        return extract_cooccurrence_simple(texts, keyword, top_n)
    
    # ストップワード
    stopwords = {
        'こと', 'ため', 'もの', 'これ', 'それ', 'あれ', 'この', 'その', 'あの',
        'ここ', 'そこ', 'あそこ', 'です', 'ます', 'ある', 'いる', 'なる', 'する',
        'できる', 'という', 'として', 'により', 'について', 'において', 'に対して',
        'の', 'に', 'を', 'は', 'が', 'で', 'と', 'も', 'から', 'まで', 'より',
        'へ', 'や', 'か', 'ね', 'よ', 'な', 'だ', 'た', 'て', 'れ', 'ば'
    }
    
    # キーワードもストップワードに追加
    keyword_words = set(re.findall(r'\w+', keyword))
    stopwords.update(keyword_words)
    
    # フィルタリング（2文字以上、ストップワード除外）
    filtered_words = [
        w for w in words 
        if len(w) >= 2 and w not in stopwords and re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', w)
    ]
    
    # 出現回数をカウント
    word_counts = Counter(filtered_words)
    
    # 上位N件を取得
    top_words = word_counts.most_common(top_n)
    
    print(f"✅ 共起語抽出完了: {len(top_words)}件")
    
    return top_words


def extract_cooccurrence_simple(texts, keyword, top_n=50):
    """簡易的な共起語抽出（MeCab不使用）"""
    combined_text = ' '.join(texts)
    
    # 2〜4文字の日本語フレーズを抽出
    words = re.findall(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]{2,4}', combined_text)
    
    stopwords = {
        'こと', 'ため', 'もの', 'これ', 'それ', 'あれ', 'この', 'その', 'あの',
        'ここ', 'そこ', 'あそこ', 'です', 'ます', 'ある', 'いる', 'なる', 'する',
        'できる', 'という', 'として', 'により', 'について', 'において', 'に対して'
    }
    
    keyword_words = set(re.findall(r'\w+', keyword))
    stopwords.update(keyword_words)
    
    filtered_words = [w for w in words if w not in stopwords]
    word_counts = Counter(filtered_words)
    top_words = word_counts.most_common(top_n)
    
    return top_words


@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        'status': 'ok',
        'mecab_available': mecab is not None,
        'ahrefs_api_configured': bool(AHREFS_API_KEY),
        'valueserp_api_configured': bool(VALUESERP_API_KEY)
    })


@app.route('/extract', methods=['POST'])
def extract_cooccurrence():
    """共起語抽出エンドポイント"""
    try:
        data = request.get_json()
        
        if not data or 'keyword' not in data:
            return jsonify({'error': 'キーワードが指定されていません'}), 400
        
        keyword = data['keyword']
        country = data.get('country', 'jp')
        top_pages = data.get('top_pages', 10)
        top_words = data.get('top_words', 50)
        use_api = data.get('use_api', 'hybrid')  # 'ahrefs', 'valueserp', 'hybrid'
        
        print(f"\n{'='*60}")
        print(f"共起語抽出リクエスト: {keyword}")
        print(f"使用API: {use_api}")
        print(f"取得ページ数: 1〜{top_pages}位")
        print(f"{'='*60}\n")
        
        # 1. 上位ページのURL取得
        if use_api == 'valueserp':
            top_urls = get_top_ranking_pages_valueserp(keyword, country, top_pages)
            api_used = 'valueserp'
        elif use_api == 'ahrefs':
            top_urls = get_top_ranking_pages(keyword, country, top_pages)
            api_used = 'ahrefs'
        else:  # hybrid
            top_urls, api_used = get_top_ranking_pages_hybrid(keyword, country, top_pages)
        
        if not top_urls:
            return jsonify({
                'error': '上位ページが取得できませんでした',
                'keyword': keyword,
                'cooccurrence_words': [],
                'analyzed_pages': 0,
                'api_used': api_used,
                'debug_info': {
                    'message': 'APIから0件の結果が返されました。上記のログを確認してください。'
                }
            }), 500
        
        # 2. 各ページのコンテンツをスクレイピング
        print(f"\n📥 {len(top_urls)}ページのコンテンツをスクレイピング中...")
        texts = []
        
        for i, url in enumerate(top_urls, 1):
            print(f"  [{i}/{len(top_urls)}] {url}")
            content = scrape_page_content(url)
            
            if content:
                texts.append(content)
                print(f"    ✅ 取得成功 ({len(content)}文字)")
            else:
                print(f"    ⚠️  取得失敗")
            
            time.sleep(1)
        
        if not texts:
            return jsonify({
                'error': 'コンテンツが取得できませんでした',
                'keyword': keyword,
                'cooccurrence_words': [],
                'analyzed_pages': 0,
                'api_used': api_used
            }), 500
        
        print(f"\n✅ {len(texts)}ページのコンテンツ取得完了")
        
        # 3. 共起語抽出（MeCab使用）
        cooccurrence_words = extract_cooccurrence_with_mecab(texts, keyword, top_words)
        
        # 4. 結果を整形
        result_list = [word for word, count in cooccurrence_words]
        result_str = ', '.join(result_list)
        
        print(f"\n{'='*60}")
        print(f"✅ 共起語抽出完了!")
        print(f"{'='*60}")
        print(f"\n【抽出された共起語 (上位20件)】")
        for i, (word, count) in enumerate(cooccurrence_words[:20], 1):
            print(f"  {i:2d}. {word:20s} ({count:3d}回)")
        
        return jsonify({
            'keyword': keyword,
            'cooccurrence_words': result_list,
            'cooccurrence_string': result_str,
            'analyzed_pages': len(texts),
            'top_urls': top_urls,
            'mecab_used': mecab is not None,
            'api_used': api_used
        })
    
    except Exception as e:
        print(f"⚠️  エラー: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("共起語抽出APIサーバー起動中（最終版）...")
    print("="*60)
    print(f"MeCab: {'✅ 利用可能' if mecab else '⚠️  利用不可'}")
    print(f"Ahrefs API: {'✅ 設定済み' if AHREFS_API_KEY else '⚠️  未設定'}")
    print(f"ValueSERP API: {'✅ 設定済み' if VALUESERP_API_KEY else '⚠️  未設定'}")
    print(f"対応国数: {len(COUNTRY_CONFIG)}ヶ国")
    print(f"AI Overview: ❌ 除外（通常の検索結果のみ）")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
