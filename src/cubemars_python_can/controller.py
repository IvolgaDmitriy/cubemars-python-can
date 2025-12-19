import math
import socket
import struct

from bitstring import BitArray
from loguru import logger

from cubemars_python_can.encoding import float_to_uint, uint_to_float
from cubemars_python_can.motors_configs import MotorOperationRanges, RotationDirection
from cubemars_python_can.protocol_defs import (
    CAN_FRAME_FMT_RECV,
    CAN_FRAME_FMT_SEND,
    CAN_RECV_BYTES,
    DT_SLEEP,
    ENTER_MOTOR_CONTROL_MODE,
    EXIT_MOTOR_CONTROL_MODE,
    MAX_RAW_KD,
    MAX_RAW_KP,
    SET_ZERO_POSITION,
    SET_ZERO_SLEEP,
)
from cubemars_python_can.utils import wait_for


class MIT_MotorController:
    """
    Class for creating a Mini-Cheetah Motor Controller over CAN. Uses SocketCAN driver for
    communication.
    """

    can_socket_declared = False
    motor_socket = None

    def __init__(
        self,
        motor_cfg: MotorOperationRanges,
        can_socket: str = "can0",
        motor_id: int = 1,
        socket_timeout: float = 0.05,
        rotation_direction: RotationDirection = RotationDirection.FORWARD,
    ):
        self.motor_cfg = motor_cfg
        self.motor_id = motor_id
        self._rotation_direction = rotation_direction.value

        # Initialize the command BitArrays for performance optimization
        self._des_pos_bits = BitArray(
            uint=float_to_uint(
                0,
                self.motor_cfg.pos_min,
                self.motor_cfg.pos_max,
                16,  # FIXME: magic number
            ),
            length=16,
        )
        self._des_vel_bits = BitArray(
            uint=float_to_uint(
                0,
                self.motor_cfg.vel_min,
                self.motor_cfg.vel_max,
                12,  # FIXME: magic number
            ),
            length=12,
        )
        self._kp_bits = BitArray(uint=0, length=12)
        self._kd_bits = BitArray(uint=0, length=12)
        self._feed_forward_bits = BitArray(uint=0, length=12)
        self._cmd_bytes = BitArray(uint=0, length=64)
        self._recv_bytes = BitArray(uint=0, length=48)

        self._initialize_can_socket(can_socket, socket_timeout)

    def _initialize_can_socket(self, can_socket: str, socket_timeout: float):
        """
        Initialize the CAN Socket if not already initialized.
        """
        if MIT_MotorController.can_socket_declared:
            logger.info(
                f"CAN socket already declared. Using existing socket: {MIT_MotorController.motor_socket}"
            )
        else:
            logger.info(f"Declaring CAN socket on interface: {can_socket}")

            can_socket = (can_socket,)
            try:
                MIT_MotorController.motor_socket = socket.socket(
                    socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW
                )
                # Disable CAN loopback (do not receive own frames)
                MIT_MotorController.motor_socket.setsockopt(
                    socket.SOL_CAN_RAW, socket.CAN_RAW_LOOPBACK, 0
                )
                MIT_MotorController.motor_socket.bind(can_socket)
                MIT_MotorController.motor_socket.settimeout(socket_timeout)

                MIT_MotorController.can_socket_declared = True
                logger.success(f"Bound to: {can_socket}")
            except Exception as e:
                logger.error(f"Unable to Connect to Socket Specified: {can_socket}")
                logger.error(f"Error: {e}")

    def _send_can_frame(self, data: bytes) -> None:
        """
        Send raw CAN data frame (in bytes) to the motor.
        """
        can_dlc = len(data)
        can_msg = struct.pack(CAN_FRAME_FMT_SEND, self.motor_id, can_dlc, data)
        try:
            MIT_MotorController.motor_socket.send(can_msg)
        except Exception as e:
            logger.error("Unable to Send CAN Frame.")
            logger.error("Error: ", e)

    def _recv_can_frame(self) -> tuple[int, int, bytes]:
        """
        Receive a CAN frame and unpack it. Returns can_id, can_dlc (data length), data (in bytes)
        """
        try:
            # The motor sends back only 6 bytes.
            frame, _ = MIT_MotorController.motor_socket.recvfrom(CAN_RECV_BYTES)
            can_id, can_dlc, data = struct.unpack(CAN_FRAME_FMT_RECV, frame)
            return can_id, can_dlc, data[:can_dlc]
        except Exception as e:
            logger.error("Unable to Receive CAN Frame.")
            logger.error("Error: ", e)

    def set_zero_position(self) -> None:
        """
        Sends command to set current position as Zero position.
        """
        try:
            self._send_can_frame(SET_ZERO_POSITION)
            wait_for(SET_ZERO_SLEEP)

            can_id, can_dlc, motorStatusData = self._recv_can_frame()
            # TODO: Do we need to process the status after setting zero position?
            # rawMotorData = self.decode_motor_status(motorStatusData)
            # pos, vel, curr = self.convert_raw_to_physical_rad(
            #     rawMotorData[0], rawMotorData[1], rawMotorData[2]
            # )
            logger.success("Zero Position set.")

        except Exception as e:
            logger.error("Error Setting Zero Position!")
            logger.error(f"Error: {e}")

    def enable_motor(self) -> None:
        """
        Sends the enable motor command to the motor.
        """
        try:
            # Remove the kick at the first initialization of the motor 
            self.set_zero_position()
            
            self._send_can_frame(ENTER_MOTOR_CONTROL_MODE)
            
            wait_for(DT_SLEEP)
            
            can_id, can_dlc, motorStatusData = self._recv_can_frame()
            # TODO: Do we need to process the status after setting zero position?
            # rawMotorData = self.decode_motor_status(motorStatusData)
            # pos, vel, curr = self.convert_raw_to_physical_rad(
            #     rawMotorData[0], rawMotorData[1], rawMotorData[2]
            # )
            logger.success("Motor Enabled.")
            
        except Exception as e:
            logger.error("Error Enabling Motor!")
            logger.error(f"Error: {e}")

    def disable_motor(self) -> None:
        """
        Sends the disable motor command to the motor.
        """
        try:
            # Remove the last command from the controller's memory
            _, _, _ = self.send_rad_command(0, 0, 0, 0, 0)

            # Disable the motor
            self._send_can_frame(EXIT_MOTOR_CONTROL_MODE)
            wait_for(DT_SLEEP)

            # Receive motor status after disabling
            _, _, status = self._recv_can_frame()
            logger.info("Motor disabled")

            # TODO: Do we need to process the status after disabling?
            # rawMotorData = self.decode_motor_status(status)
            # pos, vel, curr = self.convert_raw_to_physical_rad(
            #     rawMotorData[0], rawMotorData[1], rawMotorData[2]
            # )

        except Exception as e:
            logger.error("Error Disabling Motor!")
            logger.error(f"Error: {e}")

    def _decode_motor_status(self, data_frame) -> tuple[float, float, float]:
        """
        Decodes the motor status reply message into its constituent raw values.

        The CAN reply packet structure is as follows:
            - 16-bit position, between -4*pi and 4*pi
            - 12-bit velocity, between -30 and +30 rad/s
            - 12-bit current, between -40 and 40
            - CAN packet is 5 bytes (8 bits each)
            - Format:
            0: [position[15-8]]
            1: [position[7-0]]
            2: [velocity[11-4]]
            3: [velocity[3-0], current[11-8]]
            4: [current[7-0]]

        Args:
            data_frame (bytes): The CAN reply message from the motor.

        Returns:
            tuple[int, int, int]: Raw values for position, velocity, and current.
        """

        # Convert the message from motor to a bit string as this is easier to deal with than hex
        # while seperating individual values.
        self._recv_bytes.bytes = data_frame

        # Separate motor status values from the bit string.
        # Motor ID not considered necessary at the moment.
        # motor_id = self._recv_bytes.bytes [:8]
        position_bytes = self._recv_bytes.bin[8:24]
        velocity_bytes = self._recv_bytes.bin[24:36]
        current_bytes = self._recv_bytes.bin[36:48]

        # motor_id = int(motor_id, 2)
        positionRawValue = int(position_bytes, 2)
        velocityRawValue = int(velocity_bytes, 2)
        currentRawValue = int(current_bytes, 2)

        # TODO: Is it necessary/better to return motor_id?
        # return motor_id, positionRawValue, velocityRawValue, currentRawValue
        return positionRawValue, velocityRawValue, currentRawValue

    def _convert_raw_to_measured(
        self, raw_pos_value, raw_vel_value, raw_curr_value
    ) -> tuple[float, float, float]:
        """
        Converts raw motor values to physical units.

        Args:
            raw_pos_value (int): Raw position value from the motor.
            raw_vel_value (int): Raw velocity value from the motor.
            raw_curr_value (int): Raw current value from the motor.

        Returns:
            tuple: A tuple containing:
            - position (float): Position in radians.
            - velocity (float): Velocity in radians per second.
            - current (float): Current in amps.

        Note:
            CAN Reply Packet Structure:
            - 16-bit position, between -4*pi and 4*pi
            - 12-bit velocity, between -30 and +30 rad/s
            - 12-bit current, between -40 and 40
            - CAN Packet is 5 bytes (8 bits each)
            - Format:
                0: [position[15-8]]
                1: [position[7-0]]
                2: [velocity[11-4]]
                3: [velocity[3-0], current[11-8]]
                4: [current[7-0]]
        """

        measured_position_rad = uint_to_float(
            raw_pos_value, self.motor_cfg.pos_min, self.motor_cfg.pos_max, 16
        ) * self._rotation_direction
        measured_velocity_rad = uint_to_float(
            raw_vel_value, self.motor_cfg.vel_min, self.motor_cfg.vel_max, 12
        ) * self._rotation_direction
        measured_current = uint_to_float(
            raw_curr_value, self.motor_cfg.torque_min, self.motor_cfg.torque_max, 12
        ) * self._rotation_direction

        return measured_position_rad, measured_velocity_rad, measured_current

    def _convert_desired_to_raw(self, p_des_rad, v_des_rad, kp, kd, tau_ff) -> tuple[int, int, int, int, int]:
        # Correct the Axis Direction
        p_des_rad = p_des_rad * self._rotation_direction
        v_des_rad = v_des_rad * self._rotation_direction
        tau_ff = tau_ff * self._rotation_direction

        rawPosition = float_to_uint(
            p_des_rad, self.motor_cfg.pos_min, self.motor_cfg.pos_max, 16
        )
        rawVelocity = float_to_uint(
            v_des_rad, self.motor_cfg.vel_min, self.motor_cfg.vel_max, 12
        )
        rawTorque = float_to_uint(
            tau_ff, self.motor_cfg.torque_min, self.motor_cfg.torque_max, 12
        )

        rawKp = (MAX_RAW_KP * kp) / self.motor_cfg.kp_max

        rawKd = (MAX_RAW_KP * kd) / self.motor_cfg.kd_max

        return (
            int(rawPosition),
            int(rawVelocity),
            int(rawKp),
            int(rawKd),
            int(rawTorque),
        )

    def _send_raw_command(self, p_des, v_des, kp, kd, tau_ff):
        """
        Package and send raw (uint) values of correct length to the motor.

        _send_raw_command(desired position, desired velocity, position gain, velocity gain,
                        feed-forward torque)

        Sends data over CAN, reads response, and returns the motor status data (in bytes).
        """
        self._des_pos_bits.uint = p_des
        self._des_vel_bits.uint = v_des
        self._kp_bits.uint = kp
        self._kd_bits.uint = kd
        self._feed_forward_bits.uint = tau_ff
        cmd_bits = (
            self._des_pos_bits.bin
            + self._des_vel_bits.bin
            + self._kp_bits.bin
            + self._kd_bits.bin
            + self._feed_forward_bits.bin
        )

        self._cmd_bytes.bin = cmd_bits

        try:
            self._send_can_frame(self._cmd_bytes.tobytes())
            wait_for(DT_SLEEP)
            can_id, can_dlc, data = self._recv_can_frame()
            return data
        except Exception as e:
            logger.error("Error Sending Raw Commands!")
            logger.error(f"Error: {e}")

    def send_deg_command(self, p_des_deg, v_des_deg, kp, kd, tau_ff):
        """
        Function to send data to motor in physical units:
        send_deg_command(position (deg), velocity (deg/s), kp, kd, Feedforward Torque (Nm))
        Sends data over CAN, reads response, and prints the current status in deg, deg/s, amps.
        If any input is outside limits, it is clipped. Only if torque is outside limits, a log
        message is shown.
        """
        p_des_rad = math.radians(p_des_deg)
        v_des_rad = math.radians(v_des_deg)

        pos_rad, vel_rad, curr = self.send_rad_command(
            p_des_rad, v_des_rad, kp, kd, tau_ff
        )
        pos = math.degrees(pos_rad)
        vel = math.degrees(vel_rad)
        return pos, vel, curr

    def send_rad_command(self, p_des_rad, v_des_rad, kp, kd, tau_ff):
        """
        Function to send data to motor in physical units:
        send_rad_command(position (rad), velocity (rad/s), kp, kd, Feedforward Torque (Nm))
        Sends data over CAN, reads response, and prints the current status in rad, rad/s, amps.
        If any input is outside limits, it is clipped. Only if torque is outside limits, a log
        message is shown.
        """
        # Check for Torque Limits
        if tau_ff < self.motor_cfg.torque_min:
            logger.warning("Torque Commanded lower than the limit. Clipping Torque...")
            logger.warning("Commanded Torque: {}".format(tau_ff))
            logger.warning("Torque Limit: {}".format(self.motor_cfg.torque_min))
            tau_ff = self.motor_cfg.torque_min
        elif tau_ff > self.motor_cfg.torque_max:
            logger.warning("Torque Commanded higher than the limit. Clipping Torque...")
            logger.warning("Commanded Torque: {}".format(tau_ff))
            logger.warning("Torque Limit: {}".format(self.motor_cfg.torque_max))
            tau_ff = self.motor_cfg.torque_max

        # Clip Position if outside Limits
        p_des_rad = min(
            max(self.motor_cfg.pos_min, p_des_rad), self.motor_cfg.pos_max
        )
        # Clip Velocity if outside Limits
        v_des_rad = min(
            max(self.motor_cfg.vel_min, v_des_rad), self.motor_cfg.vel_max
        )
        # Clip Kp if outside Limits
        kp = min(max(self.motor_cfg.kp_min, kp), self.motor_cfg.kp_max)
        # Clip Kd if outside Limits
        kd = min(max(self.motor_cfg.kd_min, kd), self.motor_cfg.kd_max)

        rawPos, rawVel, rawKp, rawKd, rawTauff = self._convert_desired_to_raw(
            p_des_rad, v_des_rad, kp, kd, tau_ff
        )

        motorStatusData = self._send_raw_command(rawPos, rawVel, rawKp, rawKd, rawTauff)
        rawMotorData = self._decode_motor_status(motorStatusData)
        pos, vel, curr = self._convert_raw_to_measured(
            rawMotorData[0], rawMotorData[1], rawMotorData[2]
        )

        return pos, vel, curr


if __name__ == "__main__":
    pass
