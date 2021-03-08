from http import HTTPStatus
from unittest.mock import Mock

from functions.source.mural_crud.mural_crud import lambda_handler


def test_delete_mural_when_does_not_exist_returns_not_found(
    fake_environment, murals_table
):
    event = {
        "requestContext": {"httpMethod": "DELETE"},
        "pathParameters": {
            "mural_id": "test-id",
            "artist_name_en": "some artist",
        },
    }
    context = Mock()

    actual = lambda_handler(event, context)

    assert actual["statusCode"] == HTTPStatus.NOT_FOUND


def test_delete_mural_when_exists_deletes_mural(fake_environment, murals_table):
    murals_table.put_item(
        Item={
            "id": "test-id",
            "artist_name_en": "some-artist",
            "attribute-2": "attribute-2",
        }
    )
    event = {
        "requestContext": {"httpMethod": "DELETE"},
        "pathParameters": {
            "mural_id": "test-id",
            "artist_name_en": "some-artist",
        },
    }
    context = Mock()

    scan_result = murals_table.scan()
    assert scan_result["Count"] == 1
    actual = lambda_handler(event, context)

    assert actual["statusCode"] == HTTPStatus.OK
    scan_result = murals_table.scan()
    assert scan_result["Count"] == 0
