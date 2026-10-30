"""Скрипт анализа access.log файла
Формат лога:
%h - - %t "%r" %s %b "%{Referer}" "%{User-Agent}" %d
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Any, List

#регулярное выражение для парсинга строки лога
LOG_LINE_PATTERN = re.compile(
    r'^(?P<ip>\S+)\s+'                 # %h
    r'-\s+-\s+'                        # - -
    r'\[(?P<time>[^\]]+)\]\s+'         # %t
    r'"(?P<request>[^"]+)"\s+'        # "%r"
    r'(?P<status>\d+)\s+'             # %s
    r'(?P<bytes>\S+)\s+'              # %b
    r'"(?P<referer>[^"]*)"\s+'        # "%{Referer}"
    r'"(?P<user_agent>[^"]*)"\s+'     # "%{User-Agent}"
    r'(?P<duration_ms>\d+)$'          # %d
)

METHODS_TO_COUNT = {"GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"}


def parse_log_line(line: str):
    """
    Парсит одну строку лога. Возвращает словарь с полями или None, если строка не подходит.
    """
    match = LOG_LINE_PATTERN.match(line.strip())
    if not match:
        return None

    data = match.groupdict()
    # bytes может быть "-" вместо числа
    bytes_val = data["bytes"]
    data["bytes_int"] = int(bytes_val) if bytes_val.isdigit() else 0

    # duration_ms всегда число по ТЗ!!
    data["duration_ms_int"] = int(data["duration_ms"])

    # разбираем request на метод и URL
    req_parts = data["request"].split(" ", 2)
    if len(req_parts) >= 2:
        data["method"] = req_parts[0]
        data["url"] = req_parts[1]
    else:
        data["method"] = ""
        data["url"] = data["request"]

    return data


def analyze_file(path: Path) -> Dict[str, Any]:
    """
    Анализирует один лог-файл и возвращает статистику.
    """
    total_requests = 0
    method_counts = Counter()
    ip_counts = Counter()
    long_requests: List[Dict[str, Any]] = []  # топ долгих

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parsed = parse_log_line(line)
            if parsed is None:
                continue

            total_requests += 1
            ip_counts[parsed["ip"]] += 1

            method = parsed["method"]
            if method in METHODS_TO_COUNT:
                method_counts[method] += 1

            # для долгого хранения - храним нужные поля
            long_requests.append({
                "method": parsed["method"],
                "url": parsed["url"],
                "ip": parsed["ip"],
                "duration_ms": parsed["duration_ms_int"],
                "time": parsed["time"],
            })

    # топ 3 IP
    top_ips = ip_counts.most_common(3)

    # сортируем по длительности (по убыванию), берем топ 3
    long_requests_sorted = sorted(
        long_requests,
        key=lambda x: x["duration_ms"],
        reverse=True
    )[:3]

    stats = {
        "file": str(path),
        "total_requests": total_requests,
        "methods": {m: method_counts.get(m, 0) for m in METHODS_TO_COUNT},
        "top_ips": [
            {"ip": ip, "count": count} for ip, count in top_ips
        ],
        "top_long_requests": long_requests_sorted,
    }
    return stats


def save_stats_to_json(stats: Dict[str, Any], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def print_stats(stats: Dict[str, Any]):
    print(f"\n=== Статистика для файла: {stats['file']} ===")
    print(f"Общее количество запросов: {stats['total_requests']}")

    print("\nКоличество запросов по HTTP-методам:")
    for method in METHODS_TO_COUNT:
        count = stats["methods"].get(method, 0)
        print(f"{method} - {count}")

    print("\nТоп 3 IP-адреса по количеству запросов:")
    for i, item in enumerate(stats["top_ips"], start=1):
        print(f"{i}. IP: {item['ip']}, запросов: {item['count']}")

    print("\nТоп 3 самых долгих запроса:")
    if not stats["top_long_requests"]:
        print("(нет данных)")
    else:
        for i, req in enumerate(stats["top_long_requests"], start=1):
            print(
                f"{i}. Метод: {req['method']}, URL: {req['url']}, "
                f"IP: {req['ip']}, длительность: {req['duration_ms']} мс, "
                f"время: {req['time']}"
            )
    print("=" * 60)


def get_log_files(path_input: str) -> List[Path]:
    input_path = Path(path_input)
    files = []

    if input_path.is_file():
        if input_path.suffix.lower() == ".log":
            files.append(input_path)
        else:
            raise ValueError(f"Указан файл не с расширением .log: {input_path}")
    elif input_path.is_dir():
        # берем все .log файлы в директории
        files = sorted([f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() == ".log"])
        if not files:
            raise ValueError(f"В директории {input_path} не найдено файлов .log")
    else:
        raise ValueError(f"Путь не существует или не является файлом/директорией: {input_path}")

    return files


def build_output_path(log_path: Path, output_dir: Path) -> Path:
    """
    Строит путь к JSON-файлу статистики.
    Если входной файл: logs/access.log -> output/access_log.json
    """
    name_base = log_path.stem  # без расширения
    # заменяем точки и прочие символы на подчеркивания, чтобы имя было безопасным
    safe_name = re.sub(r"[^a-zA-Z0-9]", "_", name_base)
    return output_dir / f"{safe_name}.json"


def main():
    parser = argparse.ArgumentParser(
        description="Анализатор access.log: статистика по запросам, методам, IP и долгим запросам."
    )
    parser.add_argument(
        "path",
        help="Путь к конкретному .log файлу или к директории с логами."
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Директория для сохранения JSON-файлов со статистикой (по умолчанию: output)."
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    log_files = get_log_files(args.path)

    for log_path in log_files:
        stats = analyze_file(log_path)
        out_path = build_output_path(log_path, output_dir)
        save_stats_to_json(stats, out_path)
        print_stats(stats)
        print(f"Статистика сохранена в: {out_path.resolve()}")


if __name__ == "__main__":
    main()
