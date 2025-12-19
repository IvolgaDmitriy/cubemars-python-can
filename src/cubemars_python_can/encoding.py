from cubemars_python_can import protocol_defs

def float_to_uint(x, x_min, x_max, numBits):
    span = x_max - x_min
    offset = x_min

    if numBits == 16:
        bitRange = protocol_defs.MAX_RAW_POSITION
    elif numBits == 12:
        bitRange = protocol_defs.MAX_RAW_VELOCITY
    else:
        bitRange = 2**numBits - 1
    return int(((x - offset) * (bitRange)) / span)


def uint_to_float(x_int, x_min, x_max, numBits):
    span = x_max - x_min
    offset = x_min
    if numBits == 16:
        bitRange = protocol_defs.MAX_RAW_POSITION
    elif numBits == 12:
        bitRange = protocol_defs.MAX_RAW_VELOCITY
    else:
        bitRange = 2**numBits - 1
    return ((x_int * span) / (bitRange)) + offset

if __name__ == "__main__":
    pass
