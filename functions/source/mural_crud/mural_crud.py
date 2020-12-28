"""Create, update and delete Mural lambdal"""
import json
import logging
import os
from http import HTTPStatus

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))


def format_response(status_code, body=None):
    """Formats response"""
    result = {"statusCode": status_code}
    if body is not None:
        result["body"] = json.dumps(body)
        result["headers"] = {"Content-Type": "application/json"}
    return result


def lambda_handler(event, context):
    """Entrypoint of the lambda function"""
    logger.info(
        "mural_crud start with event: %s", json.dumps(event, indent=2, default=str)
    )
    logger.debug("context: %s", context.__dict__)
    format_response(HTTPStatus.OK, {"message": "ok"})
