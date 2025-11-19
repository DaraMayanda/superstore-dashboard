import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# =============================================================================
# 1. SETUP HALAMAN & GAYA TAMPILAN (PREMIUM CSS)
# =============================================================================
st.set_page_config(page_title="Executive Dashboard", page_icon="🏢", layout="wide")

# CSS Custom untuk Kartu KPI yang elegan & Shadow
st.markdown("""
<style>
    .stApp {background-color: #f8f9fa;}
    
    /* Styling Container KPI */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    /* Judul Halaman */
    .title-text {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1f2937;
    }
    
    div.block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. LOAD DATA
# =============================================================================
@st.cache_data
def load_data():
    try:
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
# 3. SIDEBAR NAVIGASI & FILTER
# =============================================================================
with st.sidebar:
    st.title("📱 Menu Utama")
    
    # --- BAGIAN A: MENU NAVIGASI (PILIHAN HALAMAN) ---
    # Ini yang membuat dashboard terasa seperti aplikasi profesional
    menu = st.radio(
        "Pilih Tampilan:", 
        ["🏠 Executive Summary", "💰 Analisis Penjualan", "📉 Analisis Profitabilitas"]
    )
    
    st.markdown("---")
    
    # --- BAGIAN B: FILTER GLOBAL ---
    st.header("🎛️ Filter Data")
    
    # 1. Tahun
    years = sorted(df['Year'].unique().tolist(), reverse=True)
    sel_year = st.multiselect("📅 Tahun", years, default=years[:2]) 
    if not sel_year: sel_year = years
    df_filtered = df[df['Year'].isin(sel_year)]

    # 2. Region
    regions = sorted(df_filtered['Region'].unique())
    sel_region = st.multiselect("🌍 Region", regions, default=regions)
    if not sel_region: sel_region = regions
    df_filtered = df_filtered[df_filtered['Region'].isin(sel_region)]

    # 3. State
    states = sorted(df_filtered['State'].unique())
    sel_state = st.multiselect("📍 State", states)
    if sel_state:
        df_filtered = df_filtered[df_filtered['State'].isin(sel_state)]
    
    st.markdown("---")
    st.caption("Dashboard Corporate v2.0")

# =============================================================================
# 4. LOGIKA HALAMAN (KONTEN BERUBAH SESUAI MENU)
# =============================================================================

# --- HALAMAN 1: EXECUTIVE SUMMARY (GAMBARAN BESAR) ---
if menu == "🏠 Executive Summary":
    st.title("🏠 Executive Overview")
    st.markdown("Ringkasan performa utama: **Pendapatan**, **Profit**, dan **Tren Pertumbuhan**.")
    
    # 1. KPI CARDS
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = df_filtered['Sales'].sum()
    total_profit = df_filtered['Profit'].sum()
    margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
    total_trx = df_filtered['Order.ID'].nunique()
    
    col1.metric("Total Pendapatan (Sales)", f"${total_sales:,.0f}", delta="Gross Revenue")
    col2.metric("Total Keuntungan (Profit)", f"${total_profit:,.0f}", delta=f"{margin:.1f}% Margin")
    col3.metric("Total Transaksi", f"{total_trx:,}", delta="Orders")
    col4.metric("Rata-rata Diskon", f"{df_filtered['Discount'].mean()*100:.1f}%", delta="Avg Discount", delta_color="inverse")
    
    st.markdown("---")
    
    # 2. CHART UTAMA: COMBO CHART (SALES vs PROFIT MARGIN)
    st.subheader("📈 Tren Pendapatan & Kesehatan Profit")
    
    trend_data = df_filtered.groupby("Month_Year").agg({"Sales":"sum", "Profit":"sum"}).reset_index()
    trend_data["Margin"] = (trend_data["Profit"] / trend_data["Sales"]) * 100
    
    fig_combo = go.Figure()
    # Bar Sales
    fig_combo.add_trace(go.Bar(x=trend_data["Month_Year"], y=trend_data["Sales"], name="Sales ($)", marker_color="#3b82f6"))
    # Line Margin
    fig_combo.add_trace(go.Scatter(x=trend_data["Month_Year"], y=trend_data["Margin"], name="Margin (%)", yaxis="y2", line=dict(color="#10b981", width=3)))
    
    fig_combo.update_layout(
        template="plotly_white", height=450, hovermode="x unified",
        yaxis=dict(title="Sales Amount"),
        yaxis2=dict(title="Profit Margin (%)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_combo, use_container_width=True)
    
    # 3. PIE CHART SEGMEN
    col_seg1, col_seg2 = st.columns(2)
    with col_seg1:
        st.subheader("Komposisi Segmen Pelanggan")
        fig_pie = px.pie(df_filtered, values="Sales", names="Segment", hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_seg2:
        st.subheader("Sales per Wilayah (Region)")
        fig_reg = px.bar(df_filtered.groupby("Region")["Sales"].sum().reset_index(), x="Sales", y="Region", orientation='h', text_auto='.2s')
        st.plotly_chart(fig_reg, use_container_width=True)


# --- HALAMAN 2: ANALISIS PENJUALAN (DETAIL SALES) ---
elif menu == "💰 Analisis Penjualan":
    st.title("💰 Detail Analisis Penjualan")
    st.markdown("Fokus pada performa produk dan kategori terlaris.")
    
    # 1. Breakdown Kategori
    col_cat1, col_cat2 = st.columns([2, 1])
    with col_cat1:
        st.subheader("Penjualan per Kategori & Sub-Kategori")
        fig_sun = px.sunburst(df_filtered, path=['Category', 'Sub.Category'], values='Sales', color='Sales', color_continuous_scale='Blues')
        st.plotly_chart(fig_sun, use_container_width=True)
    
    with col_cat2:
        st.subheader("Top Kategori")
        cat_sales = df_filtered.groupby("Category")["Sales"].sum().reset_index().sort_values("Sales")
        fig_cat = px.bar(cat_sales, x="Sales", y="Category", orientation='h', text_auto='.2s', color="Sales", color_continuous_scale="Blues")
        st.plotly_chart(fig_cat, use_container_width=True)
        
    st.markdown("---")
    
    # 2. Top Products
    st.subheader("🏆 Top 10 Produk Terlaris (Penyumbang Omzet Terbesar)")
    top_prod = df_filtered.groupby("Product.Name")["Sales"].sum().nlargest(10).reset_index()
    top_prod["Product Name"] = top_prod["Product.Name"].str.slice(0, 50) + "..."
    
    fig_top = px.bar(top_prod, x="Sales", y="Product Name", orientation='h', text_auto='.2s', color="Sales", color_continuous_scale="Blues")
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)


# --- HALAMAN 3: ANALISIS PROFITABILITAS (CUAN vs RUGI) ---
elif menu == "📉 Analisis Profitabilitas":
    st.title("📉 Detail Profitabilitas")
    st.markdown("Mengidentifikasi area yang **Menguntungkan** vs **Merugikan**.")
    
    # 1. Scatter Plot: Diskon vs Profit
    st.subheader("🔍 Hubungan Diskon & Profit (Apakah diskon membunuh profit?)")
    fig_scat = px.scatter(df_filtered, x="Discount", y="Profit", color="Category", size="Sales", 
                          hover_data=["Sub.Category"], template="plotly_white",
                          title="Titik di bawah garis 0 = Transaksi Rugi")
    st.plotly_chart(fig_scat, use_container_width=True)
    
    st.markdown("---")
    
    # 2. Top & Bottom Analysis
    col_win, col_loss = st.columns(2)
    
    with col_win:
        st.subheader("✅ Top 5 Produk Paling Untung")
        win_prod = df_filtered.groupby("Product.Name")["Profit"].sum().nlargest(5).reset_index()
        win_prod["Name"] = win_prod["Product.Name"].str.slice(0, 40) + "..."
        fig_win = px.bar(win_prod, x="Profit", y="Name", orientation='h', text_auto='.2s', color_discrete_sequence=['#10b981']) # Hijau
        fig_win.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_win, use_container_width=True)
        
    with col_loss:
        st.subheader("⚠️ Top 5 Produk Paling Rugi")
        loss_prod = df_filtered.groupby("Product.Name")["Profit"].sum().nsmallest(5).reset_index().sort_values("Profit", ascending=False) # Sort biar chartnya rapi
        loss_prod["Name"] = loss_prod["Product.Name"].str.slice(0, 40) + "..."
        fig_loss = px.bar(loss_prod, x="Profit", y="Name", orientation='h', text_auto='.2s', color_discrete_sequence=['#ef4444']) # Merah
        fig_loss.update_layout(yaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig_loss, use_container_width=True)