#!/usr/bin/sh

# install Node version switcher (NVS)
export NVS_HOME="$HOME/.nvs"
git clone https://github.com/jasongin/nvs "$NVS_HOME"
. "$NVS_HOME/nvs.sh" install

# Install Software Development Kit MAnager (SDKMAN)
curl -s "https://get.sdkman.io" | bash

# Restart bash profile
source "$HOME/.sdkman/bin/sdkman-init.sh"
