$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSCommandPath
$FRONTEND = Join-Path $ROOT "frontend"
$BACKEND  = Join-Path $ROOT "backend"
$DIST     = Join-Path $ROOT "dist"
$APP_NAME = "SaberMail"
$APP_DIR  = Join-Path $DIST $APP_NAME

Write-Host "[1/4] Verificando PyInstaller..." -ForegroundColor Cyan
$pyInstalled = pip show pyinstaller 2>$null
if (-not $pyInstalled) {
    Write-Host " Instalando PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    if (-not $?) { throw "Falha ao instalar PyInstaller" }
}

Remove-Item -Recurse -Force (Join-Path $ROOT "build") -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "*.spec" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $APP_DIR -ErrorAction SilentlyContinue

Write-Host "[2/4] Empacotando com PyInstaller (--onedir)..." -ForegroundColor Cyan
pyinstaller --onedir --windowed `
    --distpath $DIST `
    --workpath (Join-Path $ROOT "build\_pyi") `
    --specpath (Join-Path $ROOT "build") `
    --name $APP_NAME `
    --icon (Join-Path $FRONTEND "icon.ico") `
    --add-data "$FRONTEND\icon.png;frontend" `
    --add-data "$FRONTEND\icon.ico;frontend" `
    --paths $FRONTEND `
    --paths $BACKEND `
    --hidden-import "dotenv" `
    --hidden-import "imaplib" `
    --hidden-import "ttkbootstrap" `
    --hidden-import "PIL" `
    (Join-Path $FRONTEND "app.py")

if (-not $?) { throw "PyInstaller falhou" }
Write-Host " OK: $APP_DIR criada" -ForegroundColor Green

Write-Host "[3/5] Copiando backend/..." -ForegroundColor Cyan
$targetBackend = Join-Path $APP_DIR "backend"
Remove-Item -Recurse -Force $targetBackend -ErrorAction SilentlyContinue
Copy-Item -Recurse $BACKEND $targetBackend -Exclude "__pycache__"
Write-Host " OK: backend/ copiado" -ForegroundColor Green

Write-Host "[4/5] Copiando frontend/..." -ForegroundColor Cyan
$targetFrontend = Join-Path $APP_DIR "frontend"
Remove-Item -Recurse -Force $targetFrontend -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $targetFrontend -Force | Out-Null
Copy-Item (Join-Path $FRONTEND "icon.ico") $targetFrontend
Copy-Item (Join-Path $FRONTEND "icon.png") $targetFrontend
Write-Host " OK: frontend/ copiado" -ForegroundColor Green

Write-Host "[5/5] Gerando .env padrao..." -ForegroundColor Cyan
$targetEnv = Join-Path $APP_DIR ".env"
if (-not (Test-Path $targetEnv)) {
    $sample = Join-Path $BACKEND ".env.example"
    if (Test-Path $sample) {
        Copy-Item $sample $targetEnv
    } else {
        Set-Content -Path $targetEnv -Value @"
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_SSL=false
SMTP_USERNAME=
SMTP_PASSWORD=
FROM_NAME=
SUBJECT=
TEMPLATE_PATH=
REPLY_TO=
RATE_PER_MIN=12
"@ -Encoding utf8
    }
    Write-Host " OK: .env criado" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " BUILD CONCLUIDO!" -ForegroundColor Cyan
Write-Host " Pasta: $APP_DIR" -ForegroundColor Cyan
Write-Host " .exe:  $(Join-Path $APP_DIR "$APP_NAME.exe")" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para gerar instalador .exe, instale Inno Setup e execute:" -ForegroundColor Yellow
Write-Host '  ISCC.exe installer.iss' -ForegroundColor Yellow
Write-Host "Download: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
