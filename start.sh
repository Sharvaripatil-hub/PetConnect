#!/usr/bin/env bash
# Start script for Render deployment
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 2 --timeout 0 PetConnect.wsgi:application