import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import time
from datetime import datetime, timedelta, timezone

# --- 1. 時間處理函數 ---
def get_tw_time():
    # 建立 UTC+8 時區物件
    tw_tz = timezone(timedelta(hours=8))
    return datetime.now(tw_tz).strftime('%H:%M:%S')

# --- 網頁配置 ---
st.set_page_config(page_title="我的台股監控", page_icon="📈")

# 自定義 CSS 讓手機版顯示更精緻
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
    .stMetric { background-color: #262730; padding: 15px; border-radius: 10px; border-left: 5px solid #444; }
    </style>
""", unsafe_allow_html=True)

# 1. 你的自選股名單 (只需輸入代號)
# WATCHLIST = ["2330", "2317", "2454", "8069", "6488", "3131", "2881"]
WATCHLIST = ["3294", "3481", "2634", "6189", "3605", "2834", "2317", "4114", "6122", "2884", "3290", "1519"]



@st.cache_data(ttl=55) # 快取 55 秒，避免過度請求
def fetch_stock_data(ids):
    results = []
    for s_id in ids:
        # 自動判斷市場字尾
        if s_id in twstock.twse:
            ticker, market = f"{s_id}.TW", "上市"
        elif s_id in twstock.tpex:
            ticker, market = f"{s_id}.TWO", "上櫃"
        else:
            continue
            
        try:
            stock = yf.Ticker(ticker)
            info = twstock.codes.get(s_id)
            fast = stock.fast_info
            
            price = fast['last_price']
            prev_close = fast['previous_close']
            change = price - prev_close
            pct = (change / prev_close) * 100
            
            results.append({
                "id": s_id,
                "name": info.name,
                "market": market,
                "price": price,
                "change": change,
                "pct": pct
            })
        except:
            pass
    return results

# --- 介面呈現 ---
# --- 3. 介面呈現 ---
st.title("📈 台股即時監控")
# 使用剛剛定義的台灣時間
st.caption(f"伺服器位置：雲端中心 | 最後更新時間：{get_tw_time()} (台灣時間)")


# st.title("📈 台股即時監控")
# st.caption(f"數據每分鐘自動更新 | 最後更新：{time.strftime('%H:%M:%S')}")

data = fetch_stock_data(WATCHLIST)

# 使用 columns 進行排版 (手機上會自動堆疊)
if data:
    cols = st.columns(2)
    for i, s in enumerate(data):
        with cols[i % 2]:
            # 💡 這裡有個小眉角：st.metric 的 delta_color="normal" 是「綠漲紅跌」(美股模式)
            # 在台灣我們需要手動判斷或反轉
            label_text = f"{s['name']} ({s['id']}) {s['market']}"
            
            # 判斷漲跌
            if s['change'] > 0:
                d_color = "inverse"  # 漲 -> 顯示紅色
            elif s['change'] < 0:
                d_color = "inverse"  # 跌 -> 顯示綠色
            else:
                d_color = "off"      # 平盤 -> 顯示灰色
                
            st.metric(
                label=label_text,
                value=f"{s['price']:.2f}",
                delta=f"{s['change']:+.2f} ({s['pct']:+.2f}%)",
                delta_color=d_color
            )
else:
    st.error("暫無數據，請確認代號或交易時間。")

# --- 自動刷新邏輯 ---
# 這是 Streamlit 的黑科技，讓網頁在倒數後自動重跑
time.sleep(60)
st.rerun()