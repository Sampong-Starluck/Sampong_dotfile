# Node installation (via node version manager or NVM for Unix Like OS)

## Lazy loading nvm

lazy_load_nvm(){
  unset -f node
  export NVM_DIR="~/.nvm"
  [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"  # This loads nvm
  [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
}

node(){
  lazy_load_nvm
  node $@
}

## Add node to path and don't load nvm unless invoke nvm command

# Add default node to path
# export PATH=~/.nvm/versions/node/*/bin:$PATH

## Load NVM
# export NVM_DIR=~/.nvm
# [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh" --no-use
# [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion" --no-use

## Original method

# export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
# [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Configuration
# Theme
eval "$(oh-my-posh init bash --config "C:\Users\Sampong Lim\AppData\Local\Programs\oh-my-posh\themes\kali.omp.json")"
# Tools
export PYTHONIOENCODING=utf8
eval $(thefuck --alias)
# eval $(thefuck --alias FUCK)

# alias
alias cls='clear'
alias ll='ls -l'
alias node_stable_update='nvm install node --reinstall-packages-from=node --latest-npm'
alias node_lts_update='nvm install "lts/*" --reinstall-packages-from="$(nvm current)" --latest-npm'
alias tree='cmd //c tree //a //f'
alias htop='ntop'
alias damnit='fuck'
alias time_profile='time source ./.bash_profile'
alias time_rc='time source ./.bashrc'

# History_configuration
# PROMPT_COMMAND='history -a'

# Load Angular CLI autocompletion.
source <(ng completion script)
