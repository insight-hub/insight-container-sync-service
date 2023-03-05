import os
import logging
import sys

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
import docker
from fastapi.responses import JSONResponse
import uvicorn

docker_client = docker.from_env()
AUTH_TOKEN = os.getenv('CI_TOKEN', None)

log = logging.getLogger(__name__)
app = FastAPI()


@app.middleware('http')
async def check_token(req: Request, next):
    if req.headers.get('Authorization') != AUTH_TOKEN:
        return JSONResponse(status_code=401, content={
            "message": "yout shall not pass"})

    res = await next(req)
    return res


@app.get('/info')
async def get_active_containers():
    containers = docker_client.containers.list()
    result = []
    for container in containers:
        result.append({
            'short_id': container.short_id,
            'container_name': container.name,
            'image_name': container.image.tags,
            'created_at': container.attrs['Created'],
            'status': container.status,
            'ports': container.ports,
        })

    return jsonable_encoder(result)


def main():
    if not AUTH_TOKEN:
        log.error('THERE IS NOT AUTH TOKEN IN ENV')
        sys.exit(1)

    uvicorn.run(app)


if __name__ == '__main__':
    main()
