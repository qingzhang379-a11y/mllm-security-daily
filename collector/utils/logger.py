"""
Logging utility for the collector.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(name: str = "mllm_collector", level: str = "INFO",
                 log_file: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_fmt = logging.Formatter(
            "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "mllm_collector") -> logging.Logger:
    return logging.getLogger(name)
