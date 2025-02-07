import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# ページ設定
st.set_page_config(page_title="販売データ分析ダッシュボード", layout="wide")
st.title("販売データ分析ダッシュボード")

# データ読み込み
@st.cache_data
def load_data():
    # データファイルの存在確認
    data_path = 'data/sample-data.csv'
    if not os.path.exists(data_path):
        st.error(f"データファイル {data_path} が見つかりません。")
        # サンプルデータの作成
        df = pd.DataFrame({
            '購入日': pd.date_range(start='2023-01-01', end='2023-12-31', freq='D'),
            '購入金額': np.random.randint(1000, 100000, size=365),
            '購入カテゴリー': np.random.choice(['食品', '衣類', '電化製品', '書籍', '雑貨'], size=365),
            '年齢': np.random.randint(20, 70, size=365),
            '性別': np.random.choice(['男性', '女性'], size=365),
            '地域': np.random.choice(['東京', '大阪', '名古屋', '福岡', '札幌'], size=365),
        })
        # データディレクトリの作成
        os.makedirs('data', exist_ok=True)
        # サンプルデータの保存
        df.to_csv(data_path, index=False)
        st.info("サンプルデータを作成しました。")
    else:
        df = pd.read_csv(data_path)
    
    df['購入日'] = pd.to_datetime(df['購入日'])
    # 年齢層の計算を追加
    df['年齢層'] = pd.cut(df['年齢'], bins=[0, 20, 30, 40, 50, 60, 100], labels=['20歳未満', '20代', '30代', '40代', '50代', '60歳以上'])
    return df

df = load_data()

# サイドバー - フィルター
st.sidebar.header('フィルター')
min_date = df['購入日'].min()
max_date = df['購入日'].max()
start_date = st.sidebar.date_input('開始日', min_date)
end_date = st.sidebar.date_input('終了日', max_date)

# カテゴリーフィルター
categories = ['すべて'] + list(df['購入カテゴリー'].unique())
selected_category = st.sidebar.selectbox('カテゴリー', categories)

# データのフィルタリング
mask = (df['購入日'].dt.date >= start_date) & (df['購入日'].dt.date <= end_date)
if selected_category != 'すべて':
    mask = mask & (df['購入カテゴリー'] == selected_category)
filtered_df = df[mask]

# メインページを3カラムに分割
col1, col2, col3 = st.columns(3)

# KPI表示
with col1:
    st.metric("総売上", f"¥{filtered_df['購入金額'].sum():,.0f}")
with col2:
    st.metric("平均購入金額", f"¥{filtered_df['購入金額'].mean():,.0f}")
with col3:
    st.metric("購入者数", f"{len(filtered_df):,}人")

# タブで各セクションを分ける
tab1, tab2, tab3 = st.tabs(["基本分析", "顧客分析", "商品分析"])

with tab1:
    # 月別売上推移
    monthly_sales = filtered_df.groupby(filtered_df['購入日'].dt.strftime('%Y-%m'))['購入金額'].sum().reset_index()
    fig_monthly = px.line(monthly_sales, x='購入日', y='購入金額', title='月別売上推移')
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    # カテゴリー別売上
    category_sales = filtered_df.groupby('購入カテゴリー')['購入金額'].sum().reset_index()
    fig_category = px.pie(category_sales, values='購入金額', names='購入カテゴリー', title='カテゴリー別売上構成')
    st.plotly_chart(fig_category, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # 年齢層別分析（計算はすでにload_data内で実行済み）
        age_sales = filtered_df.groupby('年齢層')['購入金額'].mean().reset_index()
        fig_age = px.bar(age_sales, x='年齢層', y='購入金額', title='年齢層別平均購入金額')
        st.plotly_chart(fig_age, use_container_width=True)
    
    with col2:
        # 性別による購買傾向
        gender_sales = filtered_df.groupby('性別')['購入金額'].mean().reset_index()
        fig_gender = px.bar(gender_sales, x='性別', y='購入金額', title='性別別平均購入金額')
        st.plotly_chart(fig_gender, use_container_width=True)
    
    # 地域別の売上分布
    region_sales = filtered_df.groupby('地域')['購入金額'].sum().reset_index()
    fig_region = px.pie(region_sales, values='購入金額', names='地域', title='地域別売上分布')
    st.plotly_chart(fig_region, use_container_width=True)

with tab3:
    st.subheader("商品分析詳細")
    
    # 時間帯別の売上傾向
    filtered_df['時間帯'] = filtered_df['購入日'].dt.hour
    hourly_sales = filtered_df.groupby('時間帯')['購入金額'].sum().reset_index()
    fig_hourly = px.line(hourly_sales, x='時間帯', y='購入金額', 
                        title='時間帯別売上傾向',
                        labels={'時間帯': '時刻（24時間制）', '購入金額': '売上金額'})
    st.plotly_chart(fig_hourly, use_container_width=True)

    # 季節性の分析
    filtered_df['月'] = filtered_df['購入日'].dt.month
    seasonal_sales = filtered_df.groupby('月')['購入金額'].mean().reset_index()
    fig_seasonal = px.line(seasonal_sales, x='月', y='購入金額',
                          title='月別平均売上（季節性分析）',
                          labels={'月': '月', '購入金額': '平均売上金額'})
    fig_seasonal.update_xaxes(ticktext=['1月', '2月', '3月', '4月', '5月', '6月', 
                                      '7月', '8月', '9月', '10月', '11月', '12月'],
                             tickvals=list(range(1, 13)))
    st.plotly_chart(fig_seasonal, use_container_width=True)

    # 価格帯別の販売数分析
    price_bins = [0, 1000, 5000, 10000, 50000, 100000, float('inf')]
    price_labels = ['1,000円未満', '1,000-5,000円', '5,000-10,000円', 
                   '10,000-50,000円', '50,000-100,000円', '100,000円以上']
    filtered_df['価格帯'] = pd.cut(filtered_df['購入金額'], bins=price_bins, labels=price_labels)
    price_range_sales = filtered_df.groupby('価格帯').size().reset_index(name='販売数')
    fig_price_range = px.bar(price_range_sales, x='価格帯', y='販売数',
                            title='価格帯別販売数分布')
    st.plotly_chart(fig_price_range, use_container_width=True)

    # 商品カテゴリーのクロス分析
    st.subheader("カテゴリー間の関連性分析")
    
    # 同じ日時に購入されたカテゴリーの組み合わせを分析
    filtered_df['購入日時'] = filtered_df['購入日'].dt.strftime('%Y-%m-%d %H:00:00')
    category_combinations = filtered_df.groupby('購入日時')['購入カテゴリー'].agg(list).reset_index()
    
    # カテゴリーのペアを作成
    category_pairs = []
    for categories in category_combinations['購入カテゴリー']:
        unique_categories = list(set(categories))  # 重複を除去
        if len(unique_categories) > 1:
            for i in range(len(unique_categories)):
                for j in range(i+1, len(unique_categories)):
                    category_pairs.append(tuple(sorted([unique_categories[i], unique_categories[j]])))
    
    # ペアの出現回数をカウント
    if category_pairs:
        pair_counts = pd.DataFrame(category_pairs, columns=['カテゴリー1', 'カテゴリー2'])
        pair_counts = pair_counts.groupby(['カテゴリー1', 'カテゴリー2']).size().reset_index(name='同時購入回数')
        pair_counts = pair_counts.sort_values('同時購入回数', ascending=False)
        
        # 上位の組み合わせを表示
        st.write("よく同じ時間帯に購入されるカテゴリーの組み合わせ（上位10件）")
        st.dataframe(pair_counts.head(10))
        
        # ヒートマップの作成
        if len(pair_counts) > 1:  # ヒートマップを作成するのに十分なデータがある場合
            heatmap_data = pair_counts.pivot(index='カテゴリー1', columns='カテゴリー2', values='同時購入回数')
            fig_heatmap = px.imshow(heatmap_data,
                                   title='カテゴリー間の同時購入ヒートマップ',
                                   labels=dict(x='カテゴリー2', y='カテゴリー1', color='同時購入回数'))
            st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.write("同時購入データが見つかりませんでした")

# データテーブルの表示（折りたたみ可能）
with st.expander("詳細データを表示"):
    st.dataframe(filtered_df) 