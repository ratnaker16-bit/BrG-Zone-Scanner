import streamlit as st
import pandas as pd
import yfinance as yf

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title="Institutional D&S Zone Scanner",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Institutional D&S Zone Scanner")
st.caption("Advanced Supply & Demand Zone Scanner | Smart Money Concepts")

# ============================================================
# NSE STOCKS LIST
# ============================================================
NSE_STOCKS = {
    "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS", "SBIN": "SBIN.NS",
    "AXISBANK": "AXISBANK.NS", "KOTAKBANK": "KOTAKBANK.NS", "LT": "LT.NS",
    "BHARTIARTL": "BHARTIARTL.NS", "ITC": "ITC.NS", "HINDUNILVR": "HINDUNILVR.NS",
    "MARUTI": "MARUTI.NS", "M&M": "M&M.NS", "TATAMOTORS": "TATAMOTORS.NS",
    "TATASTEEL": "TATASTEEL.NS", "HINDALCO": "HINDALCO.NS", "ADANIENT": "ADANIENT.NS",
    "ADANIPORTS": "ADANIPORTS.NS", "SUNPHARMA": "SUNPHARMA.NS", "BAJFINANCE": "BAJFINANCE.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS", "WIPRO": "WIPRO.NS", "HCLTECH": "HCLTECH.NS",
    "TECHM": "TECHM.NS", "COALINDIA": "COALINDIA.NS", "ONGC": "ONGC.NS",
    "NTPC": "NTPC.NS", "POWERGRID": "POWERGRID.NS", "JSWSTEEL": "JSWSTEEL.NS",
    "TATACONSUM": "TATACONSUM.NS", "TITAN": "TITAN.NS", "ULTRACEMCO": "ULTRACEMCO.NS",
    "ASIANPAINT": "ASIANPAINT.NS", "EICHERMOT": "EICHERMOT.NS", "HEROMOTOCO": "HEROMOTOCO.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS", "DRREDDY": "DRREDDY.NS", "CIPLA": "CIPLA.NS",
    "DIVISLAB": "DIVISLAB.NS", "APOLLOHOSP": "APOLLOHOSP.NS", "BEL": "BEL.NS",
    "HAL": "HAL.NS", "TRENT": "TRENT.NS", "INDUSINDBK": "INDUSINDBK.NS",
    "BANKBARODA": "BANKBARODA.NS", "PNB": "PNB.NS", "CANBK": "CANBK.NS",
    "IDFCFIRSTB": "IDFCFIRSTB.NS", "IOC": "IOC.NS", "BPCL": "BPCL.NS",
    "GAIL": "GAIL.NS", "VEDL": "VEDL.NS", "JINDALSTEL": "JINDALSTEL.NS",
    "SAIL": "SAIL.NS", "INDHOTEL": "INDHOTEL.NS", "DLF": "DLF.NS",
    "IRCTC": "IRCTC.NS", "ZOMATO": "ZOMATO.NS", "UPL": "UPL.NS", "RECLTD": "RECLTD.NS", "HDFCAMC": "HDFCAMC.NS"
}

# ============================================================
# DATA FETCHING & TIMEFRAME HANDLING
# ============================================================
def fetch_data(symbol, timeframe):
    if timeframe == "1 Minute":
        interval, period = "1m", "7d"
    elif timeframe == "5 Minutes":
        interval, period = "5m", "59d"
    elif timeframe == "15 Minutes":
        interval, period = "15m", "59d"
    elif timeframe == "1 Hour":
        interval, period = "1h", "730d"
    elif timeframe == "4 Hours":
        # Yahoo Finance सीधे 4h नहीं देता, इसलिए 1h डेटा को रीसेंपल (Resample) करेंगे
        interval, period = "1h", "730d"
    elif timeframe == "Daily":
        interval, period = "1d", "max"
    else:
        interval, period = "1d", "max"

    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # यदि टाइमफ्रेम 4 Hours है, तो 1-hour डेटा को 4 घंटे में बदलें
        if timeframe == "4 Hours":
            df = df.resample('4h').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()

        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in df.columns for col in required_cols):
            return pd.DataFrame()

        return df[required_cols].dropna()
    except Exception:
        return pd.DataFrame()

# ============================================================
# ZONE IDENTIFICATION & STATUS (Fresh/Tested/HQ)
# ============================================================
def identify_zones(df, symbol, timeframe):
    zones = []
    if len(df) < 10:
        return zones

    for i in range(2, len(df) - 2):
        prev_open = float(df["Open"].iloc[i - 1])
        prev_close = float(df["Close"].iloc[i - 1])

        base_open = float(df["Open"].iloc[i])
        base_close = float(df["Close"].iloc[i])
        base_high = float(df["High"].iloc[i])
        base_low = float(df["Low"].iloc[i])

        base_body = abs(base_close - base_open)
        base_range = base_high - base_low

        if base_range <= 0 or (base_body / base_range) > 0.40:
            continue

        next_open = float(df["Open"].iloc[i + 1])
        next_close = float(df["Close"].iloc[i + 1])
        next_high = float(df["High"].iloc[i + 1])
        next_low = float(df["Low"].iloc[i + 1])

        next_body = abs(next_close - next_open)
        next_range = next_high - next_low

        if next_range <= 0 or (next_body / next_range) < 0.60:
            continue

        zone_type = None
        # Demand (Drop -> Base -> Rally)
        if prev_close < prev_open and next_close > next_open:
            zone_type = "DEMAND"
        # Supply (Rally -> Base -> Drop)
        elif prev_close > prev_open and next_close < next_open:
            zone_type = "SUPPLY"

        if zone_type:
            z_high = round(base_high, 2)
            z_low = round(base_low, 2)
            
            # चेक करें कि ज़ोन बनने के बाद कीमत दोबारा उस ज़ोन में आई या नहीं (Fresh vs Tested)
            is_tested = False
            for j in range(i + 2, len(df)):
                curr_l = df["Low"].iloc[j]
                curr_h = df["High"].iloc[j]
                if zone_type == "DEMAND" and curr_l <= z_high:
                    is_tested = True
                    break
                elif zone_type == "SUPPLY" and curr_h >= z_low:
                    is_tested = True
                    break

            status = "Tested" if is_tested else "Fresh"
            
            # High Quality (HQ) निर्धारण: अगर वॉल्यूम मजबूत है या बड़ा डिपार्चर है
            is_hq = next_body > (base_range * 1.5)
            hq_label = "★ HQ" if is_hq else "Standard"

            # ट्रेडिंगव्यू का डायरेक्ट चार्ट लिंक फॉर्मेट
            clean_symbol = symbol.replace(".NS", "")
            tv_link = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_symbol}"

            zones.append({
                "एसेट": clean_symbol,
                "चार्ट खोलें": tv_link,
                "टाइमफ्रेम": timeframe,
                "दिशा": f"🟢 DEMAND" if zone_type == "DEMAND" else f"🔴 SUPPLY",
                "पैटर्न": "Drop-Base-Rally" if zone_type == "DEMAND" else "Rally-Base-Drop",
                "ज़ोन हाई": z_high,
                "ज़ोन लो": z_low,
                "स्थिति": status,
                "क्वालिटी": hq_label,
                "समय": str(df.index[i])
            })

    return zones

# ============================================================
# SIDEBAR CONTROLS
# ============================================================
st.sidebar.header("⚙️ Scanner Settings")

selected_stocks = st.sidebar.multiselect(
    "शेयर चुनें (NSE Stocks)",
    list(NSE_STOCKS.keys()),
    default=["RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "TATASTEEL", "UPL", "RECLTD", "HDFCAMC"]
)

timeframe = st.sidebar.selectbox(
    "टाइमफ्रेम चुनें",
    ["1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "4 Hours", "Daily"],
    index=3
)

# ============================================================
# MAIN SCANNER EXECUTION
# ============================================================
if st.button("🚀 स्कैन शुरू करें", use_container_width=True):
    if not selected_stocks:
        st.warning("⚠️ कृपया कम से कम एक शेयर चुनें।")
    else:
        all_zones = []
        progress_bar = st.progress(0)
        total_stocks = len(selected_stocks)

        with st.spinner(f"स्कैनिंग जारी है ({timeframe})..."):
            for idx, stock_name in enumerate(selected_stocks):
                symbol_code = NSE_STOCKS[stock_name]
                df = fetch_data(symbol_code, timeframe)
                if not df.empty:
                    stock_zones = identify_zones(df, symbol_code, timeframe)
                    all_zones.extend(stock_zones)
                progress_bar.progress(int(((idx + 1) / total_stocks) * 100))

        progress_bar.empty()

        if all_zones:
            res_df = pd.DataFrame(all_zones)
            
            # डैशबोर्ड मैट्रिक्स कैलकुलेशन
            total_zones_count = len(res_df)
            fresh_count = len(res_df[res_df["स्थिति"] == "Fresh"])
            tested_count = len(res_df[res_df["स्थिति"] == "Tested"])
            hq_count = len(res_df[res_df["क्वालिटी"] == "★ HQ"])

            # स्क्रीनशॉट जैसा टॉप डैशबोर्ड बॉक्स
            st.markdown(
                f"""
                <div style="background-color: #0f172a; padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;">
                    <p style="margin: 0; font-size: 16px;">📦 कुल Zones: <b>{total_zones_count}</b> &nbsp;&nbsp;|&nbsp;&nbsp; 🟢 Fresh: <b>{fresh_count}</b> &nbsp;&nbsp;|&nbsp;&nbsp; 🟡 Tested: <b>{tested_count}</b> &nbsp;&nbsp;|&nbsp;&nbsp; ⭐ HQ: <b>{hq_count}</b></p>
                </div>
                """, 
                unsafe_allow_html=True
            )

            st.success(f"सफलतापूर्वक स्कैन पूरा हुआ! कुल {total_zones_count} ज़ोन मिले।")

            # डेटा टेबल दिखाना (TradingView लिंक्स को क्लिकेबल बनाने के लिए st.data_editor या st.dataframe का उपयोग)
            st.dataframe(
                res_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "चार्ट खोलें": st.column_config.LinkColumn(
                        "📊 चार्ट खोलें",
                        help="क्लिक करके ट्रेडिंगव्यू पर चार्ट देखें",
                        validate="^https://.*",
                        display_text="📈 Open"
                    )
                }
            )
        else:
            st.warning("⚠️ चुने गए शेयरों और टाइमफ्रेम पर कोई ज़ोन नहीं मिला। कृपया दूसरा टाइमफ्रेम या शेयर आज़माएं।")

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("Institutional D&S Zone Scanner | Custom Multi-Timeframe Build")
