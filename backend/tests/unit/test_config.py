import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_requires_real_secret():
    with pytest.raises(ValidationError):
        Settings(environment="production")


def test_production_rejects_debug():
    with pytest.raises(ValidationError):
        Settings(environment="production", debug=True, secret_key="x" * 40)


def test_valid_production_settings():
    s = Settings(environment="production", secret_key="x" * 40)
    assert s.is_production
