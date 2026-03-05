# Detector

C++ source for the UltraVox ELAN real-time USV detector. It listens to ultrasonic microphones and sends detected calls over UDP to the receiver on your PC.

The detector requires the proprietary `bb-audio` and `ultravox-sdk` libraries to build. Contact [Brain Builders](https://brainbuilders.eu) for access.

## Configuration

The detector uses `.UVL` configuration files to define devices and call definitions. See [`config/ELAN.UVL`](../config/ELAN.UVL) for an example.

## Running at boot (systemd)

An example systemd service is provided in [`config/ultravox-elan.service`](../config/ultravox-elan.service). It assumes the detector binary and config are installed in `/opt/`.

```bash
sudo cp config/ultravox-elan.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ultravox-elan
```

Check status and logs:

```bash
sudo systemctl status ultravox-elan
journalctl -u ultravox-elan -f
```

Make sure the `--log-target` IP in the service file matches the IP address of the PC running the receiver. See the [main README](../README.md#connecting-a-windows-pc-directly-to-the-usv-detector) for how to find this address.
