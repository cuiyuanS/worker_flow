from fastapi import UploadFile

from . import router
from src.helper.response import resp_500, json_response
from src.config.base import FILE_HOST
from src.helper.common import save_file


@router.post("/tool/upload", include_in_schema=False)
def tool_upload(file: UploadFile):
    # 调用gearman
    try:
        file_path = save_file(file)
    except Exception as e:
        return resp_500(message=str(e))

    return json_response(data={"file_path": FILE_HOST + file_path})
