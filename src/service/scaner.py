import logging

def scan(conn, path, ext=None, name=None):
    print(conn, path, ext, name)
    logging.info("Все хороше, запустилось!")
