import os
import socket
import psutil
from typing import List, Tuple, Optional, Dict
from loguru import logger as log

class PortManager:
    """Port allocation, availability checks, process cleanup, and usage reporting."""

    def __repr__(self):
        return "[TooManyPorts]"

    @staticmethod
    def is_available(port: int) -> bool:
        """Return True if the port can be bound (i.e., is free)."""
        try:
            with socket.socket() as sock:
                sock.bind(("", port))
            return True
        except OSError:
            return False

    @classmethod
    def find(cls, start: int = 3000, count: int = 1) -> List[int]:
        """Find `count` available ports, searching from `start` upward."""
        out: List[int] = []
        p = start
        while len(out) < count and p < 65535:
            if cls.is_available(p):
                out.append(p)
            p += 1
        if len(out) < count:
            raise RuntimeError(f"{cls}: could not find {count} ports from {start}")
        return out

    @staticmethod
    def kill(port: int, force: bool = True) -> bool:
        """Kill the process listening on `port`. Skip if it's the current process."""
        me = os.getpid()
        found = False
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                found = True
                pid = conn.pid
                if pid == me:
                    log.warning(f"{PortManager}: skipping kill of current process (pid={me}) on port {port}")
                    continue
                proc = psutil.Process(pid)
                try:
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                except Exception as e:
                    log.error(f"{PortManager}: failed killing pid {pid}: {e}")
                    return False
                else:
                    log.success(f"{PortManager}: killed pid {pid} on port {port}")
                    return True
        if not found:
            log.debug(f"{PortManager}: no listener found on port {port}")
        return found

    @classmethod
    def kill_all(cls, ports: List[int]) -> Dict[int, bool]:
        """Kill processes listening on each port in `ports`."""
        return {p: cls.kill(p) for p in ports}

    @classmethod
    def list_usage(cls, port_range: Tuple[int, int] = (3000, 3010)) -> Dict[int, Optional[int]]:
        """Map each port in the given range to a PID or None."""
        return {
            p: next(
                (conn.pid for conn in psutil.net_connections(kind='inet')
                 if conn.laddr.port == p and conn.status == psutil.CONN_LISTEN),
                None
            )
            for p in range(port_range[0], port_range[1] + 1)
        }

    @staticmethod
    def random_port() -> int:
        """Ask the OS for an ephemeral free port."""
        with socket.socket() as sock:
            sock.bind(("", 0))
            return sock.getsockname()[1]

    def __call__(self, start: int = 3000) -> int:
        """Shortcut: find and return one free port starting from `start`."""
        return self.find(start, 1)[0]
