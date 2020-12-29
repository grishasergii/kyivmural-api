"""Create, update and delete Mural lambdal"""
import json
import logging
import os
from http import HTTPStatus

import boto3  # pylint: disable=import-error

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))


def format_response(status_code, body=None):
    """Formats response"""
    result = {"statusCode": status_code}
    if body is not None:
        result["body"] = json.dumps(body)
        result["headers"] = {"Content-Type": "application/json"}
    return result


def add_mural(data, murals_table):
    """Adds a mural item if it does not exist"""
    data["artist_name_en"] = data.get("artist_name_en", "unknown")
    try:
        response = murals_table.put_item(
            Item=data,
            ConditionExpression="attribute_not_exists(id) AND attribute_not_exists(artist_name_en)",
        )
    except murals_table.meta.client.exceptions.ConditionalCheckFailedException:
        return HTTPStatus.CONFLICT, {"message": "item already exists"}
    return HTTPStatus.CREATED, response


def get_mural(mural_id, artist_name_en, murals_table):
    """Returns a mural item by its id and artist name"""
    response = murals_table.get_item(
        Key={"id": mural_id, "artist_name_en": artist_name_en}
    )
    if "Item" not in response:
        return HTTPStatus.NOT_FOUND, {"message": "mural not found"}
    return HTTPStatus.OK, response["Item"]


def lambda_handler(event, context):
    """Entrypoint of the lambda function"""
    logger.info(
        "mural_crud start with event: %s", json.dumps(event, indent=2, default=str)
    )
    logger.debug("context: %s", context.__dict__)

    http_method = event["requestContext"]["httpMethod"]
    logger.debug("http method is %s", http_method)

    dynamodb = boto3.resource("dynamodb")
    murals_table = dynamodb.Table(os.environ["MURALS_TABLE"])

    response_code = HTTPStatus.BAD_REQUEST
    response_body = {"message": "Unknown request"}

    if http_method == "POST":
        mural_data = json.loads(event["body"])
        response_code, response_body = add_mural(mural_data, murals_table)

    result = format_response(response_code, response_body)
    return result
