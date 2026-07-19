"""Lightweight and semantic metrics for generated procedural text."""

from __future__ import annotations

import os
import re
from typing import Any

from common import failure, require, result_envelope


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
DEFAULT_KEYWORD_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def as_text(value: str | list[str]) -> str:
    return "\n".join(value) if isinstance(value, list) else value


def as_steps(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        return [step.strip() for step in value if step.strip()]
    return [step.strip() for step in value.splitlines() if step.strip()]


def token_overlap(reference: str, prediction: str) -> tuple[float, float, float]:
    reference_tokens = TOKEN_PATTERN.findall(reference.lower())
    prediction_tokens = TOKEN_PATTERN.findall(prediction.lower())
    if not reference_tokens or not prediction_tokens:
        exact_empty = float(reference_tokens == prediction_tokens)
        return exact_empty, exact_empty, exact_empty
    remaining: dict[str, int] = {}
    for token in reference_tokens:
        remaining[token] = remaining.get(token, 0) + 1
    overlap = 0
    for token in prediction_tokens:
        if remaining.get(token, 0):
            overlap += 1
            remaining[token] -= 1
    precision = overlap / len(prediction_tokens)
    recall = overlap / len(reference_tokens)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


class SemanticBackend:
    def __init__(
        self,
        *,
        offline: bool,
        embedding_model: str,
        keyword_model: str,
        similarity_threshold: float,
    ) -> None:
        try:
            import nltk
            import numpy as np
            from keybert import KeyBERT
            from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
            from nltk.translate.meteor_score import meteor_score
            from rouge_score import rouge_scorer
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Semantic dependencies are missing. Install requirements-semantic.txt."
            ) from exc

        self.nltk = nltk
        self.np = np
        self.SmoothingFunction = SmoothingFunction
        self.sentence_bleu = sentence_bleu
        self.meteor_score = meteor_score
        self.rouge_scorer = rouge_scorer
        self.similarity_threshold = similarity_threshold
        self._ensure_nltk_resource("tokenizers/punkt", "punkt", offline)
        self._ensure_nltk_resource("tokenizers/punkt_tab", "punkt_tab", offline)
        self._ensure_nltk_resource("corpora/wordnet", "wordnet", offline)

        previous_offline = os.environ.get("HF_HUB_OFFLINE")
        if offline:
            os.environ["HF_HUB_OFFLINE"] = "1"
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            self.keyword_model = KeyBERT(SentenceTransformer(keyword_model))
        except Exception as exc:
            mode = "offline cache" if offline else "model registry or local path"
            raise RuntimeError(f"Could not load semantic models from {mode}: {exc}") from exc
        finally:
            if offline:
                if previous_offline is None:
                    os.environ.pop("HF_HUB_OFFLINE", None)
                else:
                    os.environ["HF_HUB_OFFLINE"] = previous_offline

    def _ensure_nltk_resource(self, path: str, package: str, offline: bool) -> None:
        for candidate in (path, path + ".zip"):
            try:
                self.nltk.data.find(candidate)
                return
            except LookupError:
                pass
        if offline:
            raise RuntimeError(f"Missing NLTK resource in offline mode: {package}")
        if not self.nltk.download(package, quiet=True):
            raise RuntimeError(f"Failed to download NLTK resource: {package}")

    def text_metrics(self, reference: str, prediction: str) -> dict[str, float]:
        reference_tokens = self.nltk.word_tokenize(reference.lower())
        prediction_tokens = self.nltk.word_tokenize(prediction.lower())
        bleu = self.sentence_bleu(
            [reference_tokens],
            prediction_tokens,
            weights=(0.5, 0.5),
            smoothing_function=self.SmoothingFunction().method1,
        )
        meteor = self.meteor_score([reference_tokens], prediction_tokens)
        scorer = self.rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
        rouge = scorer.score(reference, prediction)
        return {
            "bleu": float(bleu),
            "meteor": float(meteor),
            "rouge1": float(rouge["rouge1"].fmeasure),
            "rouge2": float(rouge["rouge2"].fmeasure),
            "rougeL": float(rouge["rougeL"].fmeasure),
        }

    def keyword_overlap(self, reference: str, prediction: str, top_k: int) -> tuple[float, float, float]:
        reference_keywords = {
            keyword for keyword, _ in self.keyword_model.extract_keywords(reference, top_n=top_k)
        }
        prediction_keywords = {
            keyword for keyword, _ in self.keyword_model.extract_keywords(prediction, top_n=top_k)
        }
        if not reference_keywords or not prediction_keywords:
            return 0.0, 0.0, 0.0
        overlap = reference_keywords & prediction_keywords
        precision = len(overlap) / len(prediction_keywords)
        recall = len(overlap) / len(reference_keywords)
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return precision, recall, f1

    def step_scores(self, reference: list[str], prediction: list[str]) -> tuple[float, float]:
        if not reference:
            return 1.0, 0.0 if prediction else 1.0
        if not prediction:
            return 0.0, 1.0
        reference_vectors = self.embedding_model.encode(reference, normalize_embeddings=True)
        prediction_vectors = self.embedding_model.encode(prediction, normalize_embeddings=True)
        similarities = self.np.matmul(reference_vectors, prediction_vectors.T)
        matched_references = int((similarities.max(axis=1) >= self.similarity_threshold).sum())
        matched_predictions = int((similarities.max(axis=0) >= self.similarity_threshold).sum())
        return matched_references / len(reference), matched_predictions / len(prediction)


def evaluate(
    records: list[dict[str, Any]],
    *,
    metrics_mode: str = "core",
    offline: bool = False,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    keyword_model: str = DEFAULT_KEYWORD_MODEL,
    similarity_threshold: float = 0.7,
    top_k: int = 64,
    **_: Any,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    if metrics_mode not in {"core", "semantic", "all"}:
        raise ValueError("metrics_mode must be core, semantic, or all")
    if not 0 <= similarity_threshold <= 1:
        raise ValueError("similarity_threshold must be between 0 and 1")
    if top_k < 1:
        raise ValueError("top_k must be positive")

    semantic = metrics_mode in {"semantic", "all"}
    backend = (
        SemanticBackend(
            offline=offline,
            embedding_model=embedding_model,
            keyword_model=keyword_model,
            similarity_threshold=similarity_threshold,
        )
        if semantic
        else None
    )
    metric_names = []
    if metrics_mode in {"core", "all"}:
        metric_names += ["exact_match", "token_precision", "token_recall", "token_f1"]
    if semantic:
        metric_names += [
            "bleu", "meteor", "rouge1", "rouge2", "rougeL",
            "keyword_precision", "keyword_recall", "keyword_f1",
            "step_recall", "redundancy_penalty",
        ]
    values: dict[str, list[float]] = {name: [] for name in metric_names}
    errors: list[dict[str, str]] = []

    for index, item in enumerate(records):
        try:
            prediction = require(item, "prediction")
            reference = require(item, "reference")
            if not isinstance(prediction, (str, list)) or not isinstance(reference, (str, list)):
                raise ValueError("prediction and reference must be strings or lists of strings")
            if isinstance(prediction, list) and not all(isinstance(step, str) for step in prediction):
                raise ValueError("prediction list must contain strings")
            if isinstance(reference, list) and not all(isinstance(step, str) for step in reference):
                raise ValueError("reference list must contain strings")
            prediction_text = as_text(prediction)
            reference_text = as_text(reference)
            sample: dict[str, float] = {}
            if metrics_mode in {"core", "all"}:
                precision, recall, f1 = token_overlap(reference_text, prediction_text)
                sample.update(
                    exact_match=float(prediction_text.strip() == reference_text.strip()),
                    token_precision=precision,
                    token_recall=recall,
                    token_f1=f1,
                )
            if backend is not None:
                sample.update(backend.text_metrics(reference_text, prediction_text))
                precision, recall, f1 = backend.keyword_overlap(reference_text, prediction_text, top_k)
                sample.update(keyword_precision=precision, keyword_recall=recall, keyword_f1=f1)
                if isinstance(reference, list):
                    step_recall, redundancy = backend.step_scores(reference, as_steps(prediction))
                    sample.update(step_recall=step_recall, redundancy_penalty=redundancy)
            for name, value in sample.items():
                values[name].append(value)
        except Exception as exc:
            errors.append(failure(item, index, exc))

    metrics = {name: mean(entries) for name, entries in values.items()}
    scored = len(records) - len(errors)
    config: dict[str, Any] = {"metrics_mode": metrics_mode}
    if semantic:
        config.update(
            embedding_model=embedding_model,
            keyword_model=keyword_model,
            similarity_threshold=similarity_threshold,
            top_k=top_k,
            offline=offline,
        )
    return (
        result_envelope(
            "protocol-generation",
            len(records),
            scored,
            metrics,
            errors,
            config,
        ),
        errors,
    )
