import os
from pathlib import Path
from typing import Dict, List, Tuple

import yaml
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


class ColumnMapper:
    def __init__(self, model_path: str = 'output/models/ml_mapper.pkl') -> None:
        self.model_path = Path(model_path)
        self.model: Pipeline = None  # type: ignore
        self.labels = [
            'timestamp', 'type', 'base_asset', 'base_amount',
            'quote_asset', 'quote_amount', 'fee_amount', 'fee_asset', 'notes'
        ]

    def fit_from_yaml(self, config_path: str = 'config/exchanges.yaml') -> None:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        X: List[str] = []
        y: List[str] = []

        synonyms = {
            'timestamp': ['time', 'date', 'datetime', 'created at', 'created', 'timestamp'],
            'type': ['type', 'side', 'action', 'operation', 'transaction type', 'kind'],
            'base_asset': ['base asset', 'asset', 'coin', 'token', 'symbol', 'product', 'token in', 'asset sent', 'from asset'],
            'base_amount': ['amount', 'qty', 'quantity', 'size', 'vol', 'volume', 'executed', 'amount in'],
            'quote_asset': ['quote asset', 'counter asset', 'spot price currency', 'fiat', 'market', 'pair', 'token out', 'asset received', 'to asset'],
            'quote_amount': ['total', 'value', 'subtotal', 'cost', 'price', 'amount out', 'usd amount', 'usd value'],
            'fee_amount': ['fee', 'commission', 'trading fee', 'network fee', 'gas', 'fees and/or spread'],
            'fee_asset': ['fee currency', 'fee coin', 'fee asset', 'network fee asset', 'bnb', 'usd'],
            'notes': ['notes', 'info', 'remark', 'specification', 'description']
        }

        for _, mapping in data.items():
            if not isinstance(mapping, dict):
                continue
            for label in self.labels:
                v = mapping.get(label)
                if isinstance(v, str) and v and v != 'None':
                    for txt in self._augment(v):
                        X.append(txt)
                        y.append(label)
                for syn in synonyms.get(label, []):
                    for txt in self._augment(syn):
                        X.append(txt)
                        y.append(label)

        if not X:
            raise ValueError('No training data for ML column mapper')

        self.model = Pipeline(steps=[
            ('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5))),
            ('clf', LogisticRegression(max_iter=1000, class_weight='balanced'))
        ])
        self.model.fit(X, y)

        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({'model': self.model, 'labels': self.labels}, self.model_path)

    def load_or_fit(self, config_path: str = 'config/exchanges.yaml') -> None:
        if self.model_path.exists():
            try:
                obj = joblib.load(self.model_path)
                self.model = obj['model']
                self.labels = obj['labels']
                return
            except Exception:
                pass
        self.fit_from_yaml(config_path)

    def predict(self, columns: List[str]) -> Dict[str, Tuple[str, float]]:
        if self.model is None:
            self.load_or_fit()
        preds: Dict[str, Tuple[str, float]] = {}
        clf = self.model.named_steps['clf']
        has_proba = hasattr(clf, 'predict_proba')
        y = self.model.predict(columns)
        proba_map = {}
        if has_proba:
            probs = clf.predict_proba(self.model.named_steps['tfidf'].transform(columns))
            classes = list(clf.classes_)
            for i, col in enumerate(columns):
                lbl = y[i]
                try:
                    p = float(probs[i][classes.index(lbl)])
                except Exception:
                    p = 0.5
                proba_map[col] = p
        for i, col in enumerate(columns):
            lbl = y[i]
            p = proba_map.get(col, 0.5)
            preds[col] = (lbl, p)
        return preds

    def predict_mapping(self, columns: List[str], threshold: float = 0.8) -> Dict[str, Tuple[str, float]]:
        if self.model is None:
            self.load_or_fit()
        clf = self.model.named_steps['clf']
        probs = clf.predict_proba(self.model.named_steps['tfidf'].transform(columns))
        classes = list(clf.classes_)
        idx_map = {lbl: i for i, lbl in enumerate(classes)}
        pairs: List[Tuple[float, int, int]] = []
        for i, col in enumerate(columns):
            for lbl in self.labels:
                if lbl in idx_map:
                    p = float(probs[i][idx_map[lbl]])
                    if p >= 0.5:
                        pairs.append((p, i, idx_map[lbl]))
        pairs.sort(reverse=True, key=lambda x: x[0])
        assigned_cols = set()
        assigned_lbls = set()
        result: Dict[str, Tuple[str, float]] = {}
        for p, ci, li in pairs:
            lbl = classes[li]
            if ci in assigned_cols or lbl in assigned_lbls:
                continue
            if p < threshold:
                continue
            assigned_cols.add(ci)
            assigned_lbls.add(lbl)
            result[columns[ci]] = (lbl, p)
        return result

    def _augment(self, s: str) -> List[str]:
        s = str(s)
        cand = {
            s,
            s.lower(),
            s.strip(),
            s.replace('-', ' '),
            s.replace('_', ' '),
            s.replace('/', ' '),
        }
        return list(cand)
