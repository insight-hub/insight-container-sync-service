import os
import logging
import sys

from fastapi import FastAPI
import docker
import uvicorn

docker_client = docker.from_env()
AUTH_TOKEN = os.getenv('CI_TOKEN', None)

log = logging.getLogger(__name__)
app = FastAPI()


def main():
    if not AUTH_TOKEN:
        log.error('THERE IS NOT AUTH TOKEN IN ENV')
        sys.exit(1)

    uvicorn.run(app)


if __name__ == '__main__':
    main()
