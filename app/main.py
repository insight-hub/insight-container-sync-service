import os
import logging
import sys
from pydantic import BaseModel

import uvicorn
import docker
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from logging.config import dictConfig
from .logger import LogConfig


docker_client = docker.from_env()
AUTH_TOKEN = os.getenv('CI_TOKEN', None)

dictConfig(LogConfig().dict())
log = logging.getLogger("sync")
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


def get_container_name(owner: str, repository: str, tag: str):
    if owner and repository and tag:
        return f'{owner}/{repository}:{tag}', repository
    if repository and tag:
        return f'{repository}:{tag}', repository
    return "", ""


def kill_old_container(container_name: str):
    try:
        container = docker_client.containers.get(container_name)
        container.kill()

    except Exception as e:
        log.warning(f'Error while delete container {container_name}, {e}')
        return False

    finally:
        log.info(docker_client.containers.prune())
        log.info(docker_client.images.prune())

    log.info(f'Container deleted. container_name = {container_name}')
    return True


def get_ports_interface(ports: dict):
    return {key: ('127.0.0.1', value) for key, value in ports.items()}


@app.post('/update')
async def deploy_new_container(
        owner: str = Body(),
        repository: str = Body(),
        tag: str = Body(),
        ports: dict = Body(),
):
    image_name, container_name = get_container_name(owner, repository, tag)

    try:
        log.info(f'pull {image_name}, name={container_name}')
        docker_client.images.pull(image_name)
        log.info('Sucess')
        kill_old_container(container_name)
        docker_client.containers.run(
            image=image_name,
            name=container_name,
            ports=get_ports_interface(ports),
            detach=True
        )

        return {"message": f'{container_name} are God damn deployed'}

    except Exception as e:
        log.error(f'Error while deploing container {container_name} {e}')
        raise HTTPException(
            status_code=400,
            detail=f"error while deploing contaier {container_name}"
        )


def main():
    if not AUTH_TOKEN:
        log.error('THERE IS NOT AUTH TOKEN IN ENV')
        sys.exit(1)

    uvicorn.run(app, port=7777)


if __name__ == '__main__':
    main()
