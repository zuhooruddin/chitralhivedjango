module.exports = {
  apps: [
    {
      name: 'django-server',
      script: 'gunicorn',
      args: 'ecommerce_backend.wsgi:application --bind 0.0.0.0:8092 --workers 3',
      interpreter: 'python3',
      cwd: '/var/www/sharp/sharplogician-final-django',
      env: {
        DJANGO_SETTINGS_MODULE: 'ecommerce_backend.settings',
        PYTHONUNBUFFERED: '1'
      }
    }
  ]}
