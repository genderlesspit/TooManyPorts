import socket
import pytest
from toomanyports import PortManager

def test_is_available_and_find_and_random():
    p = PortManager.random_port()
    assert isinstance(p, int)
    assert PortManager.is_available(p)

    free = PortManager.find(start=p, count=1)[0]
    assert free >= p
    assert PortManager.is_available(free)

def test_kill_and_list_usage(tmp_path):
    # open a dummy socket
    sock = socket.socket()
    port = PortManager.find(start=40000, count=1)[0]
    sock.bind(("localhost", port))
    sock.listen(1)

    info = PortManager.list_usage((port, port))[port]
    assert info == socket.gethostbyname.__qualname__ or isinstance(info, int)

    killed = PortManager.kill(port)
    assert killed
    sock.close()
    assert PortManager.is_available(port)

    # bulk kill
    # no errors if no listener
    res = PortManager.kill_all([port, port+1])
    assert isinstance(res, dict)
