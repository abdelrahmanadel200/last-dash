"""
Amecath Hemodialysis Catheters — MENA Market Intelligence Dashboard
Production-ready Streamlit app for deployment on Streamlit Community Cloud.
Author: Senior Python Developer / Data Visualization Expert
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Amecath | MENA Market Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DESIGN TOKENS & GLOBAL CSS
# ─────────────────────────────────────────────
NAVY      = "#0F172A"
TEAL      = "#0EA5E9"
GOLD      = "#F59E0B"
EMERALD   = "#10B981"
OFF_WHITE = "#F8FAFC"
SLATE     = "#1E293B"
SLATE2    = "#334155"
MUTED     = "#94A3B8"
RED       = "#EF4444"

COUNTRY_FLAG = {
    "Saudi Arabia": "🇸🇦",
    "UAE":          "🇦🇪",
    "Qatar":        "🇶🇦",
    "Kuwait":       "🇰🇼",
    "Oman":         "🇴🇲",
    "Jordan":       "🇯🇴",
    "Lebanon":      "🇱🇧",
    "Iraq":         "🇮🇶",
    "Bahrain":      "🇧🇭",
}

GCC     = ["Saudi Arabia", "UAE", "Qatar", "Kuwait", "Oman", "Bahrain"]
NON_GCC = ["Jordan", "Lebanon", "Iraq"]

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=OFF_WHITE, family="Inter, system-ui, sans-serif"),
        title_font=dict(size=16, color=OFF_WHITE),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_color=OFF_WHITE),
        xaxis=dict(gridcolor=SLATE2, zerolinecolor=SLATE2, tickcolor=MUTED),
        yaxis=dict(gridcolor=SLATE2, zerolinecolor=SLATE2, tickcolor=MUTED),
        colorway=[TEAL, GOLD, EMERALD, "#A78BFA", "#F87171", "#34D399", "#60A5FA"],
        margin=dict(l=20, r=20, t=50, b=20),
    )
)

def apply_template(fig):
    """Apply the dark theme template to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=OFF_WHITE, family="Inter, system-ui, sans-serif"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_color=OFF_WHITE),
        margin=dict(l=10, r=10, t=55, b=10),
    )
    fig.update_xaxes(gridcolor=SLATE2, zerolinecolor=SLATE2, tickfont_color=MUTED)
    fig.update_yaxes(gridcolor=SLATE2, zerolinecolor=SLATE2, tickfont_color=MUTED)
    return fig

st.markdown(f"""
<style>
  /* ── Global reset & background ── */
  html, body, [data-testid="stAppViewContainer"] {{
      background-color: {NAVY};
      color: {OFF_WHITE};
      font-family: "Inter", system-ui, sans-serif;
  }}
  [data-testid="stSidebar"] {{
      background-color: {SLATE} !important;
      border-right: 1px solid {SLATE2};
  }}
  [data-testid="stSidebar"] * {{ color: {OFF_WHITE} !important; }}
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stMultiSelect label {{
      color: {MUTED} !important;
      font-size: 0.78rem;
      letter-spacing: .05em;
      text-transform: uppercase;
  }}

  /* ── Metric cards ── */
  [data-testid="stMetric"] {{
      background: {SLATE};
      border: 1px solid {SLATE2};
      border-radius: 12px;
      padding: 18px 22px;
      box-shadow: 0 4px 24px rgba(0,0,0,.35);
  }}
  [data-testid="stMetricLabel"]  {{ color: {MUTED} !important; font-size: .78rem; letter-spacing:.05em; text-transform:uppercase; }}
  [data-testid="stMetricValue"]  {{ color: {OFF_WHITE} !important; font-size: 1.75rem; font-weight: 700; }}
  [data-testid="stMetricDelta"]  {{ font-size: .82rem !important; }}

  /* ── Tab bar ── */
  .stTabs [data-baseweb="tab-list"] {{
      background: {SLATE};
      border-radius: 10px;
      gap: 4px;
      padding: 4px;
      border: 1px solid {SLATE2};
  }}
  .stTabs [data-baseweb="tab"] {{
      background: transparent;
      border-radius: 8px;
      color: {MUTED};
      padding: 8px 18px;
      font-weight: 500;
  }}
  .stTabs [aria-selected="true"] {{
      background: {TEAL} !important;
      color: {NAVY} !important;
      font-weight: 700;
  }}

  /* ── DataFrames ── */
  [data-testid="stDataFrame"] {{
      border-radius: 10px;
      overflow: hidden;
      border: 1px solid {SLATE2};
  }}

  /* ── Section headers ── */
  .section-header {{
      font-size: 1.05rem;
      font-weight: 600;
      color: {TEAL};
      border-left: 3px solid {TEAL};
      padding-left: 10px;
      margin: 22px 0 12px;
      text-transform: uppercase;
      letter-spacing: .08em;
  }}

  /* ── KPI cards (custom HTML) ── */
  .kpi-card {{
      background: {SLATE};
      border: 1px solid {SLATE2};
      border-radius: 14px;
      padding: 20px 24px;
      box-shadow: 0 4px 20px rgba(0,0,0,.3);
  }}
  .kpi-label {{ color: {MUTED}; font-size: .75rem; text-transform: uppercase; letter-spacing:.07em; margin-bottom: 6px; }}
  .kpi-value {{ color: {OFF_WHITE}; font-size: 1.7rem; font-weight: 700; }}
  .kpi-sub   {{ color: {TEAL}; font-size: .8rem; margin-top: 4px; }}

  /* ── Badge pills ── */
  .badge-active   {{ background:{EMERALD}22; color:{EMERALD}; border:1px solid {EMERALD}55;
                     border-radius:20px; padding:2px 12px; font-size:.75rem; font-weight:600; }}
  .badge-upcoming {{ background:{GOLD}22; color:{GOLD}; border:1px solid {GOLD}55;
                     border-radius:20px; padding:2px 12px; font-size:.75rem; font-weight:600; }}
  .badge-past     {{ background:{MUTED}22; color:{MUTED}; border:1px solid {MUTED}55;
                     border-radius:20px; padding:2px 12px; font-size:.75rem; font-weight:600; }}

  /* ── Hotspot city card ── */
  .city-card {{
      background: {SLATE};
      border: 1px solid {SLATE2};
      border-radius: 12px;
      padding: 14px 18px;
      margin-bottom: 10px;
      box-shadow: 0 2px 12px rgba(0,0,0,.25);
  }}
  .city-card-title {{ color: {TEAL}; font-weight: 700; font-size: .95rem; }}
  .city-card-body  {{ color: {MUTED}; font-size: .82rem; margin-top: 4px; line-height: 1.5; }}

  /* ── Procurement card ── */
  .proc-card {{
      background: {SLATE};
      border-left: 4px solid {GOLD};
      border-radius: 10px;
      padding: 14px 18px;
      margin-bottom: 10px;
  }}
  .proc-title {{ color: {GOLD}; font-weight: 700; }}
  .proc-body  {{ color: {MUTED}; font-size: .83rem; margin-top: 4px; }}

  /* ── Dividers ── */
  hr {{ border-color: {SLATE2} !important; }}

  /* Scrollbars */
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: {NAVY}; }}
  ::-webkit-scrollbar-thumb {{ background: {SLATE2}; border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING  (cached)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading market intelligence data…")
def load_data(source):
    """Read every sheet from the Excel workbook and return a dict of DataFrames."""
    xl = pd.ExcelFile(source)
    sheets = {}
    for sheet in xl.sheet_names:
        try:
            sheets[sheet] = xl.parse(sheet, header=0)
        except Exception:
            sheets[sheet] = pd.DataFrame()
    return sheets


def clean_money(val):
    """Parse strings like '$9.3M' → 9.3 (float, millions)."""
    if pd.isna(val):
        return None
    s = str(val).replace("$", "").replace(",", "").strip()
    if s.endswith("M"):
        try:
            return float(s[:-1])
        except Exception:
            return None
    try:
        return float(s) / 1_000_000
    except Exception:
        return None


def clean_flag(name):
    """Strip flag emoji from country strings like '🇸🇦 Saudi Arabia'."""
    return re.sub(r"[^\x00-\x7F]+\s*", "", str(name)).strip()


@st.cache_data(show_spinner=False)
def build_overview(raw: pd.DataFrame) -> pd.DataFrame:
    """Tidy the overview sheet into a clean, analysis-ready DataFrame."""
    df = raw.copy()
    # Drop purely NaN rows / columns
    df = df.dropna(how="all").dropna(axis=1, how="all")
    # Rename columns to friendly names based on position / known header
    rename_map = {
        df.columns[0]: "idx",
        df.columns[1]: "Country",
        df.columns[2]: "Population",
        df.columns[3]: "HD_Patients",
        df.columns[4]: "PD_Patients",
        df.columns[5]: "Annual_Growth",
        df.columns[6]: "Dialysis_Facilities",
        df.columns[7]: "Hospital_Growth",
        df.columns[8]: "Unit_Growth",
        df.columns[9]: "Nephrologists",
        df.columns[10]: "Vascular_Surgeons",
        df.columns[11]: "Radiologists",
        df.columns[12]: "HD_Machines",
        df.columns[13]: "Catheter_Demand",
        df.columns[14]: "Market_Value_Raw",
        df.columns[15]: "Healthcare_Coverage",
        df.columns[16]: "OOP_Share",
        df.columns[17]: "Distributors",
        df.columns[18]: "KOLs",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Keep only valid data rows (col 1 must have numeric index)
    df = df[pd.to_numeric(df.get("idx", pd.Series()), errors="coerce").notna()].copy()

    # Clean country names
    df["Country"] = df["Country"].apply(clean_flag)

    # Parse numeric columns
    df["Population"]      = pd.to_numeric(df["Population"],      errors="coerce")
    df["HD_Patients"]     = pd.to_numeric(df["HD_Patients"],      errors="coerce")
    df["Annual_Growth"]   = pd.to_numeric(df["Annual_Growth"],    errors="coerce")
    df["Catheter_Demand"] = pd.to_numeric(df["Catheter_Demand"],  errors="coerce")
    df["Market_Value_M"]  = df["Market_Value_Raw"].apply(clean_money)

    # Region tag
    df["Region"] = df["Country"].apply(
        lambda c: "GCC" if c in GCC else "Non-GCC"
    )

    # Weighted ASP = Market_Value_M * 1e6 / Catheter_Demand
    df["Market_ASP"] = (df["Market_Value_M"] * 1_000_000) / df["Catheter_Demand"]

    return df.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_distributors(raw: pd.DataFrame) -> pd.DataFrame:
    """Parse the multi-country distributor table into a flat DataFrame."""
    rows = []
    current_country = None
    header_found = False
    for _, row in raw.iterrows():
        vals = row.tolist()
        first = str(vals[0]).strip() if vals[0] is not None else ""
        # Detect country header rows
        clean_first = clean_flag(first).replace("BAHRAIEN", "Bahrain").replace("BAHREIN", "Bahrain")
        if clean_first.upper() in [c.upper() for c in COUNTRY_FLAG.keys()]:
            for c in COUNTRY_FLAG.keys():
                if c.upper() == clean_first.upper():
                    current_country = c
                    break
            header_found = False
            continue
        # Detect column header rows
        if str(first).strip() == "#":
            header_found = True
            continue
        if not header_found or current_country is None:
            continue
        # Data row
        try:
            num = int(float(str(vals[0])))
        except Exception:
            continue
        name    = str(vals[1]).strip() if len(vals) > 1 else ""
        why     = str(vals[2]).strip() if len(vals) > 2 else ""
        contact = str(vals[3]).strip() if len(vals) > 3 else ""
        prio    = str(vals[4]).strip() if len(vals) > 4 else ""
        if name and name.lower() != "nan":
            rows.append({
                "Country":   current_country,
                "Region":    "GCC" if current_country in GCC else "Non-GCC",
                "#":         num,
                "Distributor": name,
                "Relevance": why,
                "Contact":   contact,
                "Priority":  prio,
            })
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def build_kols(raw: pd.DataFrame) -> pd.DataFrame:
    """Parse the multi-country KOL table into a flat DataFrame."""
    rows = []
    current_country = None
    header_found = False
    for _, row in raw.iterrows():
        vals = row.tolist()
        first = str(vals[0]).strip() if vals[0] is not None else ""
        clean_first = clean_flag(first).replace("BAHRAIEN", "Bahrain").replace("BAHREIN", "Bahrain")
        if clean_first.upper() in [c.upper() for c in COUNTRY_FLAG.keys()]:
            for c in COUNTRY_FLAG.keys():
                if c.upper() == clean_first.upper():
                    current_country = c
                    break
            header_found = False
            continue
        if str(first).strip() == "#":
            header_found = True
            continue
        if not header_found or current_country is None:
            continue
        try:
            num = int(float(str(vals[0])))
        except Exception:
            continue
        name     = str(vals[1]).strip() if len(vals) > 1 else ""
        spec     = str(vals[2]).strip() if len(vals) > 2 else ""
        inst     = str(vals[3]).strip() if len(vals) > 3 else ""
        contact  = str(vals[4]).strip() if len(vals) > 4 else ""
        if name and name.lower() != "nan":
            rows.append({
                "Country":     current_country,
                "Region":      "GCC" if current_country in GCC else "Non-GCC",
                "#":           num,
                "KOL":         name,
                "Specialty":   spec,
                "Institution": inst,
                "Contact":     contact,
            })
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def build_tenders(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean the tenders sheet."""
    df = raw.copy().dropna(how="all")
    # Standardise column names using position
    col_map = {}
    for i, c in enumerate(df.columns):
        lc = str(c).lower()
        if "country" in lc:        col_map[c] = "Country"
        elif "title" in lc:        col_map[c] = "Title"
        elif "ref" in lc or "id" in lc: col_map[c] = "Ref"
        elif "entity" in lc or "issu" in lc: col_map[c] = "Entity"
        elif "publish" in lc:      col_map[c] = "Published"
        elif "clos" in lc:         col_map[c] = "Closing_Date"
        elif "value" in lc:        col_map[c] = "Value"
        elif "winner" in lc:       col_map[c] = "Winner"
        elif "note" in lc or "scope" in lc: col_map[c] = "Notes"
        elif "link" in lc or "url" in lc:   col_map[c] = "Link"
    df = df.rename(columns=col_map)

    # Drop rows without a title
    if "Title" in df.columns:
        df = df[df["Title"].notna() & (df["Title"].astype(str).str.strip() != "")]
    if "Country" in df.columns:
        df["Country"] = df["Country"].apply(clean_flag)

    # Derive status badge
    def get_status(row):
        closing = str(row.get("Closing_Date", "")).lower()
        if "2026" in closing or "aug" in closing or "jul" in closing or "jun" in closing:
            return "Active 2026"
        elif "2025" in closing or "jan" in closing or "nov" in closing:
            return "Upcoming"
        elif "rolling" in closing or "rolling" in str(row.get("Notes", "")).lower():
            return "Rolling"
        else:
            return "Past"
    df["Status"] = df.apply(get_status, axis=1)
    return df.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_our_asp(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy().dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={
        df.columns[0]: "Country",
        df.columns[1]: "Short_Term",
        df.columns[2]: "Mid_Term",
        df.columns[3]: "Long_Term",
    })
    df["Country"] = df["Country"].apply(clean_flag)
    df = df[df["Country"].notna() & df["Country"].str.strip().ne("")]
    df["Short_Term"] = pd.to_numeric(df["Short_Term"], errors="coerce")
    df["Mid_Term"]   = pd.to_numeric(df["Mid_Term"],   errors="coerce")
    df["Long_Term"]  = pd.to_numeric(df["Long_Term"],  errors="coerce")
    df["Region"] = df["Country"].apply(lambda c: "GCC" if c in GCC else "Non-GCC")
    return df.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_comp_asp(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy().dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    # Keep only rows where Company col has real data
    col0 = df.columns[0]
    df = df[df[col0].notna() & df[col0].astype(str).str.strip().ne("")]
    rename_map = {
        df.columns[0]: "Company",
        df.columns[1]: "Region",
        df.columns[2]: "Short_Term_ASP_Raw",
        df.columns[3]: "Long_Term_ASP_Raw",
        df.columns[4]: "Notes",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    def parse_range_mid(val):
        """Take '~90–130' → 110 (midpoint)."""
        s = str(val).replace("~", "").replace(",", "")
        # look for a dash/en-dash range
        m = re.search(r"([\d.]+)\s*[–-]\s*([\d.]+)", s)
        if m:
            return (float(m.group(1)) + float(m.group(2))) / 2
        try:
            return float(re.search(r"[\d.]+", s).group())
        except Exception:
            return None

    df["ST_Mid"] = df["Short_Term_ASP_Raw"].apply(parse_range_mid)
    df["LT_Mid"] = df["Long_Term_ASP_Raw"].apply(parse_range_mid)
    return df.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_hotspots(raw: pd.DataFrame) -> pd.DataFrame:
    """Parse the Hot Areas sheet — one row per rank, columns per country."""
    df = raw.copy().dropna(how="all")
    df = df.dropna(axis=1, how="all")
    # First column = Rank, remaining = countries
    rows = []
    countries_in_sheet = [clean_flag(c) for c in df.columns[1:]]
    for _, row in df.iterrows():
        rank = row.iloc[0]
        try:
            rank_int = int(float(str(rank)))
        except Exception:
            continue
        for i, country in enumerate(countries_in_sheet):
            cell = str(row.iloc[i + 1]) if i + 1 < len(row) else ""
            if cell and cell.lower() not in ("nan", "none", "–", ""):
                # Strip source citations in brackets
                clean_cell = re.sub(r"\[.*?\]", "", cell).strip()
                rows.append({
                    "Country": country,
                    "Region":  "GCC" if country in GCC else "Non-GCC",
                    "Rank":    rank_int,
                    "City_Detail": clean_cell,
                    "City": clean_cell.split("(")[0].split("–")[0].strip().rstrip(","),
                })
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def build_procurement(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy().dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    col0 = df.columns[0]
    df = df[df[col0].notna() & df[col0].astype(str).str.strip().ne("")]
    rename_map = {
        df.columns[0]: "Idx",
        df.columns[1]: "Country",
        df.columns[2]: "Primary_Body",
        df.columns[3]: "Secondary_Buyers",
        df.columns[4]: "Notes",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df["Country"] = df["Country"].apply(clean_flag)
    return df.reset_index(drop=True)


# ─────────────────────────────────────────────
# LOAD & PARSE
# ─────────────────────────────────────────────
try:
    raw_sheets = load_data("Amecath_Dash.xlsx")
except FileNotFoundError:
    st.warning("⚠️ `Amecath_Dash.xlsx` not found in the app directory. Please upload it below.")
    uploaded = st.file_uploader("Upload Amecath_Dash.xlsx", type=["xlsx"])
    if uploaded is None:
        st.stop()
    raw_sheets = load_data(uploaded)

overview_raw    = raw_sheets.get("overview",        pd.DataFrame())
hotspot_raw     = raw_sheets.get("Hot Areas",       pd.DataFrame())
dist_raw        = raw_sheets.get("Distributors",    pd.DataFrame())
kol_raw         = raw_sheets.get("KOLS",            pd.DataFrame())
tender_raw      = raw_sheets.get("tenders",         pd.DataFrame())
asp_raw         = raw_sheets.get("our ASP",         pd.DataFrame())
comp_asp_raw    = raw_sheets.get("comp asp",        pd.DataFrame())
procurement_raw = raw_sheets.get("procurement body",pd.DataFrame())

overview_df    = build_overview(overview_raw)    if not overview_raw.empty    else pd.DataFrame()
hotspot_df     = build_hotspots(hotspot_raw)     if not hotspot_raw.empty     else pd.DataFrame()
dist_df        = build_distributors(dist_raw)    if not dist_raw.empty        else pd.DataFrame()
kol_df         = build_kols(kol_raw)             if not kol_raw.empty         else pd.DataFrame()
tender_df      = build_tenders(tender_raw)        if not tender_raw.empty      else pd.DataFrame()
asp_df         = build_our_asp(asp_raw)           if not asp_raw.empty         else pd.DataFrame()
comp_asp_df    = build_comp_asp(comp_asp_raw)     if not comp_asp_raw.empty    else pd.DataFrame()
procurement_df = build_procurement(procurement_raw) if not procurement_raw.empty else pd.DataFrame()


# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 16px 0 8px;">
      <span style="font-size:2rem;">🩺</span>
      <div style="font-size:1.1rem; font-weight:800; color:{OFF_WHITE}; margin-top:6px;">AMECATH</div>
      <div style="font-size:.72rem; color:{MUTED}; letter-spacing:.1em; text-transform:uppercase;">
        MENA Market Intelligence
      </div>
    </div>
    <hr style="border-color:{SLATE2}; margin:10px 0 18px;"/>
    """, unsafe_allow_html=True)

    region_filter = st.selectbox(
        "REGION",
        options=["All Regions", "GCC", "Non-GCC (Levant & Iraq)"],
    )

    all_countries = list(COUNTRY_FLAG.keys())
    if region_filter == "GCC":
        default_countries = GCC
    elif region_filter == "Non-GCC (Levant & Iraq)":
        default_countries = NON_GCC
    else:
        default_countries = all_countries

    country_filter = st.multiselect(
        "COUNTRIES",
        options=all_countries,
        default=default_countries,
        format_func=lambda c: f"{COUNTRY_FLAG.get(c, '')} {c}",
    )

    if not country_filter:
        country_filter = all_countries

    st.markdown(f"""
    <hr style="border-color:{SLATE2}; margin:18px 0 12px;"/>
    <div style="font-size:.7rem; color:{MUTED}; line-height:1.6; padding:0 4px;">
      <b style="color:{TEAL};">Data vintage:</b> 2026 estimates<br/>
      <b style="color:{TEAL};">Coverage:</b> 9 MENA countries<br/>
      <b style="color:{TEAL};">Distributors:</b> 90+ mapped<br/>
      <b style="color:{TEAL};">KOLs:</b> 90+ profiled<br/>
      <b style="color:{TEAL};">Tenders:</b> 17 active/recent
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILTER HELPER
# ─────────────────────────────────────────────
def filter_df(df, country_col="Country"):
    if df.empty or country_col not in df.columns:
        return df
    return df[df[country_col].isin(country_filter)].copy()


# ─────────────────────────────────────────────
# HEADER BANNER
# ─────────────────────────────────────────────
st.markdown(f"""
<div style="
  background: linear-gradient(135deg, {SLATE} 0%, {NAVY} 100%);
  border: 1px solid {SLATE2};
  border-radius: 16px;
  padding: 24px 32px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 18px;
">
  <div style="font-size:3rem;">🩺</div>
  <div>
    <div style="font-size:1.65rem; font-weight:800; color:{OFF_WHITE};">
      Amecath Hemodialysis Catheters
    </div>
    <div style="font-size:.92rem; color:{MUTED}; margin-top:4px;">
      MENA Market Intelligence Dashboard &nbsp;·&nbsp;
      <span style="color:{TEAL};">9 Countries</span> &nbsp;·&nbsp;
      <span style="color:{GOLD};">2026 Estimates</span> &nbsp;·&nbsp;
      Powered by Amecath Commercial Analytics
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "👔 Executive Summary",
    "💵 Pricing & Competitive Intel",
    "🗺️ Hotspots & Commercial Network",
    "📋 Tenders Tracker",
])


# ═══════════════════════════════════════════════════════════════
# TAB 1 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════
with tab1:
    ov = filter_df(overview_df)

    if ov.empty:
        st.warning("No data for selected filters.")
    else:
        total_market   = ov["Market_Value_M"].sum()
        total_demand   = ov["Catheter_Demand"].sum()
        total_patients = ov["HD_Patients"].sum()
        wtd_asp        = (ov["Market_Value_M"].sum() * 1_000_000) / ov["Catheter_Demand"].sum() if total_demand else 0

        # ── KPI Row ──
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Market Value",    f"${total_market:,.2f}M")
        k2.metric("Total Catheter Demand", f"{int(total_demand):,} units")
        k3.metric("Total HD Patients",     f"{int(total_patients):,}")
        k4.metric("Weighted Avg Market ASP", f"${wtd_asp:,.1f}")

        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

        # ── Row 1: Bar chart + Donut ──
        col_a, col_b = st.columns([3, 2], gap="medium")

        with col_a:
            st.markdown("<div class='section-header'>Market Value by Country</div>", unsafe_allow_html=True)
            bar_df = ov.sort_values("Market_Value_M", ascending=False)
            bar_df["Flag_Country"] = bar_df["Country"].map(lambda c: f"{COUNTRY_FLAG.get(c,'')} {c}")
            bar_df["Color"] = bar_df["Country"].apply(
                lambda c: TEAL if c in ov.nlargest(3, "Market_Value_M")["Country"].values else SLATE2
            )
            fig_bar = go.Figure(go.Bar(
                x=bar_df["Market_Value_M"],
                y=bar_df["Flag_Country"],
                orientation="h",
                marker=dict(
                    color=bar_df["Market_Value_M"],
                    colorscale=[[0, SLATE2], [0.4, TEAL], [1, EMERALD]],
                    showscale=False,
                ),
                text=[f"${v:.2f}M" for v in bar_df["Market_Value_M"]],
                textposition="outside",
                textfont=dict(color=OFF_WHITE, size=12),
                hovertemplate="<b>%{y}</b><br>Market Value: $%{x:.2f}M<extra></extra>",
            ))
            fig_bar.update_layout(
                title="Market Value ($M) — Sorted by Size",
                xaxis_title="USD Millions",
                yaxis=dict(autorange="reversed"),
                height=380,
            )
            apply_template(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_b:
            st.markdown("<div class='section-header'>GCC vs Non-GCC Split</div>", unsafe_allow_html=True)
            region_data = ov.groupby("Region")["Market_Value_M"].sum().reset_index()
            fig_donut = go.Figure(go.Pie(
                labels=region_data["Region"],
                values=region_data["Market_Value_M"],
                hole=0.55,
                marker=dict(colors=[TEAL, GOLD], line=dict(color=NAVY, width=2)),
                textinfo="label+percent",
                textfont=dict(color=OFF_WHITE, size=13),
                hovertemplate="<b>%{label}</b><br>$%{value:.2f}M<br>%{percent}<extra></extra>",
            ))
            fig_donut.update_layout(
                title="Market Share by Region",
                height=380,
                showlegend=True,
                legend=dict(orientation="h", y=-0.05),
                annotations=[dict(
                    text=f"<b>${total_market:.1f}M</b><br>Total",
                    x=0.5, y=0.5,
                    font=dict(size=16, color=OFF_WHITE),
                    showarrow=False,
                )],
            )
            apply_template(fig_donut)
            st.plotly_chart(fig_donut, use_container_width=True)

        # ── Row 2: Dual horizontal bar — patients + demand ──
        st.markdown("<div class='section-header'>Dialysis Patient Volume & Catheter Demand by Country</div>", unsafe_allow_html=True)

        pop_df = ov.sort_values("HD_Patients", ascending=True)
        fig_pop = make_subplots(
            rows=1, cols=2,
            subplot_titles=["HD Patients (2026 Est.)", "Annual Catheter Demand (Units)"],
            horizontal_spacing=0.08,
        )
        fig_pop.add_trace(go.Bar(
            y=[f"{COUNTRY_FLAG.get(c,'')} {c}" for c in pop_df["Country"]],
            x=pop_df["HD_Patients"],
            orientation="h",
            marker_color=TEAL,
            name="HD Patients",
            hovertemplate="<b>%{y}</b><br>%{x:,} patients<extra></extra>",
            text=[f"{int(v):,}" for v in pop_df["HD_Patients"]],
            textposition="outside",
            textfont=dict(color=OFF_WHITE, size=10),
        ), row=1, col=1)
        fig_pop.add_trace(go.Bar(
            y=[f"{COUNTRY_FLAG.get(c,'')} {c}" for c in pop_df["Country"]],
            x=pop_df["Catheter_Demand"],
            orientation="h",
            marker_color=GOLD,
            name="Catheter Demand",
            hovertemplate="<b>%{y}</b><br>%{x:,} units<extra></extra>",
            text=[f"{int(v):,}" for v in pop_df["Catheter_Demand"]],
            textposition="outside",
            textfont=dict(color=OFF_WHITE, size=10),
        ), row=1, col=2)
        fig_pop.update_layout(height=400, showlegend=False)
        fig_pop.update_xaxes(gridcolor=SLATE2, zerolinecolor=SLATE2, tickfont_color=MUTED)
        fig_pop.update_yaxes(gridcolor=SLATE2, zerolinecolor=SLATE2, tickfont_color=MUTED)
        apply_template(fig_pop)
        st.plotly_chart(fig_pop, use_container_width=True)

        # ── Row 3: Summary Table ──
        st.markdown("<div class='section-header'>Country Summary Table</div>", unsafe_allow_html=True)
        table_df = ov[[
            "Country", "Population", "HD_Patients", "Catheter_Demand",
            "Market_Value_M", "Market_ASP", "Annual_Growth", "Region"
        ]].copy()
        table_df["Flag"] = table_df["Country"].map(COUNTRY_FLAG)
        table_df["Country Display"] = table_df["Flag"].fillna("") + " " + table_df["Country"]
        table_df = table_df.rename(columns={
            "Population":      "Population (2026)",
            "HD_Patients":     "HD Patients",
            "Catheter_Demand": "Catheter Demand",
            "Market_Value_M":  "Market Value ($M)",
            "Market_ASP":      "Market ASP ($)",
            "Annual_Growth":   "Growth Rate",
        })
        display_cols = [
            "Country Display", "Region", "Population (2026)", "HD Patients",
            "Catheter Demand", "Market Value ($M)", "Market ASP ($)", "Growth Rate",
        ]
        table_df = table_df[display_cols].sort_values("Market Value ($M)", ascending=False)
        st.dataframe(
            table_df.style
                .format({
                    "Population (2026)": "{:,.0f}",
                    "HD Patients":       "{:,.0f}",
                    "Catheter Demand":   "{:,.0f}",
                    "Market Value ($M)": "${:.2f}M",
                    "Market ASP ($)":    "${:.1f}",
                    "Growth Rate":       "{:.1%}",
                })
                .set_properties(**{
                    "background-color": SLATE,
                    "color": OFF_WHITE,
                    "border": f"1px solid {SLATE2}",
                }),
            use_container_width=True,
            height=370,
        )


# ═══════════════════════════════════════════════════════════════
# TAB 2 — PRICING & COMPETITIVE INTELLIGENCE
# ═══════════════════════════════════════════════════════════════
with tab2:
    ov_f   = filter_df(overview_df)
    asp_f  = filter_df(asp_df)
    comp_f = filter_df(comp_asp_df, country_col="Region")  # comp_asp uses Region, not Country

    st.markdown("<div class='section-header'>Amecath ASP vs. Competitor Benchmarks</div>", unsafe_allow_html=True)

    # ── KPIs: price spread ──
    if not asp_f.empty and not ov_f.empty:
        avg_st = asp_f["Short_Term"].mean()
        avg_lt = asp_f["Long_Term"].mean()
        avg_mid = asp_f["Mid_Term"].mean()
        # vs BD GCC midpoint
        bd_st_mid = 110.0   # midpoint of ~90-130
        bd_lt_mid = 220.0   # midpoint of ~180-260
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Amecath Avg Short-Term ASP",  f"${avg_st:.0f}",  delta=f"${bd_st_mid - avg_st:.0f} below BD/GCC")
        k2.metric("Amecath Avg Mid-Term ASP",    f"${avg_mid:.0f}")
        k3.metric("Amecath Avg Long-Term ASP",   f"${avg_lt:.0f}",  delta=f"${bd_lt_mid - avg_lt:.0f} below BD/GCC")
        k4.metric("Price Advantage vs BD (ST)",  f"{((bd_st_mid - avg_st)/bd_st_mid*100):.0f}% lower")

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # ── ASP Comparison Chart ──
    if not asp_f.empty:
        col_p, col_q = st.columns([3, 2], gap="medium")

        with col_p:
            st.markdown("<div class='section-header'>Amecath ASP by Country & Term</div>", unsafe_allow_html=True)
            asp_melt = asp_f.melt(
                id_vars=["Country", "Region"],
                value_vars=["Short_Term", "Mid_Term", "Long_Term"],
                var_name="Term",
                value_name="ASP",
            )
            term_labels = {"Short_Term": "Short-Term", "Mid_Term": "Mid-Term", "Long_Term": "Long-Term"}
            asp_melt["Term"] = asp_melt["Term"].map(term_labels)
            asp_melt["Flag_Country"] = asp_melt["Country"].map(
                lambda c: f"{COUNTRY_FLAG.get(c, '')} {c}"
            )
            fig_asp = px.bar(
                asp_melt,
                x="Flag_Country",
                y="ASP",
                color="Term",
                barmode="group",
                color_discrete_map={
                    "Short-Term": TEAL,
                    "Mid-Term":   GOLD,
                    "Long-Term":  EMERALD,
                },
                labels={"Flag_Country": "", "ASP": "ASP (USD)", "Term": "Catheter Type"},
                hover_data={"Flag_Country": True, "ASP": ":.0f", "Term": True},
            )
            fig_asp.update_layout(
                title="Amecath Selling Price (Ex-Factory to Distributor)",
                height=380,
                legend=dict(orientation="h", y=1.08),
            )
            apply_template(fig_asp)
            st.plotly_chart(fig_asp, use_container_width=True)

        with col_q:
            st.markdown("<div class='section-header'>Competitor ASP Landscape (GCC)</div>", unsafe_allow_html=True)
            if not comp_asp_df.empty:
                # Show ST midpoint per company for GCC region
                gcc_comp = comp_asp_df[comp_asp_df["Region"].str.contains("GCC", na=False)].copy()
                gcc_comp = gcc_comp.dropna(subset=["ST_Mid"]).sort_values("ST_Mid", ascending=True)
                # Highlight Amecath as a reference line
                amecath_st = asp_df["Short_Term"].mean() if not asp_df.empty else 19
                fig_comp = go.Figure()
                fig_comp.add_trace(go.Bar(
                    y=gcc_comp["Company"],
                    x=gcc_comp["ST_Mid"],
                    orientation="h",
                    marker=dict(
                        color=gcc_comp["ST_Mid"],
                        colorscale=[[0, EMERALD], [0.5, GOLD], [1, RED]],
                        showscale=False,
                    ),
                    text=[f"${v:.0f}" for v in gcc_comp["ST_Mid"]],
                    textposition="outside",
                    textfont=dict(color=OFF_WHITE, size=10),
                    hovertemplate="<b>%{y}</b><br>ST ASP midpoint: $%{x:.0f}<extra></extra>",
                    name="Competitor ASP",
                ))
                fig_comp.add_vline(
                    x=amecath_st,
                    line=dict(color=TEAL, dash="dash", width=2),
                    annotation_text=f"Amecath ${amecath_st:.0f}",
                    annotation_font_color=TEAL,
                    annotation_position="top right",
                )
                fig_comp.update_layout(
                    title="Short-Term ASP Midpoints (GCC)",
                    height=380,
                    showlegend=False,
                    yaxis=dict(autorange="reversed"),
                )
                apply_template(fig_comp)
                st.plotly_chart(fig_comp, use_container_width=True)

    # ── Margin Estimator ──
    st.markdown("---")
    st.markdown("<div class='section-header'>Interactive Margin Estimator</div>", unsafe_allow_html=True)

    col_slider, col_result = st.columns([1, 2], gap="large")
    with col_slider:
        st.markdown(f"""
        <div class='kpi-card'>
          <div class='kpi-label'>Distributor Markup (%)</div>
        """, unsafe_allow_html=True)
        markup_pct = st.slider("Markup %", min_value=10, max_value=150, value=60, step=5, label_visibility="collapsed")
        term_select = st.selectbox("Catheter Type", ["Short-Term", "Mid-Term", "Long-Term"])
        st.markdown("</div>", unsafe_allow_html=True)

    with col_result:
        if not asp_f.empty:
            term_col = {"Short-Term": "Short_Term", "Mid-Term": "Mid_Term", "Long-Term": "Long_Term"}[term_select]
            margin_df = asp_f[["Country", "Region", term_col]].copy()
            margin_df = margin_df.rename(columns={term_col: "Ex_Factory"})
            margin_df["Distributor_Price"] = margin_df["Ex_Factory"] * (1 + markup_pct / 100)
            margin_df["Distributor_Profit"] = margin_df["Distributor_Price"] - margin_df["Ex_Factory"]
            margin_df["Margin_Pct"]   = markup_pct
            margin_df["Flag_Country"] = margin_df["Country"].map(
                lambda c: f"{COUNTRY_FLAG.get(c, '')} {c}"
            )

            fig_margin = go.Figure()
            fig_margin.add_trace(go.Bar(
                name="Ex-Factory (Amecath)",
                x=margin_df["Flag_Country"],
                y=margin_df["Ex_Factory"],
                marker_color=TEAL,
                hovertemplate="<b>%{x}</b><br>Ex-Factory: $%{y:.0f}<extra></extra>",
            ))
            fig_margin.add_trace(go.Bar(
                name="Distributor Margin",
                x=margin_df["Flag_Country"],
                y=margin_df["Distributor_Profit"],
                marker_color=GOLD,
                hovertemplate="<b>%{x}</b><br>Distributor Profit: $%{y:.0f}<extra></extra>",
            ))
            fig_margin.update_layout(
                title=f"Price Stack at {markup_pct}% Markup — {term_select} Catheters",
                barmode="stack",
                height=330,
                legend=dict(orientation="h", y=1.08),
                yaxis_title="USD per unit",
            )
            apply_template(fig_margin)
            st.plotly_chart(fig_margin, use_container_width=True)

            # Summary table
            margin_display = margin_df[[
                "Flag_Country", "Ex_Factory", "Distributor_Price", "Distributor_Profit"
            ]].rename(columns={
                "Flag_Country":      "Country",
                "Ex_Factory":        "Ex-Factory ($)",
                "Distributor_Price": f"Dist. Price ({markup_pct}% up) ($)",
                "Distributor_Profit": "Dist. Profit ($)",
            })
            st.dataframe(
                margin_display.style.format({
                    "Ex-Factory ($)": "${:.1f}",
                    f"Dist. Price ({markup_pct}% up) ($)": "${:.1f}",
                    "Dist. Profit ($)": "${:.1f}",
                }),
                use_container_width=True,
                hide_index=True,
            )


# ═══════════════════════════════════════════════════════════════
# TAB 3 — HOTSPOTS & COMMERCIAL NETWORK
# ═══════════════════════════════════════════════════════════════
with tab3:
    # ── 3A: City Hotspots ──
    st.markdown("<div class='section-header'>Dialysis Center Hotspots by City</div>", unsafe_allow_html=True)

    hot_f = filter_df(hotspot_df)
    if not hot_f.empty:
        search_city = st.text_input("🔍 Search city or detail…", placeholder="e.g. Riyadh, Baghdad, Dubai")
        if search_city:
            hot_f = hot_f[hot_f["City_Detail"].str.contains(search_city, case=False, na=False)]

        # Show as card grid — 3 columns
        hot_top = hot_f[hot_f["Rank"] <= 5].sort_values(["Country", "Rank"])
        cols_hot = st.columns(3)
        for i, row in hot_top.iterrows():
            with cols_hot[i % 3]:
                flag = COUNTRY_FLAG.get(row["Country"], "")
                rank_badge = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][min(row["Rank"] - 1, 4)]
                st.markdown(f"""
                <div class='city-card'>
                  <div class='city-card-title'>{rank_badge} {flag} {row['Country']}</div>
                  <div class='city-card-body'>{row['City_Detail'][:220]}{"…" if len(row['City_Detail']) > 220 else ""}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hotspot data available for selected filters.")

    st.markdown("---")

    # ── 3B: Distributors Directory ──
    st.markdown("<div class='section-header'>Distributors Directory</div>", unsafe_allow_html=True)

    dist_f = filter_df(dist_df)
    if not dist_f.empty:
        col_ds, col_dc = st.columns([2, 1])
        with col_ds:
            search_dist = st.text_input("🔍 Search distributor…", placeholder="e.g. dialysis, vascular, catheter")
        with col_dc:
            prio_options = ["All"] + sorted(dist_f["Priority"].dropna().unique().tolist())
            prio_filter  = st.selectbox("Filter by Priority", prio_options)

        display_dist = dist_f.copy()
        if search_dist:
            mask = (
                display_dist["Distributor"].str.contains(search_dist, case=False, na=False) |
                display_dist["Relevance"].str.contains(search_dist, case=False, na=False)
            )
            display_dist = display_dist[mask]
        if prio_filter != "All":
            display_dist = display_dist[display_dist["Priority"] == prio_filter]

        st.markdown(f"<div style='color:{MUTED}; font-size:.8rem; margin-bottom:6px;'>"
                    f"Showing {len(display_dist)} of {len(dist_f)} distributors</div>",
                    unsafe_allow_html=True)
        st.dataframe(
            display_dist[["Country", "Region", "#", "Distributor", "Relevance", "Contact", "Priority"]]
            .reset_index(drop=True),
            use_container_width=True,
            height=380,
            hide_index=True,
        )
    else:
        st.info("No distributor data for selected filters.")

    st.markdown("---")

    # ── 3C: KOL Directory ──
    st.markdown("<div class='section-header'>Key Opinion Leaders (KOLs) — Nephrology & Interventional Radiology</div>", unsafe_allow_html=True)

    kol_f = filter_df(kol_df)
    if not kol_f.empty:
        search_kol = st.text_input("🔍 Search KOL, specialty, or institution…",
                                   placeholder="e.g. nephrology, vascular, dialysis")
        if search_kol:
            mask_kol = (
                kol_f["KOL"].str.contains(search_kol, case=False, na=False) |
                kol_f["Specialty"].str.contains(search_kol, case=False, na=False) |
                kol_f["Institution"].str.contains(search_kol, case=False, na=False)
            )
            kol_f = kol_f[mask_kol]

        st.dataframe(
            kol_f[["Country", "Region", "#", "KOL", "Specialty", "Institution", "Contact"]]
            .reset_index(drop=True),
            use_container_width=True,
            height=360,
            hide_index=True,
        )
    else:
        st.info("No KOL data for selected filters.")

    st.markdown("---")

    # ── 3D: Procurement Bodies ──
    st.markdown("<div class='section-header'>Central Procurement Bodies</div>", unsafe_allow_html=True)

    proc_f = filter_df(procurement_df)
    if not proc_f.empty:
        cols_proc = st.columns(2)
        for i, row in proc_f.iterrows():
            with cols_proc[i % 2]:
                flag = COUNTRY_FLAG.get(str(row.get("Country", "")), "")
                st.markdown(f"""
                <div class='proc-card'>
                  <div class='proc-title'>{flag} {row.get("Country", "")}</div>
                  <div class='proc-body'>
                    <b>Primary:</b> {row.get("Primary_Body", "N/A")}<br/>
                    <b>Secondary:</b> {str(row.get("Secondary_Buyers", ""))[:160]}<br/>
                    <b>Notes:</b> {str(row.get("Notes", ""))[:200]}
                  </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No procurement data available.")


# ═══════════════════════════════════════════════════════════════
# TAB 4 — TENDERS TRACKER
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-header'>Active & Upcoming Tender Pipeline</div>", unsafe_allow_html=True)

    tender_f = filter_df(tender_df)
    if not tender_f.empty:
        # Status filter pills via selectbox
        status_opts = ["All"] + sorted(tender_f["Status"].dropna().unique().tolist())
        col_ts, col_tc = st.columns([1, 2])
        with col_ts:
            status_sel = st.selectbox("Filter by Status", status_opts)
        with col_tc:
            tender_search = st.text_input("🔍 Search tenders…", placeholder="e.g. dialysis, catheter, consumables")

        display_tender = tender_f.copy()
        if status_sel != "All":
            display_tender = display_tender[display_tender["Status"] == status_sel]
        if tender_search:
            mask_t = (
                display_tender.get("Title", pd.Series(dtype=str)).str.contains(tender_search, case=False, na=False) |
                display_tender.get("Entity", pd.Series(dtype=str)).str.contains(tender_search, case=False, na=False) |
                display_tender.get("Notes", pd.Series(dtype=str)).str.contains(tender_search, case=False, na=False)
            )
            display_tender = display_tender[mask_t]

        # KPI row
        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Total Tenders",   len(tender_f))
        t2.metric("Active 2026",     len(tender_f[tender_f["Status"] == "Active 2026"]))
        t3.metric("Upcoming",        len(tender_f[tender_f["Status"] == "Upcoming"]))
        t4.metric("Rolling / Open",  len(tender_f[tender_f["Status"] == "Rolling"]))

        st.markdown(f"<div style='color:{MUTED}; font-size:.8rem; margin:8px 0;'>"
                    f"Showing {len(display_tender)} tenders</div>", unsafe_allow_html=True)

        # Render as individual cards for readability
        for _, row in display_tender.iterrows():
            status = row.get("Status", "")
            badge_class = {
                "Active 2026": "badge-active",
                "Upcoming":    "badge-upcoming",
                "Rolling":     "badge-upcoming",
                "Past":        "badge-past",
            }.get(status, "badge-past")

            country   = str(row.get("Country", ""))
            flag      = COUNTRY_FLAG.get(country, "")
            title     = str(row.get("Title", "N/A"))
            entity    = str(row.get("Entity", "N/A"))
            closing   = str(row.get("Closing_Date", "N/A"))
            notes     = str(row.get("Notes", ""))[:200]
            ref       = str(row.get("Ref", ""))
            link      = str(row.get("Link", ""))

            link_html = (f'<a href="{link}" target="_blank" '
                         f'style="color:{TEAL}; text-decoration:none; font-size:.8rem;">🔗 Open Tender</a>'
                         if link and link.startswith("http") else "")

            st.markdown(f"""
            <div style="
              background:{SLATE};
              border:1px solid {SLATE2};
              border-radius:12px;
              padding:16px 20px;
              margin-bottom:10px;
              box-shadow: 0 2px 10px rgba(0,0,0,.25);
            ">
              <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
                <div>
                  <span style="font-size:.8rem; color:{MUTED};">{flag} {country} &nbsp;·&nbsp; Ref: {ref}</span><br/>
                  <span style="font-size:1rem; font-weight:700; color:{OFF_WHITE};">{title}</span>
                </div>
                <span class="{badge_class}">{status}</span>
              </div>
              <div style="margin-top:10px; font-size:.83rem; color:{MUTED}; line-height:1.6;">
                <b style="color:{TEAL};">Issuing Entity:</b> {entity} &nbsp;·&nbsp;
                <b style="color:{TEAL};">Closing:</b> {closing}<br/>
                <b style="color:{TEAL};">Scope:</b> {notes}
              </div>
              <div style="margin-top:8px;">{link_html}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Tender volume by country chart ──
        st.markdown("<div class='section-header'>Tender Distribution by Country</div>", unsafe_allow_html=True)
        tend_count = tender_f["Country"].value_counts().reset_index()
        tend_count.columns = ["Country", "Count"]
        tend_count["Flag"] = tend_count["Country"].map(lambda c: f"{COUNTRY_FLAG.get(c,'')} {c}")
        fig_tend = px.bar(
            tend_count.sort_values("Count", ascending=True),
            x="Count",
            y="Flag",
            orientation="h",
            color="Count",
            color_continuous_scale=[[0, SLATE2], [0.5, TEAL], [1, EMERALD]],
            labels={"Flag": "", "Count": "# Tenders"},
            text="Count",
        )
        fig_tend.update_layout(title="Number of Tenders by Country", height=320, coloraxis_showscale=False)
        fig_tend.update_traces(textposition="outside", textfont_color=OFF_WHITE)
        apply_template(fig_tend)
        st.plotly_chart(fig_tend, use_container_width=True)

    else:
        st.info("No tender data for selected filters.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(f"""
<hr style="border-color:{SLATE2}; margin: 32px 0 16px;"/>
<div style="text-align:center; color:{MUTED}; font-size:.75rem; line-height:1.8;">
  🩺 <b style="color:{TEAL};">Amecath Hemodialysis Catheters</b> — MENA Market Intelligence Dashboard<br/>
  Data vintage: 2026 estimates · 9 MENA countries · Sources: expert judgment, MOH portals, HMC, IQTenders, Etimad<br/>
  <span style="color:{SLATE2};">Built with Streamlit + Plotly · For internal commercial use only</span>
</div>
""", unsafe_allow_html=True)
