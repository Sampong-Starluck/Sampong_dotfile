# Streamlined Nushell functions

# List files in current directory
export def ll [] { ls | where type == 'File' }

# Change to GitHub directory
export def g [] { cd ~/Documents/Github }

# Git pull with smart origin handling
export def gpull [branch?: string] {
    git pull origin ($branch | default (git branch --show-current))
}

# Git log with optional formatting
export def glog [--decorative(-d)] {
    if $decorative {
        git log --graph --oneline --decorate
    } else {
        git log
    }
}

# Git commands with sensible defaults
export def gcom [message: string] { git add . | git commit -m $message }
export def gamend [] { git add . | git commit --amend --no-edit }
export def gstat [] { git status }

# Smart git checkout with validation
export def gcheck [branch?: string] {
    if ($branch | is-empty) { 
        error make --unspanned { msg: "Error: Branch name required" } 
    } else { 
        git checkout $branch 
    }
}

# Combined lazy git workflows
export def lazygit [
    message?: string,
    --amend(-a),
    --branch(-b): string = "development",
    --no-pull(-n),
    --no-push(-p)
] {
    # Add changes
    git add .
    
    # Commit changes (amend or new)
    if $amend {
        git commit --amend --no-edit
    } else if (not ($message | is-empty)) {
        git commit -m $message
    } else if (not $amend) {
        error make --unspanned { msg: "Error: Commit message required when not amending" }
        return
    }
    
    # Pull changes (if not disabled)
    if (not $no_pull) { git pull origin $branch }
    
    # Push changes (if not disabled)
    if (not $no_push) { git push }
}

# Get public IP address
export def get-pubip [] {
    curl --silent http://ifconfig.me/ip | str trim
}

# Load Oh My Posh theme with validation
export def load_theme [theme: string = "catppuccin_frappe"] {
    let theme_path = $"($env.POSH_THEMES_PATH)/($theme).omp.json"
    
    if (not ($theme_path | path exists)) {
        error make --unspanned { msg: $"Theme not found: ($theme)" }
        return
    }
    
    oh-my-posh init nu --config $theme_path | save --force ~/.oh-my-posh.nu
    # source ~/.oh-my-posh.nu
}

# Startup configuration
export def startup [] {
    # Configure settings in one go
    $env.config = {
        show_banner: false
        history: {
            file_format: sqlite
            max_size: 1_000_000
            sync_on_enter: true
            isolation: true
        }
    }
    
    # Set editor with smart fallback
    $env.config.buffer_editor = if (which vim | length) > 0 { "vim" } else { "code" }
}
