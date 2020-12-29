import json
from http import HTTPStatus
from unittest.mock import Mock

from functions.source.mural_crud.mural_crud import lambda_handler


def test_get_mural_does_not_exist_returns_not_found(fake_environment, murals_table):
    event = {
        "requestContext": {"http": {"method": "GET"}},
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
        "requestContext": {"http": {"method": "GET"}},
        "pathParameters": {
            "muralId": expected["id"],
            "artistNameEn": expected["artist_name_en"],
        },
    }

    context = Mock()

    actual = lambda_handler(event, context)

    assert actual["statusCode"] == HTTPStatus.OK
    assert json.loads(actual["body"]) == expected


def test_get_all_murals_when_empty_table_returns_empty_list(
    fake_environment, murals_table
):
    event = {"requestContext": {"http": {"method": "GET"}}, "pathParameters": None}

    context = Mock()

    actual = lambda_handler(event, context)
    assert actual["statusCode"] == HTTPStatus.OK
    assert len(json.loads(actual["body"])) == 0


def test_get_all_murals_when_table_has_murals_result_contains_only_specified_fields(
    fake_environment, murals_table
):
    item = {
        "id": "test-1",
        "artist_name_en": "artist-1",
        "attribute-1": "attribute-1",
        "attribute-2": "attribute-2",
        "geo_position": {"latitude": "1", "longitude": "1"},
        "thumbnail": "dickpic",
        "status": "active",
    }
    expected = {
        "id": "test-1",
        "artist_name_en": "artist-1",
        "geo_position": {"latitude": "1", "longitude": "1"},
        "thumbnail": "dickpic",
        "status": "active",
    }
    murals_table.put_item(Item=item)

    event = {
        "requestContext": {"http": {"method": "GET"}},
    }

    context = Mock()

    actual = lambda_handler(event, context)
    assert actual["statusCode"] == HTTPStatus.OK
    actual_items = json.loads(actual["body"])
    assert len(actual_items) == 1
    assert actual_items[0] == expected


def test_get_all_murals_when_table_has_murals_returns_list_with_all_murals(
    fake_environment, murals_table
):
    num_murals = 500
    for i in range(num_murals):
        item = {
            "id": f"test-{i}",
            "artist_name_en": f"artist-{i}",
            "attribute-1": "attribute-1",
        }
        murals_table.put_item(Item=item)

    event = {
        "requestContext": {"http": {"method": "GET"}},
    }

    context = Mock()

    actual = lambda_handler(event, context)
    assert actual["statusCode"] == HTTPStatus.OK
    assert len(json.loads(actual["body"])) == num_murals
