from fastapi.testclient import TestClient

from ai_detector.service import MIN_WORDS, ServiceSettings, create_app


class FakeTokenizer:
    def __call__(self, text):
        return {"input_ids": text.split()}


class FakeClassifier:
    def __init__(self, probability):
        self.probability = probability
        self.max_length = 8192
        self.tokenizer = FakeTokenizer()
        self.received_texts = []

    def score_many(self, texts, *, batch_size=8):
        assert batch_size == 1
        self.received_texts.extend(texts)
        return [self.probability for _ in texts]


SETTINGS = ServiceSettings(model="modernbert", device="cpu", max_tokens=60)


def test_health_reports_model_and_token_cap():
    with TestClient(create_app(SETTINGS, FakeClassifier(0.1))) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model": "modernbert",
        "max_tokens": 60,
    }


def test_score_returns_typed_response():
    classifier = FakeClassifier(0.87341)
    text = "word " * MIN_WORDS
    with TestClient(create_app(SETTINGS, classifier)) as client:
        response = client.post("/v1/score", json={"text": text})

    assert response.status_code == 200
    assert response.json() == {
        "score": 87.341,
        "label": "AI-generated",
        "model": "modernbert",
        "word_count": MIN_WORDS,
        "token_count": MIN_WORDS,
        "truncated": False,
    }
    assert classifier.received_texts == [text.strip()]


def test_score_flags_truncated_text():
    classifier = FakeClassifier(0.2)
    with TestClient(create_app(SETTINGS, classifier)) as client:
        response = client.post("/v1/score", json={"text": "word " * 100})

    body = response.json()
    assert response.status_code == 200
    assert body["label"] == "human-written"
    assert body["token_count"] == 100
    assert body["truncated"] is True
    assert classifier.max_length == 60


def test_short_text_is_rejected():
    classifier = FakeClassifier(0.5)
    with TestClient(create_app(SETTINGS, classifier)) as client:
        response = client.post(
            "/v1/score", json={"text": "word " * (MIN_WORDS - 1)}
        )

    assert response.status_code == 422
    assert classifier.received_texts == []


def test_settings_read_environment(monkeypatch):
    monkeypatch.setenv("AI_DETECTOR_MODEL", "distilbert")
    monkeypatch.setenv("AI_DETECTOR_DEVICE", "cuda")
    monkeypatch.setenv("AI_DETECTOR_MAX_TOKENS", "512")

    assert ServiceSettings.from_env() == ServiceSettings(
        model="distilbert", device="cuda", max_tokens=512
    )
