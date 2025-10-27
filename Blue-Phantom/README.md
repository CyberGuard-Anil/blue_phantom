# 👻 blue_phantom.py

**Bluetooth Audio Spy Tool (HFP/HSP Recorder)**

**blue\_phantom.py** is a Python-based utility designed to automate the process of connecting to a target Bluetooth device (like headphones or a car kit) and recording its live microphone audio stream (specifically targeting the Headset Profile/Hands-Free Profile, HFP/HSP) into an **MP3** file.

## ⚠️ Disclaimer

**This tool is intended for security research, testing, and educational purposes only.** Unauthorized access to or interception of private communication is illegal and unethical. The developer is not responsible for any misuse of this program. **Use it responsibly and only on devices you own or have explicit permission to test.**

-----

## ✨ Features

  * **L2CAP Ping Check:** Verifies target device reachability.
  * **Automated Pairing & Trust:** Uses `bluetoothctl` to force pairing, trust, and connection.
  * **HFP/HSP Source Discovery:** Automatically locates the active PulseAudio Bluetooth microphone source.
  * **MP3 Recording:** Records audio directly into a time-stamped MP3 file using `parecord` piped to `lame`.
  * **Graceful Cleanup:** Automatically disconnects and removes (un-trusts/un-pairs) the target device upon exit.

-----

## 🛠️ Prerequisites

This tool requires a Linux operating system (like Ubuntu, Kali, or Parrot OS) and a Bluetooth adapter. The following dependencies must be installed:

### Installation (Debian/Ubuntu-based Systems)

Open your terminal and run:

```bash
sudo apt update
sudo apt install bluez pulseaudio-utils lame python3 python3-pip
```

-----

## 🚀 Usage

### 1\. Clone the Repository

```bash
git clone <YOUR-REPOSITORY-LINK>
cd blue_phantom
```

### 2\. Run the Tool

The script requires **root privileges (`sudo`)** for interacting with Bluetooth hardware and **the target's MAC Address** as an argument.

**Syntax:**

```bash
sudo python3 blue_phantom.py -a <TARGET_MAC_ADDRESS>
```

**Example:**

```bash
sudo python3 blue_phantom.py -a A1:B2:C3:D4:E5:F6
```

### Stopping the Recording

Press **`Ctrl + C`** at any time to stop the recording gracefully. The script will automatically clean up the connection and save the final MP3 file before exiting.

-----

## 📂 Output

All recordings are saved in the automatically created `recordings/` directory with a timestamped filename format:

```
recordings/A1_B2_C3_D4_E5_F6_20251027_101530.mp3
```

-----

## 👤 Developer

Developed by: **Anil Yadav**

-----

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details. *(Note: You should create a LICENSE file if you don't have one.)*
