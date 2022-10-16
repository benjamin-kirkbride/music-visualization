import multiprocessing as mp
import sys
import time

import tomli
import typer

from . import (
    PROJECT_ROOT,
    config,
    emulated_led_wall,
    frame_generation,
    remote_led_wall,
)

app = typer.Typer()


@app.command()
def main():
    frame_queues = []
    if config["emulator-window"]["enabled"]:
        emulator_frame_queue = mp.Queue()
        frame_queues.append(emulator_frame_queue)

    if config["led-matrix"]["enabled"]:
        remote_frame_queue = mp.Queue()
        frame_queues.append(remote_frame_queue)

    frame_generation_process = mp.Process(
        target=frame_generation.process_function,
        kwargs={
            "frame_queues": frame_queues,
            "teensy_port": config["serial_port"],
            "width": config["matrix_width"],
            "height": config["matrix_height"],
            "style": config["style"],
            "gradient_str": config["gradient"],
        },
        daemon=True,
    )
    frame_generation_process.start()

    if config["emulator-window"]["enabled"]:
        emulated_led_wall_process = mp.Process(
            target=emulated_led_wall.process,
            kwargs={
                "display_scale": config["emulator-window"]["display_scale"],
                "matrix_width": config["matrix_width"],
                "matrix_height": config["matrix_height"],
                "frame_queue": emulator_frame_queue,
            },
            daemon=True,
        )
        emulated_led_wall_process.start()

    if config["led-matrix"]["enabled"]:
        remote_led_wall_process = mp.Process(
            target=remote_led_wall.process,
            kwargs={
                "matrix_width": config["matrix_width"],
                "matrix_height": config["matrix_height"],
                "frame_queue": remote_frame_queue,
                "led_wall_server": config["led-matrix"]["url"],
                "brightness": config["led-matrix"]["brightness"],
            },
            daemon=True,
        )
        remote_led_wall_process.start()

    while True:
        # this ensures on first loop that the processes have time to start
        # also prevents the loop from running too hot
        time.sleep(0.1)
        if not frame_generation_process.is_alive():
            sys.exit()

        if config["emulator-window"]["enabled"]:
            if not emulated_led_wall_process.is_alive():
                sys.exit("Emulator Window closed, exiting...")

        if config["led-matrix"]["enabled"]:
            if not remote_led_wall_process.is_alive():
                sys.exit(
                    "Process sending frames to the led matrix stopped, exiting..."
                )


if __name__ == "__main__":
    app()
