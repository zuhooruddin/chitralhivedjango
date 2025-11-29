# PowerShell script to start PostgreSQL and verify connection

Write-Host "Checking PostgreSQL status..." -ForegroundColor Cyan

# Try to find PostgreSQL service
$postgresServices = Get-Service | Where-Object {
    $_.DisplayName -like "*PostgreSQL*" -or 
    $_.Name -like "*postgres*" -or
    $_.Name -like "*postgresql*"
}

if ($postgresServices) {
    Write-Host "Found PostgreSQL services:" -ForegroundColor Green
    $postgresServices | Format-Table Name, Status, DisplayName
    
    # Try to start the first PostgreSQL service found
    $service = $postgresServices[0]
    if ($service.Status -ne 'Running') {
        Write-Host "Starting PostgreSQL service: $($service.Name)..." -ForegroundColor Yellow
        try {
            Start-Service -Name $service.Name
            Write-Host "PostgreSQL service started successfully!" -ForegroundColor Green
        } catch {
            Write-Host "Error starting service: $_" -ForegroundColor Red
            Write-Host "Try running as Administrator or start manually from Services (services.msc)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "PostgreSQL service is already running!" -ForegroundColor Green
    }
} else {
    Write-Host "PostgreSQL service not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "1. PostgreSQL might be installed but service has different name"
    Write-Host "2. Check if PostgreSQL is installed: Get-Command psql -ErrorAction SilentlyContinue"
    Write-Host "3. Check running processes: Get-Process -Name postgres -ErrorAction SilentlyContinue"
    Write-Host "4. Open Services GUI: services.msc and look for PostgreSQL"
    Write-Host ""
}

# Check if PostgreSQL process is running
$postgresProcess = Get-Process -Name postgres -ErrorAction SilentlyContinue
if ($postgresProcess) {
    Write-Host "PostgreSQL process is running!" -ForegroundColor Green
} else {
    Write-Host "PostgreSQL process not found." -ForegroundColor Yellow
}

# Check port 5432
Write-Host ""
Write-Host "Checking port 5432..." -ForegroundColor Cyan
$portCheck = netstat -an | Select-String ":5432"
if ($portCheck) {
    Write-Host "Port 5432 is in use:" -ForegroundColor Green
    $portCheck
} else {
    Write-Host "Port 5432 is not in use - PostgreSQL might not be running" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. If PostgreSQL is running, try: python manage.py seed_chitrali_products"
Write-Host "2. If not running, start PostgreSQL service manually"
Write-Host "3. Check database connection settings in settings.py"

