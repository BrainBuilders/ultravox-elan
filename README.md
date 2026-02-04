# ultravox-elan

Real-time USV (Ultrasonic Vocalization) detector CLI tool. Monitors microphones and outputs detected calls as CSV data compatible with UltraVox export format.

## Overview

`ultravox-elan` is a command-line application that:
- Reads experiment configuration from an UltraVox experiment directory
- Captures audio from one to four USB microphones in real-time
- Detects ultrasonic vocalizations using the same algorithm as UltraVox
- Outputs detected calls as CSV rows to stdout

The tool is designed to run as a service on Linux (e.g., Raspberry Pi), streaming detection results over the network to a Python client.

## Requirements

- Linux (tested on Raspberry Pi)
- USB ultrasonic microphones (e.g., Ultrasound Microphone)
- C++17 compiler
- CMake 3.16+
- Dependencies:
  - bb-audio library
  - ultravox-sdk library
  - PortAudio
  - spdlog

## Building

```bash
# Assuming bb-audio and ultravox-sdk are installed in /usr/local

mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH="/path/to/bb-audio;/path/to/ultravox-sdk"
make
```

### Build with vcpkg

If using vcpkg for dependencies:

```bash
cmake .. -DCMAKE_TOOLCHAIN_FILE=/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake
make
```

## Usage

```bash
ultravox-elan <experiment_directory>
```

### Arguments

- `experiment_directory` - Path to an UltraVox experiment directory containing:
  - `Experiment.UVX` - Main experiment configuration file
  - One or more `.UVC` files - Call definition files

### Output

CSV data is written to **stdout** with semicolon (`;`) delimiter.
Status messages and errors are written to **stderr**.

### Example

```bash
# Basic usage - output to console
./ultravox-elan /path/to/MyExperiment

# Save to file
./ultravox-elan /path/to/MyExperiment > calls.csv

# Stream over network (using netcat)
./ultravox-elan /path/to/MyExperiment | nc -l 5000

# Run as systemd service (see below)
```

## CSV Output Format

The output is UltraVox-compatible with an additional `Microphone` column:

| Column | Description |
|--------|-------------|
| Call | Sequential call number (1, 2, 3, ...) |
| Microphone | Name of the microphone that detected the call |
| Call name | Name of the matching call definition |
| Label Label | Label (empty for real-time detection) |
| Duration (ms) | Call duration in milliseconds |
| Start Time (s) | Start time in seconds since capture began |
| Stop Time (s) | Stop time in seconds since capture began |
| Freq at Max Amp (Hz) | Dominant frequency in Hz |
| Mean Amplitude | Average amplitude during the call |

### Example Output

```csv
Call;Microphone;Call name;Label Label;Duration (ms);Start Time (s);Stop Time (s);Freq at Max Amp (Hz);Mean Amplitude
1;Mic1;USV_50kHz;;45.500;1.234567;1.280067;52000.000;0.085
2;Mic1;USV_70kHz;;38.200;2.450000;2.488200;74500.000;0.072
3;Mic2;USV_50kHz;;52.100;2.600000;2.652100;51200.000;0.091
```

## Experiment Directory Structure

The tool expects an UltraVox experiment directory:

```
MyExperiment/
├── Experiment.UVX           # Main configuration (INI format)
├── Recording1.UVC           # Call definitions (INI format)
└── ...
```

### Experiment.UVX Format

```ini
[Experiment]
Name=MyExperiment
SpectrogramFftLength=512
SpectrogramOverlap=0.5

[Device_1]
DevName=Ultrasound Microphone (hw:0,0)
UserDevName=Mic1
Level=50
Enabled=true
Samplerate=384000

[Device_2]
DevName=Ultrasound Microphone (hw:0,1)
UserDevName=Mic2
Level=50
Enabled=true
Samplerate=384000
```

### Call Definition (.UVC) Format

```ini
[DefCall_1]
Name=USV_50kHz
MinFreq=45000
MaxFreq=55000
MinAmp=0.05
MinDur=0.010
MaxDur=0.500
MinGap=0.010

[DefCall_2]
Name=USV_70kHz
MinFreq=65000
MaxFreq=80000
MinAmp=0.05
MinDur=0.010
MaxDur=0.500
MinGap=0.010
```

## Running as a Service

### Systemd Service

Create `/etc/systemd/system/ultravox-elan.service`:

```ini
[Unit]
Description=UltraVox Real-time USV Detector
After=network.target sound.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/ultravox-elan /home/pi/experiments/MyExperiment
StandardOutput=append:/var/log/ultravox-elan/calls.csv
StandardError=append:/var/log/ultravox-elan/error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo mkdir -p /var/log/ultravox-elan
sudo systemctl enable ultravox-elan
sudo systemctl start ultravox-elan
```

### Streaming Over Network

To stream results to a remote Python client:

```bash
# On Raspberry Pi - stream via TCP
./ultravox-elan /path/to/experiment | nc -l -k 5000

# On Python client - receive
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('raspberry-pi-ip', 5000))
for line in s.makefile():
    print(line.strip())
```

Or use a named pipe:

```bash
# Create pipe
mkfifo /tmp/usv_calls

# Start detector
./ultravox-elan /path/to/experiment > /tmp/usv_calls &

# Read from pipe
cat /tmp/usv_calls
```

## Detection Algorithm

The detection uses spectrogram-based frequency domain analysis:

1. **Audio Capture**: Continuously captures audio into a 60-second ring buffer
2. **FFT Analysis**: Computes spectrogram using configurable FFT length and overlap
3. **Threshold Detection**: For each call definition, checks if any frequency bin exceeds the minimum amplitude threshold
4. **Call Validation**: Validates detected calls against:
   - Minimum/maximum duration constraints
   - Minimum gap between calls (merges short gaps)
5. **Output**: Emits CSV row when a call completes (gap detected or end of analysis window)

Detection runs every 500ms with a 1-second safety margin to avoid reporting incomplete calls.

## Signal Handling

- `SIGINT` (Ctrl+C): Graceful shutdown - stops capture and flushes output
- `SIGTERM`: Graceful shutdown (for systemd)

## Troubleshooting

### No microphones detected

1. Check USB connection: `lsusb`
2. Check ALSA devices: `arecord -l`
3. Ensure correct permissions: `sudo usermod -a -G audio $USER`

### Permission denied

Run with appropriate permissions or configure udev rules:

```bash
# /etc/udev/rules.d/99-usb-mic.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="xxxx", ATTR{idProduct}=="yyyy", MODE="0666"
```

### High CPU usage

- Reduce FFT length (e.g., 256 instead of 512)
- Increase detection interval in source code

## License

See LICENSE file for details.

## Related Projects

- [bb-audio](https://github.com/...) - Audio capture library
- [ultravox-sdk](https://github.com/...) - USV detection SDK
- [ultravox-desktop](https://github.com/...) - Desktop GUI application
