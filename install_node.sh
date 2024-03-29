#!/bin/bash
# Install node and npm in the system without sudo rights

DOWNLOAD_PATH="$HOME/.tmp/node-latest-install"
NODE_URL="https://nodejs.org/dist/node-latest.tar.gz"
NODE_FILE="node-latest.tar.gz"

# prepend to path
mkdir -p ~/.local/bin
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
. ~/.bashrc
mkdir -p "$DOWNLOAD_PATH"
cd "$DOWNLOAD_PATH"

wget -Nc "$NODE_URL"
# unzip
echo "Decompressing NodeJS..."
tar -xf "$NODE_FILE" --strip-components=1
# Install node
echo "Compiling NodeJS..."
./configure --prefix="~/.local"
make -j4
make  install

# Download the NPM install script and run it
echo "Installing NPM..."
wget -c "https://www.npmjs.org/install.sh"
./install.sh
rm install.sh
npm install -g npm@latest