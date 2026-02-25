"""Tests for exception hierarchy."""

from pymoonraker.exceptions import (
    MoonrakerAPIError,
    MoonrakerAuthError,
    MoonrakerConnectionError,
    MoonrakerError,
    MoonrakerRPCError,
    MoonrakerTimeoutError,
)


class TestExceptionHierarchy:
    def test_base_class(self):
        assert issubclass(MoonrakerConnectionError, MoonrakerError)
        assert issubclass(MoonrakerTimeoutError, MoonrakerError)
        assert issubclass(MoonrakerAuthError, MoonrakerError)
        assert issubclass(MoonrakerRPCError, MoonrakerError)
        assert issubclass(MoonrakerAPIError, MoonrakerError)

    def test_rpc_error_attrs(self):
        err = MoonrakerRPCError(code=-32600, message="Invalid Request", data={"detail": "x"})
        assert err.code == -32600
        assert err.message == "Invalid Request"
        assert err.data == {"detail": "x"}
        assert "-32600" in str(err)

    def test_api_error_attrs(self):
        err = MoonrakerAPIError(status_code=404, message="Not Found")
        assert err.status_code == 404
        assert "404" in str(err)
