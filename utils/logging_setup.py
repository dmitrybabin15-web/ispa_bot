import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


def setup_logging(
    *,
    logs_dir: str = "logs",
    level: int = logging.INFO,
    console_level: int | None = None,
    keep_days: int = 14,
) -> None:
    """
    Unified logging for environments without systemd/journald (e.g. shared hosting).
    - Always logs to console (stdout) so nohup can capture it.
    - Always logs to rotating files in logs_dir.
    """
    os.makedirs(logs_dir, exist_ok=True)

    # Ensure log files exist (some hosting FS setups behave oddly with handler creation).
    all_log_path = os.path.join(logs_dir, "app.log")
    err_log_path = os.path.join(logs_dir, "error.log")
    for p in (all_log_path, err_log_path):
        try:
            with open(p, "a", encoding="utf-8"):
                pass
        except OSError:
            # If file logging can't be initialized, we'll still have stdout/stderr logs.
            pass

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers if setup_logging is called more than once.
    if getattr(root, "_ispa_logging_configured", False):
        return

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    ch = logging.StreamHandler()
    ch.setLevel(console_level if console_level is not None else level)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    try:
        fh_all = TimedRotatingFileHandler(all_log_path, when="midnight", backupCount=keep_days, encoding="utf-8")
        fh_all.setLevel(level)
        fh_all.setFormatter(fmt)
        root.addHandler(fh_all)
    except Exception as e:
        print(f"[logging_setup] Could not init file handler for {all_log_path}: {e!r}", file=sys.stderr)

    try:
        fh_err = TimedRotatingFileHandler(err_log_path, when="midnight", backupCount=keep_days, encoding="utf-8")
        fh_err.setLevel(logging.WARNING)
        fh_err.setFormatter(fmt)
        root.addHandler(fh_err)
    except Exception as e:
        print(f"[logging_setup] Could not init file handler for {err_log_path}: {e!r}", file=sys.stderr)

    root._ispa_logging_configured = True

