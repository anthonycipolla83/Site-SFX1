#!/bin/sh
# Reconstruit la version de test du site après une modification (Python 3.12+ et Pillow requis)
cd "$(dirname "$0")" && python3 build.py ../SFX1_V5_TEST
