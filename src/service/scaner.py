import logging
from pathlib import Path
import sqlite3
from datetime import datetime

from src.config import SKIP_FILES

def show_index(conn: sqlite3.Connection, path: str, limit=50):
    root = str(Path(path).resolve())
    logging.debug("Зашел в index")
    rows = conn.execute(
        "SELECT rel, size, ext FROM files WHERE root = ? ORDER BY rel", (root,)
    ).fetchall()

    if not rows:
        print("Пусто. Сначала выполните scan.")
        return
    for row in rows[:limit]:
        print(f"{row['size']}  {row['rel']}")
    if len(rows) > limit:
        print(f"Оставшиеся файлы: {len(rows) - limit}")
    print(f"Всего файлов: {len(rows)}")
    logging.info(f"Прошел Index, все оккей")

def show_history(conn: sqlite3.Connection, path: str, limit=50):
    root = str(Path(path).resolve())
    logging.debug("Зашел в history")

    rows = conn.execute("SELECT * FROM scans WHERE root = ? ORDER BY id DESC LIMIT ?", (root, limit)).fetchall()
    if not rows:
        print("Пусто. Сначала выполните scan.")
        return

    for row in rows:
        logging.debug("Прохожусь по всему: %s", row)
        print(f"{row['id']} {row['at']} найдено={row['found']}, добавлено={row['added']}, обновлено={row['updated']}, "
              f"удалено={row['removed']} {row['root']}")

def _parse_ext(ext: str):
    if not ext:
        return None

    result = set()
    for piece in ext.split(","):
        piece = piece.strip().lower()
        if piece:
            result.add(piece if piece.startswith(".") else "." + piece)

    return result or None


def walk(folder: Path, root: Path, rows: list):
    for entry in folder.iterdir():
        if entry.is_dir():
            if entry.name in SKIP_FILES:
                continue
            walk(entry, root, rows)
        elif entry.is_file():
            st = entry.stat()
            logging.debug("Нашёл файл %s, размером %s", entry.relative_to(root), st.st_size)
            rows.append(
                (
                    str(root),
                    str(entry.relative_to(root)),
                    entry.name,
                    st.st_size,
                    st.st_mtime,
                    entry.suffix
                )
            )

def scan(conn: sqlite3.Connection, path: str, ext: str | None=None, name: str | None=None):
    path = Path(path).resolve()
    exts = _parse_ext(ext)
    rows = []
    walk(path, path, rows)
    update = added = deleted = 0

    selected = []
    for row in rows:
        root, rel, f_name, size, mtime, suffix = row
        if exts and suffix.lower() not in exts:
            continue
        if name and name.lower() not in f_name.lower():
            continue

        selected.append(row)

        old_file = conn.execute(
            """SELECT size, mtime FROM files WHERE root = ? AND rel = ?""", (root, rel)
        ).fetchall()

        if old_file:
            conn.execute(
                """REPLACE INTO files (root, rel, size, mtime, ext) 
                   VALUES (?, ?, ?, ?, ?)""",
                (root, rel, size, mtime ,suffix),
            )
            update += 1
        else:
            conn.execute(
                """INSERT INTO files (root, rel, size, mtime, ext) 
                   VALUES (?, ?, ?, ?, ?)""",
                (root, rel, size, mtime ,suffix),
            )
            added += 1

        print(rel, size)

    seen = {row[1] for row in rows}
    old = {r["rel"] for r in conn.execute("SELECT rel FROM files WHERE root=?", (str(path),))}
    logging.info("old - seen: %s", old - seen)
    for rel in old - seen:
        conn.execute("DELETE FROM files WHERE root=? AND rel=?", (str(path), rel))
        deleted += 1

    conn.execute(
        "INSERT INTO scans (root, at, found, added, updated, removed) VALUES (?,?,?,?,?,?)",
        (str(path), datetime.now().isoformat(timespec="seconds"), len(rows), added, update, deleted),
    )

    logging.info("Готово, файлов: %s, Изменено файлов: %s, Добавленно файлов: %s, удалено: %s", len(selected), update, added, deleted)
    return len(selected)
