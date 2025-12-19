import time

from cubemars_python_can.protocol_defs import DT_SLEEP


def wait_for(dt: float) -> None:
    end = time.perf_counter() + dt
    while True:
        remaining = end - time.perf_counter()
        if remaining <= 0:
            break
        time.sleep(min(remaining, DT_SLEEP))


if __name__ == "__main__":
    pass
