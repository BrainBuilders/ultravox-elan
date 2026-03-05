# Tools

Development utilities for working with the USV detector.

## dhcp_server.py

Minimal DHCP server for connecting directly to the detector through a PoE injector (no router). Assigns a fixed IP to the detector so you don't have to hunt for link-local addresses.

### Setup

1. Set a static IP on your USB-to-Ethernet adapter (Windows):

   - Open **Settings > Network & Internet > Ethernet** and select your USB adapter
   - Click **Edit** next to IP assignment
   - Set IP to `10.0.0.1`, Subnet to `255.255.255.0`, leave the rest empty

2. Run the DHCP server **as Administrator**:

   ```
   python tools/dhcp_server.py
   ```

3. Power on (or reboot) the detector. You should see:

   ```
   DHCP server running on 10.0.0.1
   Will assign 10.0.0.100 to any device that asks.

   DISCOVER from aa:bb:cc:dd:ee:ff -> offering 10.0.0.100
   REQUEST  from aa:bb:cc:dd:ee:ff -> assigning 10.0.0.100
   ```

4. The detector is now reachable at `10.0.0.100`. Its `--log-target` should point to `10.0.0.1:9999`.

### Notes

- Requires Administrator privileges (DHCP uses port 67).
- No external dependencies — uses only the Python standard library.
- Only intended for development with a single detector. In production, use a managed PoE switch/router with its own DHCP server.
