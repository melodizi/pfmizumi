# Script to set OPENAI_API_KEY permanently on Windows
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OpenAI API Key - Permanent Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  This script requires Administrator privilege" -ForegroundColor Yellow
    Write-Host "Attempting to elevate..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Prompt for API Key
$apiKey = Read-Host "Enter your OpenAI API Key (sk-proj-...)"

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "❌ API Key cannot be empty" -ForegroundColor Red
    exit
}

if (-not $apiKey.StartsWith("sk-")) {
    Write-Host "⚠️  Warning: API Key should start with 'sk-'" -ForegroundColor Yellow
}

# Set User-level environment variable (recommended - doesn't need system restart)
try {
    [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $apiKey, "User")
    Write-Host "✅ OPENAI_API_KEY set successfully (User level)" -ForegroundColor Green
    Write-Host "   Key: $($apiKey.Substring(0, 10))...***" -ForegroundColor Cyan
    Write-Host ""
    
    # Verify
    $verify = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
    if ($verify -eq $apiKey) {
        Write-Host "✅ Verification: Configuration is correct" -ForegroundColor Green
    } else {
        Write-Host "❌ Verification failed" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ Error setting environment variable: $_" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Close all Terminal windows" -ForegroundColor Cyan
Write-Host "2. Open new Terminal/PowerShell" -ForegroundColor Cyan
Write-Host "3. Run: python -m streamlit run app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Environment variable is now persistent and will work in:" -ForegroundColor Yellow
Write-Host "   • New PowerShell windows" -ForegroundColor Yellow
Write-Host "   • Command Prompt (cmd)" -ForegroundColor Yellow
Write-Host "   • Python scripts" -ForegroundColor Yellow
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
