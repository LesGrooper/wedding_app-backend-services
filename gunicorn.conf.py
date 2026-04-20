# gunicorn.conf.py
# Usage: gunicorn -c gunicorn.conf.py app.main:app

import multiprocessing

# Workers = (2 × CPU cores) + 1  — good default for I/O-bound apps
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

bind = "127.0.0.1:8000"
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/wedding/access.log"
errorlog  = "/var/log/wedding/error.log"
loglevel  = "info"

# Process naming
proc_name = "wedding-backend"
