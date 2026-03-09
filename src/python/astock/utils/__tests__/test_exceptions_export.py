from astock.utils import AlertError


def test_alert_error_is_exported() -> None:
    assert issubclass(AlertError, Exception)
