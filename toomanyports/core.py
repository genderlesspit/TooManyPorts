import socket
import psutil
from typing import List, Tuple, Optional, Dict
from loguru import logger as log

class PortManager:
    """port allocation. availability. cleanup. usage reporting."""

    @staticmethod
    def is_available(port: int) -> bool:
        try:
            with socket.socket() as sock:
                sock.bind(('', port))
            return True
        except OSError:
            return False

    @classmethod
    def find(cls, start: int = 3000, count: int = 1) -> List[int]:
        out = []
        p = start
        while len(out) < count and p < 65535:
            if cls.is_available(p):
                out.append(p)
            p += 1
        if len(out) < count:
            raise RuntimeError(f'could not find {count} ports from {start}')
        return out

    @staticmethod
    def kill(port: int, force: bool = True) -> bool:
        for c in psutil.net_connections(kind='inet'):
            if c.laddr.port == port and c.status == psutil.CONN_LISTEN:
                proc = psutil.Process(c.pid)
                try:
                    force and proc.kill() or proc.terminate()
                except Exception as e:
                    log.error(f'failed killing pid {c.pid}: {e}')
                    return False
                else:
                    log.success(f'killed pid {c.pid} on port {port}')
                    return True
        log.debug(f'no listener on port {port}')
        return False

    @classmethod
    def kill_all(cls, ports: List[int]) -> Dict[int, bool]:
        return {p: cls.kill(p) for p in ports}

    @classmethod
    def list_usage(cls, port_range: Tuple[int, int] = (3000, 3010)) -> Dict[int, Optional[int]]:
        return {
            p: next(
                (c.pid for c in psutil.net_connections(kind='inet')
                 if c.laddr.port == p and c.status == psutil.CONN_LISTEN),
                None
            )
            for p in range(port_range[0], port_range[1] + 1)
        }

    @staticmethod
    def random_port() -> int:
        """ask OS for an ephemeral free port"""
        with socket.socket() as sock:
            sock.bind(('', 0))
            return sock.getsockname()[1]

    def __call__(self, start: int = 3000) -> int:
        return self.find(start, 1)[0]
