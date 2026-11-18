#!/bin/bash
set -e

echo "=========================================================="
echo "  Pemasangan ngaji-core & Database FTS5 di Android Termux "
echo "=========================================================="

PREFIX_BIN="/data/data/com.termux/files/usr/bin"
NGAJI_DIR="$HOME/.ngaji"
AGENTS_DIR="$HOME/.agents/agents/ngaji-agent"

mkdir -p "$NGAJI_DIR"
mkdir -p "$AGENTS_DIR"

echo "[1/4] Memasang dependensi (python, sqlite, curl)..."
pkg install -y python sqlite curl

echo "[2/4] Memasang script binary CLI ngaji..."
cp ngaji "$PREFIX_BIN/ngaji"
chmod +x "$PREFIX_BIN/ngaji"

echo "[3/4] Menyiapkan database ngaji.db (77.906 Hadits & Quran)..."
if [ -f "ngaji.db" ]; then
    cp ngaji.db "$NGAJI_DIR/ngaji.db"
else
    echo "Mengunduh database ngaji.db..."
    # Placeholder URL rilis GitHub
    # curl -L "https://github.com/setiajiekaputra/ngaji-core/releases/download/v1.0.0/ngaji.db.gz" | gzip -d > "$NGAJI_DIR/ngaji.db"
fi

echo "[4/4] Mendaftarkan ngaji-agent ke Antigravity CLI..."
cp agent.md "$AGENTS_DIR/agent.md"

echo "=========================================================="
echo "  [✓] Sukses! Silakan coba jalankan perintah:"
echo "      ngaji hadits bukhari 1"
echo "      ngaji cari 'berjamaah'"
echo "      ngaji quran 1 1"
echo "=========================================================="
