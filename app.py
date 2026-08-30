import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, time as dt_time
import pytz
import time

# ============================================================
# SUMAN INTRADAY STOCK SCREENER V3.3 PRO
# ============================================================
#
# 9:20 AM FIRST 5-MINUTE CANDLE STRATEGY
#
# LOGIC:
#
# STEP 1
# Sector Heatmap से Top Gainer Sector
# और Top Loser Sector निकालना
#
# STEP 2
# Top Gainer Sector के F&O stocks:
#   • 9:15–9:20 candle GREEN
#   • Previous Close से +4% से अधिक नहीं
#
# Top Loser Sector के F&O stocks:
#   • 9:15–9:20 candle RED
#   • Previous Close से -4% से अधिक नहीं
#
# STEP 3
# 5M strength / weakness के आधार पर Top 3
#
# INDICATORS:
#   Previous Close
#   5M OHLC
#   5M %
#   Previous Close %
#   Volume
#   Volume x
#   VWAP
#   EMA20
#   RSI9
#   Signal
#
# ============================================================


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Suman Intraday Screener V3.3",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Suman Intraday Stock Screener V3.3 PRO")

st.caption(
    "Sector Heatmap → 9:15–9:20 First 5M Candle → "
    "Top 3 Gainers / Top 3 Losers"
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
# SECTOR → STOCK MAPPING
# ============================================================
#
# F&O focused universe
#
# IMPORTANT:
# Same stock can technically belong to
# more than one economic sector.
#
# Sector selection is handled separately.
#
# ============================================================

SECTORS = {

    "BANK": [
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "AXISBANK.NS",
        "KOTAKBANK.NS",
        "INDUSINDBK.NS",
        "BANKBARODA.NS",
        "PNB.NS",
        "IDFCFIRSTB.NS",
        "FEDERALBNK.NS"
    ],

    "FINANCIAL SERVICES": [
        "BAJFINANCE.NS",
        "BAJAJFINSV.NS",
        "SHRIRAMFIN.NS",
        "CHOLAFIN.NS",
        "PFC.NS",
        "RECLTD.NS",
        "MUTHOOTFIN.NS"
    ],

    "IT": [
        "TCS.NS",
        "INFY.NS",
        "HCLTECH.NS",
        "WIPRO.NS",
        "TECHM.NS",
        "LTIM.NS",
        "MPHASIS.NS",
        "PERSISTENT.NS",
        "COFORGE.NS",
        "OFSS.NS"
    ],

    "AUTO": [
        "MARUTI.NS",
        "M&M.NS",
        "TATAMOTORS.NS",
        "EICHERMOT.NS",
        "HEROMOTOCO.NS",
        "BAJAJ-AUTO.NS",
        "TVSMOTOR.NS",
        "ASHOKLEY.NS",
        "BHARATFORG.NS",
        "BOSCHLTD.NS"
    ],

    "PHARMA": [
        "SUNPHARMA.NS",
        "DRREDDY.NS",
        "CIPLA.NS",
        "DIVISLAB.NS",
        "LUPIN.NS",
        "AUROPHARMA.NS",
        "BIOCON.NS",
        "TORNTPHARM.NS",
        "ZYDUSLIFE.NS",
        "ALKEM.NS"
    ],

    "HEALTHCARE": [
        "APOLLOHOSP.NS",
        "MAXHEALTH.NS",
        "FORTIS.NS",
        "SYNGENE.NS",
        "LALPATHLAB.NS",
        "METROPOLIS.NS",
        "MEDANTA.NS",
        "POLYMED.NS",
        "RAINBOW.NS"
    ],

    "FMCG": [
        "HINDUNILVR.NS",
        "ITC.NS",
        "NESTLEIND.NS",
        "BRITANNIA.NS",
        "TATACONSUM.NS",
        "DABUR.NS",
        "MARICO.NS",
        "COLPAL.NS",
        "GODREJCP.NS",
        "VBL.NS"
    ],

    "METAL": [
        "TATASTEEL.NS",
        "HINDALCO.NS",
        "JSWSTEEL.NS",
        "COALINDIA.NS",
        "VEDL.NS",
        "JINDALSTEL.NS",
        "NMDC.NS",
        "SAIL.NS",
        "NATIONALUM.NS",
        "HINDZINC.NS"
    ],

    "ENERGY": [
        "RELIANCE.NS",
        "NTPC.NS",
        "POWERGRID.NS",
        "ONGC.NS",
        "BPCL.NS",
        "IOC.NS",
        "GAIL.NS",
        "ADANIGREEN.NS",
        "ADANIENSOL.NS",
        "TATAPOWER.NS"
    ],

    "OIL & GAS": [
        "RELIANCE.NS",
        "ONGC.NS",
        "BPCL.NS",
        "IOC.NS",
        "GAIL.NS",
        "PETRONET.NS",
        "HINDPETRO.NS",
        "IGL.NS",
        "MGL.NS",
        "ATGL.NS"
    ],

    "REALTY": [
        "DLF.NS",
        "LODHA.NS",
        "GODREJPROP.NS",
        "OBEROIRLTY.NS",
        "PRESTIGE.NS",
        "PHOENIXLTD.NS",
        "SOBHA.NS",
        "BRIGADE.NS",
        "MACROTECH.NS",
        "SUNTECK.NS"
    ],

    "CONSUMER DURABLES": [
        "DIXON.NS",
        "VOLTAS.NS",
        "WHIRLPOOL.NS",
        "HAVELLS.NS",
        "CROMPTON.NS",
        "KAYNES.NS",
        "AMBER.NS",
        "BLUESTARCO.NS",
        "TITAN.NS"
    ],

    "MEDIA": [
        "ZEEL.NS",
        "SUNTV.NS",
        "PVRINOX.NS",
        "NETWORK18.NS"
    ],

    "TELECOM": [
        "BHARTIARTL.NS",
        "INDUSTOWER.NS",
        "IDEA.NS"
    ],

    "CEMENT": [
        "ULTRACEMCO.NS",
        "GRASIM.NS",
        "SHREECEM.NS",
        "AMBUJACEM.NS",
        "ACC.NS",
        "DALBHARAT.NS",
        "JKCEMENT.NS",
        "RAMCOCEM.NS"
    ],

    "CAPITAL GOODS": [
        "LT.NS",
        "SIEMENS.NS",
        "ABB.NS",
        "BEL.NS",
        "BHEL.NS",
        "HAL.NS",
        "RVNL.NS",
        "BEML.NS",
        "CGPOWER.NS",
        "THERMAX.NS"
    ],

    "CHEMICALS": [
        "SRF.NS",
        "PIDILITIND.NS",
        "UPL.NS",
        "DEEPAKNTR.NS",
        "PIIND.NS",
        "AARTIIND.NS",
        "ATUL.NS",
        "NAVINFLUOR.NS",
        "FLUOROCHEM.NS",
        "TATACHEM.NS"
    ],

    "INFRASTRUCTURE": [
        "LT.NS",
        "ADANIPORTS.NS",
        "RVNL.NS",
        "IRFC.NS",
        "NCC.NS",
        "NBCC.NS",
        "CONCOR.NS",
        "GMRINFRA.NS",
        "ASHOKLEY.NS"
    ],

    "PSU": [
        "BEL.NS",
        "HAL.NS",
        "BHEL.NS",
        "ONGC.NS",
        "COALINDIA.NS",
        "NTPC.NS",
        "POWERGRID.NS",
        "RECLTD.NS",
        "PFC.NS",
        "GAIL.NS"
    ]
}


# ============================================================
# RSI
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

    return 100 - (
        100 / (1 + rs)
    )


# ============================================================
# CLEAN YFINANCE COLUMNS
# ============================================================

def clean_columns(data):

    if isinstance(
        data.columns,
        pd.MultiIndex
    ):

        data.columns = (
            data.columns
            .get_level_values(0)
        )

    return data


# ============================================================
# NORMALIZE INDEX
# ============================================================

def normalize_index(data):

    try:

        if data.index.tz is None:

            data.index = data.index.tz_localize(
                "UTC"
            )

        data.index = data.index.tz_convert(
            INDIA_TZ
        )

    except Exception:

        pass

    return data


# ============================================================
# PREVIOUS DAY CLOSE
# ============================================================

def get_previous_close(symbol):

    try:

        daily = yf.download(
            symbol,
            period="15d",
            interval="1d",
            progress=False,
            auto_adjust=False,
            threads=False
        )

        if daily is None or daily.empty:

            return None

        daily = clean_columns(daily)

        if "Close" not in daily.columns:

            return None

        closes = (
            daily["Close"]
            .dropna()
        )

        if len(closes) < 2:

            return None

        previous_close = float(
            closes.iloc[-2]
        )

        if previous_close <= 0:

            return None

        return previous_close

    except Exception:

        return None


# ============================================================
# FIRST 5 MINUTE CANDLE
# ============================================================

def get_first_5m_candle(data):

    try:

        data = normalize_index(data)

        today = now.date()

        today_data = data[
            data.index.date == today
        ].copy()

        if today_data.empty:

            return None

        first_window = today_data[
            (
                today_data.index.time
                >= dt_time(9, 15)
            )
            &
            (
                today_data.index.time
                < dt_time(9, 20)
            )
        ]

        if first_window.empty:

            return None

        return first_window.iloc[0]

    except Exception:

        return None


# ============================================================
# STOCK ANALYSIS
# ============================================================

def analyze_stock(symbol):

    try:

        # ----------------------------------------------------
        # 5M DATA
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

        data = clean_columns(data)

        required = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        if not all(
            col in data.columns
            for col in required
        ):

            return None

        data = data.dropna()

        if len(data) < 20:

            return None


        # ----------------------------------------------------
        # PREVIOUS CLOSE
        # ----------------------------------------------------

        previous_close = get_previous_close(
            symbol
        )

        if previous_close is None:

            return None


        # ----------------------------------------------------
        # FIRST 5M CANDLE
        # ----------------------------------------------------

        first_candle = get_first_5m_candle(
            data
        )

        if first_candle is None:

            return None


        first_open = float(
            first_candle["Open"]
        )

        first_high = float(
            first_candle["High"]
        )

        first_low = float(
            first_candle["Low"]
        )

        first_close = float(
            first_candle["Close"]
        )

        first_volume = float(
            first_candle["Volume"]
        )


        if first_open <= 0:

            return None


        # ----------------------------------------------------
        # FIRST 5M CHANGE
        # ----------------------------------------------------

        first_5m_change = (
            (
                first_close -
                first_open
            )
            /
            first_open
        ) * 100


        # ----------------------------------------------------
        # CANDLE TYPE
        # ----------------------------------------------------

        if first_close > first_open:

            candle_type = "🟢 GREEN"

        elif first_close < first_open:

            candle_type = "🔴 RED"

        else:

            candle_type = "⚪ DOJI"


        # ----------------------------------------------------
        # PREVIOUS CLOSE → FIRST 5M CLOSE
        # ----------------------------------------------------

        first_5m_daily_change = (
            (
                first_close -
                previous_close
            )
            /
            previous_close
        ) * 100


        # ----------------------------------------------------
        # CURRENT LTP
        # ----------------------------------------------------

        ltp = float(
            data["Close"].iloc[-1]
        )


        # ----------------------------------------------------
        # VWAP
        # ----------------------------------------------------

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
            typical_price *
            volume
        ).cumsum()

        vwap_series = (
            cumulative_pv /
            cumulative_volume.replace(
                0,
                np.nan
            )
        )

        vwap = float(
            vwap_series.iloc[-1]
        )


        # ----------------------------------------------------
        # EMA20
        # ----------------------------------------------------

        ema20 = float(
            close.ewm(
                span=20,
                adjust=False
            ).mean().iloc[-1]
        )


        # ----------------------------------------------------
        # RSI9
        # ----------------------------------------------------

        rsi_series = calculate_rsi(
            close,
            9
        )

        rsi9 = float(
            rsi_series.iloc[-1]
        )


        # ----------------------------------------------------
        # CURRENT VOLUME
        # ----------------------------------------------------

        current_volume = float(
            volume.iloc[-1]
        )


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
                current_volume /
                avg_volume
            )

        else:

            volume_ratio = 0


        # ----------------------------------------------------
        # VWAP STATUS
        # ----------------------------------------------------

        if ltp > vwap:

            vwap_status = "Above"

        elif ltp < vwap:

            vwap_status = "Below"

        else:

            vwap_status = "At VWAP"


        # ----------------------------------------------------
        # SIGNAL
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        return {

            "Symbol":
                symbol.replace(
                    ".NS",
                    ""
                ),

            "Prev Close":
                round(
                    previous_close,
                    2
                ),

            "5M Open":
                round(
                    first_open,
                    2
                ),

            "5M High":
                round(
                    first_high,
                    2
                ),

            "5M Low":
                round(
                    first_low,
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

            "Prev Close %":
                round(
                    first_5m_daily_change,
                    2
                ),

            "5M Candle":
                candle_type,

            "5M Volume":
                int(
                    first_volume
                ),

            "LTP":
                round(
                    ltp,
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
    stocks
):

    results = []

    for symbol in stocks:

        result = analyze_stock(
            symbol
        )

        if result is not None:

            result["Sector"] = sector

            results.append(
                result
            )

    if not results:

        return None

    return pd.DataFrame(
        results
    )


# ============================================================
# RUN SCANNER
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

        sector_results = []


        for symbol in stocks:

            result = analyze_stock(
                symbol
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

                sector_results.append(
                    result
                )


        if sector_results:

            df = pd.DataFrame(
                sector_results
            )

            # ------------------------------------------------
            # SECTOR PERFORMANCE
            # Previous Close → First 5M Close
            # ------------------------------------------------

            sector_change = float(
                df[
                    "Prev Close %"
                ].mean()
            )

            all_sector_data[
                sector
            ] = {

                "change":
                    sector_change,

                "stocks":
                    df
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
# BEFORE 9:20
# ============================================================

if not is_scan_time():

    st.warning(
        "⏳ Scanner 9:20 AM के बाद चलेगा।"
    )

    st.write(
        "पहली 5-minute candle "
        "9:15–9:20 complete होने के बाद "
        "SCAN NOW दबाएँ।"
    )


# ============================================================
# AUTO SCAN
# ============================================================

auto_scan = False


if is_scan_time():

    today_string = now.strftime(
        "%Y-%m-%d"
    )

    last_scan_date = (
        st.session_state.get(
            "last_scan_date",
            None
        )
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


    # ========================================================
    # NO DATA
    # ========================================================

    if not sector_data:

        st.error(
            "❌ आज की 5-minute market data उपलब्ध नहीं है।"
        )

        st.info(
            "कुछ सेकंड बाद SCAN NOW फिर दबाएँ।"
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

                "Change %":
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
                "Change %",
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
            sector_df.iloc[0]["Change %"]
        )


        # ====================================================
        # TOP LOSER SECTOR
        # ====================================================

        top_loser_sector = (
            sector_df.iloc[-1]["Sector"]
        )

        top_loser_change = (
            sector_df.iloc[-1]["Change %"]
        )


        # ====================================================
        # SECTOR HEATMAP
        # ====================================================

        st.subheader(
            "🔥 SECTOR HEATMAP"
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
        # GREEN FIRST 5M
        # Previous Close <= +4%
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
                    "Prev Close %"
                ] <= 4
            )
        ].copy()


        # ====================================================
        # GAINER RANKING
        # ====================================================

        gainer_qualified = (
            gainer_qualified
            .sort_values(
                [
                    "5M %",
                    "Prev Close %"
                ],
                ascending=False
            )
            .head(3)
            .reset_index(
                drop=True
            )
        )


        st.markdown(
            "### 🟢 TOP 3 GAINER STOCKS"
        )


        if gainer_qualified.empty:

            st.warning(
                "इस Top Gainer Sector में "
                "Green + ≤4% condition वाला "
                "कोई stock नहीं मिला।"
            )

        else:

            st.dataframe(
                gainer_qualified[
                    [
                        "Symbol",
                        "Prev Close",
                        "5M Open",
                        "5M High",
                        "5M Low",
                        "5M Close",
                        "5M %",
                        "Prev Close %",
                        "5M Candle",
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
        # RED FIRST 5M
        # Previous Close >= -4%
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
                    "Prev Close %"
                ] >= -4
            )
        ].copy()


        # ====================================================
        # LOSER RANKING
        # ====================================================

        loser_qualified = (
            loser_qualified
            .sort_values(
                [
                    "5M %",
                    "Prev Close %"
                ],
                ascending=True
            )
            .head(3)
            .reset_index(
                drop=True
            )
        )


        st.markdown(
            "### 🔴 TOP 3 LOSER STOCKS"
        )


        if loser_qualified.empty:

            st.warning(
                "इस Top Loser Sector में "
                "Red + ≤4% fall condition वाला "
                "कोई stock नहीं मिला।"
            )

        else:

            st.dataframe(
                loser_qualified[
                    [
                        "Symbol",
                        "Prev Close",
                        "5M Open",
                        "5M High",
                        "5M Low",
                        "5M Close",
                        "5M %",
                        "Prev Close %",
                        "5M Candle",
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
        # FINAL TRADE CANDIDATES
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🎯 9:20 AM TRADE CANDIDATES"
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
            "LONG = Top Gainer Sector + "
            "Green 9:15–9:20 candle + "
            "Previous Close से ≤ +4%"
        )

        st.caption(
            "SHORT = Top Loser Sector + "
            "Red 9:15–9:20 candle + "
            "Previous Close से ≥ -4%"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Suman Intraday Stock Screener V3.3 PRO | "
    "9:20 AM First 5M Candle | "
    "Expanded Sector Universe | "
    "Top 3 Long + Top 3 Short"
)
