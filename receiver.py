#!/usr/bin/env python3
"""
UDP receiver for ultravox-elan.

Listens for UDP datagrams sent by the detector (--log-target) and dispatches
each line to callbacks registered by regex pattern. All matching handlers
are invoked (not just the first).

Example::

    from receiver import Receiver

    def on_call(num, device, name, duration, start, end, freq, amp):
        print(f"Call {num} on {device}: {freq} Hz")

    r = Receiver(port=9999)
    r.on(r"^(\\d+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+)$", on_call)
    r.on(r".+", print)
    r.run()

See run.py for a ready-to-use example.
"""

from __future__ import annotations

import re
import signal
import socket
from typing import Callable


class Receiver:
    """UDP datagram receiver with pattern-based callback dispatch.

    Each incoming UDP datagram is matched against all registered patterns
    in order. Every matching pattern's callback is invoked with the capture
    groups as positional arguments (*groups). If the pattern has no capture
    groups, the full line is passed as a single argument.
    """

    def __init__(self, port: int = 9999, host: str = "0.0.0.0") -> None:
        self._port = port
        self._host = host
        self._handlers: list[tuple[re.Pattern[str], Callable[..., None]]] = []
        self._running = False

    def on(self, pattern: str, callback: Callable[..., None]) -> None:
        """Register a callback for lines matching a regex pattern.

        Args:
            pattern: Regex pattern string, tested with ``re.search``.
            callback: Called as ``callback(*groups)`` if the pattern has
                capture groups, or ``callback(line)`` if it has none.
        """
        self._handlers.append((re.compile(pattern), callback))

    def stop(self) -> None:
        """Stop the receive loop."""
        self._running = False

    def run(self) -> None:
        """Block and receive datagrams until stop() is called or SIGINT/SIGTERM."""
        self._running = True

        def on_signal(sig: int, frame: object) -> None:
            self._running = False

        prev_int = signal.signal(signal.SIGINT, on_signal)
        prev_term = None
        if hasattr(signal, "SIGTERM"):
            prev_term = signal.signal(signal.SIGTERM, on_signal)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self._host, self._port))
        sock.settimeout(1.0)

        try:
            while self._running:
                try:
                    data, addr = sock.recvfrom(4096)
                except socket.timeout:
                    continue
                except (OSError, KeyboardInterrupt):
                    break

                line = data.decode("utf-8", errors="replace").rstrip("\n")
                if not line:
                    continue

                for pattern, callback in self._handlers:
                    m = pattern.search(line)
                    if m:
                        groups = m.groups()
                        if groups:
                            if len(groups) == 1:
                                callback(groups[0])
                            else:
                                callback(*groups[1:])
                        else:
                            callback(line)
        finally:
            sock.close()
            signal.signal(signal.SIGINT, prev_int)
            if prev_term is not None:
                signal.signal(signal.SIGTERM, prev_term)
