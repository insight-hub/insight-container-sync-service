import os
import logging
import sys

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
import docker
import uvicorn

docker_client = docker.from_env()
AUTH_TOKEN = os.getenv('CI_TOKEN', None)

log = logging.getLogger(__name__)
app = FastAPI()


def get_active_containers():
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

    return result


@app.get('/info')
async def containers_info():
    return jsonable_encoder(get_active_containers())


def main():
    if not AUTH_TOKEN:
        log.error('THERE IS NOT AUTH TOKEN IN ENV')
        sys.exit(1)

    uvicorn.run(app)


if __name__ == '__main__':
    main()
