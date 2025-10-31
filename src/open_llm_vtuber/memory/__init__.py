"""
记忆系统模块
提供可选的记忆功能，不影响现有系统
"""

# 可选导入，如果失败则禁用记忆功能
try:
    from .memory_compressor import MemoryCompressor, MemoryItem, MemoryType
    from .smart_memory_manager import SmartMemoryManager
    MEMORY_AVAILABLE = True
except ImportError as e:
    print(f"记忆系统不可用: {e}")
    MEMORY_AVAILABLE = False

__all__ = ['MEMORY_AVAILABLE']

if MEMORY_AVAILABLE:
    __all__.extend(['MemoryCompressor', 'MemoryItem', 'MemoryType', 'SmartMemoryManager'])
