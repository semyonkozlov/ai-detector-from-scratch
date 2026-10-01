"""HTTP scoring service: one classifier in memory, typed JSON endpoints."""

from contextlib import asynccontextmanager
from dataclasses import dataclass
import os
import re
from threading import Lock

from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

from .classifiers import load_classifier
from .scoring import score_payload


MIN_WORDS = 50


@dataclass(frozen=True)
class ServiceSettings:
    model: str = "modernbert"
    device: str = "cpu"
    max_tokens: int = 2048

    @classmethod
    def from_env(cls):
        return cls(
            model=os.environ.get("AI_DETECTOR_MODEL", cls.model),
            device=os.environ.get("AI_DETECTOR_DEVICE", cls.device),
            max_tokens=int(
                os.environ.get("AI_DETECTOR_MAX_TOKENS", cls.max_tokens)
            ),
        )


def count_words(text):
    return len(re.findall(r"\S+", text))


class ScoreRequest(BaseModel):
    text: str = Field(description=f"Text to score, at least {MIN_WORDS} words.")

    @field_validator("text")
    @classmethod
    def has_enough_words(cls, text):
        if count_words(text) < MIN_WORDS:
            raise ValueError(f"text must contain at least {MIN_WORDS} words")
        return text.strip()


class ScoreResponse(BaseModel):
    score: float = Field(description="Calibrated P(AI) in percent, 0-100.")
    label: str
    model: str
    word_count: int
    token_count: int = Field(description="Tokens in the full text.")
    truncated: bool = Field(
        description="True when only the first max_tokens tokens were scored."
    )


class HealthResponse(BaseModel):
    status: str
    model: str
    max_tokens: int


def create_app(settings, classifier=None):
    @asynccontextmanager
    async def lifespan(application):
        active = classifier
        if active is None:
            active = load_classifier(settings.model, device=settings.device)
        active.max_length = min(int(active.max_length), settings.max_tokens)
        application.state.classifier = active
        application.state.inference_lock = Lock()
        yield

    application = FastAPI(
        title="AI Detector Service",
        version="0.1.0",
        lifespan=lifespan,
    )

    @application.get(
        "/health", response_model=HealthResponse, operation_id="health"
    )
    def health():
        return HealthResponse(
            status="ok",
            model=settings.model,
            max_tokens=application.state.classifier.max_length,
        )

    @application.post(
        "/v1/score", response_model=ScoreResponse, operation_id="score_text"
    )
    def score(request: ScoreRequest):
        active = application.state.classifier
        token_count = len(active.tokenizer(request.text)["input_ids"])
        with application.state.inference_lock:
            probability = active.score_many([request.text], batch_size=1)[0]
        score_value = score_payload(probability)["score"]
        return ScoreResponse(
            score=score_value,
            label="AI-generated" if score_value >= 50.0 else "human-written",
            model=settings.model,
            word_count=count_words(request.text),
            token_count=token_count,
            truncated=token_count > active.max_length,
        )

    return application


app = create_app(ServiceSettings.from_env())
