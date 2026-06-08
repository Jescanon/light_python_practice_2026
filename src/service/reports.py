import logging
from pathlib import Path
import sqlite3

from src.service.scaner import _human_size

logger = logging.getLogger(__name__)

def show_index(conn: sqlite3.Connection, path: str, limit: int = 50):
    root = str(Path(path).resolve())
    logger.debug("Зашел в index")
    rows = conn.execute(
        "SELECT rel, size, ext FROM files WHERE root = ? ORDER BY rel", (root,)
    ).fetchall()

    if not rows:
        print("Пусто. Сначала выполните scan.")
        return
    for row in rows[:limit]:
        print(f"{_human_size(row['size'])}  {row['rel']}")
    if len(rows) > limit:
        print(f"Оставшиеся файлы: {len(rows) - limit}")
    print(f"Всего файлов: {len(rows)}")
    logger.info(f"Прошел Index, все оккей")

def show_history(conn: sqlite3.Connection, path: str, limit: int = 50):
    root = str(Path(path).resolve())
    logger.debug("Зашел в history")

    rows = conn.execute("SELECT * FROM scans WHERE root = ? ORDER BY id DESC LIMIT ?", (root, limit)).fetchall()
    if not rows:
        print("Пусто. Сначала выполните scan.")
        return

    for row in rows:
        logger.debug("Прохожусь по всему: %s", row)
        print(f"{row['id']} {row['at']} найдено={row['found']}, добавлено={row['added']}, обновлено={row['updated']}, "
              f"удалено={row['removed']} {row['root']}")

def show_duplicates(conn: sqlite3.Connection, path: str):
    root = str(Path(path).resolve())
    logger.debug("Зашел в duplicates")

    rows = conn.execute(
        """
        SELECT hash, rel, size FROM files
        WHERE root = ? AND hash IN 
        (
        SELECT hash FROM files 
        WHERE root = ?
        GROUP BY hash 
        HAVING COUNT(*) > 1
        )
        ORDER BY hash, rel
        """,
        (root, root),
    ).fetchall()

    logger.debug("Нашедший hash %s", rows)

    if not rows:
        print("Не найдено дубликатов, или вы еще не сканировали файл python -m src.main scan ..")
        return

    duplicates = {}
    for row in rows:
        duplicates.setdefault(row["hash"], []).append(row)

    logger.info("Дубликаты в %s групп %d", root, len(duplicates))

    for duplicat in duplicates.values():
        print(f"Дубликаты: {', '.join([d['rel'] for d in duplicat])}")

def show_checks(conn: sqlite3.Connection, path: str, limit: int = 50):
    root = str(Path(path).resolve())
    logger.info("Зашел в show_checks")
    rows = conn.execute(
        "SELECT * FROM checks WHERE source=? ORDER BY id DESC LIMIT ?", (root, limit)
    ).fetchall()
    if not rows:
        print("Проверок ещё не было выполните python -m src.main compare ...")
        return

    for row in rows:
        print(f"{row['id']} {row['at']} нет {row['missing']}, изменено {row['changed']}, "
              f"лишних {row['extra']}  бэкап {row['backup']}")

    logger.info("Выдал результат show_checks")