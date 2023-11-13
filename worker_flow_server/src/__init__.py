# import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


from src.views import router
import src.config.base as base_config
from src.middleware.global_ctx import GlobalsMiddleware, SetGlobalsMiddleware
from src.middleware.transaction import TransactionMiddware

# mongodb_client = pymongo.MongoClient() # 同步
mongodb_client = AsyncIOMotorClient()


def create_app():
    app = FastAPI(
        title="工作流API",
        description="后端API接口文档",
        version="0.0.1",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1}
    )

    mongodb_client.__init__(host=base_config.MONGODB_HOST, port=base_config.MONGODB_PORT,
                            username=base_config.MONGODB_USERNAME, password=base_config.MONGODB_PASSWORD,
                            connect=base_config.MONGODB_CONNECT, authSource=base_config.MONGODB_AUTHSOURCE,
                            serverSelectionTimeoutMS=base_config.MONGODB_SERVERSELECTIONTIMEOUTMS, maxPoolSize=0)

    app.include_router(router)
    app.add_middleware(TransactionMiddware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins='*',
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GlobalsMiddleware)
    app.add_middleware(SetGlobalsMiddleware)
    return app
