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

## Connecting a Windows PC directly to the USV detector

This section explains how to connect your Windows PC to the USV detector using a USB-to-Ethernet adapter and a standard Ethernet cable. The detector listens for ultrasonic calls and sends the results over the cable to the Windows PC, where `run.py` displays and records them.

### What you need

- A Windows PC with Python installed
- A USB-to-Ethernet adapter
- An Ethernet cable
- The USV detector (powered on, with a DHCP server configured)

### Step by step

#### 1. Plug in the hardware

1. Plug the USB-to-Ethernet adapter into a USB port on your Windows PC.
2. Connect the Ethernet cable between the adapter and the USV detector's Ethernet port.
3. Wait about 10 seconds for the connection to settle. Windows will automatically receive an IP address from the detector.

#### 2. Find your IP addresses

Open a Command Prompt on the Windows PC (press `Win + R`, type `cmd`, press Enter) and run:

```
ipconfig
```

Look for the adapter labeled **Ethernet** (it may have a number, e.g. "Ethernet 2"). Note two values:

- **IPv4 Address** — this is your Windows PC's IP (e.g. `192.168.1.7`)
- **Default Gateway** — this is the USV detector's IP (e.g. `192.168.1.1`)

#### 3. Verify the connection

In the same Command Prompt, ping the detector to make sure the link is working:

```
ping 192.168.1.1
```

Replace `192.168.1.1` with the Default Gateway from the previous step. You should see replies. If you see "Request timed out", wait a few seconds and try again — the detector may still be starting up.

#### 4. Allow incoming data through the Windows Firewall

The detector sends data to your PC over UDP port 9999. Windows Firewall blocks this by default. To allow it, open a Command Prompt **as Administrator** (right-click the Start button, choose "Terminal (Admin)" or "Command Prompt (Admin)") and run:

```
netsh advfirewall firewall add rule name="UltraVox ELAN" dir=in action=allow protocol=UDP localport=9999
```

You only need to do this once — the rule persists across reboots.

#### 5. Start the receiver on the Windows PC

Open a Command Prompt, navigate to this project folder, and run:

```
python run.py
```

You should see `Listening on UDP port 9999 ...`. Keep this window open.

#### 6. Start the detector

If the detector is set up as a systemd service (see [detector README](detector/README.md)), it starts automatically when the device powers on. Make sure the `--log-target` IP in the service file matches your Windows PC's IPv4 address from step 2.

To start or restart it manually, connect to the detector via SSH. Open a new Command Prompt on the Windows PC and run:

```
ssh pi@192.168.1.1
```

Replace `192.168.1.1` with the detector's IP (Default Gateway from step 2). The default username is `pi`. Once logged in, you can start the detector:

```
/opt/ultravox-elan /opt/ELAN.UVL --log-target 192.168.1.7:9999
```

Replace `192.168.1.7` with your Windows PC's IPv4 address from step 2.

#### 7. See the results

Switch back to the Command Prompt window running `run.py`. Detected calls will appear in the terminal and are saved to `calls.csv` in the project folder.

### Troubleshooting

| Problem | Solution |
|---|---|
| `ipconfig` does not show the Ethernet adapter | Unplug and re-plug the USB adapter. Make sure Windows has installed the driver (check Device Manager). |
| Ping shows "Request timed out" | Wait 30 seconds and retry. Check that the Ethernet cable is firmly plugged in at both ends. |
| `run.py` starts but no data appears | Verify the firewall rule (step 4). Make sure the `--log-target` IP on the detector matches your Windows IPv4 address exactly. |
| SSH says "Connection refused" | Make sure SSH is enabled on the detector (`sudo raspi-config` > Interface Options > SSH). |
| The IP addresses changed after a reboot | The detector's DHCP server may assign a different IP. Repeat step 2 to find the new addresses and update `--log-target` accordingly. |

## Detector

The C++ detector source and documentation is in [`detector/`](detector/).
