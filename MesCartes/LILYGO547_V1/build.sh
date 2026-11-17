#!/usr/bin/env bash
set -euo pipefail

MyPATH="$(cd "$(dirname "$0")" && pwd)"
MyBOARD="$(basename "$MyPATH")"
MyPORT="esp32"

MP_PORT_DIR="$MyPATH/../../../micropython/ports/$MyPORT"

INTERNAL_BOARD_DIR="$MP_PORT_DIR/boards/$MyBOARD"

clear

# Gestion de l'argument "clean"
if [ "${1:-}" = "clean" ]; then
    echo "🧹 Nettoyage des fichiers de compilation pour $MyBOARD..."

    # Supprime le dossier build local
    if [ -d "$MyPATH/firmware" ]; then
        rm -rf "$MyPATH/firmware"
        echo "  ✔️ Dossier local 'firmware' supprimé."
    fi

    # Supprime le dossier de la board copié dans MicroPython
    if [ -d "$INTERNAL_BOARD_DIR" ]; then
        rm -rf "$INTERNAL_BOARD_DIR"
        echo "  ✔️ Dossier interne de la board supprimé de MicroPython."
    fi

    # Supprime le dossier de build de l'ESP-IDF/MicroPython s'il existe
    if [ -d "$MP_PORT_DIR/build-$MyBOARD" ]; then
        rm -rf "$MP_PORT_DIR/build-$MyBOARD"
        echo "  ✔️ Dossier de build interne 'build-$MyBOARD' supprimé."
    elif [ -d "$MP_PORT_DIR/build" ]; then
        rm -rf "$MP_PORT_DIR/build"
        echo "  ✔️ Dossier de build interne 'build' supprimé."
    fi

    echo "✅ Nettoyage terminé avec succès."
    exit 0
fi

echo "📂 Copie du dossier de la carte vers l'emplacement interne de MicroPython..."
mkdir -p "$INTERNAL_BOARD_DIR"

# Copie de tous les fichiers de la carte (en excluant le dossier build et le script lui-même)
find "$MyPATH" -mindepth 1 -maxdepth 1 ! -name 'firmware' ! -name 'build.sh' ! -name 'flash.sh' ! -name '.git' -exec cp -rf {} "$INTERNAL_BOARD_DIR/" \;

echo "🛠 Compilation du firmware $MyBOARD..."
make -C "$MP_PORT_DIR" submodules BOARD="$MyBOARD" USER_C_MODULES="$INTERNAL_BOARD_DIR/modulesc"
make -C "$MP_PORT_DIR" BOARD="$MyBOARD" USER_C_MODULES="$INTERNAL_BOARD_DIR/modulesc" -j4

echo "📦 Récupération du firmware dans $MyPATH/build..."
mkdir -p "$MyPATH/firmware"

# MicroPython génère généralement le build dans build-ESP32_S2 ou build
if [ -d "$MP_PORT_DIR/build-$MyBOARD" ]; then
    cp -r "$MP_PORT_DIR/build-$MyBOARD/"*.bin "$MyPATH/firmware/"
    cp -r "$MP_PORT_DIR/build-$MyBOARD/"*.elf "$MyPATH/firmware/"
fi

echo "✅ Compilation terminée avec succès ! Les fichiers sont dans le dossier build/."
