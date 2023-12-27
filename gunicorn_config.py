import os
import main
workers = int(os.environ.get("GUNICORN_PROSSESS","4"))

worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "uvicorn.workers.UvicornWorker")
#threads = int(os.environ.get("GUNICORN_THREADS","4"))

# timeout = int(os.environ.get("GUNICORN_TIMEOUT" , "120"))

bind = os.environ.get("GUNICORN_BIND","127.0.0.1:8000")


forwarded_allow_ips = "*"

secure_scheme_headers = {"X-Forwarded-Proto": "https"}

app = "main:app"
