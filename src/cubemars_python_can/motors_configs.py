from enum import Enum, unique
from dataclasses import dataclass

@unique
class RotationDirection(Enum):
    FORWARD = 1
    REVERSE = -1

@dataclass(frozen=True)
class MotorOperationRanges:
    pos_min: float
    pos_max: float
    vel_min: float
    vel_max: float
    torque_min: float
    torque_max: float
    kp_min: float
    kp_max: float
    kd_min: float
    kd_max: float


AK10_9_PARAMS: MotorOperationRanges = MotorOperationRanges(
    pos_min=-12.5,
    pos_max=12.5,
    vel_min=-50.0,
    vel_max=50.0,
    torque_min=-65.0,
    torque_max=65.0,
    kp_min=0.0,
    kp_max=500.0,
    kd_min=0.0,
    kd_max=5.0,
)

AK60_6_PARAMS: MotorOperationRanges = MotorOperationRanges(
    pos_min=-12.5,
    pos_max=12.5,
    vel_min=-45.0,
    vel_max=45.0,
    torque_min=-15.0,
    torque_max=15.0,
    kp_min=0.0,
    kp_max=500.0,
    kd_min=0.0,
    kd_max=5.0,
)


AK70_10_PARAMS: MotorOperationRanges = MotorOperationRanges(
    pos_min=-12.5,
    pos_max=12.5,
    vel_min=-50.0,
    vel_max=50.0,
    torque_min=-25.0,
    torque_max=25.0,
    kp_min=0.0,
    kp_max=500.0,
    kd_min=0.0,
    kd_max=5.0,
)

AK80_6_PARAMS: MotorOperationRanges = MotorOperationRanges(
    pos_min=-12.5,
    pos_max=12.5,
    vel_min=-76.0,
    vel_max=76.0,
    torque_min=-12.0,
    torque_max=12.0,
    kp_min=0.0,
    kp_max=500.0,
    kd_min=0.0,
    kd_max=5.0,
)

AK80_9_PARAMS: MotorOperationRanges = MotorOperationRanges(
    pos_min=-12.5,
    pos_max=12.5,
    vel_min=-50.0,
    vel_max=50.0,
    torque_min=-18.0,
    torque_max=18.0,
    kp_min=0.0,
    kp_max=500.0,
    kd_min=0.0,
    kd_max=5.0,
)

AK80_64_PARAMS: MotorOperationRanges = MotorOperationRanges(
    pos_min=-12.5,
    pos_max=12.5,
    vel_min=-8.0,
    vel_max=8.0,
    torque_min=-144.0,
    torque_max=144.0,
    kp_min=0.0,
    kp_max=500.0,
    kd_min=0.0,
    kd_max=5.0,
)

AK80_8_PARAMS: MotorOperationRanges = MotorOperationRanges(
    pos_min=-12.5,
    pos_max=12.5,
    vel_min=-37.5,
    vel_max=37.5,
    torque_min=-32.0,
    torque_max=32.0,
    kp_min=0.0,
    kp_max=500.0,
    kd_min=0.0,
    kd_max=5.0,
)

AK45_36_PARAMS: MotorOperationRanges = MotorOperationRanges(
    pos_min=-12.5,
    pos_max=12.5,
    vel_min=-6.0,
    vel_max=6.0,
    torque_min=34.0,
    torque_max=34.0,
    kp_min=0.0,
    kp_max=500.0,
    kd_min=0.0,
    kd_max=5.0,
)

AK45_10_PARAMS: MotorOperationRanges = MotorOperationRanges(
    pos_min=-12.5,
    pos_max=12.5,
    vel_min=-20.0,
    vel_max=20.0,
    torque_min=-8.0,
    torque_max=8.0,
    kp_min=0.0,
    kp_max=500.0,
    kd_min=0.0,
    kd_max=5.0,
)

AK40_10_PARAMS: MotorOperationRanges = MotorOperationRanges(
    pos_min=-12.5,
    pos_max=12.5,
    vel_min=-45.0,
    vel_max=45.0,
    torque_min=-5.0,
    torque_max=5.0,
    kp_min=0.0,
    kp_max=500.0,
    kd_min=0.0,
    kd_max=5.0,
)


BASE_MOTORS_CONFIGS = {
    "AK10_9": AK10_9_PARAMS,
    "AK60_6": AK60_6_PARAMS,
    "AK70_10": AK70_10_PARAMS,
    "AK80_6": AK80_6_PARAMS,
    "AK80_9": AK80_9_PARAMS,
    "AK80_64": AK80_64_PARAMS,
    "AK80_8": AK80_8_PARAMS,
    "AK45_36": AK45_36_PARAMS,
    "AK45_10": AK45_10_PARAMS,
    "AK40_10": AK40_10_PARAMS,
}


if __name__ == "__main__":
    pass
