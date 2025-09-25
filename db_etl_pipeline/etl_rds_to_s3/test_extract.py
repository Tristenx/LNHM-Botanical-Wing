"""Tests for extract.py"""
import pyodbc
from extract import get_connection, query_database, get_data


def test_get_connection_builds_correct_conn_string(monkeypatch):
    """Tests that the get_connection function builds the correct connection string."""
    env = {
        "DB_DRIVER": "FakeDriver",
        "DB_HOST": "fakehost",
        "DB_PORT": "1234",
        "DB_NAME": "fakedb",
        "DB_USERNAME": "user",
        "DB_PASSWORD": "pass",
    }
    # Use monkeypatch.setenv() to directly set environment variables for the test
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    called_args = {}

    def fake_connect(conn_str):
        called_args["conn_str"] = conn_str
        return "FAKE_CONNECTION"

    monkeypatch.setattr(pyodbc, "connect", fake_connect)

    conn = get_connection()
    assert conn == "FAKE_CONNECTION"
    for v in env.values():
        assert v in called_args["conn_str"]


def test_query_database_returns_cursor_results():
    """Tests that the query_database function returns the correct results from the cursor."""
    executed = {}
    fake_result = [("row1",), ("row2",)]

    class FakeCursor:
        """A fake cursor for testing purposes."""
        def __enter__(self):
            """Returns the cursor itself for use in a `with` statement."""
            return self

        def __exit__(self, *a):
            """Exists the `with` statement context."""
            return False

        def execute(self, sql):
            """Mocks the execute method."""
            executed["sql"] = sql

        def fetchall(self):
            """Mocks the fetchall method."""
            return fake_result

    class FakeConn:
        """A fake connection for testing purposes."""
        def cursor(self):
            """Mocks the cursor method."""
            return FakeCursor()

    sql = "SELECT 1"
    result = query_database(FakeConn(), sql)
    assert result == fake_result
    assert executed["sql"] == sql


def test_get_data_calls_query_database_for_each_table(monkeypatch):
    """Tests that get_data queries the database for each expected table."""
    called_sql = []

    # The lambda function should return a list containing the SQL string itself
    def fake_query(_conn, sql):
        called_sql.append(sql)
        return [sql]

    monkeypatch.setattr("extract.query_database", fake_query)

    fake_conn = object()
    data = get_data(fake_conn)

    expected_keys = {"country", "city", "plant", "recording", "botanist"}
    assert set(data.keys()) == expected_keys
    for key in expected_keys:
        assert isinstance(data[key], list)
        assert isinstance(data[key][0], str)
        assert data[key][0].strip().lower().startswith("select * from alpha.")
    assert len(called_sql) == len(expected_keys)
