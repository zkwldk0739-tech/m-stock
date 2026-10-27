# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="하이브리드 주식 스캐너",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .main-title { font-size: 1.8rem; font-weight: 800; color: #1E293B; margin-bottom: 0.2rem; }
    .sub-quote { font-size: 0.95rem; color: #64748B; margin-bottom: 1.2rem; font-style: italic; }
    .buy-banner { background-color: #DCFCE7; border: 2px solid #22C55E; border-radius: 12px; padding: 1.2rem; margin-bottom: 1.5rem; }
    .rest-banner { background-color: #F1F5F9; border: 2px solid #CBD5E1; border-radius: 12px; padding: 1.2rem; margin-bottom: 1.5rem; }
    .block-banner { background-color: #FEF2F2; border: 2px solid #EF4444; border-radius: 12px; padding: 1.2rem; margin-bottom: 1.5rem; }
    .stock-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.1rem; margin-bottom: 0.8rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); color:#0F172A; }
    .stock-title { font-size: 1.2rem; font-weight: 700; color: #0F172A; }
    .stock-desc { font-size: 0.85rem; color: #64748B; margin-bottom: 0.6rem; }
    .badge-turn { background-color: #DCFCE7; color: #15803D; font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.85rem; }
    .badge-drop { background-color: #FEE2E2; color: #B91C1C; font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.85rem; }
    .badge-warn { background-color: #FEF3C7; color: #92400E; font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.85rem; }
    .step-card { background-color: #F8FAFC; border-left: 4px solid #3B82F6; padding: 0.8rem 1rem; border-radius: 6px; margin-bottom: 0.5rem; color:#0F172A; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 종목 / 섹터 (섹터당 1개 제한용)
# ==============================================================================
SECTOR = {
    "AAPL": "빅테크", "MSFT": "빅테크", "GOOGL": "빅테크", "AMZN": "빅테크", "META": "빅테크", "TSLA": "빅테크",
    "NVDA": "반도체", "AVGO": "반도체", "AMD": "반도체", "QCOM": "반도체", "TXN": "반도체", "AMAT": "반도체",
    "CSCO": "네트워크", "ORCL": "소프트웨어", "ADBE": "소프트웨어", "CRM": "소프트웨어", "INTU": "소프트웨어",
    "IBM": "소프트웨어", "NOW": "소프트웨어",
    "BRK-B": "금융", "JPM": "금융", "BAC": "금융", "WFC": "금융", "GS": "금융", "MS": "금융", "BLK": "금융",
    "AXP": "금융", "C": "금융", "SPGI": "금융", "V": "결제", "MA": "결제",
    "LLY": "헬스케어", "UNH": "헬스케어", "JNJ": "헬스케어", "ABBV": "헬스케어", "MRK": "헬스케어",
    "TMO": "헬스케어", "ABT": "헬스케어", "PFE": "헬스케어", "DHR": "헬스케어", "BMY": "헬스케어",
    "AMGN": "헬스케어", "GILD": "헬스케어",
    "WMT": "필수소비재", "PG": "필수소비재", "COST": "필수소비재", "KO": "필수소비재", "PEP": "필수소비재",
    "MDLZ": "필수소비재", "CL": "필수소비재", "TGT": "필수소비재",
    "HD": "경기소비재", "LOW": "경기소비재", "MCD": "경기소비재", "NKE": "경기소비재", "SBUX": "경기소비재",
    "CAT": "중장비", "DE": "중장비", "GE": "항공방산", "BA": "항공방산", "LMT": "항공방산", "RTX": "항공방산",
    "HON": "산업재", "UNP": "운송", "UPS": "운송", "FDX": "운송",
    "XOM": "에너지", "CVX": "에너지", "COP": "에너지", "SLB": "에너지",
    "VZ": "통신", "T": "통신", "DIS": "미디어", "NFLX": "미디어", "CMCSA": "미디어",
}
TICKERS = list(SECTOR.keys())

COMPANY_INFO = {
    "AMAT": ("어플라이드 머티어리얼즈", "세계 1위 반도체 종합 장비"),
    "CAT": ("캐터필러", "세계 1위 중장비 및 건설기계"),
    "AVGO": ("브로드컴", "글로벌 통신 및 AI 가속 칩"),
    "GE": ("GE 에어로스페이스", "세계 1위 항공기 엔진 및 방산"),
    "T": ("AT&T", "미국 최대 통신사 및 대표 고배당주"),
    "GOOGL": ("알파벳(구글)", "글로벌 검색 및 AI, 클라우드"),
    "ORCL": ("오라클", "글로벌 데이터베이스 및 엔터프라이즈 클라우드"),
    "AMD": ("AMD", "CPU 및 GPU 반도체 설계"),
    "BAC": ("뱅크오브아메리카", "미국 2대 대형 상업은행"),
    "MS": ("모건스탠리", "글로벌 톱 투자은행 및 자산관리"),
    "AAPL": ("애플", "아이폰 및 서비스 생태계"),
    "MSFT": ("마이크로소프트", "윈도우, 오피스 및 Azure 클라우드"),
    "NVDA": ("엔비디아", "글로벌 AI GPU 1위"),
    "AMZN": ("아마존", "전자상거래 및 AWS 클라우드"),
    "TSLA": ("테슬라", "전기차 및 자율주행, 에너지"),
    "META": ("메타", "페이스북, 인스타그램 및 AI"),
    "KO": ("코카콜라", "글로벌 1위 음료 브랜드"),
    "NKE": ("나이키", "세계 1위 스포츠 패션 브랜드"),
    "MCD": ("맥도날드", "글로벌 1위 패스트푸드 프랜차이즈"),
    "JNJ": ("존슨앤존슨", "글로벌 헬스케어 및 의료기기"),
    "DIS": ("월트 디즈니", "글로벌 미디어 및 테마파크"),
    "SBUX": ("스타벅스", "세계 1위 글로벌 커피 체인"),
}

RATE_DAYS = 60       # 금리 변화 측정 기간(거래일)
BB_LOOKBACK = 5      # 볼린저 하단 터치 확인 기간(거래일)
VIX_FEAR = 30        # VIX 공포 기준


# ==============================================================================
# 데이터 로딩
# ==============================================================================
def _drop_incomplete(obj):
    """미국 정규장이 진행 중이면 오늘 봉(미완성)을 제거한다. (조기폐장일은 미반영)"""
    if obj is None or len(obj) == 0:
        return obj
    now_et = pd.Timestamp.now(tz="America/New_York")
    last = pd.Timestamp(obj.index[-1])
    if last.tzinfo is not None:
        last = last.tz_localize(None)
    if last.date() == now_et.date() and now_et.hour < 16:
        return obj.iloc[:-1]
    return obj


DATA_YEARS = 12      # 내려받는 총 기간 (백테스트 최대 10년 + 지표 계산용 여유 2년)


def _start_str():
    return (pd.Timestamp.today() - pd.DateOffset(years=DATA_YEARS)).strftime("%Y-%m-%d")


def _close_series(symbol):
    d = yf.download(symbol, start=_start_str(), auto_adjust=True, progress=False)
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    s = d["Close"].dropna()
    s.index = pd.to_datetime(s.index).tz_localize(None)
    return _drop_incomplete(s)


@st.cache_data(ttl=1800, show_spinner=False)
def load_data():
    raw = yf.download(TICKERS, start=_start_str(), group_by="ticker", auto_adjust=True,
                      progress=False, threads=True)
    stocks = {}
    for t in TICKERS:
        try:
            df = raw[t][["Open", "High", "Low", "Close", "Volume"]].dropna()
            df.index = pd.to_datetime(df.index).tz_localize(None)
            df = _drop_incomplete(df)
            if len(df) > 300:
                stocks[t] = df
        except Exception:
            continue
    return {
        "stocks": stocks,
        "gspc": _close_series("^GSPC"),
        "vix": _close_series("^VIX"),
        "tnx": _close_series("^TNX"),
        "spy": _close_series("SPY"),     # 벤치마크: S&P500 ETF (배당 포함 조정가)
    }


@st.cache_data(ttl=1800, show_spinner=False)
def load_fx():
    try:
        return float(_close_series("KRW=X").iloc[-1])
    except Exception:
        return None


@st.cache_data(ttl=21600, show_spinner=False)
def next_earnings(ticker):
    """다음 실적 발표일. 조회 실패 시 None (yfinance 데이터는 부정확할 수 있음)."""
    try:
        cal = yf.Ticker(ticker).calendar
        ed = cal.get("Earnings Date") if isinstance(cal, dict) else None
        if ed:
            first = ed[0] if isinstance(ed, (list, tuple)) else ed
            return pd.Timestamp(first).date()
    except Exception:
        pass
    return None


# ==============================================================================
# 지표 / 신호
# ==============================================================================
def build_ctx(gspc, vix, tnx, rate_days=RATE_DAYS):
    base = gspc.index
    ctx = pd.DataFrame(index=base)
    ctx["spx"] = gspc
    ctx["ma200"] = gspc.rolling(200).mean()
    ctx["mkt_ok"] = ctx["spx"] >= ctx["ma200"]
    t = tnx.reindex(base, method="ffill")
    ctx["tnx"] = t
    ctx["tnx_chg"] = t - t.shift(rate_days)
    ctx["vix"] = vix.reindex(base, method="ffill")
    return ctx


def add_indicators(df):
    d = df.copy()
    c = d["Close"]
    d["MA5"] = c.rolling(5).mean()
    d["MA20"] = c.rolling(20).mean()
    sd = c.rolling(20).std()
    d["BB_low"] = d["MA20"] - 2 * sd
    touched = (d["Low"] <= d["BB_low"]).astype(float)
    d["BB_touch"] = touched.rolling(BB_LOOKBACK).max() > 0
    d["VolMA5"] = d["Volume"].rolling(5).mean()
    d["VolMA20"] = d["Volume"].rolling(20).mean()
    delta = c.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_g = gain.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    avg_l = loss.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    d["RSI"] = 100 - 100 / (1 + avg_g / (avg_l + 1e-9))
    d["RSI_prev"] = d["RSI"].shift(1)
    d["High52"] = d["High"].rolling(252, min_periods=200).max()
    d["Drop"] = (c / d["High52"] - 1) * 100
    return d


def signal_series(d, ctx, p):
    """종목별 일자별 매수 신호(불리언). 시장 필터 포함."""
    sig = (
        (d["Drop"] <= -p["drop"])
        & (d["RSI"] <= p["rsi"])
        & (d["Close"] >= d["MA5"])
        & (d["RSI"] > d["RSI_prev"])
        & (d["VolMA5"] >= d["VolMA20"] * 0.85)
    )
    if p["use_bb"]:
        sig = sig & d["BB_touch"]
    c = ctx.reindex(d.index, method="ffill")
    if p["use_mkt"]:
        sig = sig & c["mkt_ok"].fillna(False).astype(bool)
    if p["use_rate"]:
        sig = sig & ~(c["tnx_chg"] > p["rate_thr"]).fillna(False).astype(bool)
    return sig.fillna(False).astype(bool), c


# ==============================================================================
# 스캐너
# ==============================================================================
@st.cache_data(ttl=1800, show_spinner=False)
def run_scan(p):
    data = load_data()
    ctx = build_ctx(data["gspc"], data["vix"], data["tnx"])
    last = ctx.iloc[-1]
    market_ok = bool(last["mkt_ok"]) if p["use_mkt"] else True
    rate_ok = True
    if p["use_rate"] and not pd.isna(last["tnx_chg"]):
        rate_ok = bool(last["tnx_chg"] <= p["rate_thr"])
    allowed = market_ok and rate_ok

    rows, asof = [], None
    for t, df in data["stocks"].items():
        d = add_indicators(df)
        r = d.iloc[-1]
        asof = d.index[-1] if asof is None or d.index[-1] > asof else asof
        if pd.isna(r["RSI"]) or pd.isna(r["Drop"]):
            continue
        if not (r["Drop"] <= -p["drop"] and r["RSI"] <= p["rsi"]):
            continue
        turn = (r["Close"] >= r["MA5"]) and (r["RSI"] > r["RSI_prev"]) and (r["VolMA5"] >= r["VolMA20"] * 0.85)
        bb_ok = bool(r["BB_touch"]) or not p["use_bb"]
        name, desc = COMPANY_INFO.get(t, (t, "S&P 100 우량주"))
        rows.append({
            "티커": t, "이름": name, "설명": desc, "섹터": SECTOR.get(t, "기타"),
            "종가": float(r["Close"]), "하락률": float(r["Drop"]), "RSI": float(r["RSI"]),
            "BB터치": bool(r["BB_touch"]),
            "지정가상한": float(r["Close"]) * (1 + p["limit_pct"] / 100),
            "turn": bool(turn and bb_ok),
        })

    cands_all = sorted([r for r in rows if r["turn"]], key=lambda x: x["RSI"]) if allowed else []
    picked, excluded, seen = [], [], set()
    for r in cands_all:
        if r["섹터"] in seen:
            excluded.append(r)
        else:
            seen.add(r["섹터"])
            picked.append(r)
    watch = [r for r in rows if r not in cands_all]
    return {
        "picked": picked, "excluded": excluded, "watch": watch, "asof": asof,
        "market_ok": market_ok, "rate_ok": rate_ok,
        "spx": float(last["spx"]), "ma200": None if pd.isna(last["ma200"]) else float(last["ma200"]),
        "tnx": None if pd.isna(last["tnx"]) else float(last["tnx"]),
        "tnx_chg": None if pd.isna(last["tnx_chg"]) else float(last["tnx_chg"]),
        "vix": None if pd.isna(last["vix"]) else float(last["vix"]),
    }


# ==============================================================================
# 백테스트 (신호 → 다음날 지정가 체결 → 익절/손절/기간초과)
# ==============================================================================
def simulate_trade(d, i, p):
    n = len(d)
    if i + 1 >= n:
        return None
    limit_px = d["Close"].iat[i] * (1 + p["limit_pct"] / 100)
    entry = d["Open"].iat[i + 1]
    if entry > limit_px:
        return {"status": "MISSED"}
    start = i + 1
    end = min(n, start + p["max_hold"])
    lows = d["Low"].values[start:end]
    highs = d["High"].values[start:end]
    opens = d["Open"].values[start:end]
    stop = entry * (1 - p["stop"] / 100)
    target = entry * (1 + p["target"] / 100)
    s_idx = np.flatnonzero(lows <= stop)
    t_idx = np.flatnonzero(highs >= target)
    s = s_idx[0] if len(s_idx) else None
    t = t_idx[0] if len(t_idx) else None

    if s is not None and (t is None or s <= t):          # 같은 날 동시 도달 시 손절 우선(보수적)
        reason, k, exit_px = "손절", s, min(stop, opens[s])
    elif t is not None:
        reason, k, exit_px = "익절", t, target
    elif start + p["max_hold"] <= n:
        reason, k, exit_px = "기간초과", end - start - 1, d["Close"].iat[end - 1]
    else:
        reason, k, exit_px = "보유중", n - start - 1, d["Close"].iat[n - 1]

    exit_date = d.index[start + k]
    fee = p["fee"] / 100
    gross = exit_px / entry - 1
    net = exit_px * (1 - fee) / (entry * (1 + fee)) - 1
    return {
        "status": "FILLED", "entry_date": d.index[start], "entry": float(entry),
        "exit_date": exit_date, "exit": float(exit_px), "reason": reason,
        "gross": float(gross), "net": float(net),
        "hold": int((exit_date - d.index[start]).days),
    }


def portfolio_curve(trades, stocks, bench, start, end, p):
    """거래 목록 -> 일별 포트폴리오 수익 곡선. 한 종목에 자금의 1/max_pos를 배정, 남는 자금은 현금(수익 0%)."""
    days = bench.loc[start:end].index
    slot = 1.0 / p["max_pos"]
    fee = p["fee"] / 100
    daily = pd.Series(0.0, index=days)
    expo = pd.Series(0.0, index=days)
    for _, t in trades.iterrows():
        df = stocks[t["ticker"]]
        is_open = t["reason"] == "보유중"
        x = df.index[-1] if is_open else t["exit_date"]
        seg = df.loc[t["entry_date"]:x, "Close"]
        if len(seg) == 0:
            continue
        prev = seg.shift(1)
        prev.iloc[0] = t["entry"]
        r = seg / prev - 1
        if not is_open:
            r.iloc[-1] = t["exit"] / prev.iloc[-1] - 1
            r.iloc[-1] -= fee
        r.iloc[0] -= fee
        daily += (slot * r).reindex(days).fillna(0.0)
        expo += slot * pd.Series(1.0, index=r.index).reindex(days).fillna(0.0)
    equity = (1 + daily).cumprod()
    b = bench.loc[days]
    return equity, b / b.iloc[0], float(expo.mean())


def curve_metrics(eq):
    years = max((eq.index[-1] - eq.index[0]).days / 365.25, 1e-9)
    total = float(eq.iloc[-1] / eq.iloc[0] - 1)
    cagr = float((eq.iloc[-1] / eq.iloc[0]) ** (1 / years) - 1)
    mdd = float((eq / eq.cummax() - 1).min())
    return total, cagr, mdd


@st.cache_data(ttl=1800, show_spinner=False)
def run_backtest(p):
    data = load_data()
    ctx = build_ctx(data["gspc"], data["vix"], data["tnx"])
    last_date = max(df.index[-1] for df in data["stocks"].values())
    start_date = last_date - pd.DateOffset(years=p["years"])

    cands = []
    for t, df in data["stocks"].items():
        d = add_indicators(df)
        sig, c = signal_series(d, ctx, p)
        mask = sig.values & (d.index >= start_date)
        for i in np.flatnonzero(mask):
            tr = simulate_trade(d, int(i), p)
            if tr is None:
                continue
            tr.update({"signal_date": d.index[i], "ticker": t, "sector": SECTOR.get(t, "기타"),
                       "vix": None if pd.isna(c["vix"].iat[i]) else float(c["vix"].iat[i])})
            cands.append(tr)

    cands.sort(key=lambda x: (x["signal_date"], x["ticker"]))
    busy_t, busy_s, open_ends, trades, missed, capped = {}, {}, [], [], 0, 0
    for tr in cands:
        t, s = tr["ticker"], tr["sector"]
        if tr["status"] == "MISSED":
            if busy_t.get(t, pd.Timestamp.min) < tr["signal_date"] and busy_s.get(s, pd.Timestamp.min) < tr["signal_date"]:
                missed += 1
            continue
        if tr["entry_date"] <= busy_t.get(t, pd.Timestamp.min) or tr["entry_date"] <= busy_s.get(s, pd.Timestamp.min):
            continue    # 같은 종목/같은 섹터 보유 중이면 신규 진입 불가
        if sum(1 for e in open_ends if e > tr["entry_date"]) >= p["max_pos"]:
            capped += 1
            continue    # 동시 보유 종목 수 한도 초과
        end = tr["exit_date"] if tr["reason"] != "보유중" else pd.Timestamp.max
        busy_t[t] = end
        busy_s[s] = end
        open_ends.append(end)
        trades.append(tr)

    df_tr = pd.DataFrame(trades)
    out = {"trades": df_tr, "missed": missed, "capped": capped, "start": start_date, "end": last_date,
           "curve": None}
    if len(df_tr) and "spy" in data and len(data["spy"]):
        try:
            eq, bench, expo = portfolio_curve(df_tr, data["stocks"], data["spy"], start_date, last_date, p)
            out["curve"] = {"eq": eq, "bench": bench, "expo": expo,
                            "strat": curve_metrics(eq), "spy": curve_metrics(bench)}
        except Exception as e:
            out["curve_err"] = str(e)
    return out


def summarize(df_tr):
    closed = df_tr[df_tr["reason"] != "보유중"]
    out = {"n_closed": len(closed), "n_open": int((df_tr["reason"] == "보유중").sum()),
           "win_all": float((df_tr["net"] > 0).mean()), "avg_all": float(df_tr["net"].mean())}
    if len(closed) == 0:
        return out
    out.update({
        "win": float((closed["net"] > 0).mean()),
        "avg": float(closed["net"].mean()),
        "med": float(closed["net"].median()),
        "best": float(closed["net"].max()),
        "worst": float(closed["net"].min()),
        "hold": float(closed["hold"].mean()),
        "tp": int((closed["reason"] == "익절").sum()),
        "sl": int((closed["reason"] == "손절").sum()),
        "to": int((closed["reason"] == "기간초과").sum()),
    })
    return out


# ==============================================================================
# 헤더 + 설정
# ==============================================================================
st.markdown('<div class="main-title">🚀 하이브리드 주식 스캐너 (방어 필터 + 실계산 백테스트)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-quote">코스톨라니식 시장 국면(금리·지수) + 볼린저 과매도 + 모멘텀 반등을 결합. '
            '수익 보장 아님 — 탭3 백테스트로 직접 검증하세요.</div>', unsafe_allow_html=True)

verdict_box = st.container()   # 최종 결론은 맨 위에 표시 (아래 설정값 계산 후 채움)

with st.expander("⚙️ 필터 설정 (기본값 그대로 써도 됩니다)"):
    c1, c2, c3 = st.columns(3)
    with c1:
        drop = st.slider("고점 대비 하락 기준 (%)", 10, 40, 15)
        rsi = st.slider("RSI 상한", 25, 60, 45)
        target = st.slider("목표 익절 (%)", 10, 40, 20)
    with c2:
        use_bb = st.checkbox("볼린저 하단 터치 필수 (최근 5일)", True)
        use_mkt = st.checkbox("S&P500 200일선 아래면 전면 차단", True)
        use_rate = st.checkbox("금리 급등 시 차단", True)
        rate_thr = st.slider("금리 급등 기준 (60일 변화, %p)", 0.1, 1.0, 0.3, 0.05)
    with c3:
        limit_pct = st.slider("지정가 상한 (종가 대비 %)", 0.0, 3.0, 1.0, 0.1)
        stop = st.slider("손절 (%)", 10, 40, 25)
        max_hold = st.slider("최대 보유일 (백테스트)", 60, 500, 250, 10)
        fee = st.number_input("편도 수수료 (%) — 증권사별 상이, 직접 확인", value=0.25, step=0.05)
        years = st.selectbox("백테스트 기간 (년) — 길수록 하락장 포함", [3, 5, 8, 10], index=3)
        max_pos = st.slider("동시 보유 최대 종목 수 (종목당 자금 = 1/N)", 3, 20, 10)

P = {"drop": drop, "rsi": rsi, "use_bb": use_bb, "use_mkt": use_mkt, "use_rate": use_rate,
     "rate_thr": rate_thr, "limit_pct": limit_pct, "target": target, "stop": stop,
     "max_hold": max_hold, "fee": fee, "years": years, "max_pos": max_pos}

# ------------------------------------------------------------------------------
# 한눈에 결론 (설정 안 건드려도 이것만 보면 됨)
# ------------------------------------------------------------------------------
with verdict_box:
    try:
        with st.spinner("전 종목 분석 중... (처음엔 1~2분 걸릴 수 있음)"):
            v = run_scan(P)
    except Exception as e:
        v = None
        st.error(f"데이터 조회 실패: {e}")

    if v is not None:
        today_et = pd.Timestamp.now(tz="America/New_York").date()
        buys, held = [], []
        for c in v["picked"][:3]:
            ed = next_earnings(c["티커"])
            if ed is not None and 0 <= (ed - today_et).days <= 5:
                held.append((c, ed))
            else:
                buys.append(c)

        if not v["market_ok"] or not v["rate_ok"]:
            why = []
            if not v["market_ok"]:
                why.append("S&P500이 200일선 아래")
            if not v["rate_ok"]:
                why.append("금리 급등 중")
            st.markdown(f"""<div class="block-banner"><h2 style="color:#B91C1C;margin:0;">🔴 오늘은 사지 마세요</h2>
            <p style="color:#991B1B;margin:.5rem 0 0 0;">이유: {' / '.join(why)} → 시장 필터가 전 종목 매수를 막았습니다. 현금 보유.</p></div>""",
                        unsafe_allow_html=True)
        elif buys:
            lines = "".join(
                f"<li><strong>{c['이름']} ({c['티커']})</strong> — 지정가 <strong>${c['지정가상한']:.2f} 이하</strong>로 예약 매수, "
                f"금액은 배정 한도의 30%(1차만). 손절 -{P['stop']}% / 익절 +{P['target']}%</li>" for c in buys)
            st.markdown(f"""<div class="buy-banner"><h2 style="color:#166534;margin:0;">🟢 사세요 ({len(buys)}종목)</h2>
            <ul style="color:#14532D;margin:.5rem 0 0 0;">{lines}</ul>
            <p style="color:#15803D;margin:.5rem 0 0 0;font-size:.9rem;">시가가 위 가격보다 높게 열리면 자동 미체결 → 그날은 패스.</p></div>""",
                        unsafe_allow_html=True)
        else:
            st.markdown("""<div class="rest-banner"><h2 style="color:#475569;margin:0;">⚪ 오늘은 사지 마세요</h2>
            <p style="color:#64748B;margin:.5rem 0 0 0;">시장은 정상이지만 모든 조건을 충족한 종목이 없습니다. 현금 보유.</p></div>""",
                        unsafe_allow_html=True)

        for c, ed in held:
            st.warning(f"⚠️ {c['이름']} ({c['티커']}): 조건은 충족했지만 실적 발표({ed})가 5일 이내라 매수 보류.")

        try:
            bt0 = run_backtest(P)
            tr0 = bt0["trades"]
            sm0 = summarize(tr0) if tr0 is not None and len(tr0) else {"n_closed": 0}
            if sm0["n_closed"] > 0:
                line = (f"📊 이 규칙을 과거 {P['years']}년에 적용하면: 청산 {sm0['n_closed']}건, 승률 {sm0['win'] * 100:.0f}%, "
                        f"평균 {sm0['avg'] * 100:+.1f}%")
                cv = bt0.get("curve")
                if cv:
                    st_t, st_c, st_m = cv["strat"]
                    sp_t, sp_c, sp_m = cv["spy"]
                    line += (f" | 포트폴리오 연환산 {st_c * 100:+.1f}% vs S&P500(SPY) {sp_c * 100:+.1f}%, "
                             f"최대낙폭 {st_m * 100:.0f}% vs {sp_m * 100:.0f}%")
                line += " (수수료 반영, 세금·환율 제외, 생존자 편향으로 과대평가 가능)"
                if sm0["n_closed"] < 30:
                    line += " — ⚠️ 표본 30건 미만이라 신뢰도 낮음"
                st.caption(line)
            else:
                st.caption(f"📊 과거 {P['years']}년 백테스트에서 청산 완료 거래가 없어 이 규칙의 성과는 확인되지 않았습니다.")
        except Exception:
            pass
        st.caption(f"기준 데이터: {v['asof'].date()} 종가 · 투자 권유가 아닌 규칙 기반 참고 신호입니다.")

tab1, tab2, tab3 = st.tabs(["📡 실시간 스캐너", "🎯 내 보유 종목 추적기", "📊 실계산 백테스트"])

# ------------------------------------------------------------------------------
# 탭 1
# ------------------------------------------------------------------------------
with tab1:
    with st.spinner("시장 필터 및 종목 스캔 중..."):
        try:
            scan = run_scan(P)
            scan_err = None
        except Exception as e:
            scan, scan_err = None, str(e)

    if scan_err:
        st.error(f"데이터 조회 실패: {scan_err}")
    else:
        st.caption(f"기준 데이터: {scan['asof'].date()} 종가 (미완성 봉 제외)")

        def _f(x, fmt):
            return "N/A" if x is None else fmt.format(x)

        mkt_tbl = pd.DataFrame([
            {"필터": "S&P500 vs 200일선", "현재": f"{scan['spx']:.0f} / {_f(scan['ma200'], '{:.0f}')}",
             "판정": "✅ 통과" if scan["market_ok"] else "🚨 차단"},
            {"필터": f"10년물 금리 {RATE_DAYS}일 변화", "현재": f"{_f(scan['tnx'], '{:.2f}')}% ({_f(scan['tnx_chg'], '{:+.2f}')}%p)",
             "판정": "✅ 통과" if scan["rate_ok"] else "🚨 차단"},
            {"필터": "VIX (30↑ = 공포, 참고용)", "현재": _f(scan["vix"], "{:.1f}"),
             "판정": "🔥 공포 구간" if (scan["vix"] or 0) >= VIX_FEAR else "일반"},
        ])
        st.dataframe(mkt_tbl, hide_index=True)

        if not scan["market_ok"] or not scan["rate_ok"]:
            st.markdown("""<div class="block-banner"><h3 style="color:#B91C1C;margin:0 0 .5rem 0;">🚨 시장 필터 차단 중</h3>
            <p style="color:#991B1B;margin:0;">위 표의 차단 항목 때문에 매수 신호를 전면 중지했습니다. 현금 보유.</p></div>""",
                        unsafe_allow_html=True)
        elif scan["picked"]:
            st.markdown(f"""<div class="buy-banner"><h3 style="color:#166534;margin:0 0 .5rem 0;">
            🔥 매수 후보 {len(scan['picked'])}개 (섹터당 1개)</h3>
            <p style="color:#15803D;margin:0;">증권사 앱에서 <strong>지정가 예약 주문</strong>으로 입력하세요.
            시가가 상한보다 높게 시작하면 체결되지 않습니다.</p></div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="rest-banner"><h3 style="color:#475569;margin:0 0 .5rem 0;">💤 오늘은 대기</h3>
            <p style="color:#64748B;margin:0;">모든 조건을 충족한 종목이 없습니다.</p></div>""", unsafe_allow_html=True)

        today_et = pd.Timestamp.now(tz="America/New_York").date()
        for c in scan["picked"]:
            ed = next_earnings(c["티커"])
            if ed is None:
                earn = '<span class="badge-warn">실적일 조회 불가 — 직접 확인</span>'
            elif 0 <= (ed - today_et).days <= 5:
                earn = f'<span class="badge-warn">⚠️ 실적 발표 {ed} (5일 이내) — 매수 보류 권장</span>'
            else:
                earn = f'<span style="font-size:.85rem;color:#64748B;">다음 실적: {ed}</span>'
            fear = ' <span class="badge-turn">🔥 VIX 공포 구간</span>' if (scan["vix"] or 0) >= VIX_FEAR else ""
            st.markdown(f"""
            <div class="stock-card">
                <div class="stock-title">{c['이름']} ({c['티커']}) <span style="font-size:.85rem;background:#E2E8F0;padding:2px 8px;border-radius:4px;">{c['섹터']}</span></div>
                <div class="stock-desc">{c['설명']}</div>
                <div style="margin-bottom:.5rem;">
                    <span style="font-size:1.15rem;font-weight:700;">종가 ${c['종가']:.2f}</span>&nbsp;
                    <span class="badge-drop">고점 대비 {c['하락률']:.1f}%</span>&nbsp;
                    <span class="badge-turn">RSI {c['RSI']:.1f}</span>{fear}
                </div>
                <div style="background:#F8FAFC;padding:8px;border-radius:6px;font-size:.9rem;">
                    📌 <strong>지정가 매수 상한: ${c['지정가상한']:.2f}</strong> (이 가격 이하일 때만 체결)<br>
                    손절선(진입가 기준 -{P['stop']}%) / 목표(+{P['target']}%) {earn}
                </div>
            </div>""", unsafe_allow_html=True)

        if scan["excluded"]:
            with st.expander(f"섹터 중복으로 제외된 후보 {len(scan['excluded'])}개 (RSI 낮은 종목 우선 선택)"):
                st.dataframe(pd.DataFrame(scan["excluded"])[["티커", "섹터", "종가", "하락률", "RSI"]], hide_index=True)

        if scan["watch"]:
            st.subheader("⏳ 관망 그룹 (과매도지만 반등/볼린저 조건 미충족 또는 차단)")
            w = pd.DataFrame(scan["watch"])[["티커", "이름", "섹터", "종가", "하락률", "RSI", "BB터치"]]
            st.dataframe(w, hide_index=True)

    if st.button("🔄 최신 데이터로 다시 스캔"):
        st.cache_data.clear()
        st.rerun()

# ------------------------------------------------------------------------------
# 탭 2
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("🎯 보유 종목 상태 자동 판정")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        my_ticker = st.selectbox("보유 종목", TICKERS, index=TICKERS.index("AVGO"))
    with col2:
        buy1 = st.number_input("1차 매수가 ($)", value=320.0, step=1.0)
    with col3:
        avg_px = st.number_input("현재 평단가 ($) — 2차 매수 후 수정", value=320.0, step=1.0)
    with col4:
        budget = st.selectbox("총 배정 한도", [30, 40, 50, 70, 100], index=2, format_func=lambda x: f"{x}만 원")

    b1, b2, b3 = budget * 30 // 100, budget * 35 // 100, budget * 35 // 100
    buy2_trigger = buy1 * 0.94
    tgt_px = avg_px * (1 + P["target"] / 100)
    stop_px = avg_px * (1 - P["stop"] / 100)

    try:
        data = load_data()
        d = add_indicators(data["stocks"][my_ticker])
        cur, ma20 = float(d["Close"].iat[-1]), float(d["MA20"].iat[-1])
        pnl = (cur / avg_px - 1) * 100
        st.caption(f"{my_ticker} 최근 종가 {d.index[-1].date()}: ${cur:.2f}")
        status = pd.DataFrame([
            {"항목": "평단 대비 손익", "기준": f"손절 ${stop_px:.2f} / 익절 ${tgt_px:.2f}", "현재": f"{pnl:+.1f}%",
             "판정": "🚨 손절선 이탈 — 규칙대로 청산" if cur <= stop_px else ("🎯 목표 도달" if cur >= tgt_px else "보유")},
            {"항목": "2차 매수 (1차 대비 -6%)", "기준": f"${buy2_trigger:.2f} 이하", "현재": f"${cur:.2f}",
             "판정": f"✅ 조건 충족 → {b2}만 원" if cur <= buy2_trigger else "대기"},
            {"항목": "3차 매수 (20일선 위 안착)", "기준": f"20일선 ${ma20:.2f} 이상", "현재": f"${cur:.2f}",
             "판정": f"✅ 조건 충족 → {b3}만 원" if cur >= ma20 else "대기"},
        ])
        st.dataframe(status, hide_index=True)
        st.caption(f"1차 투입 {b1}만 원 / 2차 {b2}만 원 / 3차 {b3}만 원. 3차는 2차 매수 이후에만 의미가 있습니다.")
    except Exception as e:
        st.warning(f"종목 데이터 조회 실패: {e}")

    st.markdown("---")
    st.subheader("💰 실수익 계산기 (수수료 + 환율 + 양도세 22%)")
    fx_auto = load_fx()
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        principal = st.number_input("투입 원금 (만 원)", value=50.0, step=5.0) * 10000
        b_px = st.number_input("매수가 ($)", value=float(buy1), step=1.0, key="calc_b")
    with k2:
        s_px = st.number_input("매도가 ($)", value=float(round(buy1 * 1.2, 2)), step=1.0)
        fee_c = st.number_input("편도 수수료 (%)", value=float(P["fee"]), step=0.05, key="calc_fee")
    with k3:
        fx_b = st.number_input("매수 시 환율 (원/$)", value=float(fx_auto or 1400.0), step=5.0)
    with k4:
        fx_s = st.number_input("매도 시 환율 (원/$)", value=float(fx_auto or 1400.0), step=5.0)
    if fx_auto is None:
        st.caption("환율 자동 조회 실패 → 1400은 임시값입니다. 직접 입력하세요.")
    else:
        st.caption(f"현재 환율(자동 조회): {fx_auto:,.1f}원")

    if b_px > 0:
        f = fee_c / 100
        notional = principal / (fx_b * (1 + f))
        shares = notional / b_px
        proceeds = shares * s_px * (1 - f) * fx_s
        gain = proceeds - principal
        taxable = max(0.0, gain - 2_500_000)
        tax = taxable * 0.22
        res = pd.DataFrame([
            {"항목": "세전 손익", "금액(원)": f"{gain:,.0f}"},
            {"항목": "양도세 (연 250만 원 공제, 22%, 타 거래 없음 가정)", "금액(원)": f"{-tax:,.0f}"},
            {"항목": "세후 순손익", "금액(원)": f"{gain - tax:,.0f}"},
            {"항목": "세후 수익률", "금액(원)": f"{(gain - tax) / principal * 100:.2f}%"},
        ])
        st.dataframe(res, hide_index=True)
        st.caption("양도세는 매도 다음해 5월에 신고·납부. 같은 해 다른 해외주식 손익은 합산되므로 실제 세액은 달라질 수 있음.")

# ------------------------------------------------------------------------------
# 탭 3
# ------------------------------------------------------------------------------
with tab3:
    st.subheader(f"📊 과거 {P['years']}년 실계산 백테스트 (기간은 ⚙️ 설정에서 변경)")
    st.markdown(
        "- 신호일 종가 기준 → **다음날 시가가 지정가 상한 이하일 때만 체결**\n"
        "- 체결 후 목표 익절 / 손절 / 최대 보유일 중 먼저 오는 쪽으로 청산 (같은 날 동시 도달 시 손절 우선)\n"
        "- 같은 종목·같은 섹터 보유 중에는 신규 진입 불가, 수수료 반영, **세금·환율 미반영**, 분할매수(2·3차) 미반영(1회 진입 기준)"
    )
    st.warning("⚠️ 현재 시점의 우량주 목록으로 과거를 테스트하므로 **생존자 편향**이 있습니다 → 실제 성과는 이보다 낮을 가능성이 큽니다. "
               "또한 설정값을 결과에 맞춰 조정하면 과최적화됩니다.")

    if st.button("▶️ 백테스트 실행"):
        st.session_state["bt_run"] = True

    if st.session_state.get("bt_run"):
        with st.spinner("백테스트 계산 중..."):
            try:
                bt = run_backtest(P)
            except Exception as e:
                bt = None
                st.error(f"백테스트 실패: {e}")
        if bt is not None:
            st.caption(f"기간: {bt['start'].date()} ~ {bt['end'].date()} | 지정가 상한 초과로 미체결된 신호일: {bt['missed']}건 | "
                       f"동시 보유 한도({P['max_pos']}종목) 초과로 건너뛴 신호: {bt.get('capped', 0)}건")
            tr = bt["trades"]
            if tr is None or len(tr) == 0:
                st.info("이 설정에서는 체결된 거래가 0건입니다. 필터를 완화해 보세요 (볼린저 필수 해제, 하락 기준 완화 등).")
            else:
                sm = summarize(tr)
                if sm["n_closed"] == 0:
                    st.info(f"청산 완료 거래가 없습니다 (보유중 {sm['n_open']}건).")
                else:
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("청산 완료 거래", f"{sm['n_closed']}건", f"보유중 {sm['n_open']}건")
                    m2.metric("승률 (세전 수수료 후)", f"{sm['win'] * 100:.1f}%")
                    m3.metric("평균 / 중앙값 수익률", f"{sm['avg'] * 100:+.1f}% / {sm['med'] * 100:+.1f}%")
                    m4.metric("평균 보유일", f"{sm['hold']:.0f}일")
                    st.dataframe(pd.DataFrame([{
                        "익절": sm["tp"], "손절": sm["sl"], "기간초과": sm["to"],
                        "최고": f"{sm['best'] * 100:+.1f}%", "최악": f"{sm['worst'] * 100:+.1f}%",
                    }]), hide_index=True)
                    if sm["n_closed"] < 30:
                        st.warning(f"표본이 {sm['n_closed']}건뿐이라 통계적 신뢰도가 낮습니다.")

                    closed = tr[tr["reason"] != "보유중"].copy()
                    closed["VIX구간"] = np.where(closed["vix"].fillna(0) >= VIX_FEAR, f"VIX≥{VIX_FEAR}", f"VIX<{VIX_FEAR}")
                    vsplit = closed.groupby("VIX구간").agg(
                        거래수=("net", "size"), 승률=("net", lambda s: f"{(s > 0).mean() * 100:.1f}%"),
                        평균수익률=("net", lambda s: f"{s.mean() * 100:+.1f}%")).reset_index()
                    st.markdown("**VIX 공포 구간 vs 일반 구간 (VIX 30 이상 '강화 신호' 가설 검증)**")
                    st.dataframe(vsplit, hide_index=True)

                    if sm["n_open"] > 0:
                        st.caption(f"보유중 {sm['n_open']}건을 현재 평가손익으로 포함하면: 승률 {sm['win_all'] * 100:.1f}%, 평균 {sm['avg_all'] * 100:+.1f}% "
                                   "(아직 확정 아님)")

                    cv = bt.get("curve")
                    st.markdown("**포트폴리오 vs S&P500 보유(SPY, 배당 포함)**")
                    if cv:
                        rows = []
                        for name, m in (("이 전략", cv["strat"]), ("SPY 보유", cv["spy"])):
                            rows.append({"구분": name, "총수익": f"{m[0] * 100:+.1f}%",
                                         "연환산": f"{m[1] * 100:+.1f}%", "최대낙폭": f"{m[2] * 100:.1f}%"})
                        st.dataframe(pd.DataFrame(rows), hide_index=True)
                        st.caption(f"종목당 자금 1/{P['max_pos']}, 평균 투자 비중 {cv['expo'] * 100:.0f}% (나머지는 현금, 수익 0% 가정). "
                                   "일별 평가 기준 근사치이며 세금·환율 제외.")
                        st.line_chart(pd.DataFrame({"이 전략": cv["eq"], "SPY 보유": cv["bench"]}))
                        beat_ret = cv["strat"][1] > cv["spy"][1]
                        beat_dd = cv["strat"][2] > cv["spy"][2]
                        st.markdown(f"- 연환산 수익이 지수보다 {'✅ 높음' if beat_ret else '❌ 낮음'}\n"
                                    f"- 최대 낙폭이 지수보다 {'✅ 작음' if beat_dd else '❌ 큼'}")
                    else:
                        st.info(f"지수 비교 곡선을 만들지 못했습니다. {bt.get('curve_err', '')}")

                    cl = closed.copy()
                    cl["진입연도"] = cl["entry_date"].dt.year
                    ysplit = cl.groupby("진입연도").agg(
                        거래수=("net", "size"), 승률=("net", lambda s_: f"{(s_ > 0).mean() * 100:.0f}%"),
                        평균수익률=("net", lambda s_: f"{s_.mean() * 100:+.1f}%"),
                        손절=("reason", lambda s_: int((s_ == "손절").sum()))).reset_index()
                    st.markdown("**연도별 성과 (하락장·상승장에서 흔들리는지 확인)**")
                    st.dataframe(ysplit, hide_index=True)

                show = tr.copy()
                show["진입일"] = show["entry_date"].dt.date
                show["청산일"] = show.apply(lambda r: r["exit_date"].date() if r["reason"] != "보유중" else "-", axis=1)
                show["수익률(수수료후)"] = (show["net"] * 100).round(1).astype(str) + "%"
                show = show.rename(columns={"ticker": "티커", "sector": "섹터", "reason": "결과", "hold": "보유일"})
                st.markdown("**전체 거래 내역**")
                st.dataframe(show.sort_values("진입일", ascending=False)[
                    ["티커", "섹터", "진입일", "청산일", "결과", "보유일", "수익률(수수료후)"]], hide_index=True)

st.caption("※ 정보 제공용이며 투자 권유가 아닙니다. 데이터는 yfinance(비공식)이며 오류·지연이 있을 수 있습니다.")
