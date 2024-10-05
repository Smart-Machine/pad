import os
import sys
import time
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from libs.logger.logger import get_colorful_logger

logger = get_colorful_logger()

cmd_infra = [
    ["make", "stop-mongodb"],
    ["make", "remove-mongodb"],
    ["make", "pull-mongodb"],
    ["make", "run-mongodb"],
    ["make", "stop-rabbitmq"],
    ["make", "remove-rabbitmq"],
    ["make", "pull-rabbitmq"],
    ["make", "run-rabbitmq"],
]
cmd_api = [["make", "api"]]
cmd_processes = [["make", "crawl"]]


def run_command(cmd):
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return result.stdout, result.stderr


def wait_for_mongodb():
    bash_command = (
        "docker exec mongodb mongosh --quiet --eval \"db.adminCommand('ping').ok\""
    )
    while True:
        try:
            result = subprocess.run(
                bash_command, shell=True, capture_output=True, text=True
            )
            if result.stdout.strip() == "1":
                logger.info("MongoDB is up!")
                break
            else:
                logger.debug("Waiting for MongoDB to be ready...")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking MongoDB status: {e}")
        time.sleep(2)


def wait_for_api():
    bash_command = "curl http://0.0.0.0:8000/health"
    while True:
        try:
            result = subprocess.run(
                bash_command, shell=True, capture_output=True, text=True
            )
            if result.stdout.strip() == "healthy":
                logger.info("FastAPI is up!")
                break
            else:
                logger.debug("Waiting for FastAPI to be ready...")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking FastAPI status: {e}")
        time.sleep(2)


def run_infrastructure():
    for cmd in cmd_infra:
        logger.debug(" ".join(cmd))
        output, error = run_command(cmd)
        logger.info(f"Output: {output}")
        if error:
            logger.info(f"Error: {error}")
    wait_for_mongodb()


def run_api():
    for cmd in cmd_api:
        logger.debug(" ".join(cmd))
        output, error = run_command(cmd)
        logger.info(f"Output: {output}")
        if error:
            logger.info(f"Error: {error}")
    # wait_for_api()


def run_crawling_process():
    for cmd in cmd_processes:
        logger.debug(" ".join(cmd))
        output, error = run_command(cmd)
        logger.info(f"Output: {output}")
        if error:
            logger.info(f"Error: {error}")
 