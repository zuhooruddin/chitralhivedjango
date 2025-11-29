# Fix PostgreSQL Connection Error

## Problem
PostgreSQL server is not running or not installed.

## Solution Options

### Option 1: Install and Start PostgreSQL (Recommended)

1. **Download PostgreSQL:**
   - Go to: https://www.postgresql.org/download/windows/
   - Download PostgreSQL installer
   - Install with these settings:
     - Port: 5432
     - Username: `chitral`
     - Password: `chitral`
     - Database: `chitral_hive`

2. **After Installation, Start PostgreSQL:**
   ```powershell
   # Find the service name (usually postgresql-x64-XX)
   Get-Service | Where-Object {$_.DisplayName -like "*PostgreSQL*"}
   
   # Start it (replace with actual service name)
   Start-Service postgresql-x64-15
   # OR use Services GUI: Win+R → services.msc
   ```

3. **Create Database:**
   ```powershell
   # Connect to PostgreSQL
   psql -U chitral -h localhost
   
   # Create database
   CREATE DATABASE chitral_hive;
   \q
   ```

4. **Run Migrations:**
   ```bash
   cd chitralhivedjango
   python manage.py migrate
   ```

5. **Run Seed Command:**
   ```bash
   python manage.py seed_chitrali_products
   ```

### Option 2: Use SQLite (Quick Test - Temporary)

If you want to test the seed script without PostgreSQL:

1. **Edit `ecommerce_backend/settings.py`:**
   ```python
   # Comment out PostgreSQL config:
   # DATABASES = {
   #     'default': {
   #         'ENGINE': 'django.db.backends.postgresql',
   #         'NAME': 'chitral_hive',
   #         'USER': 'chitral',
   #         'PASSWORD': 'chitral',
   #         'HOST': 'localhost',
   #         'PORT': '5432',
   #     }
   # }
   
   # Use SQLite instead:
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

2. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Run Seed Command:**
   ```bash
   python manage.py seed_chitrali_products
   ```

**Note:** SQLite is fine for testing, but use PostgreSQL for production.

### Option 3: Check if PostgreSQL is Running Elsewhere

If PostgreSQL is installed but on a different host/port:

1. **Check your database settings in `settings.py`:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'chitral_hive',
           'USER': 'chitral',
           'PASSWORD': 'chitral',
           'HOST': 'localhost',  # Change if PostgreSQL is on different server
           'PORT': '5432',        # Change if using different port
       }
   }
   ```

2. **Test Connection:**
   ```powershell
   # If psql is installed
   psql -U chitral -h localhost -d chitral_hive
   ```

## Quick Commands

```powershell
# Check if PostgreSQL is installed
Get-Command psql -ErrorAction SilentlyContinue

# Check if PostgreSQL process is running
Get-Process -Name postgres -ErrorAction SilentlyContinue

# Check port 5432
netstat -an | Select-String ":5432"

# Open Services to start PostgreSQL manually
services.msc
```

## After PostgreSQL is Running

Once PostgreSQL is running, run:

```bash
cd chitralhivedjango
python manage.py migrate
python manage.py seed_chitrali_products
```

This will create 2000 Chitrali products in your database!

