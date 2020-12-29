import json
from http import HTTPStatus
from unittest.mock import Mock

from functions.source.mural_crud.mural_crud import lambda_handler


def test_post_request_new_mural_creates_mural(fake_environment, murals_table):
    event = {
        "requestContext": {"httpMethod": "POST"},
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

    assert actual["statusCode"] == HTTPStatus.CREATED

    response = murals_table.get_item(
        Key={"id": "test-id", "artist_name_en": "some artist"}
    )
    assert response["Item"]["id"] == "test-id"
    assert response["Item"]["artist_name_en"] == "some artist"
    assert response["Item"]["another_attribute"] == "some attribute"


def test_post_request_new_mural_without_artist_name_creates_mural(
    fake_environment, murals_table
):
    event = {
        "requestContext": {"httpMethod": "POST"},
        "body": json.dumps({"id": "test-id", "another_attribute": "some attribute"}),
    }
    context = Mock()
    actual = lambda_handler(event, context)

    assert actual["statusCode"] == HTTPStatus.CREATED

    response = murals_table.get_item(Key={"id": "test-id", "artist_name_en": "unknown"})
    assert response["Item"]["id"] == "test-id"
    assert response["Item"]["artist_name_en"] == "unknown"
    assert response["Item"]["another_attribute"] == "some attribute"


def test_post_request_existing_mural_returns_conflict(fake_environment, murals_table):
    event = {
        "requestContext": {"httpMethod": "POST"},
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
    assert actual["statusCode"] == HTTPStatus.CREATED

    actual = lambda_handler(event, context)
    assert actual["statusCode"] == HTTPStatus.CONFLICT
