from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ScoreResponse")


@_attrs_define
class ScoreResponse:
    """
    Attributes:
        score (float): Calibrated P(AI) in percent, 0-100.
        label (str):
        model (str):
        word_count (int):
        token_count (int): Tokens in the full text.
        truncated (bool): True when only the first max_tokens tokens were scored.
    """

    score: float
    label: str
    model: str
    word_count: int
    token_count: int
    truncated: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        score = self.score

        label = self.label

        model = self.model

        word_count = self.word_count

        token_count = self.token_count

        truncated = self.truncated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "score": score,
                "label": label,
                "model": model,
                "word_count": word_count,
                "token_count": token_count,
                "truncated": truncated,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        score = d.pop("score")

        label = d.pop("label")

        model = d.pop("model")

        word_count = d.pop("word_count")

        token_count = d.pop("token_count")

        truncated = d.pop("truncated")

        score_response = cls(
            score=score,
            label=label,
            model=model,
            word_count=word_count,
            token_count=token_count,
            truncated=truncated,
        )

        score_response.additional_properties = d
        return score_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
