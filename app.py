import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ============================================================
# BrG Zone Scanner
# ============================================================

st.set_page_config(
    page_title="BrG Zone Scanner",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 BrG Zone Scanner")
st.caption("Intraday Zone Scanner | NSE Stocks")

# ============================================================
# STOCK LIST
# ============================================================

NSE_STOCKS = [
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "AXISBANK.NS",
    "KOTAKBANK.NS",
    "INFY.NS",
    "TCS.NS",
    "WIPRO.NS",
    "HCLTECH.NS",
    "TECHM.NS",
    "LTIM.NS",
    "RELIANCE.NS",
    "LT.NS",
    "BHARTIARTL.NS",
    "ITC.NS",
    "HINDUNILVR.NS",
    "MARUTI.NS",
    "M&M.NS",
    "TATAMOTORS.NS",
    "TATASTEEL.NS",
    "JSWSTEEL.NS",
    "HINDALCO.NS",
    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "SUNPHARMA.NS",
    "CIPLA.NS",
    "DRREDDY.NS",
    "ONGC.NS",
    "NTPC.NS",
    "POWERGRID.NS",
    "COALINDIA.NS",
    "BEL.NS",
    "HAL.NS",
    "TITAN.NS",
    "ASIANPAINT.NS",
    "ULTRACEMCO.NS",
    "GRASIM.NS",
    "BAJFINANCE.NS",
    "BAJAJFINSV.NS",
    "INDUSINDBK.NS",
    "BANKBARODA.NS",
    "PNB.NS",
    "CANBK.NS",
    "IDFCFIRSTB.NS",
    "FEDERALBNK.NS",
    "DLF.NS",
    "TRENT.NS",
    "ZOMATO.NS"
]

# Remove duplicates
NSE_STOCKS = list(dict.fromkeys(NSE_STOCKS))

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Scanner Settings")

timeframe = st.sidebar.selectbox(
    "Timeframe चुनें",
    ["1 Min", "5 Min", "15 Min", "1 Hour"]
)

# Correct yfinance settings
if timeframe == "1 Min":
    interval = "1m"
    period = "7d"

elif timeframe == "5 Min":
    interval = "5m"
    period = "60d"

elif timeframe == "15 Min":
    interval = "15m"
    period = "60d"

else:
    interval = "60m"
    period = "730d"

# ============================================================
# STOCK SELECTION
# ============================================================

selected_stocks = st.sidebar.multiselect(
    "Stocks चुनें",
    NSE_STOCKS,
    default=NSE_STOCKS[:20]
)

scan_all = st.sidebar.checkbox(
    "सभी उपलब्ध Stocks Scan करें",
    value=False
)

if scan_all:
    stocks_to_scan = NSE_STOCKS
else:
    stocks_to_scan = selected_stocks

# ============================================================
# PARAMETERS
# ============================================================

st.sidebar.subheader("📊 Parameters")

rsi_length = st.sidebar.number_input(
    "RSI Length",
    min_value=2,
    max_value=50,
    value=9
)

ema_length = st.sidebar.number_input(
    "EMA Length",
    min_value=2,
    max_value=100,
    value=20
)

volume_length = st.sidebar.number_input(
    "Volume Average Length",
    min_value=2,
    max_value=100,
    value=20
)

zone_lookback = st.sidebar.number_input(
    "Zone Lookback",
    min_value=5,
    max_value=100,
    value=20
)

# ============================================================
# INDICATOR FUNCTIONS
# ============================================================

def calculate_rsi(series, length=9):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / length,
        min_periods=length,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / length,
        min_periods=length,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_vwap(df):
    typical_price = (
        df["High"] +
        df["Low"] +
        df["Close"]
    ) / 3

    volume = df["Volume"].fillna(0)

    cumulative_volume = volume.cumsum()

    cumulative_pv = (
        typical_price * volume
    ).cumsum()

    vwap = cumulative_pv / cumulative_volume.replace(
        0,
        np.nan
    )

    return vwap


# ============================================================
# DOWNLOAD DATA
# ============================================================

@st.cache_data(ttl=60)
def download_stock_data(symbol, interval, period):

    try:

        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False,
            threads=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # Handle MultiIndex columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        required_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        for col in required_columns:
            if col not in df.columns:
                return pd.DataFrame()

        df = df[required_columns].copy()

        df.dropna(
            subset=["Open", "High", "Low", "Close"],
            inplace=True
        )

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# ZONE DETECTION
# ============================================================

def detect_zone(df):

    if df.empty or len(df) < max(
        zone_lookback,
        ema_length,
        rsi_length
    ) + 5:
        return None

    df = df.copy()

    # --------------------------------------------------------
    # EMA
    # --------------------------------------------------------

    df["EMA"] = df["Close"].ewm(
        span=ema_length,
        adjust=False
    ).mean()

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    df["RSI"] = calculate_rsi(
        df["Close"],
        rsi_length
    )

    # --------------------------------------------------------
    # VWAP
    # --------------------------------------------------------

    df["VWAP"] = calculate_vwap(df)

    # --------------------------------------------------------
    # Volume Average
    # --------------------------------------------------------

    df["Volume_Avg"] = (
        df["Volume"]
        .rolling(volume_length)
        .mean()
    )

    df["Volume_Ratio"] = (
        df["Volume"] /
        df["Volume_Avg"].replace(0, np.nan)
    )

    # --------------------------------------------------------
    # Recent data
    # --------------------------------------------------------

    recent = df.iloc[-1]

    previous = df.iloc[-2]

    close = float(recent["Close"])
    high = float(recent["High"])
    low = float(recent["Low"])

    ema = float(recent["EMA"])
    vwap = float(recent["VWAP"])
    rsi = float(recent["RSI"])

    volume_ratio = float(
        recent["Volume_Ratio"]
    ) if pd.notna(
        recent["Volume_Ratio"]
    ) else 0

    # --------------------------------------------------------
    # Previous candle
    # --------------------------------------------------------

    prev_close = float(previous["Close"])
    prev_high = float(previous["High"])
    prev_low = float(previous["Low"])

    # --------------------------------------------------------
    # Lookback zone
    # --------------------------------------------------------

    lookback_df = df.iloc[
        -zone_lookback:
    ]

    zone_high = float(
        lookback_df["High"].max()
    )

    zone_low = float(
        lookback_df["Low"].min()
    )

    # --------------------------------------------------------
    # Gap calculation
    # --------------------------------------------------------

    first_open = float(df.iloc[0]["Open"])

    latest_close = close

    percent_change = (
        (latest_close - first_open)
        / first_open
    ) * 100 if first_open != 0 else 0

    # --------------------------------------------------------
    # Bullish / Bearish conditions
    # --------------------------------------------------------

    bullish = (
        close > ema and
        close > vwap and
        rsi >= 50
    )

    bearish = (
        close < ema and
        close < vwap and
        rsi < 50
    )

    # --------------------------------------------------------
    # Breakout
    # --------------------------------------------------------

    bullish_breakout = (
        close > zone_high
    )

    bearish_breakdown = (
        close < zone_low
    )

    # --------------------------------------------------------
    # Zone
    # --------------------------------------------------------

    if bullish_breakout:
        zone_type = "🟢 Bullish Breakout"
        zone_price = zone_high
        signal = "BUY"

    elif bearish_breakdown:
        zone_type = "🔴 Bearish Breakdown"
        zone_price = zone_low
        signal = "SELL"

    elif bullish:
        zone_type = "🟢 Bullish Zone"
        zone_price = zone_low
        signal = "WATCH BUY"

    elif bearish:
        zone_type = "🔴 Bearish Zone"
        zone_price = zone_high
        signal = "WATCH SELL"

    else:
        zone_type = "⚪ Neutral"
        zone_price = close
        signal = "WAIT"

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    score = 0

    if close > ema:
        score += 20

    if close > vwap:
        score += 20

    if rsi >= 50:
        score += 20

    if volume_ratio >= 1:
        score += 20

    if bullish_breakout:
        score += 20

    if close < ema:
        score -= 20

    if close < vwap:
        score -= 20

    if rsi < 50:
        score -= 20

    if bearish_breakdown:
        score -= 20

    score = max(
        -100,
        min(100, score)
    )

    # --------------------------------------------------------
    # Zone width
    # --------------------------------------------------------

    zone_width = zone_high - zone_low

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "Stock": symbol.replace(".NS", ""),
        "Timeframe": timeframe,
        "Signal": signal,
        "Zone": zone_type,
        "Close": round(close, 2),
        "Zone Low": round(zone_low, 2),
        "Zone High": round(zone_high, 2),
        "EMA": round(ema, 2),
        "VWAP": round(vwap, 2),
        "RSI(9)": round(rsi, 2),
        "Volume Ratio": round(volume_ratio, 2),
        "% Change": round(percent_change, 2),
        "Score": score
    }


# ============================================================
# SCAN BUTTON
# ============================================================

st.subheader(
    f"📡 Current Timeframe: {timeframe}"
)

st.info(
    f"Data Source: Yahoo Finance | "
    f"Interval: {interval} | "
    f"Period: {period}"
)

scan_button = st.button(
    "🔎 Scan Zones",
    type="primary",
    use_container_width=True
)

# ============================================================
# SCANNER
# ============================================================

if scan_button:

    if not stocks_to_scan:

        st.warning(
            "कृपया कम से कम एक Stock चुनें।"
        )

    else:

        results = []

        progress = st.progress(0)

        status = st.empty()

        total = len(stocks_to_scan)

        for i, symbol in enumerate(
            stocks_to_scan
        ):

            status.text(
                f"Scanning {symbol.replace('.NS', '')} "
                f"({i + 1}/{total})..."
            )

            df = download_stock_data(
                symbol,
                interval,
                period
            )

            if not df.empty:

                result = detect_zone(df)

                if result is not None:
                    results.append(result)

            progress.progress(
                int(
                    ((i + 1) / total) * 100
                )
            )

        progress.empty()
        status.empty()

        # ====================================================
        # RESULTS
        # ====================================================

        if not results:

            st.error(
                "कोई valid market data नहीं मिला। "
                "कृपया थोड़ी देर बाद फिर Scan करें।"
            )

        else:

            result_df = pd.DataFrame(
                results
            )

            # Sort by absolute score
            result_df["SortScore"] = (
                result_df["Score"].abs()
            )

            result_df.sort_values(
                "SortScore",
                ascending=False,
                inplace=True
            )

            result_df.drop(
                columns=["SortScore"],
                inplace=True
            )

            # =================================================
            # TOP STOCKS
            # =================================================

            st.subheader(
                "🏆 Top BrG Zones"
            )

            top_results = result_df[
                result_df["Signal"].isin(
                    [
                        "BUY",
                        "SELL",
                        "WATCH BUY",
                        "WATCH SELL"
                    ]
                )
            ].head(5)

            if not top_results.empty:

                for _, row in top_results.iterrows():

                    signal = row["Signal"]

                    if signal == "BUY":
                        st.success(
                            f"🟢 {row['Stock']} | "
                            f"{row['Zone']} | "
                            f"Score: {row['Score']}"
                        )

                    elif signal == "SELL":
                        st.error(
                            f"🔴 {row['Stock']} | "
                            f"{row['Zone']} | "
                            f"Score: {row['Score']}"
                        )

                    else:
                        st.info(
                            f"👀 {row['Stock']} | "
                            f"{row['Zone']} | "
                            f"Score: {row['Score']}"
                        )

            # =================================================
            # FULL TABLE
            # =================================================

            st.subheader(
                "📋 Scanner Results"
            )

            st.dataframe(
                result_df,
                use_container_width=True,
                hide_index=True
            )

            # =================================================
            # FILTERED ZONES
            # =================================================

            st.subheader(
                "🎯 Active Zones"
            )

            active_zones = result_df[
                result_df["Signal"].isin(
                    [
                        "BUY",
                        "SELL"
                    ]
                )
            ].copy()

            if active_zones.empty:

                st.warning(
                    "इस scan में कोई strong active BUY/SELL zone नहीं मिला।"
                )

            else:

                st.dataframe(
                    active_zones,
                    use_container_width=True,
                    hide_index=True
                )

            # =================================================
            # SUMMARY
            # =================================================

            st.subheader(
                "📊 Scan Summary"
            )

            col1, col2, col3, col4 = st.columns(4)

            buy_count = len(
                result_df[
                    result_df["Signal"] == "BUY"
                ]
            )

            sell_count = len(
                result_df[
                    result_df["Signal"] == "SELL"
                ]
            )

            watch_count = len(
                result_df[
                    result_df["Signal"].isin(
                        [
                            "WATCH BUY",
                            "WATCH SELL"
                        ]
                    )
                ]
            )

            col1.metric(
                "Total Stocks",
                len(result_df)
            )

            col2.metric(
                "🟢 BUY",
                buy_count
            )

            col3.metric(
                "🔴 SELL",
                sell_count
            )

            col4.metric(
                "👀 WATCH",
                watch_count
            )

            st.success(
                "Scan completed successfully."
            )

else:

    st.write(
        "ऊपर **🔎 Scan Zones** दबाकर "
        "चयनित Stocks का scan शुरू करें।"
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "BrG Zone Scanner | "
    "For analysis and educational use only."
)
