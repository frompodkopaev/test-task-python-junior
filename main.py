import argparse
import json
from collections import defaultdict
from typing import Dict, List, Tuple


def parse_log_file(file_path: str) -> List[Dict]:
    """Parse log file and return list of log entries."""
    logs = []
    with open(file_path, 'r') as log_file:
        for line in log_file:
            try:
                log_entry = json.loads(line.strip())
                logs.append(log_entry)
            except json.JSONDecodeError:
                continue
    return logs


def process_logs(logs: List[Dict]) -> Dict[str, Tuple[int, float]]:
    """Process logs and calculate request count and average response time per endpoint."""
    endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0.0})

    for log in logs:
        url = log.get('url', '')
        if not url:
            continue

        # Extract endpoint path
        parts = url.split('/')
        if len(parts) >= 3:
            endpoint = f"/{parts[1]}/{parts[2]}/..."
        else:
            endpoint = url

        response_time = log.get('response_time', 0.0)
        endpoint_stats[endpoint]['count'] += 1
        endpoint_stats[endpoint]['total_time'] += response_time

    # Calculate averages and prepare result
    result = {}
    for endpoint, stats in endpoint_stats.items():
        avg_time = stats['total_time'] / stats['count']
        result[endpoint] = (stats['count'], avg_time)

    return result


def generate_report(data: Dict[str, Tuple[int, float]]) -> str:
    """Generate formatted report from processed data."""
    # Prepare header
    header = f"{'  '}  {'handler':<25}  {'total':>7}  {'avg_response_time':>19}"
    separator = f"{'':->2}  {'':-<25}  {'':->7}  {'':->19}"

    # Prepare rows
    rows = []
    for index, (endpoint, (count, avg_time)) in enumerate(sorted(data.items()
            , key=lambda item: item[1][0], reverse=True)):
        rows.append(f"{str(index):>2}  {endpoint:<25}  {count:>7}  {avg_time:>19.3f}")

    # Combine everything
    return "\n".join([header, separator] + rows)


def main():
    """Main function to handle script execution."""
    parser = argparse.ArgumentParser(description='Process log files and generate reports.')
    parser.add_argument('--file', required=True, nargs='+', help='Log file path(s)')
    parser.add_argument('--report', choices=['average'], default='average',
                        help='Type of report to generate')

    args = parser.parse_args()

    # Process all files
    combined_stats = defaultdict(lambda: {'count': 0, 'total_time': 0.0})

    for file_path in args.file:
        logs = parse_log_file(file_path)
        file_stats = process_logs(logs)

        for endpoint, (count, avg_time) in file_stats.items():
            combined_stats[endpoint]['count'] += count
            combined_stats[endpoint]['total_time'] += avg_time * count

    # Calculate final averages
    final_result = {}
    for endpoint, stats in combined_stats.items():
        final_avg = stats['total_time'] / stats['count']
        final_result[endpoint] = (stats['count'], final_avg)

    # Generate and print report
    report = generate_report(final_result)
    print(report)


if __name__ == '__main__':
    main()
