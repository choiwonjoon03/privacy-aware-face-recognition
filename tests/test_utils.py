# tests/test_utils.py
import sys, os
sys.path.insert(0, os.getcwd())  # ensure repo root is importable

from src.utils.filename_cleaner import clean_filename
from src.utils.bucketer import bucket_from_p

def test_clean_filename_basic():
    got = clean_filename("kpopdemonhunters_v5_600_ba41dfa26a114c2f9c3e123456789abc.jpg")
    assert got == "kpopdemonhunters_v5_600.jpg"

def test_clean_filename_hash_tail():
    assert clean_filename("semi_ghibli_123abc.png") == "semi_ghibli.png"

def test_bucket_boundaries():
    assert bucket_from_p(0.0) == "Safe"
    assert bucket_from_p(49.9) == "Safe"
    assert bucket_from_p(50.0) == "Buffer"
    assert bucket_from_p(69.9) == "Buffer"
    assert bucket_from_p(70.0) == "Warning"
    assert bucket_from_p(84.9) == "Warning"
    assert bucket_from_p(85.0) == "High-Risk"
