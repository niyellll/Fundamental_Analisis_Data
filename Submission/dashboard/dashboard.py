import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Konfigurasi Halaman 
st.set_page_config(
    page_title="Air Quality Changping",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Konstanta 
SEASON_COLOR = {
    'Spring': '#4CAF50',
    'Summer': '#FF9800',
    'Autumn': '#CD853F',
    'Winter': '#2196F3'
}
AQI_COLOR = {
    'Good':                           '#00C853',
    'Moderate':                       '#FFD600',
    'Unhealthy for Sensitive Groups': '#FF6D00',
    'Unhealthy':                      '#D50000',
    'Very Unhealthy':                 '#6A1B9A',
    'Hazardous':                      '#37474F'
}
AQI_ORDER = [
    'Good', 'Moderate', 'Unhealthy for Sensitive Groups',
    'Unhealthy', 'Very Unhealthy', 'Hazardous'
]

# Load & Proses Data 
@st.cache_data
def load_data():
    import os
    base = os.path.dirname(__file__)
    df = pd.read_csv(os.path.join(base, 'main_data.csv'))

    # Cleaning — sama dengan notebook cell 14
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df['season'] = df['month'].map({
        12: 'Winter', 1: 'Winter',  2: 'Winter',
         3: 'Spring', 4: 'Spring',  5: 'Spring',
         6: 'Summer', 7: 'Summer',  8: 'Summer',
         9: 'Autumn',10: 'Autumn', 11: 'Autumn'
    })
    num_cols = ['PM2.5','PM10','SO2','NO2','CO','O3','TEMP','PRES','DEWP','RAIN','WSPM']
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())

    def aqi_category(pm):
        if pm <= 12:      return 'Good'
        elif pm <= 35.4:  return 'Moderate'
        elif pm <= 55.4:  return 'Unhealthy for Sensitive Groups'
        elif pm <= 150.4: return 'Unhealthy'
        elif pm <= 250.4: return 'Very Unhealthy'
        else:             return 'Hazardous'
    df['AQI_cat'] = df['PM2.5'].apply(aqi_category)

    df['pollution_level'] = pd.cut(
        df['PM2.5'],
        bins=[0, 12, 35.4, 75, 150, np.inf],
        labels=['Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi', 'Berbahaya']
    )
    return df

df = load_data()

# Sidebar Filter 
st.sidebar.title("🌫️ Filter Data")
st.sidebar.markdown("**Stasiun Changping, Beijing**")
st.sidebar.markdown("---")

years = sorted(df['year'].unique())
year_range = st.sidebar.select_slider(
    "📅 Rentang Tahun", options=years, value=(years[0], years[-1])
)

seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
sel_seasons = st.sidebar.multiselect("🌤️ Musim", options=seasons, default=seasons)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Nama:** Nathaniel Krisnahadi P\n\n"
    "**Dataset:** PRSA Air Quality – Changping\n\n"
    "**Periode:** Mar 2013 – Feb 2017"
)

# Terapkan Filter 
df_f = df[
    df['year'].between(year_range[0], year_range[1]) &
    df['season'].isin(sel_seasons)
].copy()

# Header 
st.title("Dashboard Kualitas Udara – Stasiun Changping, Beijing")
st.markdown(
    "Dashboard ini menyajikan hasil analisis kualitas udara per jam "
    "dari **Stasiun Changping** periode 2013–2017 secara interaktif."
)
st.markdown("---")

# KPI 
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📊 Total Data",    f"{len(df_f):,}")
k2.metric("🔵 Avg PM2.5",     f"{df_f['PM2.5'].mean():.1f} µg/m³")
k3.metric("🔴 Maks PM2.5",    f"{df_f['PM2.5'].max():.0f} µg/m³")
k4.metric("⚠️ % Tidak Sehat", f"{(df_f['PM2.5'] > 55.4).mean() * 100:.1f}%")
k5.metric("✅ % Good",         f"{(df_f['PM2.5'] <= 12).mean() * 100:.1f}%")
st.markdown("---")

# Tab 
tab1, tab2, tab3 = st.tabs([
    "📈 Pertanyaan 1 – Tren & Musim",
    "🌤️ Pertanyaan 2 – Pengaruh Cuaca",
    "📊 Analisis Lanjutan – Clustering"
])


# Pertanyaan 1
with tab1:
    st.subheader("Pertanyaan 1: Bagaimana tren dan pola musiman PM2.5 di Stasiun Changping?")

    # ── Tren bulanan (cell 30) ────────────────────────────────────────────────
    st.markdown("#### Tren PM2.5 Bulanan")
    monthly = df_f.groupby(['year', 'month'])['PM2.5'].mean().reset_index()
    monthly['date'] = pd.to_datetime(monthly[['year', 'month']].assign(day=1))
    monthly = monthly.sort_values('date')

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly['date'], monthly['PM2.5'], color='blue', lw=4, label='Rata-rata Bulanan')
    ax.set_xlabel('Waktu')
    ax.set_ylabel('PM2.5 (µg/m³)')
    ax.set_title('Tren PM2.5 Bulanan – Stasiun Changping')
    ax.legend()
    st.pyplot(fig)
    plt.close()

    st.markdown("---")

    #Bar musim + boxplot 
    col_a, col_b = st.columns(2)
    season_order = ['Spring', 'Summer', 'Autumn', 'Winter']

    with col_a:
        st.markdown("#### Rata-rata PM2.5 per Musim")
        s_avg = df_f.groupby('season')['PM2.5'].mean().reindex(season_order)
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        bars = ax2.bar(
            season_order, s_avg.values,
            color=[SEASON_COLOR[s] for s in season_order],
            edgecolor='white', width=0.5
        )
        ax2.set_ylabel('Avg PM2.5 (µg/m³)')
        ax2.set_title('Rata-rata PM2.5 per Musim')
        for bar, val in zip(bars, s_avg.values):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f'{val:.1f}', ha='center', fontsize=11, fontweight='bold'
            )
        st.pyplot(fig2)
        plt.close()

    with col_b:
        st.markdown("#### Distribusi PM2.5 per Musim")
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        sns.boxplot(
            data=df_f[df_f['season'].isin(season_order)],
            x='season', y='PM2.5', order=season_order,
            palette=SEASON_COLOR, ax=ax3, showfliers=False
        )
        ax3.set_xlabel('')
        ax3.set_ylabel('PM2.5 (µg/m³)')
        ax3.set_title('Distribusi PM2.5 per Musim')
        st.pyplot(fig3)
        plt.close()

    # Statistik musim 
    st.markdown("---")
    st.markdown("#### Statistik PM2.5 per Musim")
    season_stats = df_f.groupby('season').agg(
        Avg_PM25=('PM2.5', 'mean'),
        Std_PM25=('PM2.5', 'std'),
        Median_PM25=('PM2.5', 'median'),
        Pct_Hazardous=('PM2.5', lambda x: (x > 250).mean() * 100)
    ).reindex(season_order).round(2)
    st.dataframe(season_stats, use_container_width=True)

    # Pola harian 
    st.markdown("---")
    st.markdown("#### Pola PM2.5 per Jam dalam Sehari")
    hourly_pm = df_f.groupby('hour')['PM2.5'].mean()
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    ax4.plot(hourly_pm.index, hourly_pm.values, color='purple', lw=4)
    ax4.set_xlabel('Jam ke-')
    ax4.set_ylabel('Rata-rata PM2.5 (µg/m³)')
    ax4.set_title('Pola PM2.5 per Jam dalam Sehari')
    ax4.set_xticks(range(0, 24, 2))
    st.pyplot(fig4)
    plt.close()

    col1, col2 = st.columns(2)
    col1.info(f"🌙 **Jam puncak:** {hourly_pm.idxmax()}:00  ({hourly_pm.max():.1f} µg/m³)")
    col2.info(f"🌅 **Jam terbersih:** {hourly_pm.idxmin()}:00  ({hourly_pm.min():.1f} µg/m³)")

    # Kesimpulan
    st.success(
        "**Kesimpulan Pertanyaan 1:** Polusi PM2.5 di Changping dipengaruhi musim, "
        "dengan puncak polusi di musim dingin dan udara relatif bersih di musim panas."
    )

# Pertanyaan 2
with tab2:
    st.subheader("Pertanyaan 2: Bagaimana pengaruh kecepatan angin, suhu, dan tekanan udara terhadap PM2.5?")

    # Korelasi Spearman 
    st.markdown("#### Uji Korelasi Spearman: Cuaca vs PM2.5")
    weather_vars = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    corr_results = {}
    for var in weather_vars:
        r, p = stats.spearmanr(df_f['PM2.5'], df_f[var])
        corr_results[var] = {
            'Korelasi Spearman': round(r, 3),
            'p-value': round(p, 4),
            'Signifikan?': 'Ya' if p < 0.05 else 'Tidak'
        }
    st.dataframe(pd.DataFrame(corr_results).T, use_container_width=True)

    st.markdown("---")
    col_c, col_d = st.columns(2)

    # Kecepatan angin vs PM2.5
    with col_c:
        st.markdown("#### Pengaruh Kecepatan Angin terhadap PM2.5")
        ws_bins = pd.cut(
            df_f['WSPM'], bins=[0, 1, 2, 3, 5, 14],
            labels=['0–1', '1–2', '2–3', '3–5', '5+']
        )
        ws_pm = df_f.groupby(ws_bins, observed=True)['PM2.5'].mean()
        fig5, ax5 = plt.subplots(figsize=(6, 4))
        ax5.bar(ws_pm.index, ws_pm.values, color='skyblue', edgecolor='white')
        ax5.set_xlabel('Kecepatan Angin (m/s)')
        ax5.set_ylabel('Rata-rata PM2.5 (µg/m³)')
        ax5.set_title('Pengaruh Kecepatan Angin terhadap PM2.5')
        st.pyplot(fig5)
        plt.close()

    # Scatter suhu vs PM2.5 
    with col_d:
        st.markdown("#### Scatter: Suhu vs PM2.5")
        sample = df_f.sample(min(2000, len(df_f)), random_state=42)
        fig6, ax6 = plt.subplots(figsize=(6, 4))
        sns.scatterplot(data=sample, x='TEMP', y='PM2.5', alpha=0.3, ax=ax6)
        ax6.set_xlabel('Suhu (°C)')
        ax6.set_ylabel('PM2.5 (µg/m³)')
        ax6.set_title('Hubungan Suhu dan PM2.5')
        st.pyplot(fig6)
        plt.close()

    # Heatmap korelasi 
    st.markdown("---")
    st.markdown("#### Heatmap Korelasi Antar Variabel")
    corr_cols = ['PM2.5','PM10','SO2','NO2','CO','O3','TEMP','PRES','DEWP','RAIN','WSPM']
    corr_matrix = df_f[corr_cols].corr()
    fig7, ax7 = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', ax=ax7)
    ax7.set_title('Korelasi Antar Variabel')
    st.pyplot(fig7)
    plt.close()

    # Kesimpulan
    st.success(
        "**Kesimpulan Pertanyaan 2:** Faktor cuaca memang mempengaruhi polusi PM2.5. "
        "Angin kencang dan hujan membantu membersihkan udara, sedangkan suhu rendah "
        "dan kondisi musim dingin membuat polusi lebih parah."
    )

# TAB 3 — Analisis Lanjutan Clustering
with tab3:
    st.subheader("Analisis Lanjutan: Clustering Manual (Binning PM2.5)")
    st.markdown("""
    | Level | Rentang PM2.5 | Rekomendasi |
    |-------|--------------|-------------|
    | 🟢 Rendah | ≤ 12 µg/m³ | Udara aman, bebas beraktivitas di luar |
    | 🟡 Sedang | 12–35 µg/m³ | Tetap waspada, tapi masih relatif aman |
    | 🟠 Tinggi | 35–75 µg/m³ | Sebaiknya kurangi aktivitas berat di luar |
    | 🔴 Sangat Tinggi | 75–150 µg/m³ | Gunakan masker, hindari terlalu lama di luar |
    | ⚫ Berbahaya | > 150 µg/m³ | Tetap di dalam ruangan, gunakan air purifier |
    """)

    st.markdown("---")

    # Distribusi tingkat polusi 
    st.markdown("#### Distribusi Tingkat Polusi PM2.5")
    level_order = ['Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi', 'Berbahaya']
    cnt = df_f['pollution_level'].value_counts().reindex(level_order)
    pct = cnt / cnt.sum() * 100

    fig8, ax8 = plt.subplots(figsize=(7, 4))
    bars8 = ax8.bar(
        level_order, cnt.values,
        color=['green', 'yellow', 'orange', 'red', 'purple'],
        edgecolor='white'
    )
    ax8.set_xlabel('Tingkat Polusi')
    ax8.set_ylabel('Jumlah Data')
    ax8.set_title('Distribusi Tingkat Polusi PM2.5')
    for bar, p in zip(bars8, pct.values):
        ax8.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 50,
            f'{p:.1f}%', ha='center', fontsize=10, fontweight='bold'
        )
    st.pyplot(fig8)
    plt.close()

    st.markdown("---")
    col_e, col_f = st.columns(2)

    # Distribusi per musim
    with col_e:
        st.markdown("#### Tingkat Polusi per Musim (%)")
        prop_ms = (
            df_f.groupby(['season', 'pollution_level'], observed=True)
            .size().unstack(fill_value=0)
            .reindex(columns=level_order, fill_value=0)
            .reindex(['Spring', 'Summer', 'Autumn', 'Winter'])
        )
        prop_ms_pct = prop_ms.div(prop_ms.sum(axis=1), axis=0) * 100
        fig9, ax9 = plt.subplots(figsize=(6, 4))
        left = np.zeros(4)
        lv_colors = ['green', 'yellow', 'orange', 'red', 'purple']
        for lv, col in zip(level_order, lv_colors):
            if lv in prop_ms_pct.columns:
                ax9.bar(range(4), prop_ms_pct[lv].values, bottom=left,
                        color=col, label=lv, edgecolor='white')
                left += prop_ms_pct[lv].values
        ax9.set_xticks(range(4))
        ax9.set_xticklabels(['Spring', 'Summer', 'Autumn', 'Winter'])
        ax9.set_ylabel('Persentase (%)')
        ax9.set_title('Tingkat Polusi per Musim')
        ax9.legend(fontsize=8, loc='lower right')
        st.pyplot(fig9)
        plt.close()

    #  Distribusi per jam 
    with col_f:
        st.markdown("#### Tingkat Polusi per Periode Hari (%)")
        hour_groups = pd.cut(
            df_f['hour'], bins=[-1, 5, 11, 17, 23],
            labels=['Dini Hari\n(00–05)', 'Pagi\n(06–11)',
                    'Siang\n(12–17)', 'Malam\n(18–23)']
        )
        prop_hr = (
            df_f.groupby([hour_groups, 'pollution_level'], observed=True)
            .size().unstack(fill_value=0)
            .reindex(columns=level_order, fill_value=0)
        )
        prop_hr_pct = prop_hr.div(prop_hr.sum(axis=1), axis=0) * 100
        fig10, ax10 = plt.subplots(figsize=(6, 4))
        left = np.zeros(len(prop_hr_pct))
        for lv, col in zip(level_order, lv_colors):
            if lv in prop_hr_pct.columns:
                ax10.bar(range(len(prop_hr_pct)), prop_hr_pct[lv].values,
                         bottom=left, color=col, label=lv, edgecolor='white')
                left += prop_hr_pct[lv].values
        ax10.set_xticks(range(len(prop_hr_pct)))
        ax10.set_xticklabels(prop_hr_pct.index, fontsize=9)
        ax10.set_ylabel('Persentase (%)')
        ax10.set_title('Tingkat Polusi per Periode Hari')
        ax10.legend(fontsize=8)
        st.pyplot(fig10)
        plt.close()

    # Hasil temuan 
    st.markdown("---")
    st.markdown("#### Hasil Temuan")
    st.info("""
    - Polusi PM2.5 di Changping paling buruk di musim dingin, paling bersih di musim panas.
    - Selama 2013–2017 tidak ada penurunan nyata, polusi tetap tinggi.
    - Angin kencang membantu menurunkan polusi, sedangkan angin lemah dan suhu rendah membuat polusi menumpuk.
    - Hujan hanya sedikit berpengaruh terhadap penurunan PM2.5.
    """)
    st.warning("""
    **Solusi:**
    - Buat sistem peringatan dini saat cuaca berisiko (angin lemah, suhu rendah, tekanan tinggi).
    - Perketat pembatasan emisi kendaraan dan industri di musim dingin.
    - Dorong penggunaan energi bersih untuk pemanas rumah tangga.
    - Fokus monitoring di jam malam.
    """)

    # Hasil analisa 
    st.markdown("---")
    st.markdown("#### Ringkasan Hasil Analisa")
    c1, c2, c3 = st.columns(3)
    c1.metric("🏙️ Stasiun", "Changping, Beijing")
    c2.metric("📊 Total Data", f"{len(df_f):,} records")
    c3.metric("📅 Periode", "Mar 2013 – Feb 2017")
    c4, c5, c6 = st.columns(3)
    c4.metric("🔵 Avg PM2.5", f"{df_f['PM2.5'].mean():.1f} µg/m³")
    c5.metric("❄️ Musim Terburuk", f"Winter ({df_f[df_f.season=='Winter']['PM2.5'].mean():.1f} µg/m³)")
    c6.metric("☀️ Musim Terbaik", f"Summer ({df_f[df_f.season=='Summer']['PM2.5'].mean():.1f} µg/m³)")

# Footer 
st.markdown("---")
st.caption(" Nathaniel Krisnahadi P | PRSA Air Quality Dataset – Stasiun Changping | Streamlit Dashboard")
