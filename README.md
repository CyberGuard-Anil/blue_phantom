
# 👻 Blue Phantom

**Bluetooth Audio Spy / HFP-HSP Recorder (for Research & Testing)**

`blue_phantom.py` is a Python-based utility that automates Bluetooth pairing, connection, and microphone stream recording (via HFP/HSP profiles) into MP3 format.  
Designed for **security research and auditing of Bluetooth device vulnerabilities**.

---

## ⚠️ Disclaimer

> This tool is intended **for cybersecurity research, educational, and authorized testing purposes only**.  
> Unauthorized interception of Bluetooth audio is **illegal and unethical**.  
> Use only on devices you **own or have explicit permission** to test.

---

## ✨ Features

- 🔍 **Reachability Check:** Uses `l2ping` to verify if a target device is active.
- 🔗 **Auto Pair & Trust:** Automates pairing and connection using `bluetoothctl`.
- 🎙️ **HFP/HSP Audio Source Detection:** Automatically finds the correct PulseAudio microphone source.
- 🎧 **MP3 Recording:** Streams live audio using `parecord` piped through `lame` encoder.
- 🧹 **Automatic Cleanup:** Disconnects, un-pairs, and removes trust after recording ends.
- 💥 **Error Handling & Timeouts:** Prevents hangs during pairing and connection steps.

---

## 🧰 Requirements

**Platform:** Linux (Kali, Parrot, Ubuntu, etc.)  
**Dependencies:** Bluetooth tools, PulseAudio, LAME encoder, Python 3

### Install Dependencies

```bash
sudo apt update
sudo apt install bluez pulseaudio-utils lame python3 python3-pip
````

---

## 🚀 Usage

### 1. Clone the Repository

```bash
git clone https://github.com/CyberGuard-Anil/blue_phantom.git
cd blue_phantom
```

### 2. Run the Script

```bash
sudo python3 blue_phantom.py -a <TARGET_MAC_ADDRESS>
```

**Example:**

```bash
sudo python3 blue_phantom.py -a A1:B2:C3:D4:E5:F6
```

> Press **Ctrl + C** anytime to stop recording.
> The script will automatically save the MP3 file and disconnect the target.

---

## 📂 Output

All recordings are saved in the `recordings/` folder, automatically created if missing.

Example filename format:

```
recordings/A1_B2_C3_D4_E5_F6_20251027_101530.mp3
```

---

## 🧑‍💻 Developer

**Anil Yadav**
Cybersecurity Researcher | Bluetooth & Wireless Security Enthusiast

---

## 📄 License

This project is licensed under the **MIT License**.
See the [`LICENSE`](LICENSE) file for details.


Chaaho to main tumhare liye ek clean `LICENSE` file (MIT format) bhi likh du — ready-to-add GitHub style?
