import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# KONFIGURASI & THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="Netflix | Content Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

BG = "#101010"
PANEL = "#1B1B1B"
RED = "#E50914"
MUTED = "#A8A8A8"
WHITE = "#F5F5F1"
GRID = "#383838"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: {BG}; color: {WHITE}; }}
    [data-testid="stSidebar"] {{ background: #171717; border-right: 1px solid #292929; }}
    [data-testid="stSidebar"] * {{ color: {WHITE}; }}
    h1, h2, h3 {{ color: {WHITE}; letter-spacing: -0.03em; }}
    h1 {{ font-weight: 800; }}
    [data-testid="stMetric"] {{
        background: linear-gradient(145deg, #222222, #181818);
        border: 1px solid #303030; padding: 18px 20px;
        border-radius: 14px; min-height: 120px;
    }}
    [data-testid="stMetricLabel"] {{ color: {MUTED}; font-size: 0.88rem; }}
    [data-testid="stMetricValue"] {{ color: {WHITE}; font-weight: 800; }}
    [data-testid="stMetricDelta"] {{ color: #B5E5C3; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {PANEL}; border: 1px solid #303030; border-radius: 14px;
        padding: 16px 18px;
    }}
    .eyebrow {{ color: {RED}; font-weight: 800; text-transform: uppercase;
        letter-spacing: .15em; font-size: .75rem; }}
    .hero {{ padding: 8px 0 18px 0; }}
    .hero h1 {{ margin: 2px 0 4px 0; font-size: 2.35rem; }}
    .subtext {{ color: {MUTED}; font-size: 0.98rem; }}
    .section-title {{ font-size: 1.18rem; font-weight: 700; margin: 0 0 2px 0; }}
    .section-caption {{ color: {MUTED}; font-size: .84rem; margin-bottom: 12px; }}
    .stButton button, .stDownloadButton button {{
        border-radius: 8px; border: 1px solid #444; font-weight: 600;
    }}
    hr {{ border-color: #303030; }}
    </style>
    """,
    unsafe_allow_html=True,
)

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": PANEL,
    "axes.facecolor": PANEL,
    "axes.edgecolor": GRID,
    "axes.labelcolor": WHITE,
    "text.color": WHITE,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "grid.color": GRID,
    "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
})

# ---------------------------------------------------------
# DATA SIMULASI
# ---------------------------------------------------------
@st.cache_data
def generate_data(rows=1200):
    rng = np.random.default_rng(42)
    types = rng.choice(["Movie", "TV Show"], rows, p=[0.70, 0.30])
    years = rng.choice(
        np.arange(2010, 2024), rows,
        p=[0.02, 0.03, 0.05, 0.05, 0.05, 0.05, 0.08,
           0.08, 0.10, 0.10, 0.12, 0.12, 0.10, 0.05],
    )
    countries = rng.choice(
        ["United States", "India", "United Kingdom", "Japan",
         "South Korea", "Canada", "France"], rows,
    )
    ratings = rng.choice(
        ["TV-MA", "TV-14", "TV-PG", "R", "PG-13", "TV-Y7", "TV-Y"], rows,
        p=[0.25, 0.22, 0.13, 0.14, 0.12, 0.08, 0.06],
    )
    duration = rng.integers(60, 180, rows)
    return pd.DataFrame({
        "type": types,
        "release_year": years,
        "country": countries,
        "rating": ratings,
        "duration": duration,
        "added_date": pd.date_range("2015-01-01", periods=rows),
    })

df = generate_data()

# ---------------------------------------------------------
# SIDEBAR FILTER
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"<div class='eyebrow'>CONTENT INTELLIGENCE</div>", unsafe_allow_html=True)
    st.markdown("## 🎬 Netflix Analytics")
    st.caption("Dashboard eksplorasi katalog")
    st.divider()

    st.markdown("### Filter data")
    selected_types = st.multiselect(
        "Tipe konten", sorted(df["type"].unique()),
        default=sorted(df["type"].unique()),
    )
    selected_countries = st.multiselect(
        "Negara", sorted(df["country"].unique()),
        default=sorted(df["country"].unique()),
    )
    year_range = st.slider(
        "Rentang tahun rilis", 2010, 2023, (2010, 2023),
    )
    st.divider()
    st.caption("Data pada praktikum ini adalah data simulasi, bukan data resmi Netflix.")
    if st.button("Reset filter", use_container_width=True):
        st.rerun()

filtered = df[
    df["type"].isin(selected_types)
    & df["country"].isin(selected_countries)
    & df["release_year"].between(year_range[0], year_range[1])
].copy()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">STREAMING • CATALOGUE • INSIGHTS</div>
      <h1>Content Intelligence</h1>
      <div class="subtext">Ringkasan komposisi katalog, pola rilis, dan klasifikasi usia.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f"<div style='height:3px;background:linear-gradient(90deg,{RED},#541014,transparent);border-radius:4px;margin-bottom:22px'></div>",
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("Tidak ada data yang cocok dengan filter. Ubah pilihan filter di sidebar.")
    st.stop()

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
movie_count = int((filtered["type"] == "Movie").sum())
tv_count = int((filtered["type"] == "TV Show").sum())
dominant_type = filtered["type"].value_counts().idxmax()
top_year = int(filtered["release_year"].value_counts().idxmax())
top_country = filtered["country"].value_counts().idxmax()
movie_share = movie_count / len(filtered) * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("TOTAL KONTEN", f"{len(filtered):,}", help="Jumlah baris yang lolos filter.")
k2.metric("MOVIE", f"{movie_count:,}", f"{movie_share:.1f}% dari katalog")
k3.metric("TIPE DOMINAN", dominant_type)
k4.metric("NEGARA TERATAS", top_country)

st.markdown("<br>", unsafe_allow_html=True)

# Helper untuk konsistensi chart
def polish(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(WHITE)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.7)
    for spine in ax.spines.values():
        spine.set_visible(False)

# ---------------------------------------------------------
# ROW 1: KOMPOSISI & NEGARA
# ---------------------------------------------------------
left, right = st.columns([0.9, 1.4], gap="large")

with left:
    with st.container(border=True):
        st.markdown("<div class='section-title'>Komposisi katalog</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-caption'>Proporsi film dan serial TV</div>", unsafe_allow_html=True)
        counts = filtered["type"].value_counts()
        fig, ax = plt.subplots(figsize=(5.2, 3.5))
        wedges, texts, autotexts = ax.pie(
            counts.values,
            labels=counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=[RED, "#555555"][:len(counts)],
            pctdistance=0.68,
            wedgeprops={"width": 0.38, "edgecolor": PANEL, "linewidth": 3},
            textprops={"color": WHITE, "fontsize": 9},
        )
        for t in autotexts:
            t.set_color(WHITE)
            t.set_fontweight("bold")
        ax.set_aspect("equal")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

with right:
    with st.container(border=True):
        st.markdown("<div class='section-title'>Kontributor konten teratas</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-caption'>Lima negara dengan jumlah konten terbanyak pada filter aktif</div>", unsafe_allow_html=True)
        country_counts = filtered["country"].value_counts().head(5).sort_values()
        fig, ax = plt.subplots(figsize=(7.5, 3.5))
        bars = ax.barh(country_counts.index, country_counts.values, color=RED, height=0.62)
        ax.bar_label(bars, padding=5, color=WHITE, fontsize=9, fontweight="bold")
        ax.set_xlabel("Jumlah konten")
        ax.set_ylabel("")
        ax.set_xlim(0, max(country_counts.values) * 1.18)
        polish(ax)
        ax.grid(axis="y", visible=False)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

# ---------------------------------------------------------
# ROW 2: TREND & RATING
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.markdown("<div class='section-title'>Tren tahun rilis</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-caption'>Jumlah konten berdasarkan tahun rilis dan tipe</div>", unsafe_allow_html=True)
        trend = filtered.groupby(["release_year", "type"]).size().reset_index(name="count")
        fig, ax = plt.subplots(figsize=(7, 4))
        palette = {"Movie": RED, "TV Show": "#E5E5E5"}
        sns.lineplot(
            data=trend, x="release_year", y="count", hue="type",
            hue_order=["Movie", "TV Show"], palette=palette,
            marker="o", linewidth=2.5, markersize=5, ax=ax,
        )
        ax.set_xlabel("Tahun rilis")
        ax.set_ylabel("Jumlah konten")
        ax.set_xticks(list(range(year_range[0], year_range[1] + 1, max(1, (year_range[1]-year_range[0])//6 or 1))))
        ax.legend(frameon=False, labelcolor=WHITE, title="")
        polish(ax)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

with right:
    with st.container(border=True):
        st.markdown("<div class='section-title'>Rating usia</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-caption'>Distribusi klasifikasi rating pada katalog terpilih</div>", unsafe_allow_html=True)
        rating_counts = filtered["rating"].value_counts().sort_values()
        fig, ax = plt.subplots(figsize=(7, 4))
        colors = [("#E50914" if r == rating_counts.idxmax() else "#6B292D") for r in rating_counts.index]
        bars = ax.barh(rating_counts.index, rating_counts.values, color=colors, height=0.66)
        ax.bar_label(bars, padding=4, color=WHITE, fontsize=9)
        ax.set_xlabel("Jumlah konten")
        ax.set_ylabel("")
        ax.set_xlim(0, max(rating_counts.values) * 1.2)
        polish(ax)
        ax.grid(axis="y", visible=False)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

# ---------------------------------------------------------
# DATA TABLE & EXPORT
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown("<div class='section-title'>Data katalog</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-caption'>Periksa baris data yang sesuai dengan filter saat ini atau unduh sebagai CSV.</div>", unsafe_allow_html=True)
    search = st.text_input("Cari negara, tipe, atau rating", placeholder="Contoh: Japan, Movie, TV-MA")
    display_df = filtered.copy()
    if search.strip():
        mask = display_df.astype(str).apply(
            lambda col: col.str.contains(search.strip(), case=False, na=False)
        ).any(axis=1)
        display_df = display_df[mask]
    st.caption(f"{len(display_df):,} baris ditampilkan")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇  Unduh hasil filter (CSV)",
        data=display_df.to_csv(index=False).encode("utf-8"),
        file_name="netflix_content_filtered.csv",
        mime="text/csv",
    )

st.markdown(
    "<div style='text-align:center;color:#777;font-size:.8rem;padding:20px 0 6px'>"
    "PRAKTIKUM VISUALISASI DATA · DATA SIMULASI · STREAMLIT</div>",
    unsafe_allow_html=True,
)
