import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

# =============================================================================
# 1. KONFIGURASI HALAMAN
# =============================================================================
st.set_page_config(
    page_title="Dashboard Eksekutif | Superstore",
    page_icon="📊",
    layout="wide"
)

# =============================================================================
# 2. CSS STYLE (GAYA KPPN LHOKSEUMAWE)
# =============================================================================
st.markdown("""
<style>
    /* 1. Animasi Fade In */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 2. Judul Utama (Gradient Blue) */
    .title-box {
        background: linear-gradient(135deg, #005FAC, #006ac1); /* Warna Biru KPPN */
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-out;
    }
    .title-box h1 { margin-bottom: 0.5rem; font-size: 2.2rem; }
    .title-box h2 { margin-top: 0; font-size: 1.5rem; opacity: 0.9; }

    /* 3. Container Kartu (Card Style) */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] > div:first-child[data-testid="stContainer"][style*="border"] {
        min-height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border-radius: 15px !important;
        padding: 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 2px solid #e0e0e0 !important;
        background-color: white;
        margin-bottom: 2rem;
    }
    
    /* Efek Hover pada Kartu */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] > div:first-child[data-testid="stContainer"][style*="border"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border-color: #005FAC !important;
    }

    /* 4. Judul Bagian dalam Kartu (Meniru tombol page-link KPPN) */
    .section-header {
        display: block;
        background: linear-gradient(135deg, #005FAC, #006ac1);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* 5. Animasi Chart */
    @keyframes chartFadeIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    .chart-container {
        animation: chartFadeIn 0.8s ease-out;
        flex-grow: 1;
    }
    
    /* 6. Footer Gradient */
    .gradient-divider {
        height: 3px;
        background: linear-gradient(90deg, #005FAC, #D4AF37, #005FAC);
        margin: 2rem 0;
        border-radius: 3px;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 3. LOAD DATA
# =============================================================================
@st.cache_data
def load_data():
    try:
        # Pastikan file superstore.csv ada di folder yang sama
        df = pd.read_csv("superstore.csv", encoding="ISO-8859-1")
        df["Order.Date"] = pd.to_datetime(df["Order.Date"])
        df = df.sort_values("Order.Date")
        df["Year"] = df["Order.Date"].dt.year
        df["Month_Year"] = df["Order.Date"].dt.to_period("M").astype(str)
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("❌ File 'superstore.csv' tidak ditemukan!")
    st.stop()

# =============================================================================
# 4. SIDEBAR (MENU & FILTER)
# =============================================================================
with st.sidebar:
    # Logo Kecil di Sidebar
    st.image("https://cdn-icons-png.flaticon.com/512/3094/3094845.png", width=50)
    st.title("Navigasi Utama")
    
    # A. MENU NAVIGASI (Pengganti Halaman Terpisah)
    menu = st.radio(
        "Pilih Topik:", 
        ["🏠 Ringkasan Eksekutif", "📊 Analisis Produk", "💰 Analisis Profitabilitas"]
    )
    
    st.markdown("---")
    st.header("🎛️ Filter Global")
    
    # B. FILTER TANGGAL
    min_date = df["Order.Date"].min()
    max_date = df["Order.Date"].max()
    
    start_date, end_date = st.date_input(
        "Rentang Tanggal:",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # C. FILTER WILAYAH (State -> City)
    # Filter State
    all_states = ["Semua State"] + sorted(df['State'].unique().tolist())
    sel_state = st.selectbox("Pilih State:", all_states)
    
    # Filter City (Tergantung State)
    if sel_state != "Semua State":
        avail_cities = sorted(df[df['State'] == sel_state]['City'].unique().tolist())
    else:
        avail_cities = sorted(df['City'].unique().tolist())
        
    sel_city = st.multiselect("Pilih City (Opsional):", avail_cities)

    st.info("Filter ini berlaku untuk semua grafik di sebelah kanan.")

# =============================================================================
# 5. FILTERING DATA
# =============================================================================
# Terapkan filter berdasarkan input sidebar
df_filtered = df[(df["Order.Date"] >= pd.to_datetime(start_date)) & 
                 (df["Order.Date"] <= pd.to_datetime(end_date))]

if sel_state != "Semua State":
    df_filtered = df_filtered[df_filtered['State'] == sel_state]

if sel_city:
    df_filtered = df_filtered[df_filtered['City'].isin(sel_city)]

if df_filtered.empty:
    st.warning("Data kosong dengan filter yang dipilih.")
    st.stop()

# =============================================================================
# 6. LOGIKA KONTEN UTAMA
# =============================================================================

# JUDUL ANIMASI (TETAP MUNCUL DI SEMUA HALAMAN)
st.markdown(f"""
<div class="title-box">
    <h1>KINERJA SUPERSTORE</h1>
    <h2>PERIODE: {start_date} s.d {end_date}</h2>
</div>
""", unsafe_allow_html=True)

# --- HALAMAN 1: RINGKASAN EKSEKUTIF (GRID LAYOUT 2 KOLOM) ---
if menu == "🏠 Ringkasan Eksekutif":

    # KPI CARDS
    tot_sales = df_filtered['Sales'].sum()
    tot_profit = df_filtered['Profit'].sum()
    margin = (tot_profit / tot_sales) * 100 if tot_sales > 0 else 0
    tot_trx = df_filtered['Order.ID'].nunique()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", f"${tot_sales:,.0f}", delta="Revenue")
    c2.metric("Total Profit", f"${tot_profit:,.0f}", delta=f"{margin:.1f}% Margin")
    c3.metric("Total Transaksi", f"{tot_trx:,}", delta="Orders")
    c4.metric("Avg Diskon", f"{df_filtered['Discount'].mean()*100:.1f}%", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # GRID LAYOUT (KIRI - KANAN)
    col_kiri, col_kanan = st.columns(2, gap="large")

    # === KOLOM KIRI ===
    with col_kiri.container(height=500):
        # 1. TREN PENJUALAN (Ganti Kinerja Pendapatan)
        with st.container(border=True):
            st.markdown('<div class="section-header">KINERJA PENJUALAN (SALES TREND)</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            trend_data = df_filtered.groupby("Month_Year")['Sales'].sum().reset_index()
            fig_trend = px.line(trend_data, x="Month_Year", y="Sales", markers=True, 
                                line_shape="spline", color_discrete_sequence=['#005FAC'])
            fig_trend.update_layout(xaxis_title=None, yaxis_title="Sales", height=350, margin=dict(t=20, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_kiri.container(height=500):
        # 2. KOMPOSISI KATEGORI (Ganti Capaian TKD)
        with st.container(border=True):
            st.markdown('<div class="section-header">KOMPOSISI KATEGORI PRODUK</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            cat_data = df_filtered.groupby("Category")['Sales'].sum().reset_index()
            fig_pie = px.pie(cat_data, values='Sales', names='Category', hole=0.5,
                             color_discrete_sequence=['#005FAC', '#FFD700', '#ced4da'])
            fig_pie.update_layout(height=350, margin=dict(t=20, b=20), showlegend=True, legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_kiri.container(height=500):
        # 3. PERFORMA WILAYAH (Ganti UMi & KUR)
        with st.container(border=True):
            st.markdown('<div class="section-header">TOP 5 REGION / STATE</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            state_data = df_filtered.groupby("State")['Sales'].sum().nlargest(5).reset_index()
            fig_bar_h = px.bar(state_data, x="Sales", y="State", orientation='h', text_auto='.2s',
                               color="Sales", color_continuous_scale="Blues")
            fig_bar_h.update_layout(height=350, margin=dict(t=20, b=20), yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar_h, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # === KOLOM KANAN ===
    with col_kanan.container(height=500):
        # 4. PROFITABILITAS (Ganti Realisasi Belanja K/L)
        with st.container(border=True):
            st.markdown('<div class="section-header">ANALISIS PROFITABILITAS (SALES VS PROFIT)</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            prof_trend = df_filtered.groupby("Month_Year")[['Sales', 'Profit']].sum().reset_index()
            fig_combo = go.Figure()
            fig_combo.add_trace(go.Bar(x=prof_trend['Month_Year'], y=prof_trend['Sales'], name='Sales', marker_color='#d1e7dd'))
            fig_combo.add_trace(go.Scatter(x=prof_trend['Month_Year'], y=prof_trend['Profit'], name='Profit', line=dict(color='#005FAC', width=3)))
            fig_combo.update_layout(height=350, margin=dict(t=20, b=20), legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_combo, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_kanan.container(height=500):
        # 5. TOP PRODUK (Ganti Realisasi Belanja Negara)
        with st.container(border=True):
            st.markdown('<div class="section-header">TOP 5 PRODUK TERLARIS</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            prod_data = df_filtered.groupby("Product.Name")['Sales'].sum().nlargest(5).reset_index()
            prod_data['ShortName'] = prod_data['Product.Name'].str.slice(0, 35) + "..."
            fig_prod = px.bar(prod_data, x="ShortName", y="Sales", text_auto='.2s',
                              color_discrete_sequence=['#005FAC'])
            fig_prod.update_layout(height=350, margin=dict(t=20, b=50))
            st.plotly_chart(fig_prod, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_kanan.container(height=500):
        # 6. SEGMEN PELANGGAN (Ganti Monitoring KOPDES)
        with st.container(border=True):
            st.markdown('<div class="section-header">SEGMEN PELANGGAN</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            seg_data = df_filtered.groupby("Segment")['Sales'].sum().reset_index()
            fig_donut = px.pie(seg_data, values='Sales', names='Segment', hole=0.6,
                               color_discrete_sequence=['#005FAC', '#48cae4', '#caf0f8'])
            fig_donut.add_annotation(text="Sales", showarrow=False, font_size=20, y=0.5)
            fig_donut.update_layout(height=350, margin=dict(t=20, b=20), showlegend=True, legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # FULL WIDTH CHART (SCATTER)
    with st.container(height=350):
        with st.container(border=True):
            st.markdown('<div class="section-header">HUBUNGAN DISKON VS PROFIT</div>', unsafe_allow_html=True)
            fig_scat = px.scatter(df_filtered, x="Discount", y="Profit", color="Category", size="Sales",
                                  hover_data=["Sub.Category"], title="Semakin besar diskon, apakah profit turun?")
            fig_scat.update_layout(height=250, margin=dict(t=30, b=20))
            st.plotly_chart(fig_scat, use_container_width=True)

# --- HALAMAN 2: ANALISIS PRODUK (DETAIL) ---
elif menu == "📊 Analisis Produk":
    st.info("Halaman ini fokus pada detail inventori dan performa per Sub-Kategori.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
         with st.container(border=True):
            st.markdown('<div class="section-header">PILIH SUB-KATEGORI</div>', unsafe_allow_html=True)
            sel_sub = st.selectbox("Sub-Kategori:", df_filtered['Sub.Category'].unique())
            sub_data = df_filtered[df_filtered['Sub.Category'] == sel_sub]
            
            st.write(f"Total Item: {len(sub_data)}")
            st.write(f"Total Sales: ${sub_data['Sales'].sum():,.2f}")
    
    with col2:
        with st.container(border=True):
            st.markdown(f'<div class="section-header">TOP PRODUK DI {sel_sub.upper()}</div>', unsafe_allow_html=True)
            top_sub = sub_data.groupby("Product.Name")['Sales'].sum().nlargest(10).reset_index()
            top_sub['Name'] = top_sub['Product.Name'].str.slice(0,50) + "..."
            fig_sub = px.bar(top_sub, x="Sales", y="Name", orientation='h', color="Sales")
            fig_sub.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_sub, use_container_width=True)
            
    with st.expander("Lihat Data Mentah Produk"):
        st.dataframe(sub_data)

# --- HALAMAN 3: ANALISIS PROFITABILITAS (DETAIL) ---
elif menu == "💰 Analisis Profitabilitas":
    st.info("Analisis mendalam mengenai produk yang untung vs rugi.")
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown('<div class="section-header">PRODUK PALING MENGUNTUNGKAN</div>', unsafe_allow_html=True)
            win_prod = df_filtered.groupby("Product.Name")['Profit'].sum().nlargest(10).reset_index()
            win_prod['Name'] = win_prod['Product.Name'].str.slice(0,40)
            fig_win = px.bar(win_prod, x="Profit", y="Name", orientation='h', color_discrete_sequence=['#005FAC'])
            fig_win.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_win, use_container_width=True)
            
    with c2:
        with st.container(border=True):
            st.markdown('<div class="section-header">PRODUK PALING MERUGIKAN</div>', unsafe_allow_html=True)
            lose_prod = df_filtered.groupby("Product.Name")['Profit'].sum().nsmallest(10).reset_index()
            lose_prod['Name'] = lose_prod['Product.Name'].str.slice(0,40)
            fig_lose = px.bar(lose_prod, x="Profit", y="Name", orientation='h', color_discrete_sequence=['#d32f2f'])
            fig_lose.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_lose, use_container_width=True)

# --- FOOTER ---
st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 1rem;">
    © 2025 Superstore Analytics | Executive Dashboard System
</div>
""", unsafe_allow_html=True)