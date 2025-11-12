#!/usr/bin/env bash
# Render build script

set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install MeCab system package
apt-get update
apt-get install -y mecab libmecab-dev mecab-ipadic-utf8
