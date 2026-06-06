import logging
import sys
import argparse
from pathlib import Path

from src.service.reports import show_index, show_history, show_duplicates
from src.service.scaner import scan
from src.database.db import connect
from src.config import DB_PATH
from src.logs_service.logs import setup_logging

def build_parser():
    parser = argparse.ArgumentParser(prog="indexer", description="Индексатор папок (SQLite).")
    parser.add_argument("--db", default=str(DB_PATH), help="файл базы SQLite")
    parser.add_argument("-v", "--verbose", action="store_true", help="INFO лог ")
    parser.add_argument("-vv", "--vverbose", action="store_true", help="DEBUG лог")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("scan", help="просканировать папку")
    p.add_argument("path")
    p.add_argument("--ext", help="расширения через запятую: .py,.txt")
    p.add_argument("--name", help="подстрока в имени файла")

    p = sub.add_parser("list", help="показать индекс")
    p.add_argument("path")

    p = sub.add_parser("history", help="история запусков")
    p.add_argument("path")

    p = sub.add_parser("duplicates", help="найти дубликаты файлов")
    p.add_argument("path")
    return parser

def main(argv = None):
    args = build_parser().parse_args(argv)
    setup_logging(args.verbose, args.vverbose)
    with connect(Path(args.db)) as conn:
        try:
            if args.command == "scan":
                scan(
                    conn=conn,
                    path=args.path,
                    ext=args.ext,
                    name=args.name
                )
            elif args.command == "list":
                show_index(
                    conn=conn,
                    path=args.path,
                )
            elif args.command == "history":
                show_history(
                    conn=conn,
                    path=args.path,
                )
            elif args.command == "duplicates":
                show_duplicates(
                    conn=conn,
                    path=args.path,
                )
        except Exception:
            logging.exception("Ошибка запуска")
            return 1

if __name__ == '__main__':
    sys.exit(main())