######################################################################
#
#
#           ██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗
#           ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔════╝
#           ██████╔╝███████║███████╗███████║██████╔╝██║     
#           ██╔══██╗██╔══██║╚════██║██╔══██║██╔══██╗██║     
#           ██████╔╝██║  ██║███████║██║  ██║██║  ██║╚██████╗
#           ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝
#
#
######################################################################

set -o vi

HISTTIMEFORMAT="%F %T "

HISTCONTROL=ignoredups

HISTSIZE=2000

HISTFILESIZE=2000

shopt -s histappend

blk='\[\033[01;30m\]'   # Black
red='\[\033[01;31m\]'   # Red
grn='\[\033[01;32m\]'   # Green
ylw='\[\033[01;33m\]'   # Yellow
blu='\[\033[01;34m\]'   # Blue
pur='\[\033[01;35m\]'   # Purple
cyn='\[\033[01;36m\]'   # Cyan
wht='\[\033[01;37m\]'   # White
clr='\[\033[00m\]'      # Reset

# alias
alias cls='clear'
alias ll='ls -l'
alias tree='cmd //c tree //a //f'

alias gs='git status'

alias ga='git add'

alias gaa='git add --all'

alias gc='git commit'

alias gl='git log --oneline'

alias gb='git checkout -b'

alias gd='git diff'

alias ..='cd ..;pwd'

alias ...='cd ../..;pwd'

alias ....='cd ../../..;pwd'

alias c='clear'

alias h='history'

# alias tree='tree --dirsfirst -F'

alias mkdir='mkdir -p -v'

# alias jan='cal -m 01'
# alias feb='cal -m 02'
# alias mar='cal -m 03'
# alias apr='cal -m 04'
# alias may='cal -m 05'
# alias jun='cal -m 06'
# alias jul='cal -m 07'
# alias aug='cal -m 08'
# alias sep='cal -m 09'
# alias oct='cal -m 10'
# alias nov='cal -m 11'
# alias dec='cal -m 12'

# function for git add, commit or amend
function gcomamend () {
	var $message;
	if [ -z "$1" ]; then
		$message = "--amend --no-edit";
	else
		$message = "-m "$1""
	fi

	git add .
	git commit $message
	git pull 
	git push
}


function hg() {
    history | grep "$1";
}

function find_largest_files() {
    du -h -x -s -- * | sort -r -h | head -20;
}

function git_branch() {
    if [ -d .git ] ; then
        printf "%s" "($(git branch 2> /dev/null | awk '/\*/{print $2}'))";
    fi
}

# Set the prompt.
# function bash_prompt(){
#     PS1='${debian_chroot:+($debian_chroot)}'${blu}'$(git_branch)'${pur}' \W'${grn}' \$ '${clr}
# }

# bash_prompt

function git_init() {
    if [ -z "$1" ]; then
        printf "%s\n" "Please provide a directory name.";
    else
        mkdir "$1";
        builtin cd "$1";
        pwd;
        git init;
        touch readme.md .gitignore LICENSE;
        echo "# $(basename $PWD)" >> readme.md
    fi
}

# function weather_report() {

#     local response=$(curl --silent 'https://api.openweathermap.org/data/2.5/weather?id=5128581&units=imperial&appid=e9c27a15a5c3f52f7ff5e139357b5283') 

#     local status=$(echo $response | jq -r '.cod')

#     case $status in
		
#         200) printf "Location: %s %s\n" "$(echo $response | jq '.name') $(echo $response | jq '.sys.country')"  
#              printf "Forecast: %s\n" "$(echo $response | jq '.weather[].description')" 
#              printf "Temperature: %.1f°F\n" "$(echo $response | jq '.main.temp')" 
#              printf "Temp Min: %.1f°F\n" "$(echo $response | jq '.main.temp_min')" 
#              printf "Temp Max: %.1f°F\n" "$(echo $response | jq '.main.temp_max')" 
#             ;;
#         401) echo "401 error"
#             ;;
#         *) echo "error"
#             ;;

#     esac

# }

# clear

printf "\n"
# printf "   %s\n" "IP ADDR: $(curl ifconfig.me)"
# printf "   %s\n" "USER: $(echo $USER)"
printf "   %s\n" "DATE: $(date)"
# printf "   %s\n" "UPTIME: $(uptime -p)"
# printf "   %s\n" "HOSTNAME: $(hostname -f)"
# printf "   %s\n" "CPU: $(awk -F: '/model name/{print $2}' | head -1)"
# printf "   %s\n" "KERNEL: $(uname -rms)"
# printf "   %s\n" "PACKAGES: $(dpkg --get-selections | wc -l)"
# printf "   %s\n" "RESOLUTION: $(xrandr | awk '/\*/{printf $1" "}')"
# printf "   %s\n" "MEMORY: $(free -m -h | awk '/Mem/{print $3"/"$2}')"
printf "\n"


# Oh-My-Posh configuration
export ENV_POSH_THEMES="$HOME\AppData\Local\Programs\oh-my-posh\themes"
eval "$(oh-my-posh init bash --config "$ENV_POSH_THEMES\darkblood.omp.json")"

# Load Angular CLI autocompletion.
source <(ng completion script)
# Load vfox(Version-fox) for SDK managerment for bash script
eval "$(vfox activate bash)"
