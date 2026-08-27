import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.set_page_config(
    page_title="BrG Zone Scanner V1.0",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 BrG Zone Scanner V1.0")
st.caption("NSE Supply / Demand Zone Scanner")

# ---------------- NSE STOCKS ----------------
stocks = {
    "RELIANCE":"RELIANCE.NS",
    "HDFCBANK":"HDFCBANK.NS",
    "ICICIBANK":"ICICIBANK.NS",
    "SBIN":"SBIN.NS",
    "AXISBANK":"AXISBANK.NS",
    "KOTAKBANK":"KOTAKBANK.NS",
    "INFY":"INFY.NS",
    "TCS":"TCS.NS",
    "WIPRO":"WIPRO.NS",
    "HCLTECH":"HCLTECH.NS",
    "LT":"LT.NS",
    "BHARTIARTL":"BHARTIARTL.NS",
    "ITC":"ITC.NS",
    "MARUTI":"MARUTI.NS",
    "M&M":"M&M.NS",
    "TATASTEEL":"TATASTEEL.NS",
    "JSWSTEEL":"JSWSTEEL.NS",
    "HINDALCO":"HINDALCO.NS",
    "SUNPHARMA":"SUNPHARMA.NS",
    "TATAMOTORS":"TATAMOTORS.NS",
    "ADANIENT":"ADANIENT.NS",
    "ADANIPORTS":"ADANIPORTS.NS",
    "NTPC":"NTPC.NS",
    "POWERGRID":"POWERGRID.NS",
    "ONGC":"ONGC.NS",
    "COALINDIA":"COALINDIA.NS",
    "TITAN":"TITAN.NS",
    "BAJFINANCE":"BAJFINANCE.NS",
    "BAJAJFINSV":"BAJAJFINSV.NS",
    "DRREDDY":"DRREDDY.NS",
    "CIPLA":"CIPLA.NS",
    "EICHERMOT":"EICHERMOT.NS",
    "HEROMOTOCO":"HEROMOTOCO.NS",
    "APOLLOHOSP":"APOLLOHOSP.NS",
    "ULTRACEMCO":"ULTRACEMCO.NS",
    "GRASIM":"GRASIM.NS",
    "TECHM":"TECHM.NS",
    "INDUSINDBK":"INDUSINDBK.NS",
    "BEL":"BEL.NS",
    "HAL":"HAL.NS"
}

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Scan Settings")

selected = st.sidebar.multiselect(
    "🇮🇳 NSE Stocks चुनें",
    list(stocks.keys()),
    default=list(stocks.keys())[:10]
)

timeframe = st.sidebar.selectbox(
    "Timeframe चुनें",
    ["15 Min","1 Hour","4 Hours","Daily"]
)

lookback = st.sidebar.radio(
    "Lookback Period",
    ["3 महीने","6 महीने","1 वर्ष"]
)

st.sidebar.divider()

st.sidebar.header("🎯 Zone Filters")

fresh = st.sidebar.checkbox(
    "🟢 Fresh Zones दिखाएं", True
)

tested = st.sidebar.checkbox(
    "🟠 Tested Zones दिखाएं", True
)

hq = st.sidebar.checkbox(
    "⭐ सिर्फ HQ Zones (Score ≥ 75)", False
)

near = st.sidebar.checkbox(
    "🎯 सिर्फ Near-Price Zones", False
)

near_pct = st.sidebar.slider(
    "Near-Price Distance %",
    0.5, 10.0, 2.0, 0.5
)

min_score = st.sidebar.slider(
    "Minimum Zone Score",
    0, 100, 50
)

scan = st.sidebar.button(
    "🔎 Scan Zones",
    use_container_width=True
)

# ---------------- SETTINGS ----------------
if timeframe == "15 Min":
    interval = "15m"
elif timeframe == "1 Hour":
    interval = "1h"
elif timeframe == "4 Hours":
    interval = "1h"
else:
    interval = "1d"

# Yahoo Finance intraday data limitation
if timeframe == "15 Min":
    period = "60d"
elif timeframe == "1 Hour":
    period = "6mo"
elif timeframe == "4 Hours":
    period = "6mo"
else:
    if lookback == "3 महीने":
        period = "3mo"
    elif lookback == "6 महीने":
        period = "6mo"
    else:
        period = "1y"

# ---------------- RSI ----------------
def rsi(series, length=9):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1/length,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1/length,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(0,np.nan)

    return 100 - (100/(1+rs))

# ---------------- SCANNER ----------------
@st.cache_data(ttl=60)
def scan_stock(symbol):

    try:
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False
        )

        if df.empty:
            return []

        if isinstance(df.columns,pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.dropna()

        if len(df) < 30:
            return []

        df["EMA20"] = df["Close"].ewm(
            span=20,
            adjust=False
        ).mean()

        df["RSI9"] = rsi(
            df["Close"],9
        )

        tp = (
            df["High"]+
            df["Low"]+
            df["Close"]
        )/3

        df["VWAP"] = (
            (tp*df["Volume"]).cumsum() /
            df["Volume"].cumsum()
        )

        df["AVG_VOL"] = df["Volume"].rolling(20).mean()

        results = []

        data = df.tail(100).reset_index()

        for i in range(2,len(data)-2):

            c = float(data.loc[i,"Close"])
            h = float(data.loc[i,"High"])
            l = float(data.loc[i,"Low"])

            nh = float(data.loc[i+1,"High"])
            nl = float(data.loc[i+1,"Low"])
            nc = float(data.loc[i+1,"Close"])

            r = float(data.loc[i,"RSI9"])
            ema = float(data.loc[i,"EMA20"])
            vw = float(data.loc[i,"VWAP"])

            vol = float(data.loc[i,"Volume"])
            av = float(data.loc[i,"AVG_VOL"])

            if av <= 0:
                av = 1

            vr = vol/av

            current = float(
                data["Close"].iloc[-1]
            )

            # DEMAND
            if nc > h:

                score = 50

                if vr >= 1.5:
                    score += 15

                if c > ema:
                    score += 10

                if r >= 50:
                    score += 10

                if c > vw:
                    score += 10

                score = min(score,100)

                distance = (
                    abs(current-h)/
                    current*100
                )

                results.append({
                    "Symbol":symbol.replace(".NS",""),
                    "Type":"DEMAND",
                    "Zone Low":l,
                    "Zone High":h,
                    "Score":score,
                    "Current":current,
                    "Distance %":distance,
                    "RSI(9)":r,
                    "EMA20":ema,
                    "VWAP":vw,
                    "Volume Ratio":vr
                })

            # SUPPLY
            if nc < l:

                score = 50

                if vr >= 1.5:
                    score += 15

                if c < ema:
                    score += 10

                if r < 50:
                    score += 10

                if c < vw:
                    score += 10

                score = min(score,100)

                distance = (
                    abs(current-l)/
                    current*100
                )

                results.append({
                    "Symbol":symbol.replace(".NS",""),
                    "Type":"SUPPLY",
                    "Zone Low":l,
                    "Zone High":h,
                    "Score":score,
                    "Current":current,
                    "Distance %":distance,
                    "RSI(9)":r,
                    "EMA20":ema,
                    "VWAP":vw,
                    "Volume Ratio":vr
                })

        return results

    except Exception:
        return []

# ---------------- MAIN ----------------
if not scan:

    st.info(
        "Stocks और Timeframe चुनकर "
        "🔎 Scan Zones दबाइए।"
    )

else:

    if not selected:

        st.warning(
            "कम से कम एक NSE Stock चुनें।"
        )

    else:

        all_results = []

        progress = st.progress(0)

        for n,name in enumerate(selected):

            result = scan_stock(
                stocks[name]
            )

            all_results.extend(result)

            progress.progress(
                (n+1)/len(selected)
            )

        progress.empty()

        if not all_results:

            st.warning(
                "कोई zone नहीं मिला।"
            )

        else:

            df = pd.DataFrame(
                all_results
            )

            # SCORE
            df = df[
                df["Score"] >= min_score
            ]

            # HQ
            if hq:
                df = df[
                    df["Score"] >= 75
                ]

            # NEAR PRICE
            if near:
                df = df[
                    df["Distance %"] <= near_pct
                ]

            # FRESH / TESTED
            # V1.0 में सभी detected zones को
            # Fresh माना गया है.
            if fresh and not tested:
                pass

            # SORT
            df = df.sort_values(
                ["Score","Distance %"],
                ascending=[False,True]
            )

            # ---------------- TOP 3 ----------------
            st.subheader("🏆 Top 3 Zones")

            top = df.head(3)

            cols = st.columns(3)

            for i,(_,row) in enumerate(
                top.iterrows()
            ):

                with cols[i]:

                    st.metric(
                        row["Symbol"]+
                        " "+row["Type"],
                        "Score "+
                        str(int(row["Score"]))
                    )

                    st.write(
                        "Zone: "+
                        f"{row['Zone Low']:.2f}"
                        +" – "+
                        f"{row['Zone High']:.2f}"
                    )

                    st.write(
                        "Current: "+
                        f"{row['Current']:.2f}"
                    )

                    st.write(
                        "Distance: "+
                        f"{row['Distance %']:.2f}%"
                    )

                    st.write(
                        "RSI(9): "+
                        f"{row['RSI(9)']:.1f}"
                    )

            # ---------------- TABLE ----------------
            st.subheader(
                "🎯 Zones Found: "+
                str(len(df))
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # ---------------- CSV ----------------
            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Download Results",
                csv,
                "BrG_Zone_Scanner.csv",
                "text/csv",
                use_container_width=True
            )

st.divider()

st.caption(
    "BrG Zone Scanner V1.0 | "
    "Python + Streamlit"
)
