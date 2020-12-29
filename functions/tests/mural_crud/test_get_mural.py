import json
from http import HTTPStatus
from unittest.mock import Mock

from functions.source.mural_crud.mural_crud import lambda_handler


def test_get_mural_does_not_exist_returns_not_found(fake_environment, murals_table):
    event = {
        "requestContext": {"httpMethod": "GET"},
        "pathParameters": {
            "muralId": "test-id",
            "artistNameEn": "some artist",
        },
    }
    context = Mock()

    actual = lambda_handler(event, context)

    assert actual["statusCode"] == HTTPStatus.NOT_FOUND


def test_get_mural_exists_returns_the_mural(fake_environment, murals_table):
    expected = {
        "id": "test-1",
        "artist_name_en": "artist-1",
        "attribute-1": "attribute-1",
    }
    murals_table.put_item(Item=expected)
    murals_table.put_item(
        Item={
            "id": "test-1",
            "artist_name_en": "artist-2",
            "attribute-2": "attribute-2",
        }
    )

    event = {
        "requestContext": {"httpMethod": "GET"},
        "pathParameters": {
            "muralId": expected["id"],
            "artistNameEn": expected["artist_name_en"],
        },
    }

    context = Mock()

    actual = lambda_handler(event, context)

    assert actual["statusCode"] == HTTPStatus.OK
    assert json.loads(actual["body"]) == expected
