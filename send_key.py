import can
import argparse
import time
try:
    import serial
except ImportError:
    print("Error: The 'serial' module is not installed. Install it with 'pip install pyserial'.")
    exit(1)

def init_diagnostic_session(bus):
    msg = can.Message(arbitration_id=0x7E0, data=[0x02, 0x10, 0x03], is_extended_id=False)
    bus.send(msg)
    response = bus.recv(timeout=1.0)
    if response and response.arbitration_id == 0x7E8 and response.data[0:2] == [0x50, 0x03]:
        print("Extended diagnostic session started.")
        return True
    else:
        print(f"Failed to start diagnostic session: {response.data.hex() if response else 'No response'}")
        return False

def send_tester_present(bus):
    msg = can.Message(arbitration_id=0x7E0, data=[0x02, 0x3E, 0x01], is_extended_id=False)
    bus.send(msg)

def send_key(bus, key):
    key_bytes = list((key & 0xFFFFFFFFFF).to_bytes(5, 'big'))
    msg = can.Message(arbitration_id=0x7E0, data=[0x07, 0x27, 0x02] + key_bytes, is_extended_id=False)
    bus.send(msg)
    response = bus.recv(timeout=1.0)
    if response and response.arbitration_id == 0x7E8 and response.data[0:2] == [0x67, 0x02]:
        print("ECM Unlocked! Algorithm is correct.")
        return True
    elif response and response.data[0:3] == [0x7F, 0x27, 0x35]:
        print("Invalid Key (NRC 0x35). Algorithm may be incorrect.")
        return False
    elif response and response.data[0:3] == [0x7F, 0x27, 0x36]:
        print("Lockout (NRC 0x36). Waiting 10 seconds before retry...")
        time.sleep(10)
        return False
    else:
        print(f"Unexpected response: {response.data.hex() if response else 'No response'}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Send 5-byte key to GM ECM via OBDLink MX+")
    parser.add_argument("--key", required=True, help="5-byte key (e.g., 0x1D1E82E706)")
    parser.add_argument("--can-channel", default="slcan0", help="CAN channel (e.g., slcan0 for Linux)")
    args = parser.parse_args()

    try:
        bus = can.interface.Bus(interface='slcan', channel=args.can_channel, bitrate=500000)
        print(f"Connected to CAN bus on {args.can_channel}")
        if not init_diagnostic_session(bus):
            print("Aborting due to session failure.")
            bus.shutdown()
            return
        send_tester_present(bus)
        key = int(args.key, 16)
        if send_key(bus, key):
            print(f"Key {key:010X} unlocked the ECM.")
        else:
            print(f"Key {key:010X} failed.")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'bus' in locals():
            bus.shutdown()
            print("CAN bus shutdown.")

if __name__ == "__main__":
    main()
