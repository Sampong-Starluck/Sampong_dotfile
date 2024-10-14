# This script will install the following apps using winget:
# - Visual Studio Code
# - Chrome
# - Firefox
# - Notepad++
# - Jetbrain toolbox
# - Tabby terminal
# - Powershell 7
# - Telegram and Unigram
# - Arc browser
# - Zen browser
# - Nu shell

# Create a list of apps to install
$apps = @(
    "Microsoft.PowerShell"
    "Eugeny.Tabby"
    "Mozilla.Firefox.DeveloperEdition"
    "Microsoft.VisualStudioCode"
    "JetBrains.Toolbox"
    "Notepad++.Notepad++"
    "Nilesoft.Shell"
    "version-fox.vfox"
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


