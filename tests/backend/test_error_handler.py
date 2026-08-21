from app.harness.error_handler import PipelineError, handle


def test_stt_error_is_safe_for_api_clients():
    payload = handle(PipelineError("stt", "'stt' stage failed: provider decode details"))

    assert payload["message"] == "Couldn't understand the recording. Please try again."
    assert payload["detail"] == payload["message"]
    assert payload["code"] == "speech_not_understood"
    assert payload["status_code"] == 422
    assert "stage" not in payload
    assert "provider" not in str(payload).lower()
