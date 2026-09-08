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
    page_title="Suman NIFTY 500 VWAP Scanner",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# NIFTY 500 — EMBEDDED 500 STOCK UNIVERSE
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
# VALIDATION
# =========================================================

NIFTY_500_STOCKS = list(dict.fromkeys(NIFTY_500_STOCKS))

if len(NIFTY_500_STOCKS) != 500:
    st.error(
        f"❌ Stock Universe Error: "
        f"{len(NIFTY_500_STOCKS)} stocks loaded. "
        f"Expected exactly 500."
    )
    st.stop()


# =========================================================
# YAHOO FINANCE SYMBOLS
# =========================================================

YF_TICKERS = [
    f"{symbol}.NS"
    for symbol in NIFTY_500_STOCKS
]


# =========================================================
# TIMEZONE
# =========================================================

IST = pytz.timezone("Asia/Kolkata")


# =========================================================
# HEADER
# =========================================================

st.title("📊 SUMAN NIFTY 500 VWAP SCANNER")

st.markdown(
    """
    ### 5M + 15M VWAP CROSS SCANNER

    🟢 **STRONG BUY** = 5M BUY + 15M BUY  
    🔴 **STRONG SELL** = 5M SELL + 15M SELL  
    🟢 **BUY** = VWAP Bullish Cross  
    🔴 **SELL** = VWAP Bearish Cross
    """
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Scanner Settings")

st.sidebar.success(
    f"✅ NIFTY 500: {len(NIFTY_500_STOCKS)} Stocks"
)

st.sidebar.info("5 Minute: ON")
st.sidebar.info("15 Minute: ON")
st.sidebar.info("1 Hour: OFF")

show_all = st.sidebar.checkbox(
    "Show Complete 500 Stock List",
    value=False
)


# =========================================================
# COMPLETE STOCK LIST
# =========================================================

if show_all:

    st.subheader(
        f"📋 COMPLETE NIFTY 500 STOCK LIST — "
        f"{len(NIFTY_500_STOCKS)} STOCKS"
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
# VWAP
# =========================================================

def calculate_vwap(df):

    df = df.copy()

    typical_price = (
        df["High"]
        + df["Low"]
        + df["Close"]
    ) / 3

    volume = (
        pd.to_numeric(
            df["Volume"],
            errors="coerce"
        )
        .fillna(0)
    )

    cumulative_pv = (
        typical_price * volume
    ).cumsum()

    cumulative_volume = (
        volume.cumsum()
    )

    df["VWAP"] = np.where(
        cumulative_volume > 0,
        cumulative_pv /
        cumulative_volume,
        np.nan
    )

    return df


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

    df = df.dropna(
        subset=["Close"]
    )

    if df.empty:
        return None

    for col in required:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df["Volume"] = (
        df["Volume"]
        .fillna(0)
    )

    # -----------------------------------------------------
    # TIMEZONE
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # MARKET HOURS
    # -----------------------------------------------------

    try:

        df = df.between_time(
            "09:15",
            "15:30"
        )

    except Exception:
        pass

    if df.empty:
        return None

    # -----------------------------------------------------
    # VWAP
    # -----------------------------------------------------

    df = calculate_vwap(df)

    df = df.dropna(
        subset=["VWAP"]
    )

    if df.empty:
        return None

    return df


# =========================================================
# VWAP CROSS
# =========================================================

def get_signal(df):

    df = prepare_data(df)

    if df is None:
        return None

    if len(df) < 2:
        return None

    prev_close = float(
        df["Close"].iloc[-2]
    )

    curr_close = float(
        df["Close"].iloc[-1]
    )

    prev_vwap = float(
        df["VWAP"].iloc[-2]
    )

    curr_vwap = float(
        df["VWAP"].iloc[-1]
    )

    signal = "WAIT"

    # -----------------------------------------------------
    # BUY CROSS
    # -----------------------------------------------------

    if (
        prev_close <= prev_vwap
        and
        curr_close > curr_vwap
    ):

        signal = "BUY"

    # -----------------------------------------------------
    # SELL CROSS
    # -----------------------------------------------------

    elif (
        prev_close >= prev_vwap
        and
        curr_close < curr_vwap
    ):

        signal = "SELL"

    return {
        "Signal": signal,
        "Close": curr_close,
        "VWAP": curr_vwap
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

    # -----------------------------------------------------
    # BATCH DOWNLOAD
    # -----------------------------------------------------

    batch_size = 75

    for start in range(
        0,
        len(tickers),
        batch_size
    ):

        batch = tickers[
            start:
            start + batch_size
        ]

        try:

            data = yf.download(
                tickers=batch,
                period="1d",
                interval=interval,
                group_by="ticker",
                auto_adjust=False,
                prepost=False,
                threads=True,
                progress=False
            )

            if data is not None and not data.empty:

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

                                if not stock_data.empty:

                                    all_data[
                                        ticker
                                    ] = stock_data

                        except Exception:
                            continue

                else:

                    if len(batch) == 1:

                        all_data[
                            batch[0]
                        ] = data.copy()

        except Exception:
            continue

    return all_data


# =========================================================
# SCAN
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

        # -------------------------------------------------
        # 5M
        # -------------------------------------------------

        df5 = data5.get(
            yf_symbol
        )

        sig5 = get_signal(
            df5
        )

        # -------------------------------------------------
        # 15M
        # -------------------------------------------------

        df15 = data15.get(
            yf_symbol
        )

        sig15 = get_signal(
            df15
        )

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

        # -------------------------------------------------
        # FINAL SIGNAL
        # -------------------------------------------------

        if (
            signal5 == "BUY"
            and
            signal15 == "BUY"
        ):

            final_signal = "STRONG BUY"

        elif (
            signal5 == "SELL"
            and
            signal15 == "SELL"
        ):

            final_signal = "STRONG SELL"

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

                "5M VWAP": (
                    sig5["VWAP"]
                    if sig5
                    else np.nan
                ),

                "15M Close": (
                    sig15["Close"]
                    if sig15
                    else np.nan
                ),

                "15M VWAP": (
                    sig15["VWAP"]
                    if sig15
                    else np.nan
                )
            }
        )

    return pd.DataFrame(
        records
    )


# =========================================================
# BUTTON
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
    # 5M
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
    # 15M
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
        "🔎 500 Stocks का VWAP Cross scan हो रहा है..."
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
            "5M VWAP",
            "15M Close",
            "15M VWAP"
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
            "500"
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
            "🟢 BUY — VWAP CROSS"
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
            "🔴 SELL — VWAP CROSS"
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

        csv = result.to_csv(
            index=False
        ).encode(
            "utf-8"
        )

        st.download_button(
            "⬇️ Download CSV",
            csv,
            "Suman_NIFTY500_VWAP_Scanner.csv",
            "text/csv",
            use_container_width=True
        )

    else:

        st.warning(
            "कोई data उपलब्ध नहीं हुआ।"
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "SUMAN NIFTY 500 VWAP SCANNER | "
    "500 Embedded Stocks | "
    "5M + 15M VWAP Cross | "
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
