# ngaji-core: Mesin Pencari & Pengkajian Al-Qur'an & Hadits Offline (FTS5)

Mesin pengkajian mandiri berbasis **SQLite FTS5** yang memuat seluruh khazanah ilmu Al-Qur'an dan Al-Hadits secara offline, super-cepat (pencarian sub-5ms), dan ringan untuk digunakan di **Android Termux** maupun Linux PC.

---

## 📦 Isi Khazanah (100% Offline)
1. **Al-Qur'an 30 Juz**: 6.236 Ayat lengkap dengan Rasm Utsmani dan Terjemahan Bahasa Indonesia.
2. **18 Kitab Hadits Induk (77.906 Hadits Lengkap)**:
   - Shahih Al-Bukhari (7.593)
   - Shahih Muslim (7.563)
   - Sunan Abu Dawud (5.274)
   - Jami' At-Tirmidzi (3.998)
   - Sunan An-Nasa'i (5.765)
   - Sunan Ibnu Majah (4.343)
   - Musnad Ahmad (26.363)
   - Muwatta Malik (1.860)
   - Sunan Ad-Darimi (3.406)
   - Riyadhus Shalihin (1.896)
   - Bulughul Maram (1.767)
   - Al-Adab Al-Mufrad (1.326)
   - Misykatul Mashabih (4.428)
   - Musnad Asy-Syafi'i (1.800)
   - Syamail Muhammadiyah (402)
   - Arba'in An-Nawawiyah (42)
   - Hadits Qudsi 40 (40)
   - Arba'in Shah Waliullah (40)
3. **Kaidah Fikih (Qawa'id Fiqhiyyah)**: Panca Kaidah Asasiyah mu'tabar.

---

## 🚀 Cara Pasang di Termux (Android)
Cukup jalankan satu baris perintah di Termux:

```bash
pkg install -y git python sqlite curl && \
git clone https://github.com/setiajiekaputra/ngaji-core.git ~/ngaji-core && \
cd ~/ngaji-core && bash install.sh
```

---

## ⚡ Contoh Perintah CLI (`ngaji`)

### 1. Cari Hadits (FTS5 Sub-Detik)
```bash
ngaji cari "niat"
ngaji cari "berjamaah"
ngaji cari "jual beli"
```

### 2. Baca Hadits Spesifik (Kitab & Nomor)
```bash
ngaji hadits bukhari 1
ngaji hadits muslim 25
ngaji hadits abu-dawud 1500
```

### 3. Baca Ayat Al-Qur'an
```bash
ngaji quran 1 1        # QS. Al-Fatihah ayat 1
ngaji quran 2 183      # Ayat Puasa Ramadhan
```

### 4. Cari Ayat Al-Qur'an Berdasarkan Kata Kunci
```bash
ngaji cari-quran "sabar"
ngaji cari-quran "rezeki"
```

### 5. Akses Kaidah Fikih
```bash
ngaji qawaid "niat"
```

---

## 🤖 Integrasi AI Super-Agent Antigravity (`agy`)
Repositori ini menyertakan `agent.md` (`ngaji-agent`). Agen AI Anda dapat langsung mencari dan membaca dalil secara offline tanpa perlu kuota API tambahan.
