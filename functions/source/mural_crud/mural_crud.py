"""Create, update and delete Mural lambda"""
import json
import logging
import os
from decimal import Decimal
from http import HTTPStatus
from urllib.parse import unquote
import base64

import boto3  # pylint: disable=import-error

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))


class DecimalEncoder(json.JSONEncoder):
    """Custom encoder that handles Decimal type"""

    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return json.JSONEncoder.default(self, o)


def format_response(status_code, body=None):
    """Formats response"""
    result = {"statusCode": status_code}
    if body is not None:
        result["body"] = json.dumps(body, cls=DecimalEncoder)
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


def delete_mural(mural_id, artist_name_en, murals_table):
    """Removes an existing mural"""
    try:
        murals_table.delete_item(
            Key={"id": mural_id, "artist_name_en": artist_name_en},
            ConditionExpression="attribute_exists(id) AND attribute_exists(artist_name_en)",
        )
    except murals_table.meta.client.exceptions.ConditionalCheckFailedException:
        return HTTPStatus.NOT_FOUND, {"message": "mural not found"}
    return HTTPStatus.OK, {"message": "ok"}


def update_mural(data, mural_id, artist_name_en, murals_table):
    """Updates an existing mural"""
    response_status, _ = delete_mural(mural_id, artist_name_en, murals_table)
    if response_status == HTTPStatus.NOT_FOUND:
        return HTTPStatus.NOT_FOUND, {"message": "mural not found"}
    response_status, _ = add_mural(data, murals_table)
    if response_status == HTTPStatus.CONFLICT:
        return HTTPStatus.INTERNAL_SERVER_ERROR, {
            "message": "something has just happened that should have never happened"
        }
    return HTTPStatus.NO_CONTENT, {"message": "ok"}


def get_mural(mural_id, artist_name_en, murals_table):
    """Returns a mural item by its id and artist name"""
    response = murals_table.get_item(
        Key={"id": mural_id, "artist_name_en": artist_name_en}
    )
    if "Item" not in response:
        return HTTPStatus.NOT_FOUND, {"message": "mural not found"}
    return HTTPStatus.OK, response["Item"]


def get_murals(murals_table, limit, exclusive_start_key):
    """Returns all murals"""
    scan_args = {
        "ProjectionExpression": "id,artist_name_en,geo_position,thumbnail,mural_status",
        "Limit": limit
    }
    if exclusive_start_key:
        scan_args["ExclusiveStartKey"] = exclusive_start_key

    response = murals_table.scan(**scan_args)
    last_evaluated_key = response.get("LastEvaluatedKey")
    result = {
        "items": response.get("Items", []),
    }
    if last_evaluated_key:
        result["next_token"] = base64.urlsafe_b64encode(json.dumps(last_evaluated_key).encode()).decode()

    return HTTPStatus.OK, result


def lambda_handler(event, context):
    """Entrypoint of the lambda function"""
    logger.info(
        "mural_crud start with event: %s", json.dumps(event, indent=2, default=str)
    )
    logger.debug("context: %s", context.__dict__)

    try:
        http_method = event["requestContext"]["httpMethod"]
    except KeyError:
        return format_response(
            HTTPStatus.BAD_REQUEST, {"message": "http_method not found"}
        )

    logger.debug("http method is %s", http_method)

    dynamodb = boto3.resource("dynamodb")
    murals_table = dynamodb.Table(os.environ["MURALS_TABLE"])

    response_code = HTTPStatus.BAD_REQUEST
    response_body = {"message": "Unknown request"}

    if http_method == "POST":
        mural_data = json.loads(event["body"], parse_float=Decimal)
        response_code, response_body = add_mural(mural_data, murals_table)

    if http_method == "GET":
        try:
            mural_id = unquote(event["pathParameters"]["mural_id"])
            artist_name_en = unquote(event["pathParameters"]["artist_name_en"])
        except (TypeError, KeyError):
            mural_id = None
            artist_name_en = None
        if mural_id is None and artist_name_en is None:
            query_string_parameters = event.get("queryStringParameters") or {}
            limit = int(query_string_parameters.get("limit", 200))
            next_token = query_string_parameters.get("next_token", "")
            exclusive_start_key = {}
            if next_token:
                exclusive_start_key = json.loads(base64.urlsafe_b64decode(next_token).decode())
            response_code, response_body = get_murals(murals_table, limit, exclusive_start_key)
        else:
            response_code, response_body = get_mural(
                mural_id, artist_name_en, murals_table
            )

    if http_method == "PUT":
        mural_id = unquote(event["pathParameters"]["mural_id"])
        artist_name_en = unquote(event["pathParameters"]["artist_name_en"])
        mural_data = json.loads(event["body"], parse_float=Decimal)
        response_code, response_body = update_mural(
            mural_data, mural_id, artist_name_en, murals_table
        )

    if http_method == "DELETE":
        mural_id = unquote(event["pathParameters"]["mural_id"])
        artist_name_en = unquote(event["pathParameters"]["artist_name_en"])
        response_code, response_body = delete_mural(
            mural_id, artist_name_en, murals_table
        )

    result = format_response(response_code, response_body)
    return result
