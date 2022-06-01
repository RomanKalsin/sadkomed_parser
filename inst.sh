#!/bin/bash

apt update -y
apt install curl, python3-venv -y
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/root/.local/bin:$PATH"