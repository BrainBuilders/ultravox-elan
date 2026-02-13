# ultravox-elan

UDP receiver for the UltraVox real-time USV (Ultrasonic Vocalization) detector. Listens for call detection data and debug logs sent by the detector over the network.

The detector binary requires proprietary libraries and is not included in this repository. Contact [Brain Builders](https://brainbuilders.eu) for access.

## Quick start

1. Start the receiver:

```bash
python run.py
```

2. Start the detector with network logging (on the same or a remote machine):

```bash
./ultravox-elan config/ELAN.UVL --log-target 192.168.1.50:9999
```

Output:

```
[2026-02-12 14:23:01.234] [bb-audio] [debug] Opening device ...
Call;Device;Name;Duration (ms);Start (s);End (s);Freq (Hz);Amp
1;Cage1;40-120kHz;12.3;1.234;1.246;52000;8.5
```

CSV lines are written to `calls.csv`, all messages are printed to the terminal.

## Receiver API

`receiver.py` provides the `Receiver` class — no dependencies beyond the standard library, runs on Windows and Linux.

```python
from receiver import Receiver

def on_call(line_, num, device, name, start, end, freq, amp):
    duration_ms = (float(end) - float(start)) * 1000
    print(f"Call #{num} '{name}' on {device}: {freq} Hz for {duration_ms}ms (amplitude {amp})")

r = Receiver(port=9999)
r.on(r"^([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+);([^;]+)$", on_call)
r.run()
```

- **`on(pattern, callback)`**: register a regex pattern. All matching handlers are invoked per line. Each captured group will be an argument, the whole match is always the first group.
- **`run()`**: blocking receive loop. Handles Ctrl+C.
- **`stop()`**: break the loop from a callback or another thread.

## CSV format

The detector outputs semicolon-delimited CSV:

| Field     | Example  | Description                      |
|-----------|----------|----------------------------------|
| Call      | 1        | Sequential call number           |
| Device    | Cage1    | User-defined device name         |
| Name      | Distress | Call definition name             |
| Start (s) | 1.234    | Start time since detection began |
| End (s)   | 1.246    | End time                         |
| Freq (Hz) | 52000    | Frequency at max amplitude       |
| Amp       | 8.5      | Mean amplitude                   |

## Connecting a Windows PC to the USV detector

The detector is powered over Ethernet (PoE) and sends detected calls over the same cable to the Windows PC.

### What you need

- A Windows PC with Python installed
- A USB-to-Ethernet adapter
- An Ethernet cable
- A PoE injector (or PoE switch/router)
- The USV detector

### Setup

1. Connect the USB-to-Ethernet adapter to your PC, the adapter to the PoE injector's **data** port, and the injector's **PoE** port to the detector.

2. Set up networking using the included [DHCP server](tools/README.md). This gives your PC the IP `10.0.0.1` and assigns `10.0.0.100` to the detector.

3. Allow UDP through the firewall (once, as Administrator):
   ```
   netsh advfirewall firewall add rule name="UltraVox ELAN" dir=in action=allow protocol=UDP localport=9999
   ```

4. Run the receiver:
   ```
   python run.py
   ```

The detector starts automatically and sends data to `10.0.0.1:9999`. Detected calls appear in the terminal and are saved to `calls.csv`.

## Detector

The C++ detector source and documentation is in [`detector/`](detector/README.md).
