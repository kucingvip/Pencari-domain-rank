import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import time

st.set_page_config(page_title="Google Rank Tracker (Official SDK)", page_icon="🔍", layout="wide")

st.title("🔍 Google Rank Tracker App (Official SDK)")
st.write("Menggunakan pustaka resmi SerpApi untuk stabilitas koneksi maksimum.")

SERPAPI_KEY = st.sidebar.text_input("Masukkan SerpApi Key Anda", type="password")
st.sidebar.markdown("[Dapatkan API Key Gratis di SerpApi.com](https://serpapi.com)")

with st.form("seo_form"):
    domain_input = st.text_input("Masukkan Domain Anda", placeholder="vitalartists.com")
    keywords_input = st.text_area("Masukkan Kata Kunci (Satu per baris)", placeholder="lgogacor")
    submit_button = st.form_submit_button("Mulai Cari Posisi")

def cek_posisi_sdk(domain_target, keyword, api_key):
    if not api_key:
        return "API Key Kosong", "-", "-"
        
    params = {
        "engine": "google",
        "q": keyword,
        "google_domain": "google.com",
        "gl": "id",
        "hl": "id",
        "api_key": api_key
    }
    
    try:
        # Menggunakan SDK resmi SerpApi
        search = GoogleSearch(params)
        data = search.get_dict()
        
        if "error" in data:
            return f"Error API: {data['error']}", "-", "-"
            
        organic_results = data.get("organic_results", [])
        
        for result in organic_results:
            posisi = result.get("position")
            link_url = result.get("link", "")
            
            if domain_target.lower() in link_url.lower():
                halaman = (posisi - 1) // 10 + 1
                return f"Urutan ke-{posisi}", f"Halaman {halaman}", link_url
                
        return "Tidak ditemukan di halaman 1", "-", "-"
        
    except Exception as e:
        return f"Gangguan Koneksi: {str(e)}", "-", "-"

if submit_button:
    if not SERPAPI_KEY:
        st.error("Silakan masukkan SerpApi Key Anda di sidebar kiri!")
    elif not domain_input or not keywords_input:
        st.error("Mohon isi domain dan kata kunci!")
    else:
        daftar_keyword = [kw.strip() for kw in keywords_input.split("\n") if kw.strip()]
        st.info(f"Sedang melacak {len(daftar_keyword)} kata kunci...")
        
        hasil_pencarian = []
        progress_bar = st.progress(0)
        
        for index, kw in enumerate(daftar_keyword):
            urutan, halaman, url_lengkap = cek_posisi_sdk(domain_input, kw, SERPAPI_KEY)
            
            hasil_pencarian.append({
                "Kata Kunci (Keyword)": kw,
                "Posisi Urutan": urutan,
                "Ada di Halaman": halaman,
                "URL Spesifik": url_lengkap
            })
            
            progress_bar.progress((index + 1) / len(daftar_keyword))
            time.sleep(1)
            
        df = pd.DataFrame(hasil_pencarian)
        st.success("Selesai!")
        st.dataframe(df, use_container_width=True)
