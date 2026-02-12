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

CSV lines are written to `calls.csv`, all messages are printed to the terminal.

## Receiver API

`receiver.py` provides the `Receiver` class — no dependencies beyond the standard library, runs on Windows and Linux.

```python
from receiver import Receiver

def save_csv(line: str) -> None:
    open("calls.csv", "a").write(line + "\n")

r = Receiver(port=9999)
r.on(r"[^\[].*;.*", save_csv)  # CSV lines: don't start with '[', contain ';'
r.on(r".+", print)             # print all messages
r.run()
```

- **`on(pattern, callback)`** — register a regex pattern. All matching handlers are invoked per line. With capture groups: `callback(*groups)`. Without: `callback(line)`.
- **`run()`** — blocking receive loop. Handles Ctrl+C.
- **`stop()`** — break the loop from a callback or another thread.

## CSV format

| Field | Example | Description |
|---|---|---|
| Call | 1 | Sequential call number |
| Device | Cage1 | User-defined device name |
| Name | 40-120kHz | Call definition name |
| Duration (ms) | 12.3 | Call duration |
| Start (s) | 1.234 | Start time since detection began |
| End (s) | 1.246 | End time |
| Freq (Hz) | 52000 | Frequency at max amplitude |
| Amp | 8.5 | Mean amplitude |

## Running at boot (systemd)

An example systemd service is provided in [`config/ultravox-elan.service`](config/ultravox-elan.service). It assumes the detector binary and config are installed in `/opt/detector/`.

```bash
sudo cp config/ultravox-elan.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ultravox-elan
```

## Configuration

The detector uses `.UVL` configuration files to define devices and call definitions. See `config/ELAN.UVL` for an example.

## Detector source

The C++ detector source is in [`detector/`](detector/). It requires the proprietary `bb-audio` and `ultravox-sdk` libraries to build.
