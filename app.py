# ============================================================
# BrG Trading Zone V1.0
# NIFTY 200 Multi-Timeframe Demand / Supply Zone Scanner
# Timeframes: 15m, 1H, 2H, 3H, Daily, Weekly
# Data Source: Yahoo Finance
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
import time

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="BrG Trading Zone V1.0",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.title("📊 BrG Trading Zone V1.0")
st.caption(
    "NIFTY 200 | Demand & Supply | Support & Resistance | "
    "15M • 1H • 2H • 3H • Daily • Weekly"
)

# ============================================================
# NIFTY 200
# NOTE: Static snapshot. Update periodically if required.
# ============================================================

NIFTY200 = sorted(set([
    # ---------------- NIFTY 50 ----------------
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT",
    "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV",
    "BEL", "BHARTIARTL", "CIPLA", "COALINDIA",
    "DRREDDY", "EICHERMOT", "ETERNAL", "GRASIM",
    "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO",
    "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK",
    "INFY", "ITC", "JIOFIN", "JSWSTEEL",
    "KOTAKBANK", "LT", "M&M", "MARUTI",
    "NESTLEIND", "NTPC", "ONGC", "POWERGRID",
    "RELIANCE", "SBILIFE", "SBIN", "SHRIRAMFIN",
    "SUNPHARMA", "TATACONSUM", "TATASTEEL", "TCS",
    "TECHM", "TITAN", "TRENT", "ULTRACEMCO",
    "WIPRO",

    # ---------------- NEXT 50 ----------------
    "ABB", "AMBUJACEM", "BANKBARODA", "BOSCHLTD",
    "CANBK", "CGPOWER", "CHOLAFIN", "COLPAL",
    "DABUR", "DIVISLAB", "DLF", "DMART",
    "GAIL", "GODREJCP", "GODREJPROP", "HAL",
    "HAVELLS", "ICICIGI", "ICICIPRULI", "INDHOTEL",
    "INDIANB", "INDUSTOWER", "IOC", "IRCTC",
    "JINDALSTEL", "JSWENERGY", "LICI", "LODHA",
    "LUPIN", "MARICO", "MAXHEALTH", "MOTHERSON",
    "MPHASIS", "MUTHOOTFIN", "NHPC", "NMDC",
    "OBEROIRLTY", "OFSS", "OIL", "PAGEIND",
    "PAYTM", "PERSISTENT", "PFC", "PIDILITIND",
    "PIIND", "PNB", "POLYCAB", "RECLTD",
    "SAIL", "SBICARD", "SIEMENS", "SRF",
    "SUPREMEIND", "TATAPOWER", "TORNTPHARM", "TORNTPOWER",
    "TVSMOTOR", "UNITEDSPIRITS", "VEDL", "VOLTAS",

    # ---------------- MIDCAP / LARGE MIDCAP ----------------
    "ABCAPITAL", "ABFRL", "ACC", "ALKEM",
    "APLAPOLLO", "ASHOKLEY", "ASTRAL", "AUROPHARMA",
    "BALKRISIND", "BANDHANBNK", "BATAINDIA", "BHARATFORG",
    "BIOCON", "BLUESTARCO", "BSE", "CAMS",
    "CDSL", "CENTRALBK", "CESC", "COFORGE",
    "CONCOR", "COROMANDEL", "CROMPTON", "CYIENT",
    "DALBHARAT", "DEEPAKNTR", "DELHIVERY", "ESCORTS",
    "EXIDEIND", "FEDERALBNK", "FORTIS", "GLENMARK",
    "GMRINFRA", "GNFC", "GODFRYPHLP", "GUJGASLTD",
    "IDFCFIRSTB", "IEX", "IGL", "INDIAMART",
    "IPCALAB", "IRFC", "JUBLFOOD", "KALYANKJIL",
    "KEI", "KPITTECH", "LAURUSLABS", "LICHSGFIN",
    "LTIM", "MANAPPURAM", "MCX", "METROPOLIS",
    "MGL", "MINDTREE", "MRF", "NATIONALUM",
    "NAVINFLUOR", "NLCINDIA", "OLECTRA", "PEL",
    "PERSISTENT", "PHOENIXLTD", "POLYMED", "PRESTIGE",
    "RAMCOCEM", "RBLBANK", "SONACOMS", "STARHEALTH",
    "SUMICHEM", "SUNDARMFIN", "SUNTV", "TATACHEM",
    "TATACOMM", "TATAELXSI", "THERMAX", "TIMKEN",
    "TITAN", "UBL", "UNOMINDA", "UPL",
    "VBL", "VINATIORGA", "ZEEL"
]))

# ============================================================
# SETTINGS
# ============================================================

st.sidebar.header("⚙️ Scanner Settings")

account_capital = st.sidebar.number_input(
    "Capital ₹",
    min_value=1000,
    value=25000,
    step=1000
)

risk_pct = st.sidebar.number_input(
    "Risk % per trade",
    min_value=0.1,
    max_value=10.0,
    value=0.5,
    step=0.1
)

target_rr = st.sidebar.number_input(
    "Target R:R",
    min_value=0.5,
    max_value=20.0,
    value=5.0,
    step=0.5
)

atr_period = st.sidebar.number_input(
    "ATR Period",
    min_value=5,
    max_value=50,
    value=14
)

vol_sma_period = st.sidebar.number_input(
    "Volume SMA Period",
    min_value=5,
    max_value=100,
    value=20
)

st.sidebar.subheader("Zone Quality")

min_base_count = st.sidebar.number_input(
    "Min Base Candles",
    min_value=1,
    max_value=3,
    value=1
)

max_base_count = st.sidebar.number_input(
    "Max Base Candles",
    min_value=1,
    max_value=3,
    value=3
)

leg_in_min_atr = st.sidebar.number_input(
    "Leg-In Min ATR",
    min_value=0.5,
    max_value=5.0,
    value=1.0,
    step=0.1
)

leg_in_base_mult = st.sidebar.number_input(
    "Leg-In / Base Size",
    min_value=1.0,
    max_value=5.0,
    value=2.0,
    step=0.1
)

leg_in_body_pct = st.sidebar.number_input(
    "Leg-In Body %",
    min_value=0.3,
    max_value=0.95,
    value=0.60,
    step=0.05
)

leg_out_tr_mult = st.sidebar.number_input(
    "Leg-Out TR Multiplier",
    min_value=1.0,
    max_value=5.0,
    value=1.2,
    step=0.1
)

leg_out_min_ratio = st.sidebar.number_input(
    "Leg-Out / Leg-In TR",
    min_value=0.5,
    max_value=5.0,
    value=1.0,
    step=0.1
)

max_base_atr = st.sidebar.number_input(
    "Max Base TR / ATR",
    min_value=0.5,
    max_value=3.0,
    value=1.0,
    step=0.1
)

min_clv = st.sidebar.number_input(
    "Minimum CLV",
    min_value=0.3,
    max_value=0.95,
    value=0.60,
    step=0.05
)

max_wick_pct = st.sidebar.number_input(
    "Maximum Wick %",
    min_value=0.1,
    max_value=0.8,
    value=0.30,
    step=0.05
)

use_imbalance = st.sidebar.checkbox(
    "Use Imbalance Filter",
    value=True
)

max_imbalance_mult = st.sidebar.number_input(
    "Max Imbalance Multiplier",
    min_value=0.5,
    max_value=3.0,
    value=1.0,
    step=0.1
)

st.sidebar.subheader("Score")

min_valid_score = st.sidebar.number_input(
    "Minimum Valid Score",
    min_value=0,
    max_value=100,
    value=40
)

hq_score_threshold = st.sidebar.number_input(
    "HQ Zone Score",
    min_value=50,
    max_value=150,
    value=90
)

tested_retrace_pct = st.sidebar.number_input(
    "Tested Retrace %",
    min_value=0.1,
    max_value=1.0,
    value=0.50,
    step=0.05
)

max_tested_count = st.sidebar.number_input(
    "Maximum Tests",
    min_value=1,
    max_value=10,
    value=2
)

sl_buffer_atr = st.sidebar.number_input(
    "SL ATR Buffer",
    min_value=0.0,
    max_value=1.0,
    value=0.10,
    step=0.05
)

# ============================================================
# TIMEFRAME SETTINGS
# ============================================================

TIMEFRAMES = {
    "15M": "15m",
    "1H": "1h",
    "2H": "2h",
    "3H": "3h",
    "Daily": "1d",
    "Weekly": "1wk"
}

# ============================================================
# YAHOO PERIOD HELPERS
# ============================================================

def get_period_for_timeframe(tf):

    if tf == "15M":
        return "60d"

    if tf == "1H":
        return "730d"

    if tf in ["2H", "3H"]:
        return "730d"

    if tf == "Daily":
        return "5y"

    if tf == "Weekly":
        return "10y"

    return "1y"


# ============================================================
# DATA NORMALIZATION
# ============================================================

def normalize_df(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # Flatten MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            str(col[0]).lower()
            for col in df.columns
        ]
    else:
        df.columns = [
            str(col).lower()
            for col in df.columns
        ]

    rename_map = {
        "adj close": "close",
        "datetime": "datetime",
        "date": "datetime"
    }

    df = df.rename(columns=rename_map)

    required = [
        "open",
        "high",
        "low",
        "close"
    ]

    for col in required:
        if col not in df.columns:
            return pd.DataFrame()

    if "volume" not in df.columns:
        df["volume"] = 0

    df = df[
        ["open", "high", "low", "close", "volume"]
    ].copy()

    for col in [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "open",
            "high",
            "low",
            "close"
        ]
    )

    return df


# ============================================================
# FETCH DATA
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def download_data(symbol, interval):

    ticker = symbol.upper().strip()

    if not ticker.endswith(".NS"):
        ticker = ticker + ".NS"

    period = get_period_for_timeframe(interval)

    try:

        df = yf.download(
            ticker,
            period=period,
            interval=TIMEFRAMES[interval],
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = normalize_df(df)

        if df.empty:
            return pd.DataFrame()

        # Datetime index
        if not isinstance(df.index, pd.DatetimeIndex):

            try:
                df.index = pd.to_datetime(df.index)
            except Exception:
                pass

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# RESAMPLE 1H -> 2H / 3H
# ============================================================

def resample_hourly(df, hours):

    if df is None or df.empty:
        return pd.DataFrame()

    x = df.copy()

    if not isinstance(x.index, pd.DatetimeIndex):
        x.index = pd.to_datetime(x.index)

    x = x.sort_index()

    rule = f"{hours}h"

    result = x.resample(
        rule,
        label="right",
        closed="right"
    ).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    })

    result = result.dropna(
        subset=[
            "open",
            "high",
            "low",
            "close"
        ]
    )

    return result


# ============================================================
# TRUE RANGE
# ============================================================

def true_range_series(df):

    prev_close = df["close"].shift(1)

    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - prev_close).abs()
    tr3 = (df["low"] - prev_close).abs()

    return pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)


# ============================================================
# WILDER RMA
# ============================================================

def rma(series, length):

    return series.ewm(
        alpha=1 / length,
        adjust=False,
        min_periods=length
    ).mean()


# ============================================================
# CANDLE HELPERS
# ============================================================

def candle_body(row):

    return abs(
        float(row["close"]) -
        float(row["open"])
    )


def candle_range(row):

    return (
        float(row["high"]) -
        float(row["low"])
    )


def body_pct(row):

    rng = candle_range(row)

    if rng <= 0:
        return 0

    return candle_body(row) / rng


def clv(row):

    rng = candle_range(row)

    if rng <= 0:
        return 0.5

    return (
        float(row["close"]) -
        float(row["low"])
    ) / rng


def is_bull(row):

    return float(row["close"]) > float(row["open"])


def is_bear(row):

    return float(row["close"]) < float(row["open"])


# ============================================================
# ZONE STATE
# ============================================================

def get_zone_state(
    df,
    proximal,
    distal,
    zone_type,
    created_index,
    tested_retrace=tested_retrace_pct
):

    if df.empty:
        return "Fresh", 0

    try:
        start_pos = df.index.get_loc(created_index)

    except Exception:
        start_pos = max(0, len(df) - 50)

    future = df.iloc[start_pos + 1:]

    if future.empty:
        return "Fresh", 0

    touches = 0

    zone_size = abs(
        float(proximal) -
        float(distal)
    )

    if zone_size <= 0:
        return "Fresh", 0

    for _, row in future.iterrows():

        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])

        # ---------------- DEMAND ----------------

        if zone_type == "Demand":

            if low <= proximal and high >= distal:

                touches += 1

            # Broken below distal
            if close < distal:
                return "Broken", touches

        # ---------------- SUPPLY ----------------

        else:

            if high >= distal and low <= proximal:

                touches += 1

            # Broken above distal
            if close > distal:
                return "Broken", touches

    if touches == 0:
        return "Fresh", 0

    if touches <= max_tested_count:
        return "Tested", touches

    return "Broken", touches


# ============================================================
# POSITION SIZE
# ============================================================

def calculate_position_size(entry, sl):

    risk_money = (
        float(account_capital) *
        float(risk_pct) / 100
    )

    risk_per_share = abs(
        float(entry) -
        float(sl)
    )

    if risk_per_share <= 0:
        return 0

    qty = int(
        risk_money /
        risk_per_share
    )

    return max(qty, 0)


# ============================================================
# SCAN ONE DATAFRAME
# ============================================================

def run_scan(df, symbol, timeframe):

    if df is None or df.empty:
        return []

    x = df.copy()

    if len(x) < 50:
        return []

    x["TR"] = true_range_series(x)

    x["ATR"] = rma(
        x["TR"],
        int(atr_period)
    )

    x["VOL_SMA"] = (
        x["volume"]
        .rolling(int(vol_sma_period))
        .mean()
    )

    zones = []

    # Need enough candles
    for i in range(
        max(atr_period, vol_sma_period) + 3,
        len(x) - 1
    ):

        current = x.iloc[i]

        atr = float(current["ATR"])

        if not np.isfinite(atr) or atr <= 0:
            continue

        # ====================================================
        # TRY BASES 1 -> 3
        # ====================================================

        for base_count in range(
            int(min_base_count),
            int(max_base_count) + 1
        ):

            base_start = i - base_count

            if base_start < 2:
                continue

            leg_in = x.iloc[base_start - 1]
            base = x.iloc[
                base_start:i
            ]

            leg_out = x.iloc[i]

            # ------------------------------------------------
            # Base OHLC
            # ------------------------------------------------

            base_high = float(
                base["high"].max()
            )

            base_low = float(
                base["low"].min()
            )

            base_tr_max = float(
                base["TR"].max()
            )

            if base_high <= base_low:
                continue

            # ------------------------------------------------
            # Base Quality
            # ------------------------------------------------

            if base_tr_max > (
                float(max_base_atr) * atr
            ):
                continue

            # Base body should be relatively small
            base_ok = True

            for _, b in base.iterrows():

                br = candle_range(b)

                if br <= 0:
                    base_ok = False
                    break

                bp = body_pct(b)

                if bp > 0.75:
                    base_ok = False
                    break

            if not base_ok:
                continue

            # ------------------------------------------------
            # LEG-IN
            # ------------------------------------------------

            leg_in_tr = float(
                leg_in["TR"]
            )

            leg_in_body = candle_body(
                leg_in
            )

            leg_in_bp = body_pct(
                leg_in
            )

            if leg_in_tr < (
                float(leg_in_min_atr) * atr
            ):
                continue

            if leg_in_bp < float(
                leg_in_body_pct
            ):
                continue

            # ------------------------------------------------
            # LEG-IN DIRECTION
            # ------------------------------------------------

            if is_bull(leg_in):
                direction = "Bullish"

            elif is_bear(leg_in):
                direction = "Bearish"

            else:
                continue

            # ------------------------------------------------
            # LEG-IN SIZE VS BASE
            # ------------------------------------------------

            base_avg_range = float(
                base["TR"].mean()
            )

            if base_avg_range <= 0:
                continue

            leg_in_size_ok = (
                leg_in_tr >=
                float(leg_in_base_mult) *
                base_avg_range
            )

            # ------------------------------------------------
            # LEG-OUT
            # ------------------------------------------------

            leg_out_tr = float(
                leg_out["TR"]
            )

            if leg_out_tr < (
                float(leg_out_tr_mult) * atr
            ):
                continue

            if leg_out_tr < (
                float(leg_out_min_ratio) *
                leg_in_tr
            ):
                continue

            # ------------------------------------------------
            # LEG-OUT DIRECTION
            # ------------------------------------------------

            if direction == "Bullish":

                if not is_bull(leg_out):
                    continue

            else:

                if not is_bear(leg_out):
                    continue

            # ------------------------------------------------
            # CLV
            # ------------------------------------------------

            leg_out_clv = clv(
                leg_out
            )

            if direction == "Bullish":

                if leg_out_clv < float(min_clv):
                    continue

            else:

                if leg_out_clv > (
                    1 - float(min_clv)
                ):
                    continue

            # ------------------------------------------------
            # WICK FILTER
            # ------------------------------------------------

            lo = float(
                leg_out["low"]
            )

            hi = float(
                leg_out["high"]
            )

            op = float(
                leg_out["open"]
            )

            cl = float(
                leg_out["close"]
            )

            rng = hi - lo

            if rng <= 0:
                continue

            if direction == "Bullish":

                upper_wick = hi - max(op, cl)

                wick_pct = (
                    upper_wick / rng
                )

            else:

                lower_wick = min(op, cl) - lo

                wick_pct = (
                    lower_wick / rng
                )

            if wick_pct > float(max_wick_pct):
                continue

            # ------------------------------------------------
            # VOLUME
            # ------------------------------------------------

            vol = float(
                leg_out["volume"]
            )

            vol_sma = float(
                leg_out["VOL_SMA"]
            ) if np.isfinite(
                leg_out["VOL_SMA"]
            ) else 0

            volume_ok = (
                vol_sma > 0 and
                vol > vol_sma
            )

            # ------------------------------------------------
            # IMBALANCE
            # ------------------------------------------------

            imbalance_ok = True

            if use_imbalance:

                if direction == "Bullish":

                    gap = (
                        float(leg_out["low"]) -
                        float(leg_in["high"])
                    )

                else:

                    gap = (
                        float(leg_in["low"]) -
                        float(leg_out["high"])
                    )

                imbalance_ok = (
                    gap > 0 and
                    gap <=
                    float(max_imbalance_mult) *
                    atr
                )

            # ------------------------------------------------
            # PATTERN TYPE
            # ------------------------------------------------

            base_first = base.iloc[0]

            base_bull = is_bull(
                base_first
            )

            base_bear = is_bear(
                base_first
            )

            if direction == "Bullish":

                if base_bull:
                    pattern = "RBR"
                else:
                    pattern = "DBR"

                zone_type = "Demand"

            else:

                if base_bear:
                    pattern = "DBD"
                else:
                    pattern = "RBD"

                zone_type = "Supply"

            # ------------------------------------------------
            # SCORE
            # ------------------------------------------------

            score = 10

            if base_count == 1:
                score += 15

            if leg_in_tr >= (
                1.5 * atr
            ):
                score += 10

            if leg_out_tr >= (
                2.0 * leg_in_tr
            ):
                score += 15

            if leg_in_size_ok:
                score += 15

            if volume_ok:
                score += 10

            if direction == "Bullish":
                strong_close = (
                    leg_out_clv >= 0.75
                )
            else:
                strong_close = (
                    leg_out_clv <= 0.25
                )

            if strong_close:
                score += 15

            if base_bull != base_bear:
                score += 10

            if imbalance_ok:
                score += 10

            # ------------------------------------------------
            # ZONE
            # ------------------------------------------------

            if zone_type == "Demand":

                proximal = base_high
                distal = base_low

                sl = (
                    distal -
                    float(sl_buffer_atr) *
                    atr
                )

                entry = proximal

                risk = entry - sl

                if risk <= 0:
                    continue

                tp = (
                    entry +
                    float(target_rr) *
                    risk
                )

            else:

                proximal = base_low
                distal = base_high

                sl = (
                    distal +
                    float(sl_buffer_atr) *
                    atr
                )

                entry = proximal

                risk = sl - entry

                if risk <= 0:
                    continue

                tp = (
                    entry -
                    float(target_rr) *
                    risk
                )

            # ------------------------------------------------
            # SCORE FILTER
            # ------------------------------------------------

            if score < int(min_valid_score):
                continue

            hq = (
                "HQ"
                if score >= int(hq_score_threshold)
                else "Standard"
            )

            # ------------------------------------------------
            # STATE
            # ------------------------------------------------

            created_index = x.index[i]

            state, touches = get_zone_state(
                x,
                proximal,
                distal,
                zone_type,
                created_index
            )

            # ------------------------------------------------
            # POSITION SIZE
            # ------------------------------------------------

            qty = calculate_position_size(
                entry,
                sl
            )

            # ------------------------------------------------
            # CURRENT PRICE
            # ------------------------------------------------

            current_price = float(
                x["close"].iloc[-1]
            )

            # Distance to zone
            if current_price < min(
                proximal,
                distal
            ):

                distance = (
                    min(proximal, distal) -
                    current_price
                )

            elif current_price > max(
                proximal,
                distal
            ):

                distance = (
                    current_price -
                    max(proximal, distal)
                )

            else:

                distance = 0

            distance_pct = (
                distance /
                current_price *
                100
                if current_price > 0
                else 0
            )

            # ------------------------------------------------
            # ENTRY STATUS
            # ------------------------------------------------

            if zone_type == "
