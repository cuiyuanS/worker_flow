import uvicorn

from src import create_app

app = create_app()


if __name__ == '__main__':
    uvicorn.run(app="manage:app", host="0.0.0.0", port=8200, reload=True)