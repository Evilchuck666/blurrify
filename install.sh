#!/bin/bash

# 1. Create ~/.local/bin if it doesn't exist
mkdir -p ~/.local/bin

# 2. Add ~/.local/bin to PATH in ~/.bashrc if not already present
if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  echo "Updated ~/.bashrc to include ~/.local/bin in PATH"
  source ~/.bashrc
fi

# 3. Download blurrify.py to ~/.local/bin
curl -L https://raw.githubusercontent.com/Evilchuck666/blurrify/main/blurrify.py -o ~/.local/bin/blurrify

# 4. Make it executable
chmod +x ~/.local/bin/blurrify

# 5. Create ~/.config/blurrify/assets
mkdir -p ~/.config/blurrify/assets

# 6. Download haar.py and model.xml to the assets folder
curl -L https://raw.githubusercontent.com/Evilchuck666/blurrify/main/assets/haar.py -o ~/.config/blurrify/assets/haar.py
curl -L https://raw.githubusercontent.com/Evilchuck666/blurrify/main/assets/model.xml -o ~/.config/blurrify/assets/model.xml

echo "Blurrify installed successfully."
