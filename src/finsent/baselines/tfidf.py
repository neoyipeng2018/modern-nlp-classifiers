"""TF-IDF plus logistic regression.

It says how much of the task is surface vocabulary. It is also a canary: it is
fast enough to rerun on every data change, so a data bug shows up here first.
"""

from __future__ import annotations

from ..data.schema import Row


class TfidfBaseline:
    name = "tfidf-lr"
    evidence_grade = "supported"

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self.pipeline = None

    def fit(self, rows: list[Row]) -> "TfidfBaseline":
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import FeatureUnion, Pipeline

        features = FeatureUnion(
            [
                ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
                ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3)),
            ]
        )
        self.pipeline = Pipeline(
            [
                ("features", features),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=2000, C=4.0, class_weight=None, random_state=self.seed
                    ),
                ),
            ]
        )
        self.pipeline.fit([r.text for r in rows], [r.label for r in rows])
        return self

    def predict(self, texts: list[str]) -> list[str]:
        if self.pipeline is None:
            raise RuntimeError("fit before predict")
        return list(self.pipeline.predict(texts))

    def top_features(self, k: int = 15) -> dict[str, list[str]]:
        """The diagnostic. Which words carry the task tells you how lexical it is."""
        if self.pipeline is None:
            raise RuntimeError("fit before inspecting")
        names = self.pipeline.named_steps["features"].get_feature_names_out()
        clf = self.pipeline.named_steps["clf"]
        out = {}
        for index, label in enumerate(clf.classes_):
            weights = clf.coef_[index]
            top = weights.argsort()[-k:][::-1]
            out[str(label)] = [str(names[i]) for i in top]
        return out
