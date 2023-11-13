from fastapi import Request

from . import router
from src.helper.response import json_response
from src.node.constant import NODE_CLASS_MAPPINGS
from src.node import get_node_info
from ..node.execute import WorkerExecutor


@router.get("/node_info", name="所有节点", tags=["节点"])
def node_info():
    out = {}
    for x in NODE_CLASS_MAPPINGS:
        try:
            out[x] = get_node_info(x)
        except Exception as e:
            return json_response(err=f"[ERROR] An error occurred while retrieving information for the '{x}' node.")
    return json_response(data=out)


@router.post("/try_execute", name="尝试运行", tags=["节点"])
async def try_execute(request: Request):
    chain_worker = WorkerExecutor()
    chain_worker.worker_flow = await request.json()
    res = chain_worker.execute_flow()
    return json_response(data=res)


@router.post("/try_execute/{mark}", name="尝试运行mark", tags=["节点"])
def try_execute(mark):
    chain_worker = WorkerExecutor(mark=mark)
    chain_worker.get_worker_flow_json()
    res = chain_worker.execute_flow()
    return json_response(data=res)
