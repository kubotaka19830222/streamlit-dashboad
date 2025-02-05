import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ページ設定
st.set_page_config(page_title="販売データ分析ダッシュボード", layout="wide")
st.title("販売データ分析ダッシュボード")

# データ読み込み
@st.cache_data
def load_data():
    df = pd.read_csv('data/sample-data.csv')
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
    # カテゴリー別の詳細分析
    category_details = filtered_df.groupby(['購入カテゴリー', '支払方法'])['購入金額'].sum().reset_index()
    fig_category_details = px.bar(category_details, x='購入カテゴリー', y='購入金額', color='支払方法', title='カテゴリー別・支払方法別売上')
    st.plotly_chart(fig_category_details, use_container_width=True)
    
    # 支払方法の分布
    payment_dist = filtered_df['支払方法'].value_counts()
    fig_payment = px.pie(values=payment_dist.values, names=payment_dist.index, title='支払方法の分布')
    st.plotly_chart(fig_payment, use_container_width=True)

# データテーブルの表示（折りたたみ可能）
with st.expander("詳細データを表示"):
    st.dataframe(filtered_df) 