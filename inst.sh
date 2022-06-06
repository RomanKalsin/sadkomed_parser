#!/bin/bash

apt update -y
apt install curl python3-venv python3-pip -y
export PATH="/root/.local/bin:$PATH"
curl -sSL https://install.python-poetry.org | python3 -
