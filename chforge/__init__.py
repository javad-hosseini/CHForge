"""
CHForge - ClickHouse Performance Benchmark & Resource Management Framework
"""

__version__ = "0.1.0"
__author__ = "Javad Hosseini"

from .system import get_system_info, print_system_info

__all__ = [
    "get_system_info",
    "print_system_info",
]