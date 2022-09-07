# Node installation (via node version manager or NVM for Unix Like OS)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

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

# History_configuration
# PROMPT_COMMAND='history -a'

# Load Angular CLI autocompletion.
source <(ng completion script)
