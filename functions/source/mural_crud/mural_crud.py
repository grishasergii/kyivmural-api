import json
from http import HTTPStatus
import os
import logging


logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))


def format_response(status_code, body=None):
    result = {"statusCode": status_code}
    if body is not None:
        result["body"] = json.dumps(body)
        result["headers"] = {"Content-Type": "application/json"}
    return result


def lambda_handler(event, context):
    logger.info("mural_crud start with event: %s", json.dumps(event, indent=2, default=str))
    logger.debug("context: %s", context.__dict__)
    format_response(HTTPStatus.OK, {"message": "ok"})
