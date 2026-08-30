import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import pytz

# ============================================================
# SUMAN INTRADAY STOCK SCREENER V3.0
# ============================================================
# 9:20 AM FIRST 5-MINUTE CANDLE SECTOR SCANNER
#
# LOGIC:
#
# 1. Sector Heatmap
#    Previous Trading Day Close -> Current Market Price
#
# 2. TOP GAINER SECTOR
#    - First 5M candle = GREEN
#    - 9:15 Open -> 9:20 Close
#    - Previous Close से +4% से अधिक नहीं
#    - Top 3 strongest stocks
#
# 3. TOP LOSER SECTOR
#    - First 5M candle = RED
#    - 9:15 Open -> 9:20 Close
#    - Previous Close से -4% से अधिक नहीं
#    - Top 3 weakest stocks
#
# INDICATORS:
# LTP
# Daily % Change
# First 5M Open
# First 5M Close
# First 5M %
# VWAP
# EMA20
# RSI(9)
# Volume
# Volume Ratio
# Signal
#
# NO SUPPLY / DEMAND ZONES
# NO BOXES
# ============================================================


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Suman Intraday Screener V3.0",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Suman Intraday Stock Screener V3.0")

st.caption(
    "Sector Heatmap → Top Gainer / Loser Sector → "
    "First 5-Minute Candle → Top 3 Stocks"
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

# First 5-minute candle is 9:15 - 9:20.
# Therefore scanner starts after 9:20.

SCAN_HOUR = 9
SCAN_MINUTE = 20


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

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan
    )

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi


# ============================================================
# GET PREVIOUS DAY CLOSE
# ============================================================

def get_previous_close(symbol):

    try:

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

        previous_close = float(
            daily_close.iloc[-2]
        )

        if previous_close <= 0:
            return None

        return previous_close

    except Exception:

        return None


# ============================================================
# STOCK ANALYSIS
# ============================================================

def analyze_stock(symbol):

    try:

        # ====================================================
        # 5 MINUTE DATA
        # ====================================================

        data = yf.download(
            symbol,
            period="2d",
            interval="5m",
            progress=False,
            auto_adjust=False,
            threads=False
        )

        if (
            data is None
            or data.empty
        ):
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


        # ====================================================
        # PREVIOUS DAY CLOSE
        # ====================================================

        previous_close = get_previous_close(
            symbol
        )

        if previous_close is None:
            return None


        # ====================================================
        # FIND TODAY'S DATA
        # ====================================================

        today_date = now.date()


        today_data = data[
            data.index.date == today_date
        ].copy()


        if today_data.empty:
            return None


        # ====================================================
        # FIRST 5 MINUTE CANDLE
        # ====================================================

        # We need the 9:15 candle.
        # Depending on yfinance timestamp timezone,
        # use local time conversion where required.

        if today_data.index.tz is not None:

            try:

                today_data.index = (
                    today_data.index
                    .tz_convert(INDIA_TZ)
                )

            except Exception:

                pass


        first_candle = today_data[
            (
                today_data.index.hour == 9
            )
            &
            (
                today_data.index.minute == 15
            )
        ]


        if first_candle.empty:
            return None


        first_bar = first_candle.iloc[0]


        first_open = float(
            first_bar["Open"]
        )

        first_high = float(
            first_bar["High"]
        )

        first_low = float(
            first_bar["Low"]
        )

        first_close = float(
            first_bar["Close"]
        )

        first_volume = float(
            first_bar["Volume"]
        )


        if first_open <= 0:
            return None


        # ====================================================
        # FIRST 5 MINUTE CANDLE %
        # ====================================================

        first_5m_change = (
            (
                first_close - first_open
            )
            / first_open
        ) * 100


        # ====================================================
        # CANDLE TYPE
        # ====================================================

        if first_close > first_open:

            candle_type = "🟢 GREEN"

        elif first_close < first_open:

            candle_type = "🔴 RED"

        else:

            candle_type = "⚪ DOJI"


        # ====================================================
        # CURRENT LTP
        # ====================================================

        ltp = float(
            data["Close"].iloc[-1]
        )


        # ====================================================
        # DAILY % CHANGE
        # ====================================================

        daily_change = (
            (
                ltp - previous_close
            )
            / previous_close
        ) * 100


        # ====================================================
        # VWAP
        # ====================================================

        high = data["High"]

        low = data["Low"]

        close = data["Close"]

        volume = data["Volume"]


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
        # EMA20
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
        # VOLUME RATIO
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
                /
                avg_volume
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

            "Prev Close":
                round(
                    previous_close,
                    2
                ),

            "Daily %":
                round(
                    daily_change,
                    2
                ),

            "5M Open":
                round(
                    first_open,
                    2
                ),

            "5M Close":
                round(
                    first_close,
                    2
                ),

            "5M %":
                round(
                    first_5m_change,
                    2
                ),

            "5M Candle":
                candle_type,

            "5M Volume":
                int(
                    first_volume
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
# MAIN SCANNER
# ============================================================

def run_scanner():

    all_sector_data = {}

    total_stocks = sum(
        len(stocks)
        for stocks in SECTORS.values()
    )

    progress = st.progress(0)

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
                    scanned /
                    total_stocks,
                    1.0
                )
            )


            if result is not None:

                result["Sector"] = sector

                results.append(
                    result
                )


        if results:

            stock_df = pd.DataFrame(
                results
            )


            # =================================================
            # SECTOR DAILY PERFORMANCE
            # =================================================

            sector_change = float(
                stock_df[
                    "Daily %"
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
# MARKET TIME
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
        "⏳ Scanner 9:20 AM के बाद चलेगा।"
    )

    st.write(
        "पहली 5-minute candle "
        "9:15–9:20 पूरी होने के बाद "
        "SCAN NOW दबाएँ।"
    )


# ============================================================
# AUTO SCAN
# ============================================================

auto_scan = False


if is_scan_time():

    last_scan_date = (
        st.session_state.get(
            "last_scan_date",
            None
        )
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
# RUN
# ============================================================

if auto_scan or manual_scan:

    with st.spinner(
        "📊 Scanning sectors and first 5-minute candles..."
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
        # SECTOR HEATMAP
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
        # HEATMAP
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


        gainer_all = (
            sector_data[
                top_gainer_sector
            ]["stocks"]
            .copy()
        )


        # ====================================================
        # GAINER FILTER
        # ====================================================
        #
        # GREEN FIRST 5M CANDLE
        # AND DAILY CHANGE <= +4%
        #
        # ====================================================

        gainer_qualified = gainer_all[
            (
                gainer_all[
                    "5M Candle"
                ] == "🟢 GREEN"
            )
            &
            (
                gainer_all[
                    "Daily %"
                ] <= 4
            )
        ].copy()


        # ====================================================
        # RANK GAINERS
        # ====================================================
        #
        # Strongest first 5M candle
        # ====================================================

        gainer_qualified = (
            gainer_qualified
            .sort_values(
                [
                    "5M %",
                    "Daily %"
                ],
                ascending=False
            )
            .head(3)
            .reset_index(
                drop=True
            )
        )


        st.markdown(
            "### 🟢 Top 3 Gainer Stocks"
        )


        if gainer_qualified.empty:

            st.warning(
                "इस sector में कोई stock "
                "आपकी Green Candle + 4% condition "
                "को पूरा नहीं करता।"
            )

        else:

            st.dataframe(
                gainer_qualified[
                    [
                        "Symbol",
                        "Prev Close",
                        "5M Open",
                        "5M Close",
                        "5M %",
                        "Daily %",
                        "5M Volume",
                        "LTP",
                        "VWAP",
                        "EMA20",
                        "RSI(9)",
                        "Volume x",
                        "Signal"
                    ]
                ],
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


        loser_all = (
            sector_data[
                top_loser_sector
            ]["stocks"]
            .copy()
        )


        # ====================================================
        # LOSER FILTER
        # ====================================================
        #
        # RED FIRST 5M CANDLE
        # AND DAILY CHANGE >= -4%
        #
        # ====================================================

        loser_qualified = loser_all[
            (
                loser_all[
                    "5M Candle"
                ] == "🔴 RED"
            )
            &
            (
                loser_all[
                    "Daily %"
                ] >= -4
            )
        ].copy()


        # ====================================================
        # RANK LOSERS
        # ====================================================
        #
        # Weakest first 5M candle
        # ====================================================

        loser_qualified = (
            loser_qualified
            .sort_values(
                [
                    "5M %",
                    "Daily %"
                ],
                ascending=True
            )
            .head(3)
            .reset_index(
                drop=True
            )
        )


        st.markdown(
            "### 🔴 Top 3 Loser Stocks"
        )


        if loser_qualified.empty:

            st.warning(
                "इस sector में कोई stock "
                "आपकी Red Candle + 4% condition "
                "को पूरा नहीं करता।"
            )

        else:

            st.dataframe(
                loser_qualified[
                    [
                        "Symbol",
                        "Prev Close",
                        "5M Open",
                        "5M Close",
                        "5M %",
                        "Daily %",
                        "5M Volume",
                        "LTP",
                        "VWAP",
                        "EMA20",
                        "RSI(9)",
                        "Volume x",
                        "Signal"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )


        # ====================================================
        # FINAL TRADE SUMMARY
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🎯 9:20 AM Trade Candidates"
        )


        col1, col2 = st.columns(2)


        with col1:

            st.success(
                f"🟢 LONG SIDE\n\n"
                f"Sector: {top_gainer_sector}\n\n"
                f"Qualified Stocks: "
                f"{len(gainer_qualified)}"
            )


        with col2:

            st.error(
                f"🔴 SHORT SIDE\n\n"
                f"Sector: {top_loser_sector}\n\n"
                f"Qualified Stocks: "
                f"{len(loser_qualified)}"
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
            "Gainer Filter = First 5M Green + "
            "Previous Close से +4% से अधिक नहीं | "
            "Loser Filter = First 5M Red + "
            "Previous Close से -4% से अधिक नहीं"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Suman Intraday Stock Screener V3.0 | "
    "9:20 AM First 5-Minute Candle Scanner | "
    "Sector Heatmap | "
    "Top 3 Gainers / Top 3 Losers"
)
