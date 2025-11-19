import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import base64
import warnings

warnings.filterwarnings('ignore')

# =============================================================================
# 1. KONFIGURASI HALAMAN (MIRIP KPPN)
# =============================================================================
st.set_page_config(
    page_title="Sistem Informasi Eksekutif Superstore",
    page_icon="📊",
    layout="wide"
)

# =============================================================================
# 2. STYLE CSS (PERSIS KPPN - HEADER & ANIMASI)
# =============================================================================
def load_css():
    st.markdown("""
    <style>
        /* 1. HEADER ANIMASI (Title Box) */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .title-box {
            background: linear-gradient(135deg, #005FAC, #005FAC); /* Warna Biru KPPN/DJPb */
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

        /* 2. TAB STYLING (Mirip Browser Tab) */
        .stTabs [data-baseweb="tab-list"] { display: flex; width: 100%; gap: 2px; }
        .stTabs [data-baseweb="tab"] {
            flex-grow: 1; text-align: center; height: 50px;
            white-space: pre-wrap; background-color: #F0F2F6;
            border-radius: 4px 4px 0px 0px; padding: 10px;
            font-size: 16px; font-weight: 600;
        }
        .stTabs [aria-selected="true"] { background-color: #FFFFFF; border-top: 3px solid #005FAC; }

        /* 3. HEADER LOGO LAYOUT */
        div.block-container { padding-top: 2rem; }
        [data-testid="stHorizontalBlock"] { align-items: flex-end !important; }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# 3. LOAD DATA LOCAL (SUPERSTORE)
# =============================================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("superstore.csv", encoding="ISO-8859-1")
        df["Order.Date"] = pd.to_datetime(df["Order.Date"])
        df = df.sort_values("Order.Date")
        df["Year"] = df["Order.Date"].dt.year
        # Buat kolom Bulan untuk Tren
        df["Bulan"] = df["Order.Date"].dt.strftime('%B') # Nama Bulan Lengkap
        # Mapping bulan agar urut
        bulan_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        df['Bulan'] = pd.Categorical(df['Bulan'], categories=bulan_order, ordered=True)
        return df
    except FileNotFoundError:
        return None

# =============================================================================
# 4. VISUALISASI FUNCTION (STRUKTUR KPPN)
# =============================================================================
def show_pie_chart(data):
    st.subheader("⏳ Distribusi Sales per Kategori")
    # Palet Warna Mirip KPPN (Biru Emas)
    colors = ['#005FAC', '#FFD700', '#ced4da', '#8ecae6']
    
    data_sorted = data.sort_values('Sales', ascending=False)
    
    fig = px.pie(
        data_sorted, 
        names='Category', 
        values='Sales',
        color='Category',
        hole=0.4,
        color_discrete_sequence=colors
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500, showlegend=True, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

def show_sub_detail_pie(full_data):
    st.subheader("📂 Sub-detail Jenis Produk")
    
    # 1. Pilih Kategori Dulu (Mirip pilih 'Program')
    cats = full_data['Category'].unique()
    selected_cat = st.selectbox("🔎 Pilih Kategori Utama:", options=cats)
    
    # Filter Data
    sub_df = full_data[full_data['Category'] == selected_cat]
    sub_summary = sub_df.groupby('Sub.Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
    
    # Visualisasi
    fig = px.bar(
        sub_summary,
        x="Sales",
        y="Sub.Category",
        orientation='h',
        text_auto='.2s',
        color="Sales",
        color_continuous_scale="Blues",
        title=f"Detail Penjualan: {selected_cat}"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabel Detail
    with st.expander("Lihat Data Tabel"):
        st.dataframe(sub_summary, use_container_width=True)

def show_monthly_trend(full_data, year_label):
    st.subheader(f"📈 Tren Penjualan Bulanan ({year_label})")
    
    # Agregasi per Bulan & Kategori
    trend_df = full_data.groupby(['Bulan', 'Category'], observed=False)['Sales'].sum().reset_index()
    
    fig = px.line(
        trend_df,
        x="Bulan",
        y="Sales",
        color="Category",
        markers=True,
        color_discrete_sequence=['#005FAC', '#FFD700', '#ced4da']
    )
    fig.update_layout(xaxis_title=None, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 5. MAIN APP
# =============================================================================
def main():
    load_css() # Panggil CSS
    
    # --- HEADER LOGO (Pakai URL biar aman gak perlu file lokal) ---
    col_h1, col_h2 = st.columns([1, 4])
    with col_h1:
        # Logo Superstore (Placeholder Icon Keranjang)
        st.image("https://cdn-icons-png.flaticon.com/512/833/833314.png", width=100)
    with col_h2:
        # Bisa tambah logo lain di kanan jika mau
        pass

    # --- JUDUL ANIMASI ---
    st.markdown("""
    <div class="title-box">
        <h1>Executive Dashboard Superstore</h1>
        <h2>Monitoring Penjualan & Profitabilitas Wilayah</h2>
    </div>
    """, unsafe_allow_html=True)

    # --- LOAD DATA ---
    df = load_data()
    if df is None:
        st.error("File 'superstore.csv' tidak ditemukan!")
        st.stop()

    # =========================================================================
    # SIDEBAR SUPERSTORE (LOGIKA BERTINGKAT: REGION -> STATE -> CITY)
    # =========================================================================
    with st.sidebar:
        st.header("🏛️ Navigasi Wilayah")
        
        # 1. FILTER TAHUN (Paling Atas)
        years = sorted(df['Year'].unique(), reverse=True)
        selected_year = st.selectbox("📅 Pilih Tahun:", years)
        
        st.divider()
        
        # 2. FILTER REGION (Level 1 - Radio Button mirip KPPN)
        # Tambahkan opsi 'Grand Total' untuk lihat semua
        region_opts = ["Grand Total (Semua)"] + sorted(df['Region'].unique().tolist())
        
        selected_region = st.radio(
            "🌍 Pilih Region:",
            options=region_opts
        )
        
        # LOGIKA FILTER CASCADING (BERTINGKAT)
        if selected_region == "Grand Total (Semua)":
            # Kalau pilih Grand Total, ambil semua data tahun tsb
            filtered_df = df[df['Year'] == selected_year]
            display_title = "Seluruh Wilayah"
        else:
            # Kalau pilih Region tertentu, filter datanya
            df_region = df[(df['Region'] == selected_region) & (df['Year'] == selected_year)]
            
            # 3. FILTER STATE (Level 2 - Muncul setelah Region dipilih)
            state_opts = ["Semua State"] + sorted(df_region['State'].unique().tolist())
            selected_state = st.selectbox(f"📍 Filter State (di {selected_region}):", state_opts)
            
            if selected_state == "Semua State":
                filtered_df = df_region
                display_title = f"Region {selected_region}"
            else:
                df_state = df_region[df_region['State'] == selected_state]
                
                # 4. FILTER CITY (Level 3 - Muncul setelah State dipilih)
                city_opts = ["Semua City"] + sorted(df_state['City'].unique().tolist())
                selected_city = st.selectbox(f"🏙️ Filter City (di {selected_state}):", city_opts)
                
                if selected_city == "Semua City":
                    filtered_df = df_state
                    display_title = f"State {selected_state}"
                else:
                    filtered_df = df_state[df_state['City'] == selected_city]
                    display_title = f"City {selected_city}, {selected_state}"

        st.info(f"Menampilkan data untuk: **{display_title}**")

    # --- KONTEN UTAMA ---
    
    if filtered_df.empty:
        st.warning("Tidak ada data transaksi pada filter ini.")
        st.stop()

    # KPI CARDS
    tot_sales = filtered_df['Sales'].sum()
    tot_profit = filtered_df['Profit'].sum()
    margin = (tot_profit/tot_sales)*100 if tot_sales > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Penjualan (Sales)", f"${tot_sales:,.0f}")
    col2.metric("Total Profit", f"${tot_profit:,.0f}")
    col3.metric("Profit Margin", f"{margin:.1f}%", delta="Sehat" if margin > 10 else "Perlu Perhatian")
    
    st.markdown("---")

    # DATA PROCESSING UNTUK CHART
    cat_summary = filtered_df.groupby('Category')['Sales'].sum().reset_index()
    
    # TABS VISUALISASI
    tab1, tab2, tab3 = st.tabs(["💡 Kategori Produk", "👍 Detail Sub-Kategori", "🏃‍♀️ Tren Bulanan"])
    
    with tab1:
        show_pie_chart(cat_summary)
        st.markdown("---")
        # Tabel Ringkasan
        st.subheader("🔢 Tabel Ringkasan")
        st.dataframe(cat_summary.sort_values('Sales', ascending=False), use_container_width=True)
        
    with tab2:
        show_sub_detail_pie(filtered_df)
        
    with tab3:
        show_monthly_trend(filtered_df, selected_year)

if __name__ == '__main__':
    main()