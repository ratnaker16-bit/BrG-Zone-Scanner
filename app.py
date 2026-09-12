import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import time


# ============================================================
# BrG Trading Zone Screener V1.1
# Demand / Supply Zone Screener
# RBR • DBR • DBD • RBD
# 15M • 1H • 2H • 3H • Daily • Weekly
#
# V1.1
# - Pandas 3.x safe sorting
# - Timezone-safe Created timestamp
# - Numeric type normalization
# - Safe deduplication
# ============================================================


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="BrG Trading Zone",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📊 BrG Trading Zone Screener V1.1")

st.caption(
    "Demand / Supply Zone Screener | "
    "RBR • DBR • DBD • RBD | "
    "15M • 1H • 2H • 3H • Daily • Weekly"
)


# ============================================================
# NIFTY UNIVERSE
# ============================================================

NIFTY200 = sorted(set([
    "ADANIENT",
    "ADANIPORTS",
    "APOLLOHOSP",
    "ASIANPAINT",
    "AXISBANK",
    "BAJAJ-AUTO",
    "BAJFINANCE",
    "BAJAJFINSV",
    "BEL",
    "BHARTIARTL",
    "CIPLA",
    "COALINDIA",
    "DRREDDY",
    "EICHERMOT",
    "ETERNAL",
    "GRASIM",
    "HCLTECH",
    "HDFCBANK",
    "HDFCLIFE",
    "HEROMOTOCO",
    "HINDALCO",
    "HINDUNILVR",
    "ICICIBANK",
    "INDUSINDBK",
    "INFY",
    "ITC",
    "JIOFIN",
    "JSWSTEEL",
    "KOTAKBANK",
    "LT",
    "M&M",
    "MARUTI",
    "NESTLEIND",
    "NTPC",
    "ONGC",
    "POWERGRID",
    "RELIANCE",
    "SBILIFE",
    "SBIN",
    "SHRIRAMFIN",
    "SUNPHARMA",
    "TATACONSUM",
    "TATASTEEL",
    "TCS",
    "TECHM",
    "TITAN",
    "TRENT",
    "ULTRACEMCO",
    "WIPRO",

    "ABB",
    "AMBUJACEM",
    "BANKBARODA",
    "BOSCHLTD",
    "CANBK",
    "CGPOWER",
    "CHOLAFIN",
    "COLPAL",
    "DABUR",
    "DIVISLAB",
    "DLF",
    "DMART",
    "GAIL",
    "GODREJCP",
    "GODREJPROP",
    "HAL",
    "HAVELLS",
    "ICICIGI",
    "ICICIPRULI",
    "INDHOTEL",
    "INDIANB",
    "INDUSTOWER",
    "IOC",
    "IRCTC",
    "JINDALSTEL",
    "JSWENERGY",
    "LICI",
    "LODHA",
    "LUPIN",
    "MARICO",
    "MAXHEALTH",
    "MOTHERSON",
    "MPHASIS",
    "MUTHOOTFIN",
    "NHPC",
    "NMDC",
    "OBEROIRLTY",
    "OFSS",
    "OIL",
    "PAGEIND",
    "PAYTM",
    "PERSISTENT",
    "PFC",
    "PIDILITIND",
    "PIIND",
    "PNB",
    "POLYCAB",
    "RECLTD",
    "SAIL",
    "SBICARD",
    "SIEMENS",
    "SRF",
    "SUPREMEIND",
    "TATAPOWER",
    "TORNTPHARM",
    "TORNTPOWER",
    "TVSMOTOR",
    "UNITEDSPIRITS",
    "VEDL",
    "VOLTAS",

    "ABCAPITAL",
    "ABFRL",
    "ACC",
    "ALKEM",
    "APLAPOLLO",
    "ASHOKLEY",
    "ASTRAL",
    "AUROPHARMA",
    "BALKRISIND",
    "BANDHANBNK",
    "BATAINDIA",
    "BHARATFORG",
    "BIOCON",
    "BLUESTARCO",
    "BSE",
    "CAMS",
    "CDSL",
    "CENTRALBK",
    "CESC",
    "COFORGE",
    "CONCOR",
    "COROMANDEL",
    "CROMPTON",
    "CYIENT",
    "DALBHARAT",
    "DEEPAKNTR",
    "DELHIVERY",
    "ESCORTS",
    "EXIDEIND",
    "FEDERALBNK",
    "FORTIS",
    "GLENMARK",
    "GMRINFRA",
    "GNFC",
    "GODFRYPHLP",
    "GUJGASLTD",
    "IDFCFIRSTB",
    "IEX",
    "IGL",
    "INDIAMART",
    "IPCALAB",
    "IRFC",
    "JUBLFOOD",
    "KALYANKJIL",
    "KEI",
    "KPITTECH",
    "LAURUSLABS",
    "LICHSGFIN",
    "LTIM",
    "MANAPPURAM",
    "MCX",
    "METROPOLIS",
    "MGL",
    "MRF",
    "NATIONALUM",
    "NAVINFLUOR",
    "NLCINDIA",
    "OLECTRA",
    "PEL",
    "PHOENIXLTD",
    "POLYMED",
    "PRESTIGE",
    "RAMCOCEM",
    "RBLBANK",
    "SONACOMS",
    "STARHEALTH",
    "SUMICHEM",
    "SUNDARMFIN",
    "SUNTV",
    "TATACHEM",
    "TATACOMM",
    "TATAELXSI",
    "THERMAX",
    "TIMKEN",
    "UBL",
    "UNOMINDA",
    "UPL",
    "VBL",
    "VINATIORGA",
    "ZEEL"
]))


# ============================================================
# SETTINGS
# ============================================================

st.sidebar.header("⚙️ Zone Settings")

account_capital = st.sidebar.number_input(
    "Account Capital ₹",
    min_value=1000.0,
    value=25000.0,
    step=1000.0
)

risk_pct = st.sidebar.number_input(
    "Risk % per Trade",
    min_value=0.1,
    max_value=10.0,
    value=0.5,
    step=0.1
)

target_rr = st.sidebar.number_input(
    "Target RR",
    min_value=0.5,
    max_value=20.0,
    value=5.0,
    step=0.5
)

atr_period = st.sidebar.number_input(
    "ATR Period",
    min_value=5,
    max_value=50,
    value=14,
    step=1
)

vol_sma_period = st.sidebar.number_input(
    "Volume SMA Period",
    min_value=5,
    max_value=100,
    value=20,
    step=1
)


# ============================================================
# BASE / LEG SETTINGS
# ============================================================

st.sidebar.subheader("Base / Leg")

min_base_count = st.sidebar.number_input(
    "Min Base Count",
    min_value=1,
    max_value=3,
    value=1,
    step=1
)

max_base_count = st.sidebar.number_input(
    "Max Base Count",
    min_value=1,
    max_value=3,
    value=3,
    step=1
)

leg_in_min_atr = st.sidebar.number_input(
    "Leg-In Min ATR",
    min_value=0.5,
    max_value=5.0,
    value=1.0,
    step=0.1
)

leg_in_to_base_mult = st.sidebar.number_input(
    "Leg-In / Base Size",
    min_value=1.0,
    max_value=5.0,
    value=2.0,
    step=0.1
)

leg_in_body_pct = st.sidebar.number_input(
    "Leg-In Min Body %",
    min_value=0.3,
    max_value=0.95,
    value=0.60,
    step=0.05
)

max_base_atr_mult = st.sidebar.number_input(
    "Max Base TR / ATR",
    min_value=0.5,
    max_value=3.0,
    value=1.0,
    step=0.1
)


# ============================================================
# LEG-OUT SETTINGS
# ============================================================

st.sidebar.subheader("Leg-Out")

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

hq_leg_out_mult = st.sidebar.number_input(
    "HQ Leg-Out / Leg-In",
    min_value=1.0,
    max_value=5.0,
    value=2.0,
    step=0.1
)

hq_leg_in_atr_mult = st.sidebar.number_input(
    "HQ Leg-In ATR",
    min_value=1.0,
    max_value=5.0,
    value=1.5,
    step=0.1
)

max_wick_pct = st.sidebar.number_input(
    "Max Wick %",
    min_value=0.05,
    max_value=0.80,
    value=0.30,
    step=0.05
)

min_clv_pct = st.sidebar.number_input(
    "Min CLV %",
    min_value=0.30,
    max_value=0.95,
    value=0.60,
    step=0.05
)


# ============================================================
# IMBALANCE
# ============================================================

st.sidebar.subheader("Imbalance")

use_imbalance = st.sidebar.checkbox(
    "Use Imbalance",
    value=True
)

max_imbalance_mult = st.sidebar.number_input(
    "Max Imbalance / ATR",
    min_value=0.5,
    max_value=3.0,
    value=1.0,
    step=0.1
)

reject_opposite_cover = st.sidebar.number_input(
    "Reject Opposite Cover %",
    min_value=0.1,
    max_value=1.0,
    value=0.50,
    step=0.05
)


# ============================================================
# SCORE
# ============================================================

st.sidebar.subheader("Score")

min_valid_score = st.sidebar.number_input(
    "Minimum Valid Score",
    min_value=0,
    max_value=150,
    value=40,
    step=5
)

hq_score_threshold = st.sidebar.number_input(
    "HQ Score Threshold",
    min_value=50,
    max_value=150,
    value=90,
    step=5
)

leg_out_body_heavy_pct = st.sidebar.number_input(
    "Leg-Out Body Heavy %",
    min_value=0.40,
    max_value=0.95,
    value=0.60,
    step=0.05
)

tested_retrace_pct = st.sidebar.number_input(
    "Tested Leg-Out Retrace %",
    min_value=0.10,
    max_value=1.00,
    value=0.50,
    step=0.05
)

max_tested_count = st.sidebar.number_input(
    "Maximum Tests",
    min_value=1,
    max_value=10,
    value=2,
    step=1
)

sl_buffer_atr = st.sidebar.number_input(
    "SL Buffer ATR",
    min_value=0.0,
    max_value=1.0,
    value=0.10,
    step=0.05
)


# ============================================================
# TIMEFRAMES
# ============================================================

TIMEFRAMES = [
    "15M",
    "1H",
    "2H",
    "3H",
    "Daily",
    "Weekly"
]


# ============================================================
# HELPERS
# ============================================================

def add_ns(symbol):

    symbol = str(symbol).upper().strip()

    if symbol.endswith(".NS"):
        return symbol

    return symbol + ".NS"


def true_range(df):

    previous_close = df["close"].shift(1)

    tr1 = df["high"] - df["low"]

    tr2 = (
        df["high"] -
        previous_close
    ).abs()

    tr3 = (
        df["low"] -
        previous_close
    ).abs()

    return pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)


def rma(series, length):

    return series.ewm(
        alpha=1.0 / float(length),
        adjust=False,
        min_periods=length
    ).mean()


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
        return 0.0

    return candle_body(row) / rng


def is_bull(row):

    return (
        float(row["close"]) >
        float(row["open"])
    )


def is_bear(row):

    return (
        float(row["open"]) >
        float(row["close"])
    )


def clv_bull(row):

    rng = candle_range(row)

    if rng <= 0:
        return 0.0

    return (
        float(row["close"]) -
        float(row["low"])
    ) / rng


def clv_bear(row):

    rng = candle_range(row)

    if rng <= 0:
        return 0.0

    return (
        float(row["high"]) -
        float(row["close"])
    ) / rng


def total_wick_pct(row):

    rng = candle_range(row)

    if rng <= 0:
        return 0.0

    upper = (
        float(row["high"]) -
        max(
            float(row["open"]),
            float(row["close"])
        )
    )

    lower = (
        min(
            float(row["open"]),
            float(row["close"])
        ) -
        float(row["low"])
    )

    return (
        upper + lower
    ) / rng


def body_high(row):

    return max(
        float(row["open"]),
        float(row["close"])
    )


def body_low(row):

    return min(
        float(row["open"]),
        float(row["close"])
    )


# ============================================================
# DATA CLEANING
# ============================================================

def clean_dataframe(df):

    if df is None or df.empty:
        return pd.DataFrame()

    x = df.copy()

    # --------------------------------------------------------
    # MultiIndex columns
    # --------------------------------------------------------

    if isinstance(
        x.columns,
        pd.MultiIndex
    ):

        level0 = [
            str(v).lower()
            for v in x.columns.get_level_values(0)
        ]

        level1 = [
            str(v).lower()
            for v in x.columns.get_level_values(1)
        ]

        if "open" in level0:

            x.columns = level0

        elif "open" in level1:

            x.columns = level1

        else:

            x.columns = [
                str(c[0]).lower()
                for c in x.columns
            ]

    else:

        x.columns = [
            str(c).lower()
            for c in x.columns
        ]

    # --------------------------------------------------------
    # Adj Close
    # --------------------------------------------------------

    if "adj close" in x.columns:

        x = x.drop(
            columns=["adj close"],
            errors="ignore"
        )

    required = [
        "open",
        "high",
        "low",
        "close"
    ]

    for column in required:

        if column not in x.columns:

            return pd.DataFrame()

    # --------------------------------------------------------
    # Volume
    # --------------------------------------------------------

    if "volume" not in x.columns:

        x["volume"] = 0.0

    x = x[
        [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    ].copy()

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    for column in x.columns:

        x[column] = pd.to_numeric(
            x[column],
            errors="coerce"
        )

    x = x.dropna(
        subset=[
            "open",
            "high",
            "low",
            "close"
        ]
    )

    # --------------------------------------------------------
    # Datetime index
    # --------------------------------------------------------

    if not isinstance(
        x.index,
        pd.DatetimeIndex
    ):

        x.index = pd.to_datetime(
            x.index,
            errors="coerce"
        )

    x = x[
        ~x.index.isna()
    ]

    # --------------------------------------------------------
    # Normalize timezone
    #
    # इससे 15M / 1H / Daily / Weekly के बीच
    # datetime comparison safe रहता है।
    # --------------------------------------------------------

    try:

        if x.index.tz is not None:

            x.index = x.index.tz_convert(
                "UTC"
            )

        else:

            x.index = x.index.tz_localize(
                "UTC"
            )

    except Exception:

        try:

            x.index = pd.DatetimeIndex(
                x.index
            ).tz_localize(
                "UTC"
            )

        except Exception:

            pass

    x = x.sort_index()

    return x


# ============================================================
# YAHOO DOWNLOAD
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def download_batch(
    symbols,
    interval,
    period
):

    if not symbols:
        return {}

    tickers = [
        add_ns(symbol)
        for symbol in symbols
    ]

    try:

        data = yf.download(
            tickers=tickers,
            period=period,
            interval=interval,
            auto_adjust=False,
            group_by="ticker",
            threads=True,
            progress=False
        )

    except Exception:

        return {}

    if data is None or data.empty:

        return {}

    result = {}

    # ========================================================
    # MULTI SYMBOL
    # ========================================================

    if isinstance(
        data.columns,
        pd.MultiIndex
    ):

        first_level = set(
            str(x)
            for x in
            data.columns.get_level_values(0)
        )

        second_level = set(
            str(x)
            for x in
            data.columns.get_level_values(1)
        )

        for original in symbols:

            ticker = add_ns(
                original
            )

            try:

                if ticker in first_level:

                    part = data[ticker]

                elif ticker in second_level:

                    part = data.xs(
                        ticker,
                        axis=1,
                        level=1
                    )

                else:

                    continue

                part = clean_dataframe(
                    part
                )

                if not part.empty:

                    result[
                        original
                    ] = part

            except Exception:

                continue

    # ========================================================
    # SINGLE SYMBOL
    # ========================================================

    else:

        if len(symbols) == 1:

            part = clean_dataframe(
                data
            )

            if not part.empty:

                result[
                    symbols[0]
                ] = part

    return result


# ============================================================
# RESAMPLE 1H -> 2H / 3H
# ============================================================

def resample_hourly(
    df,
    hours
):

    if df is None or df.empty:

        return pd.DataFrame()

    x = df.copy()

    x = x.sort_index()

    result = x.resample(
        f"{hours}h",
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
# PREPARE ALL TIMEFRAMES
# ============================================================

def prepare_symbol_data(
    symbol,
    data_15m,
    data_1h,
    data_daily,
    data_weekly
):

    result = {}

    if symbol in data_15m:

        result["15M"] = (
            data_15m[symbol]
        )

    if symbol in data_1h:

        df1h = data_1h[symbol]

        result["1H"] = df1h

        df2h = resample_hourly(
            df1h,
            2
        )

        if not df2h.empty:

            result["2H"] = df2h

        df3h = resample_hourly(
            df1h,
            3
        )

        if not df3h.empty:

            result["3H"] = df3h

    if symbol in data_daily:

        result["Daily"] = (
            data_daily[symbol]
        )

    if symbol in data_weekly:

        result["Weekly"] = (
            data_weekly[symbol]
        )

    return result


# ============================================================
# ZONE SCANNER
# ============================================================

def scan_dataframe(
    df,
    symbol,
    timeframe
):

    if df is None or df.empty:

        return []

    x = df.copy()

    minimum_bars = max(
        60,
        int(atr_period) + 20
    )

    if len(x) < minimum_bars:

        return []

    # --------------------------------------------------------
    # ATR / TR / Volume
    # --------------------------------------------------------

    x["TR"] = true_range(x)

    x["ATR"] = rma(
        x["TR"],
        int(atr_period)
    )

    x["VOL_SMA"] = (
        x["volume"]
        .rolling(
            int(vol_sma_period)
        )
        .mean()
    )

    zones = []

    min_base = max(
        1,
        min(
            int(min_base_count),
            int(max_base_count)
        )
    )

    max_base = min(
        3,
        max(
            min_base,
            int(max_base_count)
        )
    )

    # ========================================================
    # LEG-OUT LOOP
    # ========================================================

    for i in range(
        max(
            int(atr_period) + 5,
            max_base + 5
        ),
        len(x)
    ):

        leg_out = x.iloc[i]

        if not np.isfinite(
            leg_out["ATR"]
        ):

            continue

        zone_found = False

        # ====================================================
        # BASE COUNT
        # ====================================================

        for b_count in range(
            min_base,
            max_base + 1
        ):

            leg_in_idx = (
                i -
                b_count -
                1
            )

            prev_idx = (
                leg_in_idx -
                1
            )

            base_start = (
                i -
                b_count
            )

            base_end = i

            if leg_in_idx < 1:

                continue

            if base_start < 0:

                continue

            leg_in = x.iloc[
                leg_in_idx
            ]

            base = x.iloc[
                base_start:base_end
            ]

            if len(base) != b_count:

                continue

            # =================================================
            # LEG-IN
            # =================================================

            leg_in_tr = float(
                leg_in["TR"]
            )

            leg_in_atr = float(
                leg_in["ATR"]
            )

            if (
                not np.isfinite(
                    leg_in_atr
                )
                or
                leg_in_atr <= 0
            ):

                continue

            if candle_range(
                leg_in
            ) <= 0:

                continue

            if body_pct(
                leg_in
            ) < float(
                leg_in_body_pct
            ):

                continue

            leg_in_bull = is_bull(
                leg_in
            )

            leg_in_bear = is_bear(
                leg_in
            )

            if not (
                leg_in_bull or
                leg_in_bear
            ):

                continue

            # =================================================
            # OPPOSITE COVER
            # =================================================

            if prev_idx >= 0:

                previous = x.iloc[
                    prev_idx
                ]

                opposite = (
                    (
                        leg_in_bull
                        and
                        is_bear(previous)
                    )
                    or
                    (
                        leg_in_bear
                        and
                        is_bull(previous)
                    )
                )

                if opposite:

                    overlap_high = min(
                        body_high(
                            previous
                        ),
                        float(
                            leg_in["high"]
                        )
                    )

                    overlap_low = max(
                        body_low(
                            previous
                        ),
                        float(
                            leg_in["low"]
                        )
                    )

                    overlap = max(
                        0.0,
                        overlap_high -
                        overlap_low
                    )

                    leg_in_range = (
                        candle_range(
                            leg_in
                        )
                    )

                    cover_pct = (
                        overlap /
                        leg_in_range
                        if leg_in_range > 0
                        else 0
                    )

                    if cover_pct >= float(
                        reject_opposite_cover
                    ):

                        continue

            # =================================================
            # BASE
            # =================================================

            base_high = float(
                base["high"].max()
            )

            base_low = float(
                base["low"].min()
            )

            max_base_tr = float(
                base["TR"].max()
            )

            if max_base_tr <= 0:

                continue

            base_valid = True

            for _, candle in base.iterrows():

                atr_b = float(
                    candle["ATR"]
                )

                if (
                    not np.isfinite(
                        atr_b
                    )
                    or
                    atr_b <= 0
                ):

                    base_valid = False

                    break

                if float(
                    candle["TR"]
                ) > (
                    float(
                        max_base_atr_mult
                    ) *
                    atr_b
                ):

                    base_valid = False

                    break

            if not base_valid:

                continue

            # =================================================
            # LEG-IN SIZE VS BASE
            # =================================================

            effective_base_mult = (
                1.5
                if b_count == 1
                else float(
                    leg_in_to_base_mult
                )
            )

            if leg_in_tr < (
                effective_base_mult *
                max_base_tr
            ):

                continue

            if leg_in_tr < (
                float(
                    leg_in_min_atr
                ) *
                leg_in_atr
            ):

                continue

            # =================================================
            # LEG-OUT
            # =================================================

            leg_out_tr = float(
                leg_out["TR"]
            )

            leg_out_atr = float(
                leg_out["ATR"]
            )

            if (
                not np.isfinite(
                    leg_out_atr
                )
                or
                leg_out_atr <= 0
            ):

                continue

            leg_out_bull = is_bull(
                leg_out
            )

            leg_out_bear = is_bear(
                leg_out
            )

            if not (
                leg_out_bull or
                leg_out_bear
            ):

                continue

            # =================================================
            # EXPLOSIVE LEG-OUT
            # =================================================

            if leg_out_tr < (
                float(
                    leg_out_tr_mult
                ) *
                leg_out_atr
            ):

                continue

            if leg_out_tr < (
                float(
                    leg_out_min_ratio
                ) *
                leg_in_tr
            ):

                continue

            # =================================================
            # WICK
            # =================================================

            if total_wick_pct(
                leg_out
            ) > float(
                max_wick_pct
            ):

                continue

            # =================================================
            # VOLUME
            # =================================================

            leg_out_volume = float(
                leg_out["volume"]
            )

            leg_in_volume = float(
                leg_in["volume"]
            )

            passes_volume = (
                leg_out_volume >
                leg_in_volume
            )

            if not passes_volume:

                continue

            # =================================================
            # CLV
            # =================================================

            if leg_out_bull:

                leg_out_clv = clv_bull(
                    leg_out
                )

                if leg_out_clv < float(
                    min_clv_pct
                ):

                    continue

            else:

                leg_out_clv = clv_bear(
                    leg_out
                )

                if leg_out_clv < float(
                    min_clv_pct
                ):

                    continue

            # =================================================
            # IMBALANCE
            # =================================================

            has_imbalance = True

            genuine_gap = False

            gap_size = 0.0

            if use_imbalance:

                if leg_out_bull:

                    genuine_gap = (
                        float(
                            leg_out["low"]
                        )
                        >
                        base_high
                    )

                    gap_condition = (
                        genuine_gap
                        or
                        (
                            float(
                                leg_out["close"]
                            )
                            >
                            float(
                                leg_in["high"]
                            )
                        )
                    )

                    gap_size = max(
                        0.0,
                        float(
                            leg_out["low"]
                        )
                        -
                        base_high
                    )

                else:

                    genuine_gap = (
                        float(
                            leg_out["high"]
                        )
                        <
                        base_low
                    )

                    gap_condition = (
                        genuine_gap
                        or
                        (
                            float(
                                leg_out["close"]
                            )
                            <
                            float(
                                leg_in["low"]
                            )
                        )
                    )

                    gap_size = max(
                        0.0,
                        base_low -
                        float(
                            leg_out["high"]
                        )
                    )

                has_imbalance = (
                    gap_condition
                )

                if genuine_gap:

                    if gap_size > (
                        float(
                            max_imbalance_mult
                        ) *
                        leg_in_tr
                    ):

                        continue

            if not has_imbalance:

                continue

            # =================================================
            # ENGULF CHECK
            # =================================================

            leg_out_body_high = (
                body_high(
                    leg_out
                )
            )

            leg_out_body_low = (
                body_low(
                    leg_out
                )
            )

            body_engulfs_base = (
                leg_out_body_low <=
                base_low
                and
                leg_out_body_high >=
                base_high
            )

            if (
                body_engulfs_base
                and
                not genuine_gap
            ):

                continue

            # =================================================
            # PATTERN
            # =================================================

            leg_in_range = candle_range(
                leg_in
            )

            if leg_in_range <= 0:

                continue

            leg_in_bull_clv = (
                (
                    float(
                        leg_in["close"]
                    )
                    -
                    float(
                        leg_in["low"]
                    )
                )
                /
                leg_in_range
            )

            leg_in_bear_clv = (
                (
                    float(
                        leg_in["high"]
                    )
                    -
                    float(
                        leg_in["close"]
                    )
                )
                /
                leg_in_range
            )

            is_rbr = (
                leg_in_bull
                and
                leg_in_bull_clv >= float(
                    min_clv_pct
                )
                and
                leg_out_bull
            )

            is_dbr = (
                leg_in_bear
                and
                leg_in_bear_clv >= float(
                    min_clv_pct
                )
                and
                leg_out_bull
            )

            is_dbd = (
                leg_in_bear
                and
                leg_in_bear_clv >= float(
                    min_clv_pct
                )
                and
                leg_out_bear
            )

            is_rbd = (
                leg_in_bull
                and
                leg_in_bull_clv >= float(
                    min_clv_pct
                )
                and
                leg_out_bear
            )

            if is_rbr:

                pattern = "RBR"

            elif is_dbr:

                pattern = "DBR"

            elif is_dbd:

                pattern = "DBD"

            elif is_rbd:

                pattern = "RBD"

            else:

                continue

            # =================================================
            # ZONE TYPE
            # =================================================

            zone_type = (
                "Demand"
                if leg_out_bull
                else
                "Supply"
            )

            category = (
                "Continuation"
                if pattern in [
                    "RBR",
                    "DBD"
                ]
                else
                "Reversal"
            )

            # =================================================
            # SCORE
            # =================================================

            score = 0

            if b_count == 1:

                score += 15

            if leg_in_tr >= (
                float(
                    hq_leg_in_atr_mult
                ) *
                leg_in_atr
            ):

                score += 10

            if leg_out_tr >= (
                float(
                    hq_leg_out_mult
                ) *
                leg_in_tr
            ):

                score += 15

            if (
                leg_in_tr >=
                2.0 * max_base_tr
                and
                leg_out_tr >=
                2.0 * leg_in_tr
            ):

                score += 15

            volume_sma = float(
                leg_out["VOL_SMA"]
            )

            if (
                np.isfinite(
                    volume_sma
                )
                and
                volume_sma > 0
            ):

                if (
                    leg_out_volume >
                    volume_sma
                ):

                    score += 10

            # ------------------------------------------------
            # Strong close
            # ------------------------------------------------

            if leg_out_bull:

                body_position = (
                    float(
                        leg_out["close"]
                    )
                    -
                    float(
                        leg_out["low"]
                    )
                ) / candle_range(
                    leg_out
                )

                own_body_pct = body_pct(
                    leg_out
                )

                if pattern == "DBR":

                    if (
                        body_position >= 0.80
                        or
                        own_body_pct >=
                        float(
                            leg_out_body_heavy_pct
                        )
                    ):

                        score += 15

                elif body_position >= 0.80:

                    score += 15

            else:

                body_position = (
                    float(
                        leg_out["high"]
                    )
                    -
                    float(
                        leg_out["close"]
                    )
                ) / candle_range(
                    leg_out
                )

                if body_position >= 0.80:

                    score += 15

            # ------------------------------------------------
            # Opposite-color base
            # ------------------------------------------------

            opposite_base = False

            for _, base_candle in base.iterrows():

                if (
                    leg_out_bull
                    and
                    is_bear(
                        base_candle
                    )
                ):

                    opposite_base = True

                    break

                if (
                    leg_out_bear
                    and
                    is_bull(
                        base_candle
                    )
                ):

                    opposite_base = True

                    break

            if opposite_base:

                score += 10

            # Base quality
            score += 10

            # Genuine gap
            if genuine_gap:

                score += 10

                if i > 0:

                    try:

                        previous_time = (
                            x.index[i - 1]
                        )

                        current_time = (
                            x.index[i]
                        )

                        gap_hours = (
                            current_time -
                            previous_time
                        ).total_seconds() / 3600.0

                        if gap_hours > 20:

                            score += 15

                    except Exception:

                        pass

            # ------------------------------------------------
            # Minimum score
            # ------------------------------------------------

            if score < int(
                min_valid_score
            ):

                continue

            is_hq = (
                score >= int(
                    hq_score_threshold
                )
            )

            # =================================================
            # ZONE LEVELS
            # =================================================

            if zone_type == "Demand":

                proximal = base_high

                distal = base_low

                sl = (
                    distal -
                    float(
                        sl_buffer_atr
                    ) *
                    leg_out_atr
                )

                entry = proximal

                risk = (
                    entry -
                    sl
                )

                if risk <= 0:

                    continue

                tp = (
                    entry +
                    float(target_rr) *
                    risk
                )

                test_level = (
                    float(
                        leg_out["high"]
                    )
                    -
                    float(
                        tested_retrace_pct
                    )
                    *
                    (
                        float(
                            leg_out["high"]
                        )
                        -
                        float(
                            leg_out["low"]
                        )
                    )
                )

            else:

                proximal = base_low

                distal = base_high

                sl = (
                    distal +
                    float(
                        sl_buffer_atr
                    ) *
                    leg_out_atr
                )

                entry = proximal

                risk = (
                    sl -
                    entry
                )

                if risk <= 0:

                    continue

                tp = (
                    entry -
                    float(target_rr) *
                    risk
                )

                test_level = (
                    float(
                        leg_out["low"]
                    )
                    +
                    float(
                        tested_retrace_pct
                    )
                    *
                    (
                        float(
                            leg_out["high"]
                        )
                        -
                        float(
                            leg_out["low"]
                        )
                    )
                )

            # =================================================
            # CURRENT PRICE
            # =================================================

            current_price = float(
                x["close"].iloc[-1]
            )

            zone_top = max(
                proximal,
                distal
            )

            zone_bottom = min(
                proximal,
                distal
            )

            if current_price < zone_bottom:

                distance = (
                    zone_bottom -
                    current_price
                )

            elif current_price > zone_top:

                distance = (
                    current_price -
                    zone_top
                )

            else:

                distance = 0.0

            distance_pct = (
                distance /
                current_price *
                100.0
                if current_price > 0
                else 0.0
            )

            # =================================================
            # STATE
            # =================================================

            future = x.iloc[
                i + 1:
            ]

            touch_count = 0

            state = "Fresh"

            for _, future_candle in future.iterrows():

                future_high = float(
                    future_candle["high"]
                )

                future_low = float(
                    future_candle["low"]
                )

                if zone_type == "Demand":

                    if future_low <= distal:

                        state = "Broken"

                        break

                    if future_low <= test_level:

                        touch_count += 1

                else:

                    if future_high >= distal:

                        state = "Broken"

                        break

                    if future_high >= test_level:

                        touch_count += 1

            if state != "Broken":

                if touch_count == 0:

                    state = "Fresh"

                elif touch_count <= int(
                    max_tested_count
                ):

                    state = "Tested"

                else:

                    state = "Broken"

            # =================================================
            # ENTRY STATUS
            # =================================================

            if zone_type == "Demand":

                if (
                    distal <=
                    current_price <=
                    proximal
                ):

                    entry_status = "IN ZONE"

                elif current_price < proximal:

                    entry_status = "NEAR"

                else:

                    entry_status = "ABOVE"

            else:

                if (
                    proximal <=
                    current_price <=
                    distal
                ):

                    entry_status = "IN ZONE"

                elif current_price > proximal:

                    entry_status = "NEAR"

                else:

                    entry_status = "BELOW"

            # =================================================
            # POSITION SIZE
            # =================================================

            risk_money = (
                float(account_capital) *
                float(risk_pct) /
                100.0
            )

            risk_per_share = abs(
                entry -
                sl
            )

            if risk_per_share > 0:

                quantity = int(
                    risk_money /
                    risk_per_share
                )

            else:

                quantity = 0

            # =================================================
            # CREATE ZONE RECORD
            # =================================================

            zones.append({

                "Symbol": str(symbol),

                "Timeframe": str(
                    timeframe
                ),

                "Created": x.index[i],

                "Pattern": str(
                    pattern
                ),

                "Category": str(
                    category
                ),

                "Type": str(
                    zone_type
                ),

                "Direction": (
                    "Bullish"
                    if zone_type ==
                    "Demand"
                    else
                    "Bearish"
                ),

                "Score": int(
                    score
                ),

                "HQ": (
                    "HQ"
                    if is_hq
                    else
                    "Standard"
                ),

                "State": str(
                    state
                ),

                "Touches": int(
                    touch_count
                ),

                "Current": float(
                    current_price
                ),

                "Proximal": float(
                    proximal
                ),

                "Distal": float(
                    distal
                ),

                "Entry": float(
                    entry
                ),

                "SL": float(
                    sl
                ),

                "TP": float(
                    tp
                ),

                "Risk": float(
                    risk_per_share
                ),

                "Qty": int(
                    quantity
                ),

                "Distance": float(
                    distance
                ),

                "DistancePct": float(
                    distance_pct
                ),

                "EntryStatus": str(
                    entry_status
                ),

                "Gap": bool(
                    genuine_gap
                )
            })

            zone_found = True

            # Strongest base for this leg-out
            break

        if zone_found:

            continue

    return zones


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate_zones(zones):

    if not zones:

        return []

    df = pd.DataFrame(
        zones
    )

    if df.empty:

        return []

    # ========================================================
    # SAFE TEXT TYPES
    # ========================================================

    text_columns = [
        "Symbol",
        "Timeframe",
        "Type",
        "Pattern",
        "Category",
        "Direction",
        "HQ",
        "State",
        "EntryStatus"
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .fillna("")
            )

    # ========================================================
    # SAFE SCORE
    # ========================================================

    if "Score" in df.columns:

        df["Score"] = pd.to_numeric(
            df["Score"],
            errors="coerce"
        ).fillna(0)

    # ========================================================
    # SAFE CREATED DATETIME
    #
    # IMPORTANT:
    # सभी timestamps UTC में normalize होंगे।
    # इससे Pandas 3.x Categorical error नहीं आएगा।
    # ========================================================

    if "Created" in df.columns:

        df["Created"] = pd.to_datetime(
            df["Created"],
            errors="coerce",
            utc=True
        )

        df["Created_Sort"] = (
            df["Created"].fillna(
                pd.Timestamp(
                    "1970-01-01",
                    tz="UTC"
                )
            )
        )

    else:

        df["Created_Sort"] = pd.Timestamp(
            "1970-01-01",
            tz="UTC"
        )

    # ========================================================
    # SAFE NUMERIC COLUMNS
    # ========================================================

    numeric_columns = [
        "Proximal",
        "Distal",
        "Entry",
        "SL",
        "TP",
        "Risk",
        "Current",
        "Distance",
        "DistancePct",
        "Touches"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # ========================================================
    # SAFE SORT
    #
    # Original problematic code:
    #
    # df.sort_values(...)
    #
    # is replaced by normalized columns.
    # ========================================================

    df = df.sort_values(
        by=[
            "Symbol",
            "Timeframe",
            "Score",
            "Created_Sort"
        ],
        ascending=[
            True,
            True,
            False,
            False
        ],
        kind="mergesort"
    ).reset_index(
        drop=True
    )

    # ========================================================
    # OVERLAPPING ZONE DEDUPLICATION
    # ========================================================

    keep = []

    for _, row in df.iterrows():

        duplicate = False

        for old in keep:

            if (
                row["Symbol"] ==
                old["Symbol"]
                and
                row["Timeframe"] ==
                old["Timeframe"]
                and
                row["Type"] ==
                old["Type"]
            ):

                try:

                    top1 = max(
                        float(
                            row["Proximal"]
                        ),
                        float(
                            row["Distal"]
                        )
                    )

                    bottom1 = min(
                        float(
                            row["Proximal"]
                        ),
                        float(
                            row["Distal"]
                        )
                    )

                    top2 = max(
                        float(
                            old["Proximal"]
                        ),
                        float(
                            old["Distal"]
                        )
                    )

                    bottom2 = min(
                        float(
                            old["Proximal"]
                        ),
                        float(
                            old["Distal"]
                        )
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    continue

                overlap = (
                    min(
                        top1,
                        top2
                    )
                    >=
                    max(
                        bottom1,
                        bottom2
                    )
                )

                if overlap:

                    duplicate = True

                    break

        if not duplicate:

            keep.append(
                row
            )

    # ========================================================
    # CONVERT BACK TO DICTIONARY
    # ========================================================

    final_zones = []

    for row in keep:

        row_dict = row.to_dict()

        row_dict.pop(
            "Created_Sort",
            None
        )

        final_zones.append(
            row_dict
        )

    return final_zones


# ============================================================
# FORMAT RESULT
# ============================================================

def format_result(df):

    if df.empty:

        return df

    out = df.copy()

    numeric_columns = [
        "Current",
        "Proximal",
        "Distal",
        "Entry",
        "SL",
        "TP",
        "Risk",
        "Distance",
        "DistancePct"
    ]

    for column in numeric_columns:

        if column in out.columns:

            out[column] = pd.to_numeric(
                out[column],
                errors="coerce"
            ).round(2)

    return out


# ============================================================
# SCAN ENGINE
# ============================================================

def scan_universe(
    symbols,
    progress_callback=None
):

    # ========================================================
    # 15M
    # ========================================================

    data_15m = download_batch(
        symbols,
        "15m",
        "60d"
    )

    if progress_callback:

        progress_callback(
            0.20,
            "15M data downloaded"
        )

    # ========================================================
    # 1H
    # ========================================================

    data_1h = download_batch(
        symbols,
        "1h",
        "730d"
    )

    if progress_callback:

        progress_callback(
            0.40,
            "1H data downloaded"
        )

    # ========================================================
    # DAILY
    # ========================================================

    data_daily = download_batch(
        symbols,
        "1d",
        "5y"
    )

    if progress_callback:

        progress_callback(
            0.60,
            "Daily data downloaded"
        )

    # ========================================================
    # WEEKLY
    # ========================================================

    data_weekly = download_batch(
        symbols,
        "1wk",
        "10y"
    )

    if progress_callback:

        progress_callback(
            0.70,
            "Weekly data downloaded"
        )

    # ========================================================
    # SCAN
    # ========================================================

    all_results = []

    total = len(symbols)

    for count, symbol in enumerate(
        symbols,
        start=1
    ):

        timeframe_data = (
            prepare_symbol_data(
                symbol,
                data_15m,
                data_1h,
                data_daily,
                data_weekly
            )
        )

        symbol_zones = []

        for timeframe in TIMEFRAMES:

            if timeframe not in (
                timeframe_data
            ):

                continue

            zones = scan_dataframe(
                timeframe_data[
                    timeframe
                ],
                symbol,
                timeframe
            )

            symbol_zones.extend(
                zones
            )

        # ====================================================
        # DEDUPLICATION
        # ====================================================

        symbol_zones = (
            deduplicate_zones(
                symbol_zones
            )
        )

        all_results.extend(
            symbol_zones
        )

        # ====================================================
        # PROGRESS
        # ====================================================

        if progress_callback:

            progress = (
                0.70
                +
                (
                    count /
                    max(
                        total,
                        1
                    )
                )
                *
                0.30
            )

            progress_callback(
                progress,
                f"Scanning {symbol} "
                f"({count}/{total})"
            )

    return all_results


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.divider()

st.sidebar.header(
    "🔎 Scan Mode"
)

scan_mode = st.sidebar.radio(
    "Mode",
    [
        "NIFTY Universe",
        "Single Stock"
    ]
)


# ============================================================
# NIFTY UNIVERSE SCAN
# ============================================================

if scan_mode == "NIFTY Universe":

    st.sidebar.write(
        f"Universe: {len(NIFTY200)} symbols"
    )

    scan_count = st.sidebar.number_input(
        "Stocks to Scan",
        min_value=1,
        max_value=len(NIFTY200),
        value=min(
            50,
            len(NIFTY200)
        ),
        step=10
    )

    selected_symbols = (
        NIFTY200[
            :int(scan_count)
        ]
    )

    scan_button = st.sidebar.button(
        "🚀 Run Zone Scan",
        use_container_width=True
    )

    if scan_button:

        progress_bar = st.progress(
            0.0
        )

        status_box = st.empty()

        def update_progress(
            value,
            message
        ):

            progress_bar.progress(
                min(
                    max(
                        float(value),
                        0.0
                    ),
                    1.0
                )
            )

            status_box.info(
                message
            )

        with st.spinner(
            "Downloading market data..."
        ):

            results = scan_universe(
                selected_symbols,
                update_progress
            )

        progress_bar.progress(
            1.0
        )

        status_box.success(
            "Zone scan completed."
        )

        if results:

            result_df = pd.DataFrame(
                results
            )

            # ------------------------------------------------
            # Active zones only
            # ------------------------------------------------

            if "State" in result_df.columns:

                result_df = result_df[
                    result_df["State"].isin(
                        [
                            "Fresh",
                            "Tested"
                        ]
                    )
                ].copy()

            # ------------------------------------------------
            # HQ rank
            # ------------------------------------------------

            result_df["HQRank"] = (
                result_df["HQ"]
                .eq("HQ")
                .astype(int)
            )

            # ------------------------------------------------
            # Timeframe rank
            # ------------------------------------------------

            timeframe_rank = {

                "Weekly": 6,

                "Daily": 5,

                "3H": 4,

                "2H": 3,

                "1H": 2,

                "15M": 1
            }

            result_df["TF_Rank"] = (
                result_df[
                    "Timeframe"
                ]
                .map(
                    timeframe_rank
                )
                .fillna(0)
            )

            # ------------------------------------------------
            # FINAL SAFE SORT
            # ------------------------------------------------

            result_df["Score"] = (
                pd.to_numeric(
                    result_df[
                        "Score"
                    ],
                    errors="coerce"
                ).fillna(0)
            )

            result_df["DistancePct"] = (
                pd.to_numeric(
                    result_df[
                        "DistancePct"
                    ],
                    errors="coerce"
                ).fillna(
                    999999
                )
            )

            result_df = (
                result_df.sort_values(
                    [
                        "HQRank",
                        "Score",
                        "TF_Rank",
                        "DistancePct"
                    ],
                    ascending=[
                        False,
                        False,
                        False,
                        True
                    ],
                    kind="mergesort"
                )
            )

            st.session_state[
                "brg_results"
            ] = result_df

        else:

            st.session_state[
                "brg_results"
            ] = pd.DataFrame()


# ============================================================
# SINGLE STOCK
# ============================================================

else:

    single_symbol = (
        st.sidebar.text_input(
            "NSE Symbol",
            value="RELIANCE"
        )
        .upper()
        .strip()
    )

    single_button = st.sidebar.button(
        "🚀 Scan Stock",
        use_container_width=True
    )

    if single_button:

        if not single_symbol:

            st.error(
                "Please enter NSE symbol."
            )

        else:

            progress_bar = st.progress(
                0.0
            )

            status_box = st.empty()

            def single_progress(
                value,
                message
            ):

                progress_bar.progress(
                    min(
                        max(
                            float(value),
                            0.0
                        ),
                        1.0
                    )
                )

                status_box.info(
                    message
                )

            with st.spinner(
                f"Scanning {single_symbol}..."
            ):

                results = scan_universe(
                    [single_symbol],
                    single_progress
                )

            progress_bar.progress(
                1.0
            )

            status_box.success(
                "Stock scan completed."
            )

            result_df = pd.DataFrame(
                results
            )

            if not result_df.empty:

                result_df = result_df[
                    result_df[
                        "State"
                    ].isin(
                        [
                            "Fresh",
                            "Tested"
                        ]
                    )
                ].copy()

                result_df["HQRank"] = (
                    result_df["HQ"]
                    .eq("HQ")
                    .astype(int)
                )

                result_df["Score"] = (
                    pd.to_numeric(
                        result_df[
                            "Score"
                        ],
                        errors="coerce"
                    ).fillna(0)
                )

                result_df["DistancePct"] = (
                    pd.to_numeric(
                        result_df[
                            "DistancePct"
                        ],
                        errors="coerce"
                    ).fillna(
                        999999
                    )
                )

                result_df = (
                    result_df.sort_values(
                        [
                            "HQRank",
                            "Score",
                            "DistancePct"
                        ],
                        ascending=[
                            False,
                            False,
                            True
                        ],
                        kind="mergesort"
                    )
                )

            st.session_state[
                "single_results"
            ] = result_df


# ============================================================
# DISPLAY NIFTY RESULTS
# ============================================================

if (
    scan_mode ==
    "NIFTY Universe"
    and
    "brg_results" in
    st.session_state
):

    result = st.session_state[
        "brg_results"
    ]

    if result.empty:

        st.warning(
            "कोई active Demand / Supply zone नहीं मिला."
        )

    else:

        # ====================================================
        # METRICS
        # ====================================================

        total_zones = len(
            result
        )

        hq_count = int(
            (
                result["HQ"] ==
                "HQ"
            ).sum()
        )

        demand_count = int(
            (
                result["Type"] ==
                "Demand"
            ).sum()
        )

        supply_count = int(
            (
                result["Type"] ==
                "Supply"
            ).sum()
        )

        in_zone_count = int(
            (
                result[
                    "EntryStatus"
                ] ==
                "IN ZONE"
            ).sum()
        )

        c1, c2, c3, c4, c5 = (
            st.columns(5)
        )

        c1.metric(
            "Active Zones",
            total_zones
        )

        c2.metric(
            "HQ Zones",
            hq_count
        )

        c3.metric(
            "Demand",
            demand_count
        )

        c4.metric(
            "Supply",
            supply_count
        )

        c5.metric(
            "Price In Zone",
            in_zone_count
        )

        # ====================================================
        # TOP CANDIDATES
        # ====================================================

        st.subheader(
            "🎯 BrG Trade Candidate List"
        )

        candidate_columns = [

            "Symbol",

            "Timeframe",

            "Category",

            "Pattern",

            "Type",

            "Direction",

            "HQ",

            "Score",

            "State",

            "Current",

            "Entry",

            "SL",

            "TP",

            "Qty",

            "DistancePct",

            "EntryStatus"
        ]

        candidate = (
            result[
                candidate_columns
            ].copy()
        )

        candidate = format_result(
            candidate
        )

        st.dataframe(
            candidate.head(100),
            use_container_width=True,
            hide_index=True
        )

        # ====================================================
        # FILTER
        # ====================================================

        st.subheader(
            "🔍 Zone Filters"
        )

        f1, f2, f3, f4 = (
            st.columns(4)
        )

        with f1:

            selected_tf = st.multiselect(
                "Timeframe",
                TIMEFRAMES,
                default=TIMEFRAMES
            )

        with f2:

            selected_type = st.multiselect(
                "Zone",
                [
                    "Demand",
                    "Supply"
                ],
                default=[
                    "Demand",
                    "Supply"
                ]
            )

        with f3:

            selected_state = st.multiselect(
                "State",
                [
                    "Fresh",
                    "Tested"
                ],
                default=[
                    "Fresh",
                    "Tested"
                ]
            )

        with f4:

            score_filter = st.slider(
                "Minimum Score",
                0,
                150,
                int(
                    min_valid_score
                ),
                step=5
            )

        filtered = result[
            result[
                "Timeframe"
            ].isin(
                selected_tf
            )
            &
            result[
                "Type"
            ].isin(
                selected_type
            )
            &
            result[
                "State"
            ].isin(
                selected_state
            )
            &
            (
                result[
                    "Score"
                ] >=
                score_filter
            )
        ].copy()

        st.write(
            f"**Filtered Zones: "
            f"{len(filtered)}**"
        )

        filtered_columns = [

            "Symbol",

            "Timeframe",

            "Category",

            "Pattern",

            "Type",

            "Direction",

            "HQ",

            "Score",

            "State",

            "Touches",

            "Current",

            "Proximal",

            "Distal",

            "Entry",

            "SL",

            "TP",

            "Qty",

            "DistancePct",

            "EntryStatus"
        ]

        filtered_display = (
            format_result(
                filtered[
                    filtered_columns
                ].copy()
            )
        )

        st.dataframe(
            filtered_display,
            use_container_width=True,
            hide_index=True
        )

        # ====================================================
        # DOWNLOAD
        # ====================================================

        st.download_button(
            "⬇️ Download Zone CSV",
            filtered.to_csv(
                index=False
            ).encode("utf-8"),
            file_name=(
                "BrG_Trading_Zone_Screener.csv"
            ),
            mime="text/csv"
        )


# ============================================================
# DISPLAY SINGLE STOCK RESULTS
# ============================================================

if (
    scan_mode ==
    "Single Stock"
    and
    "single_results" in
    st.session_state
):

    result = st.session_state[
        "single_results"
    ]

    if result.empty:

        st.warning(
            "इस stock में कोई active zone नहीं मिला."
        )

    else:

        st.subheader(
            "🎯 Active Demand / Supply Zones"
        )

        display_columns = [

            "Timeframe",

            "Category",

            "Pattern",

            "Type",

            "Direction",

            "HQ",

            "Score",

            "State",

            "Touches",

            "Current",

            "Proximal",

            "Distal",

            "Entry",

            "SL",

            "TP",

            "Qty",

            "DistancePct",

            "EntryStatus"
        ]

        display = format_result(
            result[
                display_columns
            ].copy()
        )

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Stock Zones",

            result.to_csv(
                index=False
            ).encode("utf-8"),

            file_name=(
                f"{single_symbol}"
                "_BrG_Zones.csv"
            ),

            mime="text/csv"
        )


# ============================================================
# LEGEND
# ============================================================

with st.expander(
    "📖 BrG Zone Logic"
):

    st.markdown(
        """
**Demand Zone**

- RBR = Rally Base Rally
- DBR = Drop Base Rally

**Supply Zone**

- DBD = Drop Base Drop
- RBD = Rally Base Drop

**Zone State**

- 🟢 Fresh = अभी तक meaningful test नहीं
- 🟡 Tested = zone test हुआ लेकिन broken नहीं
- 🔴 Broken = zone invalidate

**Score**

Pine Script के आधार पर:

- Base quality
- Leg-In strength
- Leg-Out strength
- Volume
- Strong close
- Opposite-color base
- Genuine gap

को score में शामिल किया गया है।

**महत्वपूर्ण:** Screener किसी zone को अपने-आप BUY/SELL आदेश नहीं मानता। यह Demand/Supply zone और उसके आसपास का trade candidate दिखाता है।
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "BrG Trading Zone V1.1 | "
    "Pandas 3.x Safe | "
    "Yahoo Finance | "
    "Educational / Research use"
)
