import can
import argparse
import time
try:
    import serial  # Required for slcan backend
except ImportError:
    print("Error: The 'serial' module is not installed. Install it with 'pip install pyserial'.")
    exit(1)

def init_diagnostic_session(bus):
    """Initialize an extended diagnostic session (UDS 0x10 0x03)."""
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
    """Send tester present message to keep session active (UDS 0x3E 0x01)."""
    msg = can.Message(arbitration_id=0x7E0, data=[0x02, 0x3E, 0x01], is_extended_id=False)
    bus.send(msg)

def get_seed(bus):
    """Request 5-byte seed from ECM (UDS 0x27 0x01)."""
    msg = can.Message(arbitration_id=0x7E0, data=[0x02, 0x27, 0x01], is_extended_id=False)
    bus.send(msg)
    response = bus.recv(timeout=1.0)
    if response and response.arbitration_id == 0x7E8 and response.data[0:2] == [0x67, 0x01]:
        seed = int.from_bytes(response.data[2:7], 'big')
        print(f"Seed: {seed:010X}")
        if response.data[6] != 0x06:
            print("Warning: Seed does not end in 0x06, which is unusual for Global A ECM.")
        return seed
    else:
        print(f"Failed to retrieve seed: {response.data.hex() if response else 'No response'}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Retrieve 5-byte seed from GM ECM via OBDLink MX+")
    parser.add_argument("--can-channel", default="slcan0", help="CAN channel (e.g., slcan0 for Linux, COM3 for Windows)")
    args = parser.parse_args()

    try:
        # Initialize CAN bus
        bus = can.interface.Bus(interface='slcan', channel=args.can_channel, bitrate=500000)
        print(f"Connected to CAN bus on {args.can_channel}")

        # Start extended diagnostic session
        if not init_diagnostic_session(bus):
            print("Aborting due to session failure.")
            bus.shutdown()
            return

        # Send tester present to keep session active
        send_tester_present(bus)

        # Retrieve seed
        seed = get_seed(bus)
        if seed is not None:
            print(f"Retrieved seed: {seed:010X}")
        else:
            print("Failed to retrieve seed.")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'bus' in locals():
            bus.shutdown()
            print("CAN bus shutdown.")

if __name__ == "__main__":
    main()
