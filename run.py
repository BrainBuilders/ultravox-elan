#!/usr/bin/env python3
"""Example: save CSV call data to a file and print all messages to the terminal."""

from datetime import datetime
from receiver import Receiver

csv_path = f"usv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

with open(csv_path, "w") as csv:

    # Write CSV header
    csv.write("Date,Time,Cage,Label,Duration (ms)\n")

    # Callback to save call data to CSV file.
    def save_call(_counter, cage, label, start, end, _freq, _amp):
        today = datetime.now().strftime('%Y-%m-%d')
        now = datetime.now().strftime('%H:%M:%S')
        duration_ms = (float(end) - float(start)) * 1000
        csv.write(f"{today},{now},{cage},{label},{duration_ms:.2f}\n")
        csv.flush()

    # Create a Receiver to listen for UDP datagrams on port 9999.
    r = Receiver(port=9999)

    # Register the save_call callback for lines matching the expected CSV format.
    r.on(r"^(\d+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+)$", save_call)

    # Also print all messages to the terminal.
    r.on(r".+", print)

    # Start the receive loop.
    print("Listening on UDP port 9999... Press Ctrl+C to stop.")
    r.run()
    print("Shutdown.")
