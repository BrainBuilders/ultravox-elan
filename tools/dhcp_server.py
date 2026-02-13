#!/usr/bin/env python3
"""
Minimal DHCP server for development.

Assigns a fixed IP to the USV detector when connected directly via a PoE
injector (no router). Run as Administrator on Windows.

Usage:
    1. Set a static IP on your USB-to-Ethernet adapter:
       IP: 10.0.0.1, Subnet: 255.255.255.0
    2. Run:  python dhcp_server.py
    3. Power on the detector — it will receive 10.0.0.100 via DHCP.

The detector's --log-target should point to 10.0.0.1 (this PC).
"""

import socket
import struct

SERVER_IP = "10.0.0.1"
OFFER_IP = "10.0.0.100"
SUBNET = "255.255.255.0"
LEASE_TIME = 3600

DHCP_DISCOVER = 1
DHCP_OFFER = 2
DHCP_REQUEST = 3
DHCP_ACK = 5

MAGIC_COOKIE = b"\x63\x82\x53\x63"


def ip_bytes(addr: str) -> bytes:
    return socket.inet_aton(addr)


def parse_options(data: bytes) -> dict[int, bytes]:
    opts = {}
    i = 0
    while i < len(data):
        code = data[i]
        if code == 255:
            break
        if code == 0:
            i += 1
            continue
        length = data[i + 1]
        opts[code] = data[i + 2 : i + 2 + length]
        i += 2 + length
    return opts


def build_reply(request: bytes, msg_type: int) -> bytes:
    # BOOTP header: request fields we echo back
    xid = request[4:8]
    client_mac = request[28:44]

    reply = bytearray(236)
    reply[0] = 2                              # op: BOOTREPLY
    reply[1] = 1                              # htype: Ethernet
    reply[2] = 6                              # hlen
    reply[4:8] = xid
    reply[16:20] = ip_bytes(OFFER_IP)         # yiaddr
    reply[20:24] = ip_bytes(SERVER_IP)        # siaddr
    reply[28:44] = client_mac

    # DHCP options
    options = MAGIC_COOKIE
    options += bytes([53, 1, msg_type])                          # DHCP Message Type
    options += bytes([54, 4]) + ip_bytes(SERVER_IP)              # Server Identifier
    options += bytes([51, 4]) + struct.pack("!I", LEASE_TIME)    # Lease Time
    options += bytes([1, 4]) + ip_bytes(SUBNET)                  # Subnet Mask
    options += bytes([3, 4]) + ip_bytes(SERVER_IP)               # Router
    options += bytes([255])                                      # End

    return bytes(reply) + options


def run() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("0.0.0.0", 67))

    print(f"DHCP server running on {SERVER_IP}")
    print(f"Will assign {OFFER_IP} to any device that asks.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            data, addr = sock.recvfrom(4096)
            if len(data) < 240 or data[236:240] != MAGIC_COOKIE:
                continue

            options = parse_options(data[240:])
            dhcp_type = options.get(53, b"\x00")[0]
            client_mac_hex = data[28:34].hex(":")

            if dhcp_type == DHCP_DISCOVER:
                print(f"DISCOVER from {client_mac_hex} -> offering {OFFER_IP}")
                reply = build_reply(data, DHCP_OFFER)
                sock.sendto(reply, ("255.255.255.255", 68))

            elif dhcp_type == DHCP_REQUEST:
                print(f"REQUEST  from {client_mac_hex} -> assigning {OFFER_IP}")
                reply = build_reply(data, DHCP_ACK)
                sock.sendto(reply, ("255.255.255.255", 68))
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        sock.close()


if __name__ == "__main__":
    run()
