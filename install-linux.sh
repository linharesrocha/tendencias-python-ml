#!/bin/bash
cd ~
mkdir workspace
cd workspace
git clone https://github.com/linharesrocha/tendencias-python-ml.git
cd tendencias-python-ml/
sudo apt update -y
sudo apt install python3-pip -y
pip install -r requirements.txt
pip install XlsxWriter
pip install slackclient
touch .env
cd ~
rm install-linux.sh

