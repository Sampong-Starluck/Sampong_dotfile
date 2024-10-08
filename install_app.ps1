# This script will install the following apps using winget:
# - Visual Studio Code
# - Chrome
# - Firefox
# - Notepad++

# Create a list of apps to install
$apps = @(
    "Microsoft.PowerShell"
    "Eugeny.Tabby"
    "Mozilla.Firefox.DeveloperEdition"
    "Microsoft.VisualStudioCode"
    "JetBrains.Toolbox"
    "Notepad++.Notepad++"
    "version-fox.vfox"
    "Git.Git"
    "TheBrowserCompany.Arc"
    "Telegram.TelegramDesktop"
    "Telegram.Unigram"
    "Zen-Team.Zen-Browser"
    "Nushell.Nushell"
)

# Check if winget is installed
if (Get-Command winget -ErrorAction SilentlyContinue) {
    # Install winget
    winget install winget
}

# Loop through the list of apps and install them
foreach ($app in $apps) {
    winget install -e --id $app
}

# Pause to let the user check the results
Write-Host "Press Enter to continue..."
$input = Read-Host


