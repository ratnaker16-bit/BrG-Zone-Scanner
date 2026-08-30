import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, time as dt_time
import pytz

# ============================================================
# SUMAN INTRADAY SCREENER
# 9:19 AM TOP GAINER / TOP LOSER SECTOR
# ============================================================

st.set_page_config(
    page_title="Suman 9:19 Intraday Screener",
    layout="wide"
)

# ============================================================
# SETTINGS
# ============================================================

IST = pytz.timezone("Asia/Kolkata")

SCAN_TIME = dt_time(9, 19)

MAX_GAIN = 4.0
MAX_LOSS = -4.0

# ============================================================
# NSE STOCKS + SECTORS
# ============================================================

SECTOR_STOCKS = {

    "BANKING": [
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

    "IT": [
        "TCS.NS",
        "INFY.NS",
        "HCLTECH.NS",
        "WIPRO.NS",
        "TECHM.NS",
        "LTIM.NS",
        "MPHASIS.NS",
        "COFORGE.NS",
        "PERSISTENT.NS"
    ],

    "AUTO": [
        "MARUTI.NS",
        "M&M.NS",
        "TATAMOTORS.NS",
        "EICHERMOT.NS",
        "HEROMOTOCO.NS",
        "BAJAJ-AUTO.NS",
        "TVSMOTOR.NS",
        "ASHOKLEY.NS"
    ],

    "PHARMA": [
        "SUNPHARMA.NS",
        "DRREDDY.NS",
        "CIPLA.NS",
        "DIVISLAB.NS",
        "APOLLOHOSP.NS",
        "LUPIN.NS",
        "AUROPHARMA.NS",
        "BIOCON.NS"
    ],

    "METAL": [
        "TATASTEEL.NS",
        "JSWSTEEL.NS",
        "HINDALCO.NS",
        "VEDL.NS",
        "JINDALSTEL.NS",
        "SAIL.NS",
        "NMDC.NS"
    ],

    "ENERGY": [
        "RELIANCE.NS",
        "ONGC.NS",
        "NTPC.NS",
        "POWERGRID.NS",
        "COALINDIA.NS",
        "IOC.NS",
        "BPCL.NS",
        "GAIL.NS"
    ],

    "FMCG": [
        "ITC.NS",
        "HINDUNILVR.NS",
        "NESTLEIND.NS",
        "BRITANNIA.NS",
        "TATACONSUM.NS",
        "DABUR.NS",
        "MARICO.NS",
        "GODREJCP.NS"
    ],

    "REALTY": [
        "DLF.NS",
        "LODHA.NS",
        "GODREJPROP.NS",
        "OBEROIRLTY.NS",
        "PRESTIGE.NS"
    ],

    "FINANCE": [
        "BAJFINANCE.NS",
        "BAJAJFINSV.NS",
        "SHRIRAMFIN.NS",
        "CHOLAFIN.NS",
        "MUTHOOTFIN.NS",
        "LICHSGFIN.NS",
        "RECLTD.NS",
        "PFC.NS"
    ],

    "INFRA": [
        "LT.NS",
        "ADANIPORTS.NS",
        "ADANIENT.NS",
        "BEL.NS",
        "HAL.NS",
        "SIEMENS.NS",
        "ABB.NS",
        "BHEL.NS"
    ],

    "TELECOM": [
        "BHARTIARTL.NS",
        "INDUSTOWER.NS"
    ],

    "CEMENT": [
        "ULTRACEMCO.NS",
        "GRASIM.NS",
        "AMBUJACEM.NS",
        "ACC.NS",
        "DALBHARAT.NS",
        "SHREECEM.NS"
    ],

    "CHEMICALS": [
        "SRF.NS",
        "PIDILITIND.NS",
        "UPL.NS",
        "DEEPAKNTR.NS",
        "PIIND.NS"
    ]
}

# ============================================================
# STOCK → SECTOR
# ============================================================

STOCK_SECTOR = {}

for sector, stocks in SECTOR_STOCKS.items():
    for stock in stocks:
        STOCK_SECTOR[stock] = sector

ALL_STOCKS = list(STOCK_SECTOR.keys())


# ============================================================
# SYMBOL
# ============================================================

def clean_symbol(symbol):
    return symbol.replace(".NS", "")


# ============================================================
# GET MARKET DATA
# ============================================================

@st.cache_data(ttl=30, show_spinner=False)
def get_market_data():

    results = []

    for symbol in ALL_STOCKS:

        try:

            ticker = yf.Ticker(symbol)

            # ------------------------------------------------
            # PREVIOUS DAY CLOSE
            # ------------------------------------------------

            daily = ticker.history(
                period="5d",
                interval="1d",
                auto_adjust=False
            )

            if daily.empty:
                continue

            daily = daily.dropna(subset=["Close"])

            if len(daily) < 2:
                continue

            previous_close = float(
                daily["Close"].iloc[-2]
            )

            # ------------------------------------------------
            # TODAY 5 MIN DATA
            # ------------------------------------------------

            intraday = ticker.history(
                period="1d",
                interval="5m",
                auto_adjust=False,
                prepost=False
            )

            if intraday.empty:
                continue

            intraday.index = pd.to_datetime(
                intraday.index
            )

            # Convert to IST
            if intraday.index.tz is not None:
                intraday.index = intraday.index.tz_convert(
                    IST
                )
            else:
                intraday.index = intraday.index.tz_localize(
                    IST
                )

            today = datetime.now(IST).date()

            intraday = intraday[
                intraday.index.date == today
            ]

            if intraday.empty:
                continue

            # ------------------------------------------------
            # FIRST 5-MINUTE CANDLE
            # 9:15 → 9:20
            # ------------------------------------------------

            first_candle = intraday[
                (intraday.index.time >= dt_time(9, 15)) &
                (intraday.index.time < dt_time(9, 20))
            ]

            if first_candle.empty:
                continue

            open_915 = float(
                first_candle["Open"].iloc[0]
            )

            # ------------------------------------------------
            # LATEST PRICE AVAILABLE UP TO 9:19
            # ------------------------------------------------

            current_data = intraday[
                (intraday.index.time >= dt_time(9, 15)) &
                (intraday.index.time <= dt_time(9, 19, 59))
            ]

            if current_data.empty:
                continue

            ltp = float(
                current_data["Close"].iloc[-1]
            )

            # ------------------------------------------------
            # PREVIOUS DAY CLOSE → 9:19 %
            # ------------------------------------------------

            pct_change = (
                (ltp - previous_close)
                / previous_close
            ) * 100

            # ------------------------------------------------
            # 9:15 OPEN → 9:19 PRICE
            # ------------------------------------------------

            candle_change = (
                (ltp - open_915)
                / open_915
            ) * 100

            if ltp > open_915:
                candle = "GREEN"
            elif ltp < open_915:
                candle = "RED"
            else:
                candle = "NEUTRAL"

            results.append({

                "Symbol": clean_symbol(symbol),
                "Sector": STOCK_SECTOR[symbol],

                "Previous Close": previous_close,
                "9:15 Open": open_915,
                "9:19 Price": ltp,

                "% Gain/Loss": pct_change,
                "9:15→9:19 %": candle_change,

                "Candle": candle
            })

        except Exception:
            continue

    return pd.DataFrame(results)


# ============================================================
# TITLE
# ============================================================

st.title(
    "🚀 SUMAN 9:19 AM INTRADAY SCREENER"
)

st.write(
    "Top Gainer Sector + Top Loser Sector → "
    "3 BUY + 3 SELL"
)

st.info(
    "Calculation: Previous Day Close → 9:19 Price | "
    "Direction: 9:15 Open → 9:19 Price"
)


# ============================================================
# CURRENT TIME
# ============================================================

now = datetime.now(IST)

st.caption(
    f"Current IST Time: {now.strftime('%d-%m-%Y %H:%M:%S')}"
)


# ============================================================
# MARKET CLOSED
# ============================================================

if now.weekday() >= 5:

    st.warning(
        "🔴 NSE Market Closed — आज market बंद है। "
        "अगले trading day को 9:19 AM पर scan करें।"
    )

    st.stop()


# ============================================================
# BEFORE 9:19
# ============================================================

if now.time() < SCAN_TIME:

    st.info(
        "⏳ Scanner 9:19 AM के बाद चलाएँ।"
    )


# ============================================================
# SCAN BUTTON
# ============================================================

scan = st.button(
    "🔎 SCAN 9:19 AM",
    use_container_width=True
)


# ============================================================
# RUN
# ============================================================

if scan:

    if now.time() < SCAN_TIME:

        st.warning(
            "⏳ अभी 9:19 AM नहीं हुआ है। "
            "पहली 5-minute candle अभी बन रही है।"
        )

        st.stop()

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    with st.spinner(
        "📡 Market data scan हो रहा है..."
    ):

        df = get_market_data()

    # --------------------------------------------------------
    # NO DATA
    # --------------------------------------------------------

    if df.empty:

        st.error(
            "आज की 5-minute market data उपलब्ध नहीं है। "
            "कुछ समय बाद scan करें।"
        )

        st.stop()

    # --------------------------------------------------------
    # SECTOR RANKING
    # --------------------------------------------------------

    sector_df = (
        df.groupby("Sector")["% Gain/Loss"]
        .mean()
        .reset_index()
        .sort_values(
            "% Gain/Loss",
            ascending=False
        )
    )

    if sector_df.empty:

        st.error(
            "Sector data उपलब्ध नहीं है।"
        )

        st.stop()

    # --------------------------------------------------------
    # TOP SECTORS
    # --------------------------------------------------------

    top_gainer_sector = sector_df.iloc[0]["Sector"]

    top_loser_sector = sector_df.iloc[-1]["Sector"]

    top_gainer_pct = sector_df.iloc[0]["% Gain/Loss"]

    top_loser_pct = sector_df.iloc[-1]["% Gain/Loss"]

    # ========================================================
    # TOP SECTOR DISPLAY
    # ========================================================

    st.subheader(
        "🏭 9:19 AM Sector Ranking"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            f"🟢 TOP GAINER SECTOR\n\n"
            f"### {top_gainer_sector}\n"
            f"Average: **{top_gainer_pct:+.2f}%**"
        )

    with col2:

        st.error(
            f"🔴 TOP LOSER SECTOR\n\n"
            f"### {top_loser_sector}\n"
            f"Average: **{top_loser_pct:+.2f}%**"
        )

    # ========================================================
    # BUY STOCKS
    # ========================================================

    buy_stocks = df[
        (df["Sector"] == top_gainer_sector) &
        (df["% Gain/Loss"] > 0) &
        (df["% Gain/Loss"] <= MAX_GAIN) &
        (df["9:19 Price"] > df["9:15 Open"])
    ].copy()

    buy_stocks = buy_stocks.sort_values(
        "% Gain/Loss",
        ascending=False
    ).head(3)

    # ========================================================
    # SELL STOCKS
    # ========================================================

    sell_stocks = df[
        (df["Sector"] == top_loser_sector) &
        (df["% Gain/Loss"] < 0) &
        (df["% Gain/Loss"] >= MAX_LOSS) &
        (df["9:19 Price"] < df["9:15 Open"])
    ].copy()

    sell_stocks = sell_stocks.sort_values(
        "% Gain/Loss",
        ascending=True
    ).head(3)

    # ========================================================
    # BUY RESULT
    # ========================================================

    st.subheader(
        f"🟢 BUY — {top_gainer_sector}"
    )

    if buy_stocks.empty:

        st.warning(
            "इस sector में qualifying BUY stock नहीं मिला।"
        )

    else:

        buy_display = buy_stocks[
            [
                "Symbol",
                "Previous Close",
                "9:15 Open",
                "9:19 Price",
                "% Gain/Loss",
                "9:15→9:19 %",
                "Candle"
            ]
        ].copy()

        buy_display["Signal"] = "🟢 BUY"

        buy_display["% Gain/Loss"] = (
            buy_display["% Gain/Loss"]
            .map(lambda x: f"{x:+.2f}%")
        )

        buy_display["9:15→9:19 %"] = (
            buy_display["9:15→9:19 %"]
            .map(lambda x: f"{x:+.2f}%")
        )

        st.dataframe(
            buy_display,
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # SELL RESULT
    # ========================================================

    st.subheader(
        f"🔴 SELL — {top_loser_sector}"
    )

    if sell_stocks.empty:

        st.warning(
            "इस sector में qualifying SELL stock नहीं मिला।"
        )

    else:

        sell_display = sell_stocks[
            [
                "Symbol",
                "Previous Close",
                "9:15 Open",
                "9:19 Price",
                "% Gain/Loss",
                "9:15→9:19 %",
                "Candle"
            ]
        ].copy()

        sell_display["Signal"] = "🔴 SELL"

        sell_display["% Gain/Loss"] = (
            sell_display["% Gain/Loss"]
            .map(lambda x: f"{x:+.2f}%")
        )

        sell_display["9:15→9:19 %"] = (
            sell_display["9:15→9:19 %"]
            .map(lambda x: f"{x:+.2f}%")
        )

        st.dataframe(
            sell_display,
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # COMPLETE SECTOR RANKING
    # ========================================================

    with st.expander(
        "📊 सभी Sector की Ranking देखें"
    ):

        ranking = sector_df.copy()

        ranking["% Gain/Loss"] = (
            ranking["% Gain/Loss"]
            .map(lambda x: f"{x:+.2f}%")
        )

        st.dataframe(
            ranking,
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # FINAL 9:20 SUMMARY
    # ========================================================

    st.subheader(
        "🎯 9:20 AM TRADE CANDIDATES"
    )

    c1, c2 = st.columns(2)

    with c1:

        if not buy_stocks.empty:

            st.success(
                "🟢 BUY\n\n" +
                "\n".join(
                    [
                        f"{i+1}. {row['Symbol']} "
                        f"({row['% Gain/Loss']:+.2f}%)"
                        for i, (_, row)
                        in enumerate(buy_stocks.iterrows())
                    ]
                )
            )

        else:

            st.info(
                "कोई BUY candidate नहीं।"
            )

    with c2:

        if not sell_stocks.empty:

            st.error(
                "🔴 SELL\n\n" +
                "\n".join(
                    [
                        f"{i+1}. {row['Symbol']} "
                        f"({row['% Gain/Loss']:+.2f}%)"
                        for i, (_, row)
                        in enumerate(sell_stocks.iterrows())
                    ]
                )
            )

        else:

            st.info(
                "कोई SELL candidate नहीं।"
            )

    # ========================================================
    # SCAN TIME
    # ========================================================

    st.caption(
        "Scan completed: "
        + datetime.now(IST).strftime(
            "%d-%m-%Y %H:%M:%S"
        )
        + " IST"
    )
