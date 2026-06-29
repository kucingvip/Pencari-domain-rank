import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Google Rank Tracker (Stable)", page_icon="🔍", layout="wide")

st.title("🔍 Google Rank Tracker App (SerpApi Version)")
st.write("Aplikasi pelacak posisi stabil menggunakan API resmi untuk menghindari blokir Google.")

# Input API Key untuk keamanan, atau Anda bisa hardcode langsung di variabel di bawah
SERPAPI_KEY = st.sidebar.text_input("Masukkan SerpApi Key Anda", type="password")
st.sidebar.markdown("[Dapatkan API Key Gratis di SerpApi.com](https://serpapi.com)")

with st.form("seo_form"):
    domain_input = st.text_input("Masukkan Domain Anda (Contoh: situsanda.com)", placeholder="lgogacor-1.it.com")
    keywords_input = st.text_area("Masukkan Kata Kunci (Satu per baris)", placeholder="lgogacor")
    submit_button = st.form_submit_button("Mulai Cari Posisi")

def cek_posisi_serpapi(domain_target, keyword, api_key):
    if not api_key:
        return "API Key Kosong", "-", "-"
        
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": keyword,
        "google_domain": "google.com", # Bisa diganti google.co.id jika target lokal
        "gl": "id",                     # Target Geoklokasi: Indonesia
        "hl": "id",                     # Bahasa: Indonesia
        "num": "100",                   # Ambil langsung 100 hasil pencarian
        "api_key": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=20)
        if response.status_code != 200:
            return f"Error API ({response.status_code})", "-", "-"
            
        data = response.json()
        
        # Ambil hasil pencarian organik
        organic_results = data.get("organic_results", [])
        
        for result in organic_results:
            posisi = result.get("position")
            link_url = result.get("link", "")
            
            # Cek apakah domain target ada di dalam link hasil pencarian
            if domain_target.lower() in link_url.lower():
                halaman = (posisi - 1) // 10 + 1
                return f"Urutan ke-{posisi}", f"Halaman {halaman}", link_url
                
        return "Tidak ditemukan di 100 besar", "-", "-"
        
    except Exception as e:
        return f"Error Sistem: {str(e)}", "-", "-"

if submit_button:
    if not SERPAPI_KEY:
        st.error("Silakan masukkan SerpApi Key Anda terlebih dahulu di sidebar sebelah kiri!")
    elif not domain_input or not keywords_input:
        st.error("Mohon isi domain dan kata kunci!")
    else:
        daftar_keyword = [kw.strip() for kw in keywords_input.split("\n") if kw.strip()]
        st.info(f"Sedang melacak {len(daftar_keyword)} kata kunci untuk domain **{domain_input}**...")
        
        hasil_pencarian = []
        progress_bar = st.progress(0)
        
        for index, kw in enumerate(daftar_keyword):
            urutan, halaman, url_lengkap = cek_posisi_serpapi(domain_input, kw, SERPAPI_KEY)
            
            hasil_pencarian.append({
                "Kata Kunci (Keyword)": kw,
                "Posisi Urutan": urutan,
                "Ada di Halaman": halaman,
                "URL Spesifik": url_lengkap
            })
            
            progress_bar.progress((index + 1) / len(daftar_keyword))
            time.sleep(0.5) # Menggunakan API tidak perlu jeda waktu lama (bebas blokir)
            
        df = pd.DataFrame(hasil_pencarian)
        st.success("Selesai! Berikut adalah hasil pelacakan bot Anda:")
        st.dataframe(df, use_container_width=True)
