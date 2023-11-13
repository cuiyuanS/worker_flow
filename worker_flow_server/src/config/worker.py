from src.env import cf

ASYNC_JOB_ADDRESS = cf.get("worker", "async_job_address").split(",")
SYNC_JOB_ADDRESS = cf.get("worker", "sync_job_address").split(",")
UPLOAD_SERVER_URL = "http://10.25.10.132:8200/tool/upload"