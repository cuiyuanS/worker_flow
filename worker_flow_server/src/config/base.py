from src.env import cf

MONGODB_HOST = cf.get("mongodb", "host")
MONGODB_PORT = cf.getint("mongodb", "port")
MONGODB_USERNAME = cf.get("mongodb", "username")
MONGODB_PASSWORD = cf.get("mongodb", "password")
MONGODB_DB = cf.get("mongodb", "db")
MONGODB_CONNECT = False  # `connect`（可选）：如果`True`（默认值），立即开始在后台连接MongoDB。否则，在第一次操作时进行连接。
MONGODB_AUTHSOURCE = cf.get("mongodb", "authentication_source")
MONGODB_SERVERSELECTIONTIMEOUTMS = 5000  # 连接超时5秒

DATA_PREFIX = cf.get("base", "data_prefix")
PROJECT_NAME = cf.get("base", "project_name")
ENVIRONMENT = cf.get("base", "environment")
LOG_DIR = cf.get("base", "log_dir")
FILE_HOST = cf.get("base", "file_host")