import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Work & Life — Global Balance Report",
    page_icon="⏳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0f0f13;
    color: #e8e6e0;
}
section[data-testid="stSidebar"] {
    background-color: #16161c;
    border-right: 1px solid #2a2a35;
}
section[data-testid="stSidebar"] * { color: #c8c6c0 !important; }
.main-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3rem;
    line-height: 1.1;
    color: #f0ede6;
    margin-bottom: 0.2rem;
}
.main-subtitle {
    font-size: 1rem;
    color: #888;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}
.kpi-row { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
.kpi-card {
    background: #16161c;
    border: 1px solid #2a2a35;
    border-radius: 10px;
    padding: 1.2rem 1.6rem;
    flex: 1;
    min-width: 160px;
}
.kpi-label {
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 0.3rem;
}
.kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #e8c96a;
    line-height: 1;
}
.kpi-sub { font-size: 0.78rem; color: #555; margin-top: 0.25rem; }
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    color: #f0ede6;
    border-bottom: 1px solid #2a2a35;
    padding-bottom: 0.5rem;
    margin-top: 2.5rem;
    margin-bottom: 1rem;
}
.insight-box {
    background: #1a1a22;
    border-left: 3px solid #e8c96a;
    border-radius: 0 8px 8px 0;
    padding: 0.9rem 1.2rem;
    font-size: 0.88rem;
    color: #b0aea8;
    margin-bottom: 1rem;
    line-height: 1.6;
}
.insight-box b { color: #e8c96a; }
.stPlotlyChart { border-radius: 10px; overflow: hidden; }
button[data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY THEME CONSTANTS
# ─────────────────────────────────────────────
PLOT_BG  = "#0f0f13"
PAPER_BG = "#0f0f13"
GRID_CLR = "#2a2a35"
FONT_CLR = "#c8c6c0"
ACCENT   = "#e8c96a"
PALETTE  = ["#e8c96a", "#6a8ce8", "#e86a8c", "#6ae8c9", "#c96ae8", "#8ce86a"]

# base_layout has NO xaxis / yaxis / margin — never conflicts with per-chart overrides
def base_layout(title=""):
    return dict(
        title=dict(text=title, font=dict(family="DM Serif Display", size=18, color=FONT_CLR)),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family="DM Sans", color=FONT_CLR),
        margin=dict(t=60, b=40, l=40, r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID_CLR),
    )

def style_axes(fig, x_title="", y_title=""):
    fig.update_xaxes(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR, title_text=x_title)
    fig.update_yaxes(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR, title_text=y_title)

# ─────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────

# ⚠️ EDUCATIONAL PURPOSE ONLY — never hardcode credentials in production
# Use environment variables or secrets manager instead
@st.cache_data(show_spinner="Connecting to database…")
def load_data():
    engine = create_engine(
        'postgresql://postgres:mysecretpassword@db:5432/postgres'
    )
    df = pd.read_sql("SELECT * FROM master_table", engine)
    df.columns = [c.upper() for c in df.columns]
    df = df.dropna(subset=["LIFE_EXPECTANCY", "HOURS_YEARLY", "GDP"])
    df["YEAR"] = df["YEAR"].astype(int)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Could not connect to the database. Make sure Docker & PostgreSQL are running.\n\n`{e}`")
    st.stop()

# ─────────────────────────────────────────────
#  SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⏳ Work & Life Report")
    st.markdown("---")

    all_countries = sorted(df["COUNTRY"].unique())
    selected_countries = st.multiselect(
        "Filter Countries",
        options=all_countries,
        default=[],
        placeholder="All countries"
    )

    year_min, year_max = int(df["YEAR"].min()), int(df["YEAR"].max())
    year_range = st.slider("Year Range", year_min, year_max, (year_min, year_max))

    st.markdown("---")
    st.markdown("**Work Intensity Thresholds**")
    low_thresh  = st.number_input("Low  (< hours)", value=1700, step=50)
    high_thresh = st.number_input("High (> hours)", value=1900, step=50)

    st.markdown("---")
    st.caption("Final Project · Data Analyst Bootcamp")

# ─────────────────────────────────────────────
#  APPLY FILTERS
# ─────────────────────────────────────────────
filtered = df[df["YEAR"].between(year_range[0], year_range[1])]
if selected_countries:
    filtered = filtered[filtered["COUNTRY"].isin(selected_countries)]

avg = (
    filtered
    .groupby("COUNTRY", as_index=False)
    .agg(
        LIFE_EXPECTANCY=("LIFE_EXPECTANCY", "mean"),
        HOURS_YEARLY=("HOURS_YEARLY", "mean"),
        GDP=("GDP", "mean"),
    )
)

def work_intensity(h):
    if h < low_thresh:  return "Low"
    if h > high_thresh: return "High"
    return "Medium"

avg["INTENSITY"] = avg["HOURS_YEARLY"].apply(work_intensity)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">Work & Life</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Global Balance Report · Does working more mean living longer?</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
#  KPI CARDS
# ─────────────────────────────────────────────
n_countries  = avg["COUNTRY"].nunique()
global_hours = avg["HOURS_YEARLY"].mean()
global_life  = avg["LIFE_EXPECTANCY"].mean()
global_gdp   = avg["GDP"].mean()
corr_val     = avg[["HOURS_YEARLY", "LIFE_EXPECTANCY"]].corr().iloc[0, 1]

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-label">Countries</div>
    <div class="kpi-value">{n_countries}</div>
    <div class="kpi-sub">in selected period</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Avg Work Hours / Year</div>
    <div class="kpi-value">{global_hours:,.0f}</div>
    <div class="kpi-sub">per worker</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Avg Life Expectancy</div>
    <div class="kpi-value">{global_life:.1f}</div>
    <div class="kpi-sub">years</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Avg GDP</div>
    <div class="kpi-value">${global_gdp:,.0f}</div>
    <div class="kpi-sub">per capita (USD)</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Hours ↔ Life Corr.</div>
    <div class="kpi-value">{corr_val:+.2f}</div>
    <div class="kpi-sub">Pearson r</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌍 Overview",
    "📈 Correlations",
    "🗓️ Trends Over Time",
    "🏆 Country Rankings",
    "🚨 Overworked & Rich",
])

# ══════════════════════════════════════════════
#  TAB 1 — OVERVIEW
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Work Intensity Distribution</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    Countries are categorised as <b>Low</b>, <b>Medium</b>, or <b>High</b> intensity workers.
    Use the sidebar to adjust the thresholds. The box plot shows how life expectancy
    distributes within each intensity group.
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        intensity_counts = avg["INTENSITY"].value_counts().reset_index()
        intensity_counts.columns = ["Intensity", "Count"]
        color_map = {"Low": "#6ae8c9", "Medium": ACCENT, "High": "#e86a8c"}

        fig_donut = go.Figure(go.Pie(
            labels=intensity_counts["Intensity"],
            values=intensity_counts["Count"],
            hole=0.55,
            marker=dict(colors=[color_map.get(i, "#888") for i in intensity_counts["Intensity"]]),
            textfont=dict(size=13),
            hovertemplate="<b>%{label}</b><br>%{value} countries (%{percent})<extra></extra>",
        ))
        fig_donut.update_layout(
            **base_layout("Work Intensity — Share of Countries"),
            showlegend=True,
        )
        fig_donut.add_annotation(
            text=f"<b>{n_countries}</b><br>countries",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=FONT_CLR),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        fig_box = go.Figure()
        for lvl, clr in [("Low", "#6ae8c9"), ("Medium", ACCENT), ("High", "#e86a8c")]:
            sub = avg[avg["INTENSITY"] == lvl]
            fig_box.add_trace(go.Box(
                y=sub["LIFE_EXPECTANCY"],
                name=lvl,
                marker_color=clr,
                line_color=clr,
                fillcolor="rgba(0,0,0,0)",
                hovertemplate=f"<b>{lvl}</b><br>Life Exp: %{{y:.1f}} yrs<extra></extra>",
            ))
        fig_box.update_layout(
            **base_layout("Life Expectancy by Work Intensity"),
            showlegend=False,
            height=400,
        )
        style_axes(fig_box, y_title="Life Expectancy (years)")
        st.plotly_chart(fig_box, use_container_width=True)

    # MAP
    st.markdown('<div class="section-header">Geographic Map — Annual Work Hours</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    Green = fewer hours, Red = most hours. Geographic clusters reveal regional labour norms —
    East Asia, Latin America, and parts of Africa tend to cluster on the high end.
    </div>
    """, unsafe_allow_html=True)

    fig_map = px.choropleth(
        avg,
        locations="COUNTRY",
        locationmode="country names",
        color="HOURS_YEARLY",
        hover_name="COUNTRY",
        hover_data={
            "HOURS_YEARLY": ":.0f",
            "LIFE_EXPECTANCY": ":.1f",
            "GDP": ":,.0f",
        },
        color_continuous_scale=["#6ae8c9", "#e8c96a", "#e86a8c"],
        labels={"HOURS_YEARLY": "Avg Hours/Year"},
    )
    fig_map.update_layout(
        **base_layout("Average Annual Work Hours per Worker"),
        geo=dict(
            bgcolor=PLOT_BG,
            landcolor="#1e1e2a",
            oceancolor="#0f0f13",
            showocean=True,
            coastlinecolor="#2a2a35",
            showframe=False,
        ),
        coloraxis_colorbar=dict(
            title=dict(text="Hours/Year", font=dict(color=FONT_CLR)),
            tickfont=dict(color=FONT_CLR),
        ),
        height=500,
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ══════════════════════════════════════════════
#  TAB 2 — CORRELATIONS
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Work Hours vs Life Expectancy</div>', unsafe_allow_html=True)

    corr_dir      = "negative" if corr_val < 0 else "positive"
    corr_strength = "strong" if abs(corr_val) > 0.5 else ("moderate" if abs(corr_val) > 0.3 else "weak")
    st.markdown(f"""
    <div class="insight-box">
    There is a <b>{corr_strength} {corr_dir} correlation (r = {corr_val:+.2f})</b> between annual work
    hours and life expectancy. Bubble size represents GDP — hover over any dot for full details.
    </div>
    """, unsafe_allow_html=True)

    fig_s1 = px.scatter(
        avg,
        x="HOURS_YEARLY",
        y="LIFE_EXPECTANCY",
        color="INTENSITY",
        size="GDP",
        size_max=30,
        hover_name="COUNTRY",
        hover_data={"HOURS_YEARLY": ":.0f", "LIFE_EXPECTANCY": ":.1f", "GDP": ":,.0f", "INTENSITY": False},
        color_discrete_map={"Low": "#6ae8c9", "Medium": ACCENT, "High": "#e86a8c"},
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override="#ffffff",
        labels={"HOURS_YEARLY": "Annual Work Hours", "LIFE_EXPECTANCY": "Life Expectancy (years)"},
    )
    fig_s1.update_layout(**base_layout("Work Hours vs Life Expectancy  (bubble size = GDP)"), height=520)
    style_axes(fig_s1, x_title="Annual Work Hours", y_title="Life Expectancy (years)")
    st.plotly_chart(fig_s1, use_container_width=True)

    st.markdown('<div class="section-header">GDP vs Life Expectancy</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    GDP per capita has a well-documented <b>positive</b> relationship with life expectancy.
    Colour represents work intensity — exposing countries that are <b>rich yet overworked</b>.
    </div>
    """, unsafe_allow_html=True)

    fig_s2 = px.scatter(
        avg,
        x="GDP",
        y="LIFE_EXPECTANCY",
        color="INTENSITY",
        size="HOURS_YEARLY",
        size_max=28,
        hover_name="COUNTRY",
        hover_data={"GDP": ":,.0f", "LIFE_EXPECTANCY": ":.1f", "HOURS_YEARLY": ":.0f", "INTENSITY": False},
        color_discrete_map={"Low": "#6ae8c9", "Medium": ACCENT, "High": "#e86a8c"},
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override="#ffffff",
        labels={"GDP": "GDP per Capita (USD)", "LIFE_EXPECTANCY": "Life Expectancy (years)"},
        log_x=True,
    )
    fig_s2.update_layout(**base_layout("GDP vs Life Expectancy  (bubble size = work hours)"), height=520)
    style_axes(fig_s2, x_title="GDP per Capita (USD)", y_title="Life Expectancy (years)")
    st.plotly_chart(fig_s2, use_container_width=True)

    st.markdown('<div class="section-header">Correlation Heatmap</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    Pairwise correlations between all three variables. Compare the GDP–Life Expectancy cell
    vs the Hours–Life Expectancy cell to understand which factor matters more.
    </div>
    """, unsafe_allow_html=True)

    corr_matrix = avg[["HOURS_YEARLY", "LIFE_EXPECTANCY", "GDP"]].corr().round(2)
    labels_map  = {"HOURS_YEARLY": "Work Hours", "LIFE_EXPECTANCY": "Life Expectancy", "GDP": "GDP"}
    corr_matrix.index   = [labels_map[c] for c in corr_matrix.index]
    corr_matrix.columns = [labels_map[c] for c in corr_matrix.columns]

    fig_heat = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale=[[0, "#e86a8c"], [0.5, "#1e1e2a"], [1, "#6ae8c9"]],
        zmin=-1, zmax=1,
        text=corr_matrix.values,
        texttemplate="%{text}",
        textfont=dict(size=16, color="#fff"),
        hovertemplate="%{y} × %{x}<br>r = %{z:.2f}<extra></extra>",
    ))
    fig_heat.update_layout(**base_layout("Correlation Heatmap"), height=380)
    style_axes(fig_heat)
    st.plotly_chart(fig_heat, use_container_width=True)

# ══════════════════════════════════════════════
#  TAB 3 — TRENDS OVER TIME
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">How Has Work & Life Changed Over Time?</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    The temporal dimension — select specific countries to compare trajectories,
    or leave blank to see the global average across all years.
    </div>
    """, unsafe_allow_html=True)

    time_countries = st.multiselect(
        "Highlight specific countries (leave blank for global average)",
        options=all_countries,
        default=[],
        key="time_countries",
        placeholder="Global average"
    )

    if time_countries:
        time_df   = filtered[filtered["COUNTRY"].isin(time_countries)]
        group_col = "COUNTRY"
    else:
        time_df = (
            filtered.groupby("YEAR", as_index=False)
            .agg(
                LIFE_EXPECTANCY=("LIFE_EXPECTANCY", "mean"),
                HOURS_YEARLY=("HOURS_YEARLY", "mean"),
                GDP=("GDP", "mean"),
            )
        )
        time_df["COUNTRY"] = "Global Average"
        group_col = "COUNTRY"

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        fig_t1 = px.line(
            time_df, x="YEAR", y="HOURS_YEARLY",
            color=group_col,
            markers=True,
            labels={"HOURS_YEARLY": "Avg Hours/Year", "YEAR": "Year"},
            color_discrete_sequence=PALETTE,
        )
        fig_t1.update_layout(**base_layout("Annual Work Hours Over Time"), height=380)
        fig_t1.update_traces(line=dict(width=2.5))
        style_axes(fig_t1, x_title="Year", y_title="Avg Hours/Year")
        st.plotly_chart(fig_t1, use_container_width=True)

    with col_t2:
        fig_t2 = px.line(
            time_df, x="YEAR", y="LIFE_EXPECTANCY",
            color=group_col,
            markers=True,
            labels={"LIFE_EXPECTANCY": "Life Expectancy (years)", "YEAR": "Year"},
            color_discrete_sequence=PALETTE,
        )
        fig_t2.update_layout(**base_layout("Life Expectancy Over Time"), height=380)
        fig_t2.update_traces(line=dict(width=2.5))
        style_axes(fig_t2, x_title="Year", y_title="Life Expectancy (years)")
        st.plotly_chart(fig_t2, use_container_width=True)

    st.markdown('<div class="section-header">Combined: Hours & Life Expectancy — Dual Axis</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    Both metrics on dual axes for a single country or the global average.
    Reveals whether work hours and life expectancy move together or diverge over time.
    </div>
    """, unsafe_allow_html=True)

    focus_country = st.selectbox(
        "Select a country for dual-axis view",
        options=["Global Average"] + all_countries,
        index=0,
        key="dual_country"
    )

    if focus_country == "Global Average":
        dual_df = (
            filtered.groupby("YEAR", as_index=False)
            .agg(
                LIFE_EXPECTANCY=("LIFE_EXPECTANCY", "mean"),
                HOURS_YEARLY=("HOURS_YEARLY", "mean"),
            )
        )
    else:
        dual_df = filtered[filtered["COUNTRY"] == focus_country].sort_values("YEAR")

    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
    fig_dual.add_trace(
        go.Scatter(
            x=dual_df["YEAR"], y=dual_df["HOURS_YEARLY"],
            name="Work Hours", mode="lines+markers",
            line=dict(color="#e86a8c", width=2.5),
            hovertemplate="Year %{x}<br>Hours: %{y:,.0f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig_dual.add_trace(
        go.Scatter(
            x=dual_df["YEAR"], y=dual_df["LIFE_EXPECTANCY"],
            name="Life Expectancy", mode="lines+markers",
            line=dict(color="#6ae8c9", width=2.5),
            hovertemplate="Year %{x}<br>Life Exp: %{y:.1f} yrs<extra></extra>",
        ),
        secondary_y=True,
    )
    fig_dual.update_layout(
        **base_layout(f"Work Hours & Life Expectancy — {focus_country}"),
        height=420,
    )
    fig_dual.update_xaxes(gridcolor=GRID_CLR, title_text="Year")
    fig_dual.update_yaxes(title_text="Annual Work Hours",     gridcolor=GRID_CLR, secondary_y=False)
    fig_dual.update_yaxes(title_text="Life Expectancy (yrs)", gridcolor=GRID_CLR, secondary_y=True)
    st.plotly_chart(fig_dual, use_container_width=True)

# ══════════════════════════════════════════════
#  TAB 4 — COUNTRY RANKINGS
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Countries Ranked by Annual Work Hours</div>', unsafe_allow_html=True)

    n_show     = st.slider("How many countries to display?", 5, min(40, len(avg)), 20)
    sort_order = st.radio("Order", ["Highest first", "Lowest first"], horizontal=True)
    ascending  = sort_order == "Lowest first"

    ranked = avg.sort_values("HOURS_YEARLY", ascending=ascending).head(n_show)

    fig_bar = go.Figure(go.Bar(
        x=ranked["HOURS_YEARLY"],
        y=ranked["COUNTRY"],
        orientation="h",
        marker=dict(
            color=ranked["HOURS_YEARLY"],
            colorscale=[[0, "#6ae8c9"], [0.5, ACCENT], [1, "#e86a8c"]],
            showscale=False,
        ),
        customdata=np.stack([
            ranked["LIFE_EXPECTANCY"],
            ranked["GDP"],
            ranked["INTENSITY"],
        ], axis=-1),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Hours/Year: %{x:,.0f}<br>"
            "Life Expectancy: %{customdata[0]:.1f} yrs<br>"
            "GDP: $%{customdata[1]:,.0f}<br>"
            "Intensity: %{customdata[2]}<extra></extra>"
        ),
    ))
    fig_bar.update_layout(
        **base_layout("Countries Ranked by Average Annual Work Hours"),
        height=max(400, n_show * 28),
    )
    fig_bar.update_yaxes(autorange="reversed" if not ascending else True, gridcolor=GRID_CLR)
    fig_bar.update_xaxes(title_text="Annual Work Hours", gridcolor=GRID_CLR)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('<div class="section-header">Countries Ranked by Life Expectancy</div>', unsafe_allow_html=True)

    ranked_life = avg.sort_values("LIFE_EXPECTANCY", ascending=False).head(n_show)
    fig_bar2 = go.Figure(go.Bar(
        x=ranked_life["LIFE_EXPECTANCY"],
        y=ranked_life["COUNTRY"],
        orientation="h",
        marker=dict(
            color=ranked_life["LIFE_EXPECTANCY"],
            colorscale=[[0, "#e86a8c"], [1, "#6ae8c9"]],
            showscale=False,
        ),
        customdata=np.stack([ranked_life["HOURS_YEARLY"], ranked_life["GDP"]], axis=-1),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Life Expectancy: %{x:.1f} yrs<br>"
            "Hours/Year: %{customdata[0]:,.0f}<br>"
            "GDP: $%{customdata[1]:,.0f}<extra></extra>"
        ),
    ))
    fig_bar2.update_layout(
        **base_layout("Countries Ranked by Life Expectancy"),
        height=max(400, n_show * 28),
    )
    fig_bar2.update_yaxes(autorange="reversed", gridcolor=GRID_CLR)
    fig_bar2.update_xaxes(title_text="Life Expectancy (years)", gridcolor=GRID_CLR)
    st.plotly_chart(fig_bar2, use_container_width=True)

# ══════════════════════════════════════════════
#  TAB 5 — OVERWORKED & RICH
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">The Overworked & Rich — A Work-Life Paradox</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    These countries answer the hardest part of the research question: <b>economic success without
    quality of life.</b> They sit above the GDP median (wealthy), above the hours median (overworked),
    yet <b>below the life expectancy median</b> — the paradox countries.
    </div>
    """, unsafe_allow_html=True)

    gdp_med   = avg["GDP"].median()
    hours_med = avg["HOURS_YEARLY"].median()
    life_med  = avg["LIFE_EXPECTANCY"].median()

    paradox = avg[
        (avg["GDP"]             >= gdp_med)   &
        (avg["HOURS_YEARLY"]    >= hours_med) &
        (avg["LIFE_EXPECTANCY"] <  life_med)
    ].sort_values("HOURS_YEARLY", ascending=False)

    overworked_rich = avg[
        (avg["GDP"]          >= gdp_med) &
        (avg["HOURS_YEARLY"] >= hours_med)
    ].sort_values("HOURS_YEARLY", ascending=False)

    if paradox.empty:
        st.info("No countries match the paradox criteria for the selected filters. Try broadening the year range or removing country filters.")
    else:
        st.markdown(f"**{len(paradox)} countries** match the paradox definition in the selected period.")

        col_p1, col_p2 = st.columns([1.3, 1])
        with col_p1:
            avg_labeled = avg.copy()
            avg_labeled["Category"] = avg_labeled["COUNTRY"].apply(
                lambda c: "Paradox 🚨" if c in paradox["COUNTRY"].values
                else ("High GDP + Hours" if c in overworked_rich["COUNTRY"].values else "Other")
            )
            fig_p = px.scatter(
                avg_labeled,
                x="GDP",
                y="LIFE_EXPECTANCY",
                color="Category",
                size="HOURS_YEARLY",
                size_max=28,
                hover_name="COUNTRY",
                hover_data={"GDP": ":,.0f", "LIFE_EXPECTANCY": ":.1f", "HOURS_YEARLY": ":.0f", "Category": False},
                color_discrete_map={
                    "Paradox 🚨":       "#e86a8c",
                    "High GDP + Hours": ACCENT,
                    "Other":            "#3a3a50",
                },
                log_x=True,
                labels={"GDP": "GDP per Capita", "LIFE_EXPECTANCY": "Life Expectancy (years)"},
            )
            fig_p.add_hline(y=life_med, line_dash="dot", line_color="#555", annotation_text="Life Exp. median")
            fig_p.add_vline(x=gdp_med,  line_dash="dot", line_color="#555", annotation_text="GDP median")
            fig_p.update_layout(**base_layout("GDP vs Life Expectancy — Paradox Highlighted"), height=480)
            style_axes(fig_p, x_title="GDP per Capita (USD)", y_title="Life Expectancy (years)")
            st.plotly_chart(fig_p, use_container_width=True)

        with col_p2:
            st.markdown("**Paradox Countries Table**")
            paradox_display = paradox[["COUNTRY", "HOURS_YEARLY", "GDP", "LIFE_EXPECTANCY"]].copy()
            paradox_display.columns = ["Country", "Hours/Year", "GDP", "Life Exp."]
            paradox_display["Hours/Year"] = paradox_display["Hours/Year"].round(0).astype(int)
            paradox_display["GDP"]        = paradox_display["GDP"].round(0).astype(int)
            paradox_display["Life Exp."]  = paradox_display["Life Exp."].round(1)
            st.dataframe(paradox_display, use_container_width=True, hide_index=True, height=460)

    # Radar chart
    st.markdown('<div class="section-header">Profile Comparison — Overworked Rich vs Low-Work Leaders</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    Normalised 0–1 radar comparing the average profile of the most overworked wealthy countries
    against countries with the lowest work hours.
    </div>
    """, unsafe_allow_html=True)

    top_overworked = avg.nlargest(5, "HOURS_YEARLY")
    top_relaxed    = avg.nsmallest(5, "HOURS_YEARLY")
    metrics        = ["HOURS_YEARLY", "LIFE_EXPECTANCY", "GDP"]
    m_labels       = ["Work Hours", "Life Expectancy", "GDP"]

    def normalise(col, countries):
        mn  = avg[col].min()
        mx  = avg[col].max()
        val = avg.loc[avg["COUNTRY"].isin(countries), col].mean()
        return round((val - mn) / (mx - mn + 1e-9), 3)

    fig_radar = go.Figure()
    for group_df, name, clr, fill_clr in [
        (top_overworked, "Top 5 Overworked", "#e86a8c", "rgba(232,106,140,0.15)"),
        (top_relaxed,    "Top 5 Low-Work",   "#6ae8c9", "rgba(106,232,201,0.15)"),
    ]:
        countries = group_df["COUNTRY"].tolist()
        vals      = [normalise(m, countries) for m in metrics]
        vals     += [vals[0]]

        fig_radar.add_trace(go.Scatterpolar(
            r=vals,
            theta=m_labels + [m_labels[0]],
            fill="toself",
            fillcolor=fill_clr,
            line=dict(color=clr, width=2),
            name=name,
            hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
        ))

    fig_radar.update_layout(
        **base_layout("Normalised Profile — Work, Life & Wealth"),
        polar=dict(
            bgcolor=PLOT_BG,
            radialaxis=dict(visible=True, range=[0, 1], gridcolor=GRID_CLR, color=FONT_CLR),
            angularaxis=dict(gridcolor=GRID_CLR, color=FONT_CLR),
        ),
        showlegend=True,
        height=450,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#444;font-size:0.8rem;padding:1rem 0;'>"
    "Work & Life Global Balance Report · Data Analyst Bootcamp Final Project · "
    "Data sourced via ETL pipeline → PostgreSQL"
    "</div>",
    unsafe_allow_html=True
)
