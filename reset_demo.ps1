Write-Host "Reseteando tenant de prueba (pruebabenja)..." -ForegroundColor Yellow
docker exec nom035-backend-1 python manage.py reset_demo_tenant --confirm
Write-Host "Listo." -ForegroundColor Green
