import sqlite3
import psycopg2
import os
import sys
import time

SQLITE_PATH = "/root/ngaji-core/ngaji.db"

if os.path.exists(SQLITE_PATH):
    os.remove(SQLITE_PATH)

print(f"[*] Menghubungkan ke PostgreSQL hadith_kb...")
pg = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/hadith_kb")
pcur = pg.cursor()

print(f"[*] Membuat SQLite database di {SQLITE_PATH}...")
sl = sqlite3.connect(SQLITE_PATH)
scur = sl.cursor()

# Konfigurasi SQLite kecepatan tinggi
scur.execute("PRAGMA journal_mode = WAL;")
scur.execute("PRAGMA synchronous = NORMAL;")
scur.execute("PRAGMA cache_size = -64000;") # 64MB cache

# 1. Skema Tabel Master Hadits
scur.execute("""
CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    slug TEXT UNIQUE,
    name_id TEXT,
    name_ar TEXT,
    total_hadiths INTEGER
);
""")

scur.execute("""
CREATE TABLE hadiths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_slug TEXT,
    collection_name TEXT,
    hadith_number INTEGER,
    chapter_title TEXT,
    matn_ar TEXT,
    translation_id TEXT
);
""")

# FTS5 Index Hadits
scur.execute("""
CREATE VIRTUAL TABLE hadiths_fts USING fts5(
    collection_slug UNINDEXED,
    collection_name,
    hadith_number UNINDEXED,
    matn_ar,
    translation_id,
    tokenize = 'porter unicode61'
);
""")

# 2. Skema Al-Qur'an
scur.execute("""
CREATE TABLE quran_surahs (
    surah_number INTEGER PRIMARY KEY,
    name_arabic TEXT,
    name_latin TEXT,
    name_translation TEXT,
    total_ayahs INTEGER,
    revelation_place TEXT
);
""")

scur.execute("""
CREATE TABLE quran_ayahs (
    id INTEGER PRIMARY KEY,
    surah_number INTEGER,
    ayah_number INTEGER,
    text_uthmani TEXT,
    text_latin TEXT,
    translation_id TEXT,
    juz_number INTEGER,
    page_number INTEGER
);
""")

scur.execute("""
CREATE VIRTUAL TABLE quran_fts USING fts5(
    surah_number UNINDEXED,
    ayah_number UNINDEXED,
    text_uthmani,
    translation_id,
    tokenize = 'porter unicode61'
);
""")

# 3. Skema Kaidah Fikih
scur.execute("""
CREATE TABLE fiqh_qawaid (
    id INTEGER PRIMARY KEY,
    code TEXT,
    category TEXT,
    qaidah_ar TEXT,
    translation_id TEXT,
    source_book TEXT,
    explanation_id TEXT
);
""")

print("[*] Migrasi Koleksi Hadits...")
pcur.execute("SELECT id, name_id, name_ar FROM collections ORDER BY canonical_order;")
cols = pcur.fetchall()
col_map = {}
for cid, nid, nar in cols:
    slug = nid.lower().replace(" ", "-").replace("'", "").replace("’", "").replace("`", "")
    pcur.execute("SELECT count(*) FROM hadith_occurrences WHERE collection_id = %s;", (cid,))
    tot = pcur.fetchone()[0]
    scur.execute("INSERT INTO collections VALUES (?, ?, ?, ?, ?)", (str(cid), slug, nid, nar, tot))
    col_map[cid] = (slug, nid)

print("[*] Migrasi 77.906 Hadits...")
pcur.execute("""
SELECT 
    ho.collection_id,
    hn.hadith_number,
    ch.title_ar,
    ho.matn_ar,
    t.translation_text
FROM hadith_occurrences ho
LEFT JOIN hadith_numbering hn ON hn.hadith_occurrence_id = ho.id
LEFT JOIN chapters ch ON ho.chapter_id = ch.id
LEFT JOIN translations t ON t.target_id = ho.id
""")

count = 0
batch = []
fts_batch = []
t0 = time.time()

while True:
    rows = pcur.fetchmany(5000)
    if not rows:
        break
    for cid, num, ch_title, matn, trans in rows:
        slug, cname = col_map.get(cid, ("unknown", "Unknown"))
        num = num if num is not None else 0
        matn = matn or ""
        trans = trans or ""
        ch_title = ch_title or ""
        batch.append((slug, cname, num, ch_title, matn, trans))
        fts_batch.append((slug, cname, num, matn, trans))
        count += 1
    
    scur.executemany("INSERT INTO hadiths (collection_slug, collection_name, hadith_number, chapter_title, matn_ar, translation_id) VALUES (?, ?, ?, ?, ?, ?)", batch)
    scur.executemany("INSERT INTO hadiths_fts (collection_slug, collection_name, hadith_number, matn_ar, translation_id) VALUES (?, ?, ?, ?, ?)", fts_batch)
    sl.commit()
    batch.clear()
    fts_batch.clear()
    print(f"  -> {count} hadits tersimpan ({time.time()-t0:.1f}s)...")

print(f"[✓] Selesai migrasi hadits: {count} hadits.")

# Migrasi Surah & Ayah
print("[*] Migrasi Al-Qur'an 30 Juz...")
pcur.execute("SELECT surah_number, name_arabic, name_latin, name_translation_id, number_of_ayahs, revelation_place FROM quran.surahs ORDER BY surah_number;")
for s in pcur.fetchall():
    scur.execute("INSERT INTO quran_surahs VALUES (?, ?, ?, ?, ?, ?)", s)

pcur.execute("""
SELECT 
    a.id, a.surah_number, a.ayah_number, a.text_uthmani, a.text_latin, t.translation_text, a.juz_number, a.page_number
FROM quran.ayahs a
LEFT JOIN quran.translations t ON t.surah_number = a.surah_number AND t.ayah_number = a.ayah_number AND t.language_code = 'id'
ORDER BY a.surah_number, a.ayah_number;
""")
q_batch = []
q_fts = []
for aid, snum, anum, uth, lat, trans, juz, page in pcur.fetchall():
    uth = uth or ""
    lat = lat or ""
    trans = trans or ""
    q_batch.append((aid, snum, anum, uth, lat, trans, juz, page))
    q_fts.append((snum, anum, uth, trans))

scur.executemany("INSERT INTO quran_ayahs VALUES (?, ?, ?, ?, ?, ?, ?, ?)", q_batch)
scur.executemany("INSERT INTO quran_fts VALUES (?, ?, ?, ?)", q_fts)
sl.commit()
print("[✓] Selesai migrasi 6.236 Ayat Al-Qur'an.")

# Migrasi Kaidah Fikih
print("[*] Migrasi Kaidah Fikih...")
pcur.execute("SELECT id, code, category, qaidah_ar, translation_id, source_book, explanation_id FROM fiqh.qawaid;")
for row in pcur.fetchall():
    scur.execute("INSERT INTO fiqh_qawaid VALUES (?, ?, ?, ?, ?, ?, ?)", row)
sl.commit()

# Indexing tambahan
scur.execute("CREATE INDEX idx_hadiths_col_num ON hadiths(collection_slug, hadith_number);")
scur.execute("CREATE INDEX idx_quran_surah_ayah ON quran_ayahs(surah_number, ayah_number);")
sl.commit()

scur.execute("VACUUM;")
sl.close()
pg.close()

size_mb = os.path.getsize(SQLITE_PATH) / (1024 * 1024)
print(f"[✓] SUKSES BESAR! File SQLite FTS5 jadi: {SQLITE_PATH} ({size_mb:.2f} MB)")
