import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Google Rank Tracker (Optimized)", page_icon="🔍", layout="wide")

st.title("🔍 Google Rank Tracker App (Anti-Timeout Version)")
st.write("Aplikasi pelacak posisi stabil dengan optimasi performa jaringan.")

SERPAPI_KEY = st.sidebar.text_input("Masukkan SerpApi Key Anda", type="password")
st.sidebar.markdown("[Dapatkan API Key Gratis di SerpApi.com](https://serpapi.com)")

with st.form("seo_form"):
    domain_input = st.text_input("Masukkan Domain Anda (Contoh: situsanda.com)", placeholder="vitalartists.com")
    keywords_input = st.text_area("Masukkan Kata Kunci (Satu per baris)", placeholder="lgogacor")
    submit_button = st.form_submit_button("Mulai Cari Posisi")

def cek_posisi_serpapi(domain_target, keyword, api_key):
    if not api_key:
        return "API Key Kosong", "-", "-"
        
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": keyword,
        "google_domain": "google.com",
        "gl": "id",
        "hl": "id",
        "api_key": api_key
    }
    
    # Mencoba hingga 3 kali jika terjadi gangguan jaringan/timeout
    for mencoba in range(3):
        try:
            # Gunakan timeout yang lebih panjang (30 detik)
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                organic_results = data.get("organic_results", [])
                
                for result in organic_results:
                    posisi = result.get("position")
                    link_url = result.get("link", "")
                    
                    if domain_target.lower() in link_url.lower():
                        halaman = (posisi - 1) // 10 + 1
                        return f"Urutan ke-{posisi}", f"Halaman {halaman}", link_url
                        
                return "Tidak ditemukan di halaman 1", "-", "-"
            elif response.status_code == 429:
                return "Kuota API Habis / Terblokir", "-", "-"
                
        except requests.exceptions.Timeout:
            # Jika timeout, tunggu 2 detik sebelum mencoba lagi
            time.sleep(2)
            continue
        except Exception as e:
            return f"Error Sistem: {str(e)}", "-", "-"
            
    return "Koneksi Timeout (Server SerpApi Lambat, Coba Lagi Nanti)", "-", "-"

if submit_button:
    if not SERPAPI_KEY:
        st.error("Silakan masukkan SerpApi Key Anda terlebih dahulu di sidebar sebelah kiri!")
    elif not domain_input or not keywords_input:
        st.error("Mohon isi domain dan kata kunci!")
    else:
        daftar_keyword = [kw.strip() for kw in keywords_input.split("\n") if kw.strip()]
        st.info(f"Sedang melacak {len(daftar_keyword)} kata kunci...")
        
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
            time.sleep(1)
            
        df = pd.DataFrame(hasil_pencarian)
        st.success("Selesai!")
        st.dataframe(df, use_container_width=True)
