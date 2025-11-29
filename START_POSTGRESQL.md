# How to Start PostgreSQL and Run Seed Command

## The Error
You're getting a PostgreSQL connection error because the PostgreSQL server is not running.

## Solution Options

### Option 1: Start PostgreSQL Service (Windows)

1. **Find PostgreSQL Service:**
   ```powershell
   Get-Service | Where-Object {$_.DisplayName -like "*PostgreSQL*"}
   ```

2. **Start PostgreSQL Service:**
   ```powershell
   # If service name is found (e.g., "postgresql-x64-14")
   Start-Service -Name "postgresql-x64-14"
   # OR
   net start postgresql-x64-14
   ```

3. **Alternative - Start via Services GUI:**
   - Press `Win + R`, type `services.msc`
   - Find PostgreSQL service
   - Right-click → Start

### Option 2: Check if PostgreSQL is Installed

If PostgreSQL is not installed, you have two options:

**A. Install PostgreSQL:**
1. Download from: https://www.postgresql.org/download/windows/
2. Install and set up
3. Start the service

**B. Use SQLite (Temporary Solution):**

If you want to test the seed script without PostgreSQL, you can temporarily switch to SQLite:

1. Edit `chitralhivedjango/ecommerce_backend/settings.py`
2. Comment out PostgreSQL config and use SQLite:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Option 3: Check Database Connection Settings

Verify your database settings in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## After Starting PostgreSQL

Once PostgreSQL is running, run the seed command:

```bash
cd chitralhivedjango
python manage.py seed_chitrali_products
```

## Quick Check Commands

```powershell
# Check if PostgreSQL is running
Get-Process -Name postgres -ErrorAction SilentlyContinue

# Check PostgreSQL port
netstat -an | findstr :5432

# Try to connect (if psql is in PATH)
psql -U postgres -h localhost
```

