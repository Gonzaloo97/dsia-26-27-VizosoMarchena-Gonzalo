"""El borde HTTP se prueba sin red; los smokes reales son evidencia separada."""

import json
from unittest.mock import Mock

import httpx
import pytest

from readmission_app.open_api_client import OpenAPIClient, OpenAPIError, TransientOpenAPIError, main


@pytest.mark.parametrize("method,args,payload,source,field,expected", [
    ("weather", [], {"current": {"time": "2026-11-11", "temperature_2m": 15, "wind_speed_10m": 3}}, "open-meteo", "temperature_c", 15),
    ("country", ["es"], [{}, [{"id": "ESP", "iso2Code": "ES", "name": "Spain", "capitalCity": "Madrid"}]], "worldbank", "capital", "Madrid"),
    ("fx", [], {"base": "EUR", "date": "2026-11-10", "rates": {"USD": 1.1}}, "frankfurter", "rates", {"USD": 1.1}),
    ("github", ["dmartincc", "dsia-26-27"], {"full_name": "dmartincc/dsia-26-27", "html_url": "https://github.com/dmartincc/dsia-26-27", "language": "Python", "stargazers_count": 1}, "github", "language", "Python"),
])
def test_normalized_contract(method, args, payload, source, field, expected):
    get = Mock(return_value=httpx.Response(200, json=payload))
    result = getattr(OpenAPIClient(get=get), method)(*args)
    assert result.source == source
    assert result.data[field] == expected
    assert get.call_args.kwargs["timeout"] == 15
    assert "Authorization" not in get.call_args.kwargs["headers"]


@pytest.mark.parametrize("status", [401, 403, 404])
def test_permanent_errors_are_not_retried(status):
    get, sleep = Mock(return_value=httpx.Response(status, text="PRIVATE_BODY")), Mock()
    with pytest.raises(OpenAPIError) as error:
        OpenAPIClient(get=get, sleep=sleep).country("ES")
    assert type(error.value) is OpenAPIError
    assert "PRIVATE_BODY" not in str(error.value)
    get.assert_called_once()
    sleep.assert_not_called()


@pytest.mark.parametrize("failure", [httpx.ReadTimeout("private"), httpx.Response(429), httpx.Response(503)])
def test_transient_failure_recovers(failure):
    get = Mock(side_effect=[failure, httpx.Response(200, json={"base": "EUR", "date": "2026-11-11", "rates": {"USD": 1.1}})])
    sleep = Mock()
    assert OpenAPIClient(get=get, sleep=sleep).fx().source == "frankfurter"
    assert get.call_count == 2
    sleep.assert_called_once()


def test_retry_exhaustion_and_non_json():
    get, sleep = Mock(return_value=httpx.Response(500)), Mock()
    with pytest.raises(TransientOpenAPIError):
        OpenAPIClient(get=get, sleep=sleep).country("ES")
    assert get.call_count == 3
    assert sleep.call_count == 2
    with pytest.raises(OpenAPIError, match="JSON"):
        OpenAPIClient(get=Mock(return_value=httpx.Response(200, text="not json"))).country("ES")


@pytest.mark.parametrize("method,args", [("weather", [float("nan"), 0]), ("country", ["../ES"]),
                                        ("fx", ["bad!", "USD"]), ("github", ["a/b", "repo"])])
def test_invalid_parameters_do_not_call_network(method, args):
    get = Mock()
    with pytest.raises(OpenAPIError):
        getattr(OpenAPIClient(get=get), method)(*args)
    get.assert_not_called()


@pytest.mark.parametrize("method,args", [("weather", []), ("country", ["ZZ"]), ("fx", []), ("github", ["owner", "repo"])])
def test_bad_response_is_typed_error(method, args):
    with pytest.raises(OpenAPIError):
        getattr(OpenAPIClient(get=Mock(return_value=httpx.Response(200, json={}))), method)(*args)


def test_cli_json_and_controlled_failure(capsys):
    client = OpenAPIClient(get=Mock(return_value=httpx.Response(200, json=[{}, [{"id": "ESP", "iso2Code": "ES", "name": "Spain", "capitalCity": "Madrid"}]])))
    assert main(["country", "--code", "ES"], client=client) == 0
    assert json.loads(capsys.readouterr().out)["source"] == "worldbank"
    client = OpenAPIClient(get=Mock(return_value=httpx.Response(200, json=[{}, None])))
    assert main(["country", "--code", "ZZ"], client=client) == 1
    assert "ERROR:" in capsys.readouterr().err
