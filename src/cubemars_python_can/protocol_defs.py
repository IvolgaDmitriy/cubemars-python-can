# CAN frame packing/unpacking
CAN_FRAME_FMT_SEND = "=IB3x8s"
CAN_FRAME_FMT_RECV = "=IB3x8s"
CAN_RECV_BYTES = 16

# Raw value limits
MAX_RAW_POSITION = (1 << 16) - 1
MAX_RAW_VELOCITY = (1 << 12) - 1
MAX_RAW_TORQUE = (1 << 12) - 1
MAX_RAW_KP = (1 << 12) - 1
MAX_RAW_KD = (1 << 12) - 1
MAX_RAW_CURRENT = (1 << 12) - 1

# Special motor commands (see Cubemars CAN protocol)
ENTER_MOTOR_CONTROL_MODE = bytes([
    0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFC,
])

EXIT_MOTOR_CONTROL_MODE = bytes([
    0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFD,
])

SET_ZERO_POSITION = bytes([
    0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFE,
])

# Timing
DT_SLEEP = 0.0001
SET_ZERO_SLEEP = 1.5

if __name__ == "__main__":
    pass
