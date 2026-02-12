# ultravox-elan

UDP receiver for the UltraVox real-time USV (Ultrasonic Vocalization) detector. Listens for call detection data and debug logs sent by the detector over the network.

The detector binary requires proprietary libraries and is not included in this repository. Contact [Brain Builders](https://brainbuilders.eu) for access.

## Receiver

`receiver.py` is a standalone Python script (no dependencies beyond the standard library, runs on Windows and Linux) that receives UDP datagrams from the detector and classifies each line as CSV call data or debug logging.

### Quick start

1. Start the receiver:

```bash
python receiver.py --port 9999
```

2. Start the detector with network logging (on the same or a remote machine):

```bash
./ultravox-elan config/ELAN.UVL --log-target 192.168.1.50:9999
```

### Output

The receiver prefixes each line to distinguish call data from debug logs:

```
[14:23:01] CSV | Call;Device;Name;Duration (ms);Start (s);End (s);Freq (Hz);Amp
[14:23:01] LOG | [2026-02-12 14:23:01.234] [bb-audio] [debug] Opening device ...
[14:23:05] CSV | 1;Cage1;40-120kHz;12.3;1.234;1.246;52000;8.5
```

CSV lines match the pattern `^\d+;` (data rows) or `^Call;` (header). Everything else is debug logging.

### Saving CSV data to a file

```bash
python receiver.py --port 9999 --csv calls.csv
```

This writes only CSV lines (header + data) to the file. Debug logs are still printed to the terminal but not written to the file.

### Options

| Flag | Default | Description |
|---|---|---|
| `--port` | 9999 | UDP port to listen on |
| `--csv` | — | Write CSV lines to this file |

## CSV format

The detector outputs semicolon-delimited CSV:

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

## Configuration

The detector uses `.UVL` configuration files to define devices and call definitions. See `config/ELAN.UVL` for an example.

## Detector source

The C++ detector source is in [`detector/`](detector/). It requires the proprietary `bb-audio` and `ultravox-sdk` libraries to build.
