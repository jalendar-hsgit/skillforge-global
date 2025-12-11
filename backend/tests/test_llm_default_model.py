from app.core.config import settings


def test_openai_model_default_is_raptor():
    """Ensure the default OPENAI_MODEL is set to raptor-mini (Preview) so Raptor mini is used by default."""
    assert settings.OPENAI_MODEL == "raptor-mini"
