import sqlite3
import logging
from datetime import datetime
from pathlib import Path

from src.service.scaner import index_folder

def comparing(conn: sqlite3.Connection, source: str, backup: str):
    src_root = str(Path(source).resolve())
    bak_root = str(Path(backup).resolve())

    index_folder(conn, src_root), index_folder(conn, bak_root)

    src = {rel: hash for rel, hash in conn.execute("SELECT rel, hash FROM files WHERE root=?",
                                                   (src_root, )).fetchall()}
    bak = {rel: hash for rel, hash in conn.execute("SELECT rel, hash FROM files WHERE root=?",
                                                   (bak_root, )).fetchall()}

    logging.debug("SRC: %s", src)
    logging.debug("BACK: %s", bak)

    missing = sorted(src.keys() - bak.keys())
    extra   = sorted(bak.keys() - src.keys())
    changed = sorted(rel for rel in (src.keys() & bak.keys()) if src[rel] != bak[rel])

    logging.info("Прошли выборку, все гуди")

    conn.execute(
        "INSERT INTO checks (source, backup, at, missing, changed, extra) VALUES (?,?,?,?,?,?)",
        (src_root, bak_root, datetime.now().isoformat(timespec="seconds"), len(missing), len(changed), len(extra)),
    )

    if not (missing or extra or changed):
        print("Все присутствует в бекапе!")
        return

    if missing:
        print(f"Отсутствует в бекапе файлы {len(missing)}:")
        for rel in missing:
            print(f"{rel}")

    if extra:
        print(f"\nЛишние в бекапе {len(extra)}:")
        for rel in extra:
            print(f"{rel}")

    if changed:
        print(f"\nИзмененные в бекапе {len(changed)}:")
        for rel in changed:
            print(f"{rel}")






