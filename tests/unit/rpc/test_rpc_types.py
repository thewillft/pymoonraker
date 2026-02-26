"""Tests for JSON-RPC type serialisation."""

from pymoonraker.rpc.types import RpcError, RpcNotification, RpcRequest, RpcResponse


class TestRpcRequest:
    def test_to_dict_minimal(self):
        req = RpcRequest(method="printer.info", id=1)
        d = req.to_dict()
        assert d == {"jsonrpc": "2.0", "method": "printer.info", "id": 1}

    def test_to_dict_with_params(self):
        req = RpcRequest(method="printer.gcode.script", params={"script": "G28"}, id=5)
        d = req.to_dict()
        assert d["params"] == {"script": "G28"}
        assert d["id"] == 5

    def test_to_dict_notification_no_id(self):
        req = RpcRequest(method="some.method")
        d = req.to_dict()
        assert "id" not in d

    def test_to_dict_no_params_omitted(self):
        req = RpcRequest(method="printer.info", id=1)
        d = req.to_dict()
        assert "params" not in d


class TestRpcResponse:
    def test_is_error_false(self):
        resp = RpcResponse(id=1, result={"state": "ready"})
        assert not resp.is_error

    def test_is_error_true(self):
        resp = RpcResponse(id=1, error=RpcError(code=-32600, message="Invalid Request"))
        assert resp.is_error


class TestRpcNotification:
    def test_defaults(self):
        n = RpcNotification(method="notify_klippy_ready")
        assert n.method == "notify_klippy_ready"
        assert n.params == []
