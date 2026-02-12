#!/usr/bin/env python3
"""Example: save CSV call data to a file and print all messages to the terminal."""

from receiver import Receiver


def save_csv(line: str) -> None:
    """Append CSV lines (header and data rows) to calls.csv."""
    open("calls.csv", "a").write(line + "\n")


r = Receiver(port=9999)
r.on(r"[^\[].*;.*", save_csv)  # CSV lines: don't start with '[', contain ';'
r.on(r".+", print)             # print all messages

print("Listening on UDP port 9999 ...")
r.run()
print("Shutdown.")
