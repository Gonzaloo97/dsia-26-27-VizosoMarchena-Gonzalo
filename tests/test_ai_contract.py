import json
from unittest.mock import Mock

import httpx
import pytest

from readmission_app.ai_client import FailOnceClient, MockClient, OpenAIClient, RetryingClient, create_client
from readmission_app.config import AIConfig
from readmission_app.errors import AIClientError, DataError, TransientAIError
from readmission_app.pipeline import summary_payload


def test_mock_and_fail_once_without_sleep():
    sleep = Mock()
    client = RetryingClient(FailOnceClient(MockClient()), sleep=sleep)
    response = client.complete("hola")
    assert response.provider == "mock"
    assert "[mock]" in response.text
    sleep.assert_called_once()


def test_retry_exhaustion_and_permanent_error():
    dependency = Mock()
    dependency.complete.side_effect = TransientAIError("temporal")
    sleep = Mock()
    with pytest.raises(TransientAIError):
        RetryingClient(dependency, sleep=sleep).complete("test")
    assert dependency.complete.call_count == 3
    assert sleep.call_count == 2
    dependency.reset_mock()
    dependency.complete.side_effect = AIClientError("permanente")
    with pytest.raises(AIClientError):
        RetryingClient(dependency, sleep=sleep).complete("test")
    assert dependency.complete.call_count == 1


@pytest.mark.parametrize("status,expected", [(401, AIClientError), (403, AIClientError),
                                            (400, AIClientError), (429, TransientAIError),
                                            (408, TransientAIError), (503, TransientAIError)])
def test_http_errors_classified_without_secrets(status, expected):
    post = Mock(return_value=httpx.Response(status, text="SECRET_BODY"))
    client = OpenAIClient(AIConfig(provider="openai", api_key="TEST_SECRET"), post=post)
    with pytest.raises(expected) as error:
        client.complete("no personal data")
    assert type(error.value) is expected
    assert "SECRET" not in str(error.value)


def test_real_http_contract_with_stub_no_network():
    post = Mock(return_value=httpx.Response(200, json={"choices": [{"message": {"content": "Resumen"}}]}))
    config = AIConfig(provider="openai", api_key="TEST_SECRET", model="test-model", timeout=8)
    response = OpenAIClient(config, post=post).complete("agregados")
    assert response.text == "Resumen"
    assert response.provider == "openai"
    assert post.call_args.args[0] == "https://api.openai.com/v1/chat/completions"
    kwargs = post.call_args.kwargs
    assert kwargs["timeout"] == 8
    assert kwargs["json"]["model"] == "test-model"
    assert kwargs["json"]["messages"][1]["content"] == "agregados"
    assert kwargs["json"]["store"] is False
    assert "TEST_SECRET" not in repr(config)


@pytest.mark.parametrize("body", [{}, {"choices": []}, {"choices": [{"message": {"content": ""}}]},
                                  {"choices": [{"message": {"content": None}}]}])
def test_invalid_provider_response(body):
    client = OpenAIClient(AIConfig(provider="openai", api_key="fake"), post=Mock(return_value=httpx.Response(200, json=body)))
    with pytest.raises(AIClientError):
        client.complete("agregados")


def test_timeout_is_transient_and_missing_key_is_permanent():
    with pytest.raises(AIClientError, match="OPENAI_API_KEY"):
        create_client(AIConfig(provider="openai"))
    post = Mock(side_effect=httpx.ReadTimeout("private transport details"))
    with pytest.raises(TransientAIError, match="Timeout"):
        OpenAIClient(AIConfig(provider="openai", api_key="fake"), post=post).complete("test")


@pytest.mark.parametrize("kwargs", [{"provider": "unknown"}, {"timeout": 0}, {"timeout": float("nan")},
                                    {"max_retries": -1}, {"max_retries": 6}, {"model": " "}])
def test_config_invalid(kwargs):
    with pytest.raises(DataError):
        AIConfig(**kwargs)


def test_config_env_and_prompt_validation(monkeypatch):
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", "oops")
    with pytest.raises(DataError):
        AIConfig.from_env()
    for prompt in (" ", "a" * 12001):
        with pytest.raises(AIClientError):
            create_client(AIConfig()).complete(prompt)


def test_payload_allowlist_omits_identifiers_and_diagnoses(trained):
    _, bundle, _, predictions = trained
    quality = {"rows_in": 32, "rows_out": 32, "rows_dropped": 0, "error_rate": 0,
               "unexpected_private_text": "DO_NOT_SEND"}
    payload = summary_payload(quality, predictions, bundle["metadata"])
    serialized = json.dumps(payload)
    for excluded in ("patient_nbr", "encounter_id", "diag_1", "train_patient_ids", "DO_NOT_SEND"):
        assert excluded not in serialized
    assert payload["predictions"]["predicted_positive_count"] == int(predictions.prediction_readmission_30.sum())
