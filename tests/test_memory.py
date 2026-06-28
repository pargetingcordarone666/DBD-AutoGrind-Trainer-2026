import pytest
from src.memory import MemoryManager

def test_pattern_parse():
    pattern = "48 8B 05 ? ? ? ? 48 8B 88"
    bytes_list, mask = MemoryManager._parse_pattern(pattern)
    assert len(bytes_list) == 8
    assert bytes_list[0] == 0x48
    assert mask[0] == True
    assert mask[3] == False

def test_pattern_scan_mocked(monkeypatch):
    # Mock ReadProcessMemory to return a prepared buffer
    import ctypes
    import numpy as np
    def mock_read(handle, base, buffer, size, nread):
        # Inject pattern at offset 0x100
        data = np.zeros(size, dtype=np.uint8)
        if size > 0x108:
            pattern_bytes = [0x48, 0x8B, 0x05, 0x00, 0x00, 0x00, 0x00, 0x48, 0x8B, 0x88]
            data[0x100:0x100+len(pattern_bytes)] = pattern_bytes
        ctypes.memmove(buffer, data.ctypes.data, size)
        return True

    monkeypatch.setattr(ctypes.windll.kernel32, "ReadProcessMemory", mock_read)
    mgr = MemoryManager()
    mgr.pm = type("obj", (object,), {"process_handle": 0})()  # dummy handle
    addr = mgr.pattern_scan("48 8B 05 ? ? ? ? 48 8B 88", 0x1000, 0x5000)
    assert addr == 0x1100
