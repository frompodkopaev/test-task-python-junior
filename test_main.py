import pytest
import json
import os
from io import StringIO
from unittest.mock import patch, mock_open
import argparse

from main import parse_log_file, process_logs, generate_report, main


@pytest.fixture
def sample_logs():
    return [
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200,
         "url": "/api/context/123", "request_method": "GET", "response_time": 0.024},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200,
         "url": "/api/context/456", "request_method": "GET", "response_time": 0.02},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200,
         "url": "/api/homeworks/789", "request_method": "GET", "response_time": 0.06},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200,
         "url": "/api/homeworks/012", "request_method": "GET", "response_time": 0.04},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200,
         "url": "/invalid", "request_method": "GET", "response_time": 0.01},
    ]


@pytest.fixture
def sample_log_file(sample_logs):
    return "".join(json.dumps(log) + "\n" for log in sample_logs)


@pytest.fixture
def temp_log_file(sample_log_file):
    temp_path = "temp_test.log"
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(sample_log_file)
    yield temp_path
    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_parse_log_file_with_real_file(temp_log_file):
    result = parse_log_file(temp_log_file)

    assert len(result) == 5
    assert result[0]['url'] == "/api/context/123"
    assert result[1]['response_time'] == 0.02
    assert result[-1]['url'] == "/invalid"


def test_process_logs(sample_logs):
    result = process_logs(sample_logs)

    assert len(result) == 3  # /api/context, /api/homeworks, /invalid
    assert result['/api/context'] == (2, 0.022)  # count, avg_time
    assert result['/api/homeworks'] == (2, 0.05)
    assert result['/invalid'] == (1, 0.01)


def test_generate_report():
    test_data = {
        '/api/context': (5, 0.03),
        '/api/homeworks': (10, 0.15),
        '/invalid': (1, 0.01)
    }
    report = generate_report(test_data)

    assert all(
        endpoint in report for endpoint in ['/api/context', '/api/homeworks', '/invalid']
    )
    assert "5" in report  # количество запросов для context
    assert "10" in report  # количество запросов для homeworks
    assert "30.00" in report  # 0.03 * 1000
    assert "150.00" in report  # 0.15 * 1000


@patch('builtins.print')
@patch('argparse.ArgumentParser.parse_args')
def test_main_integration(mock_args, mock_print, sample_log_file):
    # Настраиваем моки
    mock_args.return_value = argparse.Namespace(
        file=['dummy.log'],
        report='average'
    )

    # Подменяем открытие файла
    with patch('builtins.open', mock_open(read_data=sample_log_file)):
        main()

    # Проверяем что отчет был выведен
    assert mock_print.called
    report = mock_print.call_args[0][0]

    # Проверяем содержание отчета
    assert '/api/context' in report
    assert '/api/homeworks' in report
    assert 'Avg Time (ms)' in report
