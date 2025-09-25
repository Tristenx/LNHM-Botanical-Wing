import pytest
import extract


def test_get_connection_builds_correct_conn_string(monkeypatch):
    env = {
        "DB_DRIVER": "FakeDriver",
        "DB_HOST": "fakehost",
        "DB_PORT": "1234",
        "DB_NAME": "fakedb",
        "DB_USERNAME": "user",
        "DB_PASSWORD": "pass",
    }
    monkeypatch.setattr(extract, "environ", env)

    called_args = {}
    def fake_connect(conn_str):
        called_args["conn_str"] = conn_str
        return "FAKE_CONNECTION"
    monkeypatch.setattr(extract.pyodbc, "connect", fake_connect)

    conn = extract.get_connection()
    assert conn == "FAKE_CONNECTION"
    for v in env.values():
        assert v in called_args["conn_str"]


def test_query_database_returns_cursor_results():
    executed = {}
    fake_result = [("row1",), ("row2",)]

    class FakeCursor:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def execute(self, sql): executed["sql"] = sql
        def fetchall(self): return fake_result

    class FakeConn:
        def cursor(self): return FakeCursor()

    sql = "SELECT 1"
    result = extract.query_database(FakeConn(), sql)
    assert result == fake_result
    assert executed["sql"] == sql


def test_get_data_calls_query_database_for_each_table(monkeypatch):
    called_sql = []

    def fake_query(conn, sql):
        called_sql.append(sql)
        return [sql]  # return the sql string itself

    monkeypatch.setattr(extract, "query_database", fake_query)

    fake_conn = object()
    data = extract.get_data(fake_conn)

    expected_keys = {"country", "city", "plant", "recording", "botanist"}
    assert set(data.keys()) == expected_keys
    # Each stored value should be the exact SQL string we passed in
    for key in expected_keys:
        assert isinstance(data[key], list)
        assert isinstance(data[key][0], str)
        assert data[key][0].strip().lower().startswith("select * from alpha.")
    # Ensure we issued one query per key
    assert len(called_sql) == len(expected_keys)
