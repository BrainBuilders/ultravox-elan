# ultravox-elan

Real-time USV (Ultrasonic Vocalization) detector. Monitors USB microphones and outputs detected calls as CSV to stdout.

## Building

Requires [bb-audio](../../bb-audio) and [ultravox-sdk](../../ultravox-sdk) to be installed, plus vcpkg for PortAudio and spdlog.

```bash
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake
make
```

## Usage

```bash
./ultravox-elan config/ELAN.UVL
```

The argument is a `.UVL` configuration file. Stop with Ctrl+C.

## Output

Semicolon-delimited CSV to stdout:

```
Call;Device;Name;Duration (ms);Start (s);End (s);Freq (Hz);Amp
1;Cage1;40-120kHz;12.3;1.234;1.246;52000;8.5
```

Log messages go to stderr.

## Configuration

The `.UVL` file defines devices and call definitions in INI format:

```ini
[Device_1]
DevName=Pettersson M500-384kHz USB Ultr
UserDevName=Cage1
Enabled=true
Samplerate=384000

[DefCall_1]
Name=40-120kHz
MinFreq=40000
MaxFreq=120000
MinAmp=100
MinDur=0.001
MaxDur=0.400
MinGap=0.010
```

Up to 10 devices and multiple call definitions are supported. See `config/ELAN.UVL` for a complete example.
