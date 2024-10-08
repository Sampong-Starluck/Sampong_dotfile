# List files in the current directory
    export def ll [] {
        ls | where type == 'File'
    }

    # Change to GitHub directory (needs def-env if modifying the environment)
    export def g [] {
        cd ~/Documents/Github
    }

    # Git pull with up to two optional arguments
    export def gpull [branch?: string] {
        if ($branch | is-empty) {
            git pull 
        } else {
            git pull origin $branch
        }
    }

    # Git log with optional 'deco' command
    export def glog [command?] {
        if $command == 'deco' {
            git log --graph --oneline --decorate
        } else {
            git log
        }
    }

    # Git add and commit with a message
    export def gcom [message: string] {
        git add .
        git commit -m $message
    }

    # Git add and amend the last commit without editing
    export def gamend [] {
        git add .
        git commit --amend --no-edit
    }

    # Lazy git commit, pull, and push
    export def lazygcom [
        message: string,
        --branch(-b): string = "development"
    ] {
        git add .
        git commit -m $message

        git pull origin $branch
        git push
    }

    # Lazy git amend, pull, and push
    export def lazygamend [] {
        git add .
        git commit --amend --no-edit
        git pull
        git push
    }

    # Get public IP address
    export def get-pubip [] {
        curl http://ifconfig.me/ip | str trim
    }

    # Load the Oh My Posh theme (if it modifies the environment, use def-env)
    export def load_theme [theme: string] {
        let path = $env.POSH_THEMES_PATH
        oh-my-posh init nu --config "$path/catppuccin_frappe.omp.json"
    }
