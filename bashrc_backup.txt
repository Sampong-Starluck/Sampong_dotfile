# Node installation (via node version manager or NVM for Unix Like OS)

## Lazy loading nvm (method 1)

export NVM_DIR="$HOME/.nvm"
mapfile -t __NODE_GLOBALS < <(find "$NVM_DIR/versions/node/"*/bin/ -maxdepth 1 -mindepth 1 -type l -print0 | xargs --null -n1 basename $NVM_DIR | sort --unique)
__NODE_GLOBALS+=(node)
__NODE_GLOBALS+=(nvm)
__NODE_GLOBALS+=(npm)
__NODE_GLOBALS+=(npx)
# __NODE_GLOBALS+=(yarn)
# __NODE_GLOBALS+=(pnpm)

# instead of using --no-use flag, load nvm lazily:
_load_nvm() {
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
}

for cmd in "${__NODE_GLOBALS[@]}"; do
    eval "function ${cmd}(){ unset -f ${__NODE_GLOBALS[*]}; _load_nvm; unset -f _load_nvm; ${cmd} \"\$@\"; }"
done
unset cmd __NODE_GLOBALS

## lazy loading nvm (method 2)

# lazy_load_nvm(){
#     unset -f node
#     export NVM_DIR="$HOME/.nvm"
#     [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
#     [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
# }

# node(){
#     lazy_load_nvm
#     node $@
# }

# nvm() {
#   lazy_load_nvm 
#   nvm $@
# }
 
# npm() {
#   lazy_load_nvm
#   npm $@
# }

# npx() {
#   lazy_load_nvm
#   npx $@
# }

## Add node to path and don't load nvm unless invoke nvm command (method 3)

# Add default node to path
# export PATH="$HOME/.nvm/versions/node/*/bin":$PATH

## Load NVM
# export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  --no-use # This loads nvm
# [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  --no-use # This loads nvm bash_completion

## Original method

# export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
# [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Configuration
# Theme
eval "$(oh-my-posh init bash --config "C:\Users\Sampong\AppData\Local\Programs\oh-my-posh\themes\space.omp.json")"
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
