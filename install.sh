#!/bin/bash
set -e

echo "=========================================================="
echo "  Pemasangan ngaji-core & Database FTS5 di Android Termux "
echo "=========================================================="

PREFIX_BIN="/data/data/com.termux/files/usr/bin"
if [ ! -d "$PREFIX_BIN" ]; then
    PREFIX_BIN="$HOME/.local/bin"
fi
NGAJI_DIR="$HOME/.ngaji"
AGENTS_DIR="$HOME/.agents/agents/ngaji-agent"

mkdir -p "$PREFIX_BIN"
mkdir -p "$NGAJI_DIR"
mkdir -p "$AGENTS_DIR"

echo "[1/4] Memasang dependensi dasar (python, sqlite, curl)..."
if command -v pkg >/dev/null 2>&1; then
    pkg install -y python sqlite curl
elif command -v apt-get >/dev/null 2>&1; then
    apt-get update && apt-get install -y python3 sqlite3 curl
fi

echo "[2/4] Memasang script binary CLI ngaji..."
cp ngaji "$PREFIX_BIN/ngaji"
chmod +x "$PREFIX_BIN/ngaji"

echo "[3/4] Mengunduh database lengkap (77.906 Hadits & Al-Qur'an FTS5)..."
if [ ! -f "$NGAJI_DIR/ngaji.db" ]; then
    TMP_DIR=$(mktemp -d)
    echo "  -> Mengunduh 4 bagian arsip database dari GitHub..."
    curl -sL "https://github.com/setiajiep/ngaji-core/releases/download/v1.0.0/ngaji_part_aa" -o "$TMP_DIR/part_aa"
    curl -sL "https://github.com/setiajiep/ngaji-core/releases/download/v1.0.0/ngaji_part_ab" -o "$TMP_DIR/part_ab"
    curl -sL "https://github.com/setiajiep/ngaji-core/releases/download/v1.0.0/ngaji_part_ac" -o "$TMP_DIR/part_ac"
    curl -sL "https://github.com/setiajiep/ngaji-core/releases/download/v1.0.0/ngaji_part_ad" -o "$TMP_DIR/part_ad"

    echo "  -> Menggabungkan dan mengekstrak database..."
    cat "$TMP_DIR/part_aa" "$TMP_DIR/part_ab" "$TMP_DIR/part_ac" "$TMP_DIR/part_ad" | gzip -d > "$NGAJI_DIR/ngaji.db"
    rm -rf "$TMP_DIR"
    echo "  -> Database siap digunakan di $NGAJI_DIR/ngaji.db"
else
    echo "  -> Database sudah ada di $NGAJI_DIR/ngaji.db."
fi

echo "[4/4] Mendaftarkan ngaji-agent ke Antigravity CLI..."
cp agent.md "$AGENTS_DIR/agent.md"

echo "=========================================================="
echo "  [✓] SUKSES TERPASANG!"
echo "  Uji coba perintah di terminal:"
echo "    ngaji hadits bukhari 1"
echo "    ngaji cari 'berjamaah'"
echo "    ngaji quran 1 1"
echo "=========================================================="
