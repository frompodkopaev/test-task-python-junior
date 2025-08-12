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
    """Фикстура для создания временного файла с логами"""
    temp_path = "temp_test_log.log"
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(sample_log_file)
    yield temp_path
    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_parse_log_file_with_real_file(temp_log_file):
    """Тест чтения логов из реального файла"""
    result = parse_log_file(temp_log_file)

    assert len(result) == 5
    assert result[0]['url'] == "/api/context/123"
    assert result[1]['response_time'] == 0.02
    assert result[-1]['url'] == "/invalid"


def test_parse_log_file_with_mock(sample_logs):
    """Тест чтения логов с использованием mock"""
    log_data = "".join(json.dumps(log) + "\n" for log in sample_logs)
    with patch('builtins.open', mock_open(read_data=log_data)):
        result = parse_log_file("dummy_path.log")

    assert len(result) == 5
    assert result[0]['request_method'] == "GET"
    assert result[2]['url'].startswith("/api/homeworks")


def test_process_logs(sample_logs):
    """Тест обработки логов и расчета статистики"""
    result = process_logs(sample_logs)

    assert len(result) == 3  # /api/context, /api/homeworks, /invalid
    assert result['/api/context'] == (2, 0.022)  # count, avg_time
    assert result['/api/homeworks'] == (2, 0.05)
    assert result['/invalid'] == (1, 0.01)


def test_generate_report():
    """Тест генерации отчета"""
    test_data = {
        '/api/context': (5, 0.03),
        '/api/homeworks': (10, 0.15),
        '/invalid': (1, 0.01)
    }
    report = generate_report(test_data)

    # Проверяем наличие всех ожидаемых данных в отчете
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
    """Интеграционный тест main() с моками"""
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


def test_empty_log_file():
    """Тест обработки пустого файла"""
    temp_path = "empty_test_log.log"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write("")

        result = parse_log_file(temp_path)
        assert len(result) == 0
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_invalid_json_log_file():
    """Тест обработки файла с некорректным JSON"""
    temp_path = "invalid_test_log.log"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write("invalid json\n")

        result = parse_log_file(temp_path)
        assert len(result) == 0
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_partial_json_log_file(sample_logs):
    """Тест обработки файла с частично некорректным JSON"""
    temp_path = "partial_test_log.log"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(sample_logs[0]) + "\n")
            f.write("invalid json\n")
            f.write(json.dumps(sample_logs[1]) + "\n")

        result = parse_log_file(temp_path)
        assert len(result) == 2  # только 2 валидные записи
        assert result[0]['url'] == "/api/context/123"
        assert result[1]['url'] == "/api/context/456"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
