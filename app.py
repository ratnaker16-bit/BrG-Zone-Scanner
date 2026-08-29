import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import pytz
import time

# ============================================================
# SUMAN INTRADAY STOCK SCREENER V2.0
# ============================================================
# 9:19 AM DAILY SECTOR HEATMAP SCANNER
#
# DAILY % CHANGE:
# Previous Trading Day Close -> Current LTP
#
# OUTPUT:
# 1. Top Gainer Sector
# 2. Top 3 Gainer F&O Stocks
# 3. Top Loser Sector
# 4. Top 3 Loser F&O Stocks
#
# INDICATORS:
# LTP
# Daily % Change
# VWAP
# EMA20
# RSI(9)
# Volume
# Volume Ratio
# Signal
#
# NO SUPPLY / DEMAND ZONES
# NO BOXES
# NO LIQUIDITY ZONES
# ============================================================


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Suman Intraday Screener",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Suman Intraday Stock Screener")
st.caption(
    "9:19 AM Sector Heatmap → F&O Top Gainers / Top Losers"
)


# ============================================================
# TIMEZONE
# ============================================================

INDIA_TZ = pytz.timezone("Asia/Kolkata")

now = datetime.now(INDIA_TZ)

current_time = now.strftime("%H:%M:%S")

market_date = now.strftime("%d-%m-%Y")


# ============================================================
# SCAN TIME
# ============================================================

SCAN_HOUR = 9
SCAN_MINUTE = 19


def is_scan_time():

    return (
        now.hour > SCAN_HOUR
        or
        (
            now.hour == SCAN_HOUR
            and now.minute >= SCAN_MINUTE
        )
    )


# ============================================================
# SECTOR STOCK LIST
# ============================================================
# F&O-focused NSE stock universe
# ============================================================

SECTORS = {

    "NIFTY BANK": [
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "AXISBANK.NS",
        "KOTAKBANK.NS",
        "INDUSINDBK.NS",
        "BANKBARODA.NS",
        "PNB.NS"
    ],

    "NIFTY IT": [
        "TCS.NS",
        "INFY.NS",
        "HCLTECH.NS",
        "WIPRO.NS",
        "TECHM.NS",
        "LTIM.NS",
        "MPHASIS.NS",
        "PERSISTENT.NS"
    ],

    "NIFTY AUTO": [
        "MARUTI.NS",
        "M&M.NS",
        "TATAMOTORS.NS",
        "EICHERMOT.NS",
        "HEROMOTOCO.NS",
        "BAJAJ-AUTO.NS",
        "TVSMOTOR.NS",
        "ASHOKLEY.NS"
    ],

    "NIFTY PHARMA": [
        "SUNPHARMA.NS",
        "DRREDDY.NS",
        "CIPLA.NS",
        "DIVISLAB.NS",
        "APOLLOHOSP.NS",
        "LUPIN.NS",
        "AUROPHARMA.NS",
        "BIOCON.NS"
    ],

    "NIFTY FMCG": [
        "HINDUNILVR.NS",
        "ITC.NS",
        "NESTLEIND.NS",
        "BRITANNIA.NS",
        "TATACONSUM.NS",
        "DABUR.NS",
        "MARICO.NS",
        "COLPAL.NS"
    ],

    "NIFTY METAL": [
        "TATASTEEL.NS",
        "HINDALCO.NS",
        "JSWSTEEL.NS",
        "COALINDIA.NS",
        "VEDL.NS",
        "JINDALSTEL.NS",
        "NMDC.NS",
        "SAIL.NS"
    ],

    "NIFTY ENERGY": [
        "RELIANCE.NS",
        "NTPC.NS",
        "POWERGRID.NS",
        "ONGC.NS",
        "BPCL.NS",
        "IOC.NS",
        "GAIL.NS",
        "ADANIGREEN.NS"
    ],

    "NIFTY REALTY": [
        "DLF.NS",
        "LODHA.NS",
        "GODREJPROP.NS",
        "OBEROIRLTY.NS",
        "PRESTIGE.NS",
        "PHOENIXLTD.NS"
    ]
}


# ============================================================
# RSI FUNCTION
# ============================================================

def calculate_rsi(series, period=9):

    delta = series.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi


# ============================================================
# STOCK ANALYSIS
# ============================================================

def analyze_stock(symbol):

    try:

        # ----------------------------------------------------
        # INTRADAY DATA
        # ----------------------------------------------------

        data = yf.download(
            symbol,
            period="2d",
            interval="5m",
            progress=False,
            auto_adjust=False,
            threads=False
        )

        if data is None or data.empty:
            return None

        # ----------------------------------------------------
        # REMOVE MULTI INDEX
        # ----------------------------------------------------

        if isinstance(
            data.columns,
            pd.MultiIndex
        ):

            data.columns = (
                data.columns
                .get_level_values(0)
            )

        required = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        for col in required:

            if col not in data.columns:
                return None

        data = data.dropna()

        if len(data) < 25:
            return None

        close = data["Close"]

        high = data["High"]

        low = data["Low"]

        volume = data["Volume"]


        # ====================================================
        # CURRENT LTP
        # ====================================================

        ltp = float(
            close.iloc[-1]
        )


        # ====================================================
        # PREVIOUS TRADING DAY CLOSE
        # ====================================================

        daily_data = yf.download(
            symbol,
            period="10d",
            interval="1d",
            progress=False,
            auto_adjust=False,
            threads=False
        )

        if (
            daily_data is None
            or daily_data.empty
        ):
            return None


        if isinstance(
            daily_data.columns,
            pd.MultiIndex
        ):

            daily_data.columns = (
                daily_data.columns
                .get_level_values(0)
            )


        if "Close" not in daily_data.columns:
            return None


        daily_close = (
            daily_data["Close"]
            .dropna()
        )


        if len(daily_close) < 2:
            return None


        # Last completed daily candle
        previous_close = float(
            daily_close.iloc[-2]
        )


        if previous_close <= 0:
            return None


        # ====================================================
        # DAILY % CHANGE
        # ====================================================
        # Previous Trading Day Close -> Current LTP
        # ====================================================

        change_pct = (
            (
                ltp - previous_close
            )
            / previous_close
        ) * 100


        # ====================================================
        # VWAP
        # ====================================================

        typical_price = (
            high + low + close
        ) / 3


        cumulative_volume = (
            volume.cumsum()
        )


        cumulative_pv = (
            typical_price * volume
        ).cumsum()


        vwap_series = (
            cumulative_pv
            /
            cumulative_volume.replace(
                0,
                np.nan
            )
        )


        vwap = float(
            vwap_series.iloc[-1]
        )


        # ====================================================
        # EMA 20
        # ====================================================

        ema20 = float(
            close.ewm(
                span=20,
                adjust=False
            ).mean().iloc[-1]
        )


        # ====================================================
        # RSI 9
        # ====================================================

        rsi_series = calculate_rsi(
            close,
            9
        )


        rsi9 = float(
            rsi_series.iloc[-1]
        )


        # ====================================================
        # CURRENT VOLUME
        # ====================================================

        current_volume = float(
            volume.iloc[-1]
        )


        # ====================================================
        # AVERAGE VOLUME
        # ====================================================

        if len(volume) >= 21:

            avg_volume = float(
                volume.iloc[-21:-1].mean()
            )

        else:

            avg_volume = float(
                volume.iloc[:-1].mean()
            )


        if avg_volume > 0:

            volume_ratio = (
                current_volume
                / avg_volume
            )

        else:

            volume_ratio = 0


        # ====================================================
        # VWAP STATUS
        # ====================================================

        if ltp > vwap:

            vwap_status = "Above"

        elif ltp < vwap:

            vwap_status = "Below"

        else:

            vwap_status = "At VWAP"


        # ====================================================
        # SIGNAL
        # ====================================================

        if (
            ltp > vwap
            and
            ltp > ema20
            and
            rsi9 > 55
        ):

            signal = "🟢 BULLISH"

        elif (
            ltp < vwap
            and
            ltp < ema20
            and
            rsi9 < 45
        ):

            signal = "🔴 BEARISH"

        else:

            signal = "⚪ WAIT"


        # ====================================================
        # RESULT
        # ====================================================

        return {

            "Symbol":
                symbol.replace(
                    ".NS",
                    ""
                ),

            "LTP":
                round(
                    ltp,
                    2
                ),

            "% Change":
                round(
                    change_pct,
                    2
                ),

            "Prev Close":
                round(
                    previous_close,
                    2
                ),

            "VWAP":
                round(
                    vwap,
                    2
                ),

            "VWAP Status":
                vwap_status,

            "EMA20":
                round(
                    ema20,
                    2
                ),

            "RSI(9)":
                round(
                    rsi9,
                    2
                ),

            "Volume":
                int(
                    current_volume
                ),

            "Volume x":
                round(
                    volume_ratio,
                    2
                ),

            "Signal":
                signal
        }


    except Exception:

        return None


# ============================================================
# SECTOR ANALYSIS
# ============================================================

def analyze_sector(
    sector,
    stocks,
    progress_bar=None,
    current_count=0,
    total_count=1
):

    results = []

    for stock in stocks:

        result = analyze_stock(
            stock
        )

        if result is not None:

            results.append(
                result
            )

        if progress_bar is not None:

            current_count += 1

            progress_bar.progress(
                min(
                    current_count
                    / total_count,
                    1.0
                )
            )


    if not results:

        return None, None


    df = pd.DataFrame(
        results
    )


    # ========================================================
    # SECTOR DAILY PERFORMANCE
    # ========================================================

    sector_change = float(
        df["% Change"].mean()
    )


    return (
        sector_change,
        df
    )


# ============================================================
# MAIN SCANNER
# ============================================================

def run_scanner():

    all_sector_data = {}

    total_stocks = sum(
        len(stocks)
        for stocks in SECTORS.values()
    )

    progress = st.progress(
        0
    )

    scanned = 0


    for sector, stocks in SECTORS.items():

        results = []

        for stock in stocks:

            result = analyze_stock(
                stock
            )

            scanned += 1

            progress.progress(
                min(
                    scanned
                    / total_stocks,
                    1.0
                )
            )


            if result is not None:

                results.append(
                    result
                )


        if results:

            stock_df = pd.DataFrame(
                results
            )


            sector_change = float(
                stock_df[
                    "% Change"
                ].mean()
            )


            all_sector_data[
                sector
            ] = {

                "change":
                    sector_change,

                "stocks":
                    stock_df
            }


    progress.empty()

    return all_sector_data


# ============================================================
# MARKET TIME DISPLAY
# ============================================================

st.info(
    f"🇮🇳 Indian Market Time: "
    f"{market_date} {current_time}"
)


# ============================================================
# MARKET STATUS
# ============================================================

if not is_scan_time():

    st.warning(
        "⏳ Scanner 9:19 AM के बाद "
        "Daily Market Scan करेगा।"
    )

    st.write(
        "9:19 AM के बाद app को refresh "
        "करें। Scanner automatic scan करेगा।"
    )


# ============================================================
# AUTOMATIC 9:19 SCAN
# ============================================================

auto_scan = False


if is_scan_time():

    last_scan_date = st.session_state.get(
        "last_scan_date",
        None
    )


    today_string = now.strftime(
        "%Y-%m-%d"
    )


    if last_scan_date != today_string:

        auto_scan = True


# ============================================================
# MANUAL SCAN
# ============================================================

manual_scan = st.button(
    "🔎 SCAN NOW",
    use_container_width=True
)


# ============================================================
# RUN SCANNER
# ============================================================

if auto_scan or manual_scan:

    with st.spinner(
        "📊 Scanning F&O stocks and sectors..."
    ):

        sector_data = run_scanner()


    if auto_scan:

        st.session_state[
            "last_scan_date"
        ] = now.strftime(
            "%Y-%m-%d"
        )


    if not sector_data:

        st.error(
            "❌ Market data उपलब्ध नहीं है। "
            "थोड़ी देर बाद फिर Scan करें।"
        )


    else:

        # ====================================================
        # SECTOR RANKING
        # ====================================================

        sector_rows = []


        for sector, info in sector_data.items():

            sector_rows.append({

                "Sector":
                    sector,

                "% Change":
                    round(
                        info["change"],
                        2
                    )
            })


        sector_df = pd.DataFrame(
            sector_rows
        )


        sector_df = (
            sector_df
            .sort_values(
                "% Change",
                ascending=False
            )
            .reset_index(
                drop=True
            )
        )


        # ====================================================
        # TOP GAINER SECTOR
        # ====================================================

        top_gainer_sector = (
            sector_df.iloc[0]["Sector"]
        )


        top_gainer_change = (
            sector_df.iloc[0]["% Change"]
        )


        # ====================================================
        # TOP LOSER SECTOR
        # ====================================================

        top_loser_sector = (
            sector_df.iloc[-1]["Sector"]
        )


        top_loser_change = (
            sector_df.iloc[-1]["% Change"]
        )


        # ====================================================
        # SECTOR HEATMAP
        # ====================================================

        st.subheader(
            "🔥 Sector Heatmap"
        )


        st.dataframe(
            sector_df,
            use_container_width=True,
            hide_index=True
        )


        # ====================================================
        # TOP GAINER SECTOR
        # ====================================================

        st.subheader(
            f"🟢 TOP GAINER SECTOR: "
            f"{top_gainer_sector} "
            f"({top_gainer_change:+.2f}%)"
        )


        gainer_df = (
            sector_data[
                top_gainer_sector
            ]["stocks"]
            .copy()
        )


        gainer_df = (
            gainer_df
            .sort_values(
                "% Change",
                ascending=False
            )
            .head(3)
            .reset_index(
                drop=True
            )
        )


        st.dataframe(
            gainer_df,
            use_container_width=True,
            hide_index=True
        )


        # ====================================================
        # TOP LOSER SECTOR
        # ====================================================

        st.subheader(
            f"🔴 TOP LOSER SECTOR: "
            f"{top_loser_sector} "
            f"({top_loser_change:+.2f}%)"
        )


        loser_df = (
            sector_data[
                top_loser_sector
            ]["stocks"]
            .copy()
        )


        loser_df = (
            loser_df
            .sort_values(
                "% Change",
                ascending=True
            )
            .head(3)
            .reset_index(
                drop=True
            )
        )


        st.dataframe(
            loser_df,
            use_container_width=True,
            hide_index=True
        )


        # ====================================================
        # SCAN TIME
        # ====================================================

        scan_timestamp = datetime.now(
            INDIA_TZ
        ).strftime(
            "%H:%M:%S"
        )


        st.success(
            f"✅ Scan Complete at "
            f"{scan_timestamp} IST"
        )


        st.caption(
            "Daily % Change = "
            "Previous Trading Day Close → Current LTP"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Suman Intraday Stock Screener V2.0 | "
    "9:19 AM Sector Heatmap | "
    "F&O Stocks | "
    "Daily % Change + VWAP + EMA20 + RSI(9)"
)
