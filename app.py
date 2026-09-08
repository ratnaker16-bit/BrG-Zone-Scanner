import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import pytz
import time


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Suman NIFTY 500 SMA Scanner",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# NIFTY 500 — 500 STOCK UNIVERSE
# =========================================================

NIFTY_500_STOCKS = """
360ONE 3MINDIA ABB ACC ACMESOLAR AIAENG APLAPOLLO AUBANK AWL
AADHARHFC AARTIIND AAVAS ABBOTINDIA ACE ACUTAAS ADANIENSOL ADANIENT
ADANIGREEN ADANIPORTS ADANIPOWER ATGL ABCAPITAL ABFRL ABLBL ABREL
ABSLAMC CPPLUS AEGISLOG AEGISVOPAK AFCONS AFFLE AJANTPHARM ALKEM
ABDL ARE&M AMBER AMBUJACEM ANANDRATHI ANANTRAJ ANGELONE ANTHEM
ANURAS APARINDS APOLLOHOSP APOLLOTYRE APTUS ASAHIINDIA ASHOKLEY
ASIANPAINT ASTERDM ASTRAL ATHERENERG ATUL AUROPHARMA AIIL DMART
AXISBANK BEML BLS BSE BAJAJ-AUTO BAJFINANCE BAJAJFINSV BAJAJHLDNG
BAJAJHFL BALKRISIND BALRAMCHIN BANDHANBNK BANKBARODA BANKINDIA
MAHABANK BATAINDIA BAYERCROP BELRISE BERGEPAINT BDL BEL BHARATFORG
BHEL BPCL BHARTIARTL BHARTIHEXA BIKAJI GROWW BIOCON BSOFT BLUEDART
BLUEJET BLUESTARCO BBTC BOSCHLTD FIRSTCRY BRIGADE BRITANNIA MAPMYINDIA
CCL CESC CGPOWER CIEINDIA CRISIL CANFINHOME CANBK CANHLIFE CAPLIPOINT
CGCL CARBORUNIV CARTRADE CASTROLIND CEATLTD CEMPRO CENTRALBK CDSL
CHALET CHAMBLFERT CHENNPETRO CHOICEIN CHOLAHLDNG CHOLAFIN CIPLA CUB
CLEAN COALINDIA COCHINSHIP COFORGE COHANCE COLPAL CAMS CONCORDBIO
CONCOR COROMANDEL CRAFTSMAN CREDITACC CROMPTON CUMMINSIND CYIENT
DCMSHRIRAM DLF DOMS DABUR DALBHARAT DATAPATTNS DEEPAKFERT DEEPAKNTR
DELHIVERY DEVYANI DIVISLAB DIXON LALPATHLAB DRREDDY EIDPARRY EIHOTEL
EICHERMOT ELECON ELGIEQUIP EMAMILTD EMCURE EMMVEE ENDURANCE ENGINERSIN
ERIS ESCORTS ETERNAL EXIDEIND NYKAA FEDERALBNK FACT FINCABLES FSL
FIVESTAR FORCEMOT FORTIS GAIL GVT&D GMRAIRPORT GABRIEL GALLANTT GRSE
GICRE GILLETTE GLAND GLAXO GLENMARK MEDANTA GODIGIT GPIL GODFRYPHLP
GODREJCP GODREJIND GODREJPROP GRANULES GRAPHITE GRASIM GRAVITA GESHIP
FLUOROCHEM GMDCLTD HEG HBLENGINE HCLTECH HDBFS HDFCAMC HDFCBANK
HDFCLIFE HFCL HAVELLS HEROMOTOCO HEXT HSCL HINDALCO HAL HINDCOPPER
HINDPETRO HINDUNILVR HINDZINC POWERINDIA HOMEFIRST HONASA HONAUT HUDCO
HYUNDAI ICICIBANK ICICIGI ICICIAMC ICICIPRULI IDBI IDFCFIRSTB IFCI
IIFL IRB IRCON ITCHOTELS ITC ITI INDGN INDIACEM INDIAMART INDIANB
IEX INDHOTEL IOC IOB IRCTC IRFC IREDA IGL INDUSTOWER INDUSINDBK
NAUKRI INFY INOXWIND INTELLECT INDIGO IGIL IKS IPCALAB JKCEMENT JBMA
JKTYRE JMFINANCIL JSWCEMENT JSWDULUX JSWENERGY JSWINFRA JSWSTEEL
JAINREC JPPOWER J&KBANK JINDALSAW JSL JINDALSTEL JIOFIN JUBLFOOD
JUBLINGREA JUBLPHARMA JWL JYOTICNC KPRMILL KEI KPITTECH KAJARIACER
KPIL KALYANKJIL KARURVYSYA KAYNES KEC KFINTECH KIRLOSENG KOTAKBANK
KIMS LTF LTTS LGEINDIA LICHSGFIN LTFOODS LTM LT LATENTVIEW LAURUSLABS
THELEELA LEMONTREE LENSKART LICI LINDEINDIA LLOYDSME LODHA LUPIN MMTC
MRF MGL M&MFIN M&M MANAPPURAM MRPL MANKIND MARICO MARUTI MFSL
MAXHEALTH MAZDOCK MEESHO MINDACORP MSUMI MOTILALOFS MPHASIS MCX
MUTHOOTFIN NATCOPHARM NBCC NCC NHPC NLCINDIA NMDC NSLNISP NTPCGREEN
NTPC NH NATIONALUM NAVA NAVINFLUOR NESTLEIND NETWEB NEULANDLAB NEWGEN
NAM-INDIA NIVABUPA NUVAMA NUVOCO OBEROIRLTY ONGC OIL OLAELEC OLECTRA
PAYTM ONESOURCE OFSS POLICYBZR PCBL PGEL PIIND PNBHOUSING PTCIL
PVRINOX PAGEIND PARADEEP PATANJALI PERSISTENT PETRONET PFIZER PHOENIXLTD
PWL PIDILITIND PINELABS PIRAMALFIN PPLPHARMA POLYMED POLYCAB POONAWALLA
PFC POWERGRID PREMIERENE PRESTIGE PFOCUS PNB RRKABEL RBLBANK RECLTD
RHIM RITES RADICO RVNL RAILTEL RAINBOW RKFORGE REDINGTON RELIANCE RPOWER
SBFC SBICARD SBILIFE SJVN SRF SAGILITY SAILIFE SAMMAANCAP MOTHERSON
SAPPHIRE SARDAEN SAREGAMA SCHAEFFLER SCHNEIDER SCI SHREECEM SHRIRAMFIN
SHYAMMETL ENRIN SIEMENS SIGNATURE SOBHA SOLARINDS SONACOMS SONATSOFTW
STARHEALTH SBIN SAIL SUMICHEM SUNPHARMA SUNTV SUNDARMFIN SUPREMEIND
SPLPETRO SUZLON SWANCORP SWIGGY SYNGENE SYRMA TBOTEK TVSMOTOR TATACAP
TATACHEM TATACOMM TCS TATACONSUM TATAELXSI TATAINVEST TMCV TMPV TATAPOWER
TATASTEEL TATATECH TTML TECHM TECHNOE TEGA TEJASNET TENNIND NIACL RAMCOCEM
THERMAX TIMKEN TITAGARH TITAN TORNTPHARM TORNTPOWER TARIL TRAVELFOOD
TRENT TRIDENT TRITURBINE TIINDIA UCOBANK UNOMINDA UPL UTIAMC ULTRACEMCO
UNIONBANK UBL UNITDSPR URBANCO USHAMART VTL VBL VEDL VIJAYA VMM IDEA
VOLTAS WAAREEENER WELCORP WELSPUNLIV WHIRLPOOL WIPRO WOCKPHARMA YESBANK
ZFCVINDIA ZEEL ZENTEC ZENSARTECH ZYDUSLIFE ZYDUSWELL ECLERX
""".split()


# =========================================================
# REMOVE DUPLICATES + VALIDATE
# =========================================================

NIFTY_500_STOCKS = list(
    dict.fromkeys(NIFTY_500_STOCKS)
)

if len(NIFTY_500_STOCKS) != 500:

    st.error(
        f"❌ Stock Universe Error: "
        f"{len(NIFTY_500_STOCKS)} stocks loaded. "
        f"Expected exactly 500."
    )

    st.stop()


# =========================================================
# YAHOO FINANCE TICKERS
# =========================================================

YF_TICKERS = [
    f"{symbol}.NS"
    for symbol in NIFTY_500_STOCKS
]


# =========================================================
# TIMEZONE
# =========================================================

IST = pytz.timezone(
    "Asia/Kolkata"
)


# =========================================================
# HEADER
# =========================================================

st.title(
    "📊 SUMAN NIFTY 500 SMA CROSSOVER SCANNER"
)

st.markdown(
    """
### 5M + 15M — SMA 20 / SMA 200 CROSSOVER

🟢 **BUY:** Price > SMA 200 + Price crosses SMA 20 upward

🔴 **SELL:** Price < SMA 200 + Price crosses SMA 20 downward

🟢 **STRONG BUY:** 5M BUY + 15M BUY

🔴 **STRONG SELL:** 5M SELL + 15M SELL

⚪ **WAIT:** No fresh crossover
"""
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header(
    "⚙️ Scanner Settings"
)

st.sidebar.success(
    f"✅ NIFTY 500: {len(NIFTY_500_STOCKS)} Stocks"
)

st.sidebar.info(
    "5 Minute: ON"
)

st.sidebar.info(
    "15 Minute: ON"
)

st.sidebar.info(
    "SMA 20: ON"
)

st.sidebar.info(
    "SMA 200: ON"
)

show_all = st.sidebar.checkbox(
    "📋 Show Complete 500 Stock List",
    value=False
)


# =========================================================
# STOCK LIST
# =========================================================

if show_all:

    st.subheader(
        "📋 COMPLETE NIFTY 500 STOCK LIST"
    )

    stock_df = pd.DataFrame(
        {
            "No.": range(
                1,
                len(NIFTY_500_STOCKS) + 1
            ),

            "Symbol": NIFTY_500_STOCKS
        }
    )

    st.dataframe(
        stock_df,
        use_container_width=True,
        hide_index=True,
        height=600
    )


# =========================================================
# PREPARE DATA
# =========================================================

def prepare_data(df):

    if df is None or df.empty:
        return None

    df = df.copy()

    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return None

    for col in required:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=["Close"]
    )

    if df.empty:
        return None

    # =====================================================
    # TIMEZONE
    # =====================================================

    try:

        if df.index.tz is None:

            df.index = (
                df.index
                .tz_localize("UTC")
            )

        df.index = (
            df.index
            .tz_convert("Asia/Kolkata")
        )

    except Exception:
        pass

    # =====================================================
    # MARKET HOURS
    # =====================================================

    try:

        df = df.between_time(
            "09:15",
            "15:30"
        )

    except Exception:
        pass

    if df.empty:
        return None

    # =====================================================
    # SMA 20
    # =====================================================

    df["SMA20"] = (
        df["Close"]
        .rolling(
            window=20,
            min_periods=20
        )
        .mean()
    )

    # =====================================================
    # SMA 200
    # =====================================================

    df["SMA200"] = (
        df["Close"]
        .rolling(
            window=200,
            min_periods=200
        )
        .mean()
    )

    return df


# =========================================================
# SIGNAL LOGIC
# =========================================================

def get_signal(df):

    df = prepare_data(df)

    if df is None:
        return None

    # Need previous + current candle
    if len(df) < 201:
        return None

    # Remove rows where SMA not available
    valid = df.dropna(
        subset=[
            "SMA20",
            "SMA200"
        ]
    )

    if len(valid) < 2:
        return None

    prev = valid.iloc[-2]
    curr = valid.iloc[-1]

    prev_close = float(
        prev["Close"]
    )

    curr_close = float(
        curr["Close"]
    )

    prev_sma20 = float(
        prev["SMA20"]
    )

    curr_sma20 = float(
        curr["SMA20"]
    )

    curr_sma200 = float(
        curr["SMA200"]
    )

    # =====================================================
    # BUY
    #
    # Current price must be above SMA200
    # AND price crosses SMA20 upward
    # =====================================================

    buy_cross = (
        prev_close <= prev_sma20
        and
        curr_close > curr_sma20
        and
        curr_close > curr_sma200
    )

    # =====================================================
    # SELL
    #
    # Current price must be below SMA200
    # AND price crosses SMA20 downward
    # =====================================================

    sell_cross = (
        prev_close >= prev_sma20
        and
        curr_close < curr_sma20
        and
        curr_close < curr_sma200
    )

    # =====================================================
    # SIGNAL
    # =====================================================

    if buy_cross:

        signal = "BUY"

    elif sell_cross:

        signal = "SELL"

    else:

        signal = "WAIT"

    # =====================================================
    # TREND STATUS
    # =====================================================

    if curr_close > curr_sma200:

        trend = "ABOVE 200 SMA"

    elif curr_close < curr_sma200:

        trend = "BELOW 200 SMA"

    else:

        trend = "AT 200 SMA"

    return {

        "Signal": signal,

        "Close": curr_close,

        "SMA20": curr_sma20,

        "SMA200": curr_sma200,

        "Trend": trend
    }


# =========================================================
# DOWNLOAD DATA
# =========================================================

@st.cache_data(ttl=60)
def download_timeframe(
    tickers,
    interval
):

    all_data = {}

    # =====================================================
    # IMPORTANT:
    # 200 SMA के लिए पर्याप्त history
    # =====================================================

    period = "60d"

    batch_size = 75

    for start in range(
        0,
        len(tickers),
        batch_size
    ):

        batch = tickers[
            start:start + batch_size
        ]

        try:

            data = yf.download(

                tickers=batch,

                period=period,

                interval=interval,

                group_by="ticker",

                auto_adjust=False,

                prepost=False,

                threads=True,

                progress=False
            )

            if (
                data is None
                or data.empty
            ):
                continue

            # =================================================
            # MULTI STOCK DATA
            # =================================================

            if isinstance(
                data.columns,
                pd.MultiIndex
            ):

                for ticker in batch:

                    try:

                        if (
                            ticker
                            in data.columns
                            .levels[0]
                        ):

                            stock_data = (
                                data[ticker]
                                .copy()
                            )

                            if (
                                stock_data
                                is not None
                                and
                                not stock_data.empty
                            ):

                                all_data[
                                    ticker
                                ] = stock_data

                    except Exception:

                        continue

            # =================================================
            # SINGLE STOCK DATA
            # =================================================

            else:

                if len(batch) == 1:

                    all_data[
                        batch[0]
                    ] = data.copy()

        except Exception:

            continue

    return all_data


# =========================================================
# SCAN MARKET
# =========================================================

def scan_market(
    data5,
    data15
):

    records = []

    for ticker in NIFTY_500_STOCKS:

        yf_symbol = (
            f"{ticker}.NS"
        )

        # =================================================
        # 5 MINUTE
        # =================================================

        df5 = data5.get(
            yf_symbol
        )

        sig5 = get_signal(
            df5
        )

        # =================================================
        # 15 MINUTE
        # =================================================

        df15 = data15.get(
            yf_symbol
        )

        sig15 = get_signal(
            df15
        )

        # =================================================
        # SIGNALS
        # =================================================

        signal5 = (
            sig5["Signal"]
            if sig5
            else "WAIT"
        )

        signal15 = (
            sig15["Signal"]
            if sig15
            else "WAIT"
        )

        # =================================================
        # FINAL SIGNAL
        # =================================================

        if (
            signal5 == "BUY"
            and
            signal15 == "BUY"
        ):

            final_signal = (
                "STRONG BUY"
            )

        elif (
            signal5 == "SELL"
            and
            signal15 == "SELL"
        ):

            final_signal = (
                "STRONG SELL"
            )

        elif (
            signal5 == "BUY"
            or
            signal15 == "BUY"
        ):

            final_signal = "BUY"

        elif (
            signal5 == "SELL"
            or
            signal15 == "SELL"
        ):

            final_signal = "SELL"

        else:

            final_signal = "WAIT"

        # =================================================
        # RECORD
        # =================================================

        records.append(
            {

                "Symbol": ticker,

                "5M Signal": signal5,

                "15M Signal": signal15,

                "Final Signal": final_signal,

                "5M Close": (
                    sig5["Close"]
                    if sig5
                    else np.nan
                ),

                "5M SMA20": (
                    sig5["SMA20"]
                    if sig5
                    else np.nan
                ),

                "5M SMA200": (
                    sig5["SMA200"]
                    if sig5
                    else np.nan
                ),

                "5M Trend": (
                    sig5["Trend"]
                    if sig5
                    else "NO DATA"
                ),

                "15M Close": (
                    sig15["Close"]
                    if sig15
                    else np.nan
                ),

                "15M SMA20": (
                    sig15["SMA20"]
                    if sig15
                    else np.nan
                ),

                "15M SMA200": (
                    sig15["SMA200"]
                    if sig15
                    else np.nan
                ),

                "15M Trend": (
                    sig15["Trend"]
                    if sig15
                    else "NO DATA"
                )
            }
        )

    return pd.DataFrame(
        records
    )


# =========================================================
# SCAN BUTTON
# =========================================================

scan = st.button(
    "🔍 SCAN NIFTY 500",
    type="primary",
    use_container_width=True
)


# =========================================================
# AUTO REFRESH
# =========================================================

auto_refresh = st.sidebar.checkbox(
    "🔄 Auto Refresh",
    value=False
)

refresh_seconds = st.sidebar.selectbox(
    "Refresh Interval",
    [30, 60, 120, 300],
    index=1
)


# =========================================================
# RUN SCANNER
# =========================================================

if scan or auto_refresh:

    start_time = time.time()

    now = datetime.now(
        IST
    )

    st.info(
        "🕐 Scan Time: "
        + now.strftime(
            "%d-%m-%Y %H:%M:%S"
        )
        + " IST"
    )

    progress = st.progress(0)

    status = st.empty()

    # =====================================================
    # 5M DATA
    # =====================================================

    status.info(
        "📥 5 Minute data download हो रहा है..."
    )

    data5 = download_timeframe(
        YF_TICKERS,
        "5m"
    )

    progress.progress(40)

    # =====================================================
    # 15M DATA
    # =====================================================

    status.info(
        "📥 15 Minute data download हो रहा है..."
    )

    data15 = download_timeframe(
        YF_TICKERS,
        "15m"
    )

    progress.progress(70)

    # =====================================================
    # SCAN
    # =====================================================

    status.info(
        "🔎 NIFTY 500 में SMA20 / SMA200 "
        "crossover scan हो रहा है..."
    )

    result = scan_market(
        data5,
        data15
    )

    progress.progress(100)

    elapsed = round(
        time.time()
        - start_time,
        2
    )

    status.success(
        f"✅ Scan Complete — "
        f"{len(result)} Stocks Checked — "
        f"{elapsed} seconds"
    )

    # =====================================================
    # FORMAT
    # =====================================================

    if not result.empty:

        numeric_cols = [
            "5M Close",
            "5M SMA20",
            "5M SMA200",
            "15M Close",
            "15M SMA20",
            "15M SMA200"
        ]

        for col in numeric_cols:

            result[col] = (
                pd.to_numeric(
                    result[col],
                    errors="coerce"
                )
                .round(2)
            )

        # =================================================
        # SIGNAL GROUPS
        # =================================================

        strong_buy = result[
            result["Final Signal"]
            == "STRONG BUY"
        ]

        strong_sell = result[
            result["Final Signal"]
            == "STRONG SELL"
        ]

        buy = result[
            result["Final Signal"]
            == "BUY"
        ]

        sell = result[
            result["Final Signal"]
            == "SELL"
        ]

        # =================================================
        # DASHBOARD
        # =================================================

        st.subheader(
            "📊 SCANNER SUMMARY"
        )

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "NIFTY 500",
            len(result)
        )

        c2.metric(
            "🟢 STRONG BUY",
            len(strong_buy)
        )

        c3.metric(
            "🔴 STRONG SELL",
            len(strong_sell)
        )

        c4.metric(
            "🟢 BUY",
            len(buy)
        )

        c5.metric(
            "🔴 SELL",
            len(sell)
        )

        # =================================================
        # STRONG BUY
        # =================================================

        st.subheader(
            "🟢 STRONG BUY — 5M + 15M"
        )

        if strong_buy.empty:

            st.info(
                "आज कोई Strong Buy नहीं मिला।"
            )

        else:

            st.dataframe(
                strong_buy,
                use_container_width=True,
                hide_index=True
            )

        # =================================================
        # STRONG SELL
        # =================================================

        st.subheader(
            "🔴 STRONG SELL — 5M + 15M"
        )

        if strong_sell.empty:

            st.info(
                "आज कोई Strong Sell नहीं मिला।"
            )

        else:

            st.dataframe(
                strong_sell,
                use_container_width=True,
                hide_index=True
            )

        # =================================================
        # BUY
        # =================================================

        st.subheader(
            "🟢 BUY — SMA20 CROSS ABOVE"
        )

        if buy.empty:

            st.info(
                "आज कोई BUY नहीं मिला।"
            )

        else:

            st.dataframe(
                buy,
                use_container_width=True,
                hide_index=True
            )

        # =================================================
        # SELL
        # =================================================

        st.subheader(
            "🔴 SELL — SMA20 CROSS BELOW"
        )

        if sell.empty:

            st.info(
                "आज कोई SELL नहीं मिला।"
            )

        else:

            st.dataframe(
                sell,
                use_container_width=True,
                hide_index=True
            )

        # =================================================
        # ALL 500
        # =================================================

        with st.expander(
            "📊 ALL 500 STOCK RESULTS"
        ):

            st.dataframe(
                result,
                use_container_width=True,
                hide_index=True,
                height=700
            )

        # =================================================
        # CSV
        # =================================================

        csv = (
            result
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            "⬇️ Download CSV",
            csv,
            "Suman_NIFTY500_SMA20_SMA200_Scanner.csv",
            "text/csv",
            use_container_width=True
        )

    else:

        st.warning(
            "⚠️ कोई data उपलब्ध नहीं हुआ।"
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "SUMAN NIFTY 500 SMA CROSSOVER SCANNER | "
    "500 Stocks | "
    "5M + 15M | "
    "Price + SMA20 + SMA200 | "
    "Yahoo Finance Data"
)


# =========================================================
# AUTO REFRESH
# =========================================================

if auto_refresh:

    time.sleep(
        refresh_seconds
    )

    st.rerun()
