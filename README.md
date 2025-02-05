# 販売データ分析ダッシュボード

Streamlitを使用した販売データ分析ダッシュボードです。

## 機能

- 日付範囲によるデータフィルタリング
- カテゴリー別フィルタリング
- 基本的なKPI表示（総売上、平均購入金額、購入者数）
- 様々な分析グラフ
  - 月別売上推移
  - カテゴリー別売上構成
  - 年齢層別平均購入金額
  - 性別別平均購入金額
  - 地域別売上分布
  - 支払方法の分布

## セットアップ

1. 仮想環境の作成とアクティベート
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
```

2. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

3. アプリケーションの実行
```bash
streamlit run app.py
```

## データ要件

`data/sample-data.csv` に以下のカラムを含むCSVファイルを配置してください：
- 購入日
- 購入金額
- 購入カテゴリー
- 年齢
- 性別
- 地域
- 支払方法 