import pytest
from main import parse_log_file, process_logs, generate_report, main

# Test data
SAMPLE_LOGS = [
    '{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET",'
    ' "response_time": 0.02, "http_user_agent": "..."}',
    '{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/homeworks/...", "request_method": "GET",'
    ' "response_time": 0.032, "http_user_agent": "..."}',
    '{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET",'
    ' "response_time": 0.024, "http_user_agent": "..."}',
    '{"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/homeworks/...", "request_method": "GET",'
    ' "response_time": 0.06, "http_user_agent": "..."}',
    'not a json string'
]

EXPECTED_PARSED_LOGS = [
    {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET",
     "response_time": 0.02, "http_user_agent": "..."},
    {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/homeworks/...", "request_method": "GET",
     "response_time": 0.032, "http_user_agent": "..."},
    {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET",
     "response_time": 0.024, "http_user_agent": "..."},
    {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/homeworks/...", "request_method": "GET",
     "response_time": 0.06, "http_user_agent": "..."},
]

EXPECTED_PROCESSED_STATS = {
    "/api/context/...": (2, 0.022),
    "/api/homeworks/...": (2, 0.046),
}

EXPECTED_REPORT = """    handler                      total    avg_response_time
--  -------------------------  -------  -------------------
 0  /api/context/...                 2                0.022
 1  /api/homeworks/...               2                0.046"""


@pytest.fixture
def sample_log_file(tmp_path):
    file_path = tmp_path / "test.log"
    with open(file_path, 'w') as f:
        f.write("\n".join(SAMPLE_LOGS))
    return file_path


def test_parse_log_file(sample_log_file):
    logs = parse_log_file(sample_log_file)
    assert logs == EXPECTED_PARSED_LOGS


def test_parse_log_file_nonexistent():
    non_existent_file = "nonexistent.log"
    with pytest.raises(FileNotFoundError):
        parse_log_file(non_existent_file)


def test_process_logs():
    processed = process_logs(EXPECTED_PARSED_LOGS)

    assert processed == EXPECTED_PROCESSED_STATS


def test_generate_report():
    report = generate_report(EXPECTED_PROCESSED_STATS)
    assert report == EXPECTED_REPORT


def test_process_logs_with_short_url():
    logs = [
        {"url": "/short", "response_time": 0.1},
    ]
    processed = process_logs(logs)
    assert len(processed) == 1
    assert "/short" in processed


def test_main(monkeypatch, capsys, tmp_path):
    # Create test log files
    file1 = tmp_path / "log1.log"
    file2 = tmp_path / "log2.log"

    with open(file1, 'w') as f:
        f.write("\n".join(SAMPLE_LOGS[:2]))

    with open(file2, 'w') as f:
        f.write("\n".join(SAMPLE_LOGS[2:4]))

    # Mock command line arguments
    monkeypatch.setattr(
        'sys.argv',
        ['script_name', '--file', str(file1), str(file2)]
    )

    main()

    captured = capsys.readouterr()
    report = captured.out.rstrip()
    assert report == EXPECTED_REPORT