"""
common enums used in multiple apps
"""

from enum import Enum


class AppName(str, Enum):
    User = "User"
    Courses = "Courses"


class LoggingLevel(str, Enum):
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARN = "WARN"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"
