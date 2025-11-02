import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.ml_mapper import ColumnMapper

def test_predict_mapping_unique_labels():
    mapper = ColumnMapper()
    mapper.load_or_fit()
    cols = ['Date(UTC)', 'Type', 'Asset', 'Amount', 'Fee Coin']
    mapping = mapper.predict_mapping(cols, threshold=0.6)
    labels = [lbl for _, (lbl, _) in mapping.items()]
    assert len(labels) == len(set(labels))

    if 'Date(UTC)' in mapping:
        assert mapping['Date(UTC)'][0] == 'timestamp'

    if 'Fee Coin' in mapping:
        assert mapping['Fee Coin'][0] == 'fee_asset'


def test_no_double_assign_base_quote():
    mapper = ColumnMapper()
    mapper.load_or_fit()
    cols = ['Market', 'Amount', 'Total', 'Fee', 'Fee currency']
    mapping = mapper.predict_mapping(cols, threshold=0.6)
    inv = {v[0]: k for k, v in mapping.items()}
    assert not ('base_asset' in inv and 'quote_asset' in inv and inv['base_asset'] == inv['quote_asset'])
