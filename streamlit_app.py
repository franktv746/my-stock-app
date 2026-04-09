import streamlit as st
import yfinance as yf
import twstock
import time
from datetime import datetime, timedelta, timezone

# --- 網頁配置 ---
st.set_page_config(page_title="台股即時監控", layout="centered")

# --- 🚀 自定義 CSS：精確控制字體大小與版面 ---
st.markdown("""
    <style>
    /* 股票卡片容器 */
    .stock-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 6px solid #444;
        line-height: 1.6;
    }
    
    /* 第一行：代號、名稱、市場 */
    .line-1 {
        * font-size: 1.8rem;  與原股價大小一致 */
        font-size: 1rem; /* 與原股價大小一致 */
        font-weight: bold;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .market-tag {
        font-size: 1rem;
        background-color: #444;
        padding: 2px 8px;
        border-radius: 5px;
        color: #BBB;
        vertical-align: middle;
    }
    
    /* 第二行：價格、漲跌 */
    .line-2 {
        /* font-size: 1.8rem; 與原股價大小一致 */
        font-size: 1rem; /* 與原股價大小一致 */
        font-weight: bold;
        font-family: 'Consolas', monospace;
    }
    
    /* 顏色邏輯 */
    .up { color: #FF4D4D; }    /* 台股漲：紅 */
    .down { color: #00FA9A; }  /* 台股跌：綠 */
    .stable { color: #FFFFFF; }
    
    /* 隱藏 Streamlit 預設間距 */
    [data-testid="stVerticalBlock"] > div {
        padding-bottom: 0px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 數據抓取與時間處理 ---
# WATCHLIST = ["2330", "2317", "2454", "8069", "6488", "3131", "2881"]
WATCHLIST = ["3294", "3481", "2634", "6189", "3605", "2834", "2317", "4114", "6122", "2884", "3290", "1519"]

def get_tw_time():
    tw_tz = timezone(timedelta(hours=8))
    return datetime.now(tw_tz).strftime('%Y-%m-%d %H:%M:%S')

@st.cache_data(ttl=55)
def fetch_stock_data(ids):
    results = []
    for s_id in ids:
        if s_id in twstock.twse:
            ticker, market = f"{s_id}.TW", "上市"
        elif s_id in twstock.tpex:
            ticker, market = f"{s_id}.TWO", "上櫃"
        else: continue
        try:
            stock = yf.Ticker(ticker)
            name = twstock.codes.get(s_id).name
            fast = stock.fast_info
            price = fast['last_price']
            prev_close = fast['previous_close']
            change = price - prev_close
            pct = (change / prev_close) * 100
            
            # 決定顏色類別
            color_class = "up" if change > 0 else "down" if change < 0 else "stable"
            symbol = "+" if change > 0 else ""
            
            results.append({
                "id": s_id, "name": name, "market": market,
                "price": price, "change": change, "pct": pct,
                "color": color_class, "symbol": symbol
            })
        except: pass
    return results

# --- 介面呈現 ---
st.title("📈 台股即時監控")
st.caption(f"最後更新：{get_tw_time()} (台灣時間)")

data = fetch_stock_data(WATCHLIST)

if data:
    for s in data:
        # 使用 Markdown 渲染自定義 HTML
        st.markdown(f"""
            <div class="stock-card">
                <div class="line-1">
                    {s['id']} {s['name']} <span class="market-tag">{s['market']}</span>
                </div>
                <div class="line-2 {s['color']}">
                    {s['price']:.2f} &nbsp; {s['symbol']}{s['change']:.2f} ({s['symbol']}{s['pct']:.2f}%)
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.error("暫無數據，請確認交易時間。")

# --- 自動刷新 ---
time.sleep(60)
st.rerun()