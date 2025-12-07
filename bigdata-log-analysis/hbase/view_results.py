"""
Streamlit ile HBase Dashboard - TAMAMLANMIŞ
"""
import streamlit as st
import happybase
import pandas as pd
import plotly.express as px

# Ayarlar
HBASE_HOST = "hbase"
HBASE_PORT = 9090

def get_connection():
    try:
        return happybase.Connection(host=HBASE_HOST, port=HBASE_PORT, timeout=20000)
    except Exception as e:
        st.error(f"HBase Bağlantı Hatası: {e}")
        return None

def scan_table(table_name):
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        table = conn.table(table_name)
        data = []
        for key, value in table.scan():
            row = {'row_key': key.decode()}
            for k, v in value.items():
                col = k.decode().split(':')[1]
                try:
                    row[col] = float(v.decode())
                except:
                    row[col] = v.decode()
            data.append(row)
        conn.close()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# --- Sayfa Düzeni ---
st.set_page_config(page_title="Big Data Dashboard", layout="wide", page_icon="📊")

st.title("📊 Büyük Veri Analitik Paneli")
st.sidebar.title("Menü")
page = st.sidebar.radio("Sayfa Seçimi", ["Genel Bakış", "Performans", "Trafik & Kullanıcılar"])

if page == "Genel Bakış":
    st.header("🌍 Sisteme Genel Bakış")
    df_reg = scan_table("region_traffic")
    df_err = scan_table("service_errors")
    
    if not df_reg.empty and not df_err.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam İstek", f"{int(df_reg['request_count'].sum()):,}")
        col2.metric("Toplam Hata", f"{int(df_err['error_count'].sum()):,}")
        err_rate = df_err['error_count'].sum() / df_err['total_requests'].sum() * 100
        col3.metric("Genel Hata Oranı", f"%{err_rate:.2f}")
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.subheader("Bölgesel Dağılım")
        c1.plotly_chart(px.pie(df_reg, values='request_count', names='row_key'), use_container_width=True)
        
        c2.subheader("Servis Hata Oranları")
        c2.plotly_chart(px.bar(df_err, x='row_key', y='error_rate', color='error_rate'), use_container_width=True)

elif page == "Performans":
    st.header("⚡ Endpoint Performans Analizi")
    df_resp = scan_table("response_metrics")
    
    if not df_resp.empty:
        df_resp = df_resp.sort_values('avg_response_time', ascending=False).head(15)
        fig = px.bar(df_resp, x='row_key', y=['avg_response_time', 'p95_response_time'], 
                     barmode='group', title="En Yavaş 15 Endpoint (ms)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_resp)

elif page == "Trafik & Kullanıcılar":
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏰ Saatlik Trafik Trendi")
        df_hour = scan_table("hourly_traffic")
        if not df_hour.empty:
            df_hour = df_hour.sort_values('row_key')
            st.plotly_chart(px.area(df_hour, x='row_key', y='request_count'), use_container_width=True)
            
    with col2:
        st.subheader("👥 Top 20 Kullanıcı")
        df_user = scan_table("top_users")
        if not df_user.empty:
            df_user = df_user.sort_values('request_count', ascending=False).head(20)
            st.plotly_chart(px.bar(df_user, x='id', y='count', color='count'), use_container_width=True)