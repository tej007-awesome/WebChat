import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_CONFIGURED = False


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def setup_logging(app_name: str = "webchat") -> None:
    """
    Configure Python logging for the whole app.

    Writes rotating log files under LOG_DIR (default: ./logs) and optionally logs to console.
    Environment variables:
      - LOG_DIR: directory for log files (default: logs)
      - LOG_LEVEL: DEBUG|INFO|WARNING|ERROR (default: INFO)
      - LOG_TO_CONSOLE: 1/0 (default: 1)
      - LOG_MAX_BYTES: rotate size in bytes (default: 10_000_000)
      - LOG_BACKUP_COUNT: number of rotated files (default: 5)
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    log_dir = Path(os.getenv("LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    log_to_console = _env_bool("LOG_TO_CONSOLE", True)
    max_bytes = int(os.getenv("LOG_MAX_BYTES", "10000000"))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    fmt = "%(asctime)s %(levelname)s %(name)s [pid=%(process)d] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    root = logging.getLogger()
    root.setLevel(level)

    # Replace existing handlers so logs don't end up duplicated (e.g., reloaders).
    for h in list(root.handlers):
        root.removeHandler(h)

    file_all = RotatingFileHandler(
        log_dir / f"{app_name}.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_all.setLevel(level)
    file_all.setFormatter(formatter)
    root.addHandler(file_all)

    file_err = RotatingFileHandler(
        log_dir / f"{app_name}.error.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_err.setLevel(logging.ERROR)
    file_err.setFormatter(formatter)
    root.addHandler(file_err)

    if log_to_console:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(formatter)
        root.addHandler(console)

    logging.captureWarnings(True)

    # Try to make uvicorn's loggers propagate into our handlers (and avoid duplicate handlers).
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(name)
        uv_logger.propagate = True
        for h in list(uv_logger.handlers):
            uv_logger.removeHandler(h)

    _CONFIGURED = True
