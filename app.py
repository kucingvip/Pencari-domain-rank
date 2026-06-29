import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd
import time

# Pengaturan dasar halaman Streamlit
st.set_page_config(page_title="Pencari Posisi Google (Rank Tracker)", page_icon="🔍", layout="wide")

st.title("🔍 Google Rank Tracker App")
st.write("Cek posisi domain Anda di halaman berapa untuk beberapa kata kunci sekaligus.")

# Komponen Input di Sidebar atau Halaman Utama
with st.form("seo_form"):
    domain_input = st.text_input("Masukkan Domain Anda (Contoh: situsanda.com atau blogspot.com)", placeholder="situsanda.com")
    keywords_input = st.text_area("Masukkan Kata Kunci (Satu kata kunci per baris)", placeholder="prediksi toto akurat\nslot mabar gratis\nlink alternatif judi")
    submit_button = st.form_submit_button("Mulai Cari Posisi")

# Fungsi untuk scraping Google
def cek_posisi_google(domain_target, keyword):
    keyword_encoded = urllib.parse.quote_plus(keyword)
    # Ambil 100 hasil pertama langsung
    url = f"https://www.google.com/search?q={keyword_encoded}&num=100"
    
    # Gunakan User-Agent standar agar menyerupai browser asli
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 429:
            return "Terblokir (Too Many Requests / Captcha Google)", "-", "-"
        elif response.status_code != 200:
            return f"Error HTTP {response.status_code}", "-", "-"
            
        soup = BeautifulSoup(response.text, "html.parser")
        # Mencari kontainer hasil pencarian organik Google
        links = soup.find_all("div", class_="yuRUbf")
        
        posisi = 0
        for link in links:
            a_tag = link.find("a")
            if a_tag:
                href = a_tag.get("href")
                posisi += 1
                
                # Jika domain target ditemukan di dalam URL
                if domain_target.lower() in href.lower():
                    halaman = (posisi - 1) // 10 + 1
                    return f"Urutan ke-{posisi}", f"Halaman {halaman}", href
                    
        return "Tidak ditemukan di 100 besar", "-", "-"
    except Exception as e:
        return f"Error: {str(e)}", "-", "-"

# Logika ketika tombol diklik
if submit_button:
    if not domain_input or not keywords_input:
        st.error("Mohon isi domain dan minimal satu kata kunci terlebih dahulu!")
    else:
        # Pecah input kata kunci berdasarkan baris baru
        daftar_keyword = [kw.strip() for kw in keywords_input.split("\n") if kw.strip()]
        
        st.info(f"Sedang melacak {len(daftar_keyword)} kata kunci untuk domain **{domain_input}**...")
        
        # Tempat menyimpan hasil pencarian
        hasil_pencarian = []
        
        # Progress bar untuk visualisasi proses
        progress_bar = st.progress(0)
        
        for index, kw in enumerate(daftar_keyword):
            # Jalankan fungsi cek posisi
            urutan, halaman, url_lengkap = cek_posisi_google(domain_input, kw)
            
            hasil_pencarian.append({
                "Kata Kunci (Keyword)": kw,
                "Posisi Urutan": urutan,
                "Ada di Halaman": halaman,
                "URL Spesifik": url_lengkap
            })
            
            # Update progress bar
            progress_bar.progress((index + 1) / len(daftar_keyword))
            
            # Jeda waktu kecil agar tidak terlalu agresif menembak Google (menghindari soft-ban IP)
            time.sleep(2)
            
        # Mengubah hasil ke format tabel DataFrame Pandas
        df = pd.DataFrame(hasil_pencarian)
        
        st.success("Selesai! Berikut adalah hasil pelacakan bot Anda:")
        
        # Menampilkan tabel interaktif di Streamlit
        st.dataframe(df, use_container_width=True)