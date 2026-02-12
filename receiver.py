#!/usr/bin/env python3
"""
UDP receiver for ultravox-elan.

Listens for UDP datagrams sent by the detector (--log-target) and classifies
each line as CSV call data or debug logging.

Usage:
    python receiver.py                          # listen on port 9999
    python receiver.py --port 5000              # custom port
    python receiver.py --csv calls.csv          # also write CSV lines to file

Example session (two terminals):

    # Terminal 1 - start the receiver
    python receiver.py --port 9999

    # Terminal 2 - start the detector with network logging
    ./detector/build/ultravox-elan config/ELAN.UVL --log-target 127.0.0.1:9999

    # Receiver output:
    # [14:23:01] CSV | Call;Device;Name;Duration (ms);Start (s);End (s);Freq (Hz);Amp
    # [14:23:01] LOG | [2026-02-12 14:23:01.234] [bb-audio] [debug] Opening device ...
    # [14:23:05] CSV | 1;Cage1;40-120kHz;12.3;1.234;1.246;52000;8.5
"""

import argparse
import datetime
import re
import signal
import socket
import sys

# Matches CSV header and data rows: "Call;..." or "123;..."
CSV_PATTERN = re.compile(r"^\d+;|^Call;")


def main():
    parser = argparse.ArgumentParser(
        description="Receive live USV detection data from ultravox-elan over UDP.")
    parser.add_argument("--port", type=int, default=9999,
                        help="UDP port to listen on (default: 9999)")
    parser.add_argument("--csv", type=str, default=None, metavar="FILE",
                        help="write CSV lines (only) to this file")
    args = parser.parse_args()

    running = True

    def on_signal(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, on_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, on_signal)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", args.port))
    sock.settimeout(1.0)

    print(f"Listening on UDP port {args.port} ...")

    csv_file = None
    if args.csv:
        csv_file = open(args.csv, "w", encoding="utf-8")
        print(f"Writing CSV data to {args.csv}")

    try:
        while running:
            try:
                data, addr = sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break

            line = data.decode("utf-8", errors="replace").rstrip("\n")
            if not line:
                continue

            now = datetime.datetime.now().strftime("%H:%M:%S")

            if CSV_PATTERN.match(line):
                print(f"[{now}] CSV | {line}")
                if csv_file:
                    csv_file.write(line + "\n")
                    csv_file.flush()
            else:
                print(f"[{now}] LOG | {line}")
    finally:
        if csv_file:
            csv_file.close()
        sock.close()
        print("\nShutdown.")


if __name__ == "__main__":
    main()
