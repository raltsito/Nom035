$root = $PSScriptRoot
$ErrorActionPreference = "Stop"

function Check-Command($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: '$name' no esta instalado. Instalalo antes de continuar." -ForegroundColor Red
        exit 1
    }
}

Write-Host "=== Setup Intra NOM-035 ===" -ForegroundColor Cyan
Write-Host ""

# Verificar requisitos
Write-Host "Verificando requisitos..." -ForegroundColor Yellow
Check-Command "python"
Check-Command "node"
Check-Command "npm"
Check-Command "docker"
Write-Host "OK: Python, Node, npm y Docker encontrados." -ForegroundColor Green
Write-Host ""

# Crear .env si no existe
if (-not (Test-Path "$root\.env")) {
    Write-Host "Creando .env desde .env.example..." -ForegroundColor Yellow
    Copy-Item "$root\.env.example" "$root\.env"
    Write-Host "IMPORTANTE: Edita el archivo .env y completa DB_PASSWORD y DJANGO_SECRET_KEY antes de continuar." -ForegroundColor Red
    Write-Host "Puedes generar una SECRET_KEY con: python -c `"import secrets; print(secrets.token_urlsafe(50))`"" -ForegroundColor White
    Read-Host "Presiona Enter cuando hayas editado el .env"
} else {
    Write-Host "OK: .env ya existe." -ForegroundColor Green
}
Write-Host ""

# Levantar Docker
Write-Host "Levantando PostgreSQL y Redis (Docker)..." -ForegroundColor Yellow
Set-Location $root
docker compose up -d
Write-Host "OK: Docker corriendo." -ForegroundColor Green
Write-Host ""

# Backend — virtualenv e instalacion
Write-Host "Configurando backend (Python)..." -ForegroundColor Yellow
Set-Location "$root\backend"

if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "  Virtualenv creado." -ForegroundColor Gray
}

.\venv\Scripts\Activate.ps1
pip install --upgrade pip --quiet
pip install -r requirements.txt
Write-Host "OK: Dependencias Python instaladas." -ForegroundColor Green
Write-Host ""

# Migraciones
Write-Host "Ejecutando migraciones..." -ForegroundColor Yellow
python manage.py migrate
Write-Host "OK: Base de datos lista." -ForegroundColor Green
Write-Host ""

# Superusuario
$createSuper = Read-Host "Crear superusuario para el admin? (s/n)"
if ($createSuper -eq "s") {
    python manage.py createsuperuser
}
Write-Host ""

# Frontend — npm install
Write-Host "Instalando dependencias del frontend (npm)..." -ForegroundColor Yellow
Set-Location "$root\frontend"
npm install
Write-Host "OK: Dependencias Node instaladas." -ForegroundColor Green
Write-Host ""

Set-Location $root
Write-Host "=== Setup completo! ===" -ForegroundColor Cyan
Write-Host "Para levantar el sistema en el dia a dia ejecuta:" -ForegroundColor White
Write-Host "  .\dev.ps1" -ForegroundColor Yellow
