import json
from http import HTTPStatus
from unittest.mock import Mock

from functions.source.mural_crud.mural_crud import lambda_handler


def test_update_mural_when_does_not_exist_returns_not_found(
    fake_environment, murals_table
):
    event = {
        "requestContext": {"httpMethod": "PUT"},
        "pathParameters": {
            "mural_id": "test-id",
            "artist_name_en": "some artist",
        },
        "body": json.dumps(
            {
                "id": "test-id",
                "artist_name_en": "some artist",
                "another_attribute": "some attribute",
            }
        ),
    }
    context = Mock()

    actual = lambda_handler(event, context)
    assert actual["statusCode"] == HTTPStatus.NOT_FOUND


def test_update_mural_when_exists_updates_mural(fake_environment, murals_table):
    murals_table.put_item(
        Item={
            "id": "test-1",
            "artist_name_en": "artist-2",
            "attribute-2": "attribute-2",
        }
    )
    expected = {
        "id": "test-1",
        "artist_name_en": "artist-1",
        "attribute-1": "attribute-1",
    }
    event = {
        "requestContext": {"httpMethod": "PUT"},
        "pathParameters": {
            "mural_id": "test-1",
            "artist_name_en": "artist-2",
        },
        "body": json.dumps(expected),
    }
    context = Mock()

    actual = lambda_handler(event, context)
    assert actual["statusCode"] == HTTPStatus.NO_CONTENT
    scan_result = murals_table.scan()
    assert scan_result["Count"] == 1
    actual_mural = scan_result["Items"][0]
    assert actual_mural == expected
