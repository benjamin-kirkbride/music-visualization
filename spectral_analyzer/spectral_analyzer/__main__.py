import multiprocessing as mp

import typer

from . import emulated_led_wall, frame_generation, remote_led_wall

PANEL_WIDTH = 48
PANEL_HEIGHT = 27
DISPLAY_SCALE = 40

WINDOW_WIDTH = PANEL_WIDTH * DISPLAY_SCALE
WINDOW_HEIGHT = PANEL_HEIGHT * DISPLAY_SCALE

REMOTE_LED_WALL_FRAME_RATE = 1 / 60

app = typer.Typer()


@app.command()
def bar():
    typer.echo("I'm just here to mess things up...")


# what runs if no command is specified on CLI
@app.command()
def main():
    """Main function"""
    emulator_frame_queue = mp.Queue()
    remote_frame_queue = mp.Queue()

    frame_generation_process = mp.Process(
        target=frame_generation.process_function,
        kwargs={
            "frame_queues": [emulator_frame_queue, remote_frame_queue],
            "teensy_port": "/dev/ttyACM0",
            "width": PANEL_WIDTH,
            "height": PANEL_HEIGHT,
        },
    )
    frame_generation_process.start()

    emulated_led_wall_process = mp.Process(
        target=emulated_led_wall.process,
        kwargs={
            "window_width": WINDOW_WIDTH,
            "window_height": WINDOW_HEIGHT,
            "panel_width": PANEL_WIDTH,
            "panel_height": PANEL_HEIGHT,
            "display_scale": DISPLAY_SCALE,
            "frame_queue": emulator_frame_queue,
        },
    )
    emulated_led_wall_process.start()

    remote_led_wall_process = mp.Process(
        target=remote_led_wall.process,
        kwargs={
            "panel_width": PANEL_WIDTH,
            "panel_height": PANEL_HEIGHT,
            "frame_rate": REMOTE_LED_WALL_FRAME_RATE,
            "frame_queue": remote_frame_queue,
            "led_wall_server": "led-wall.caverage.lan:12345",
        },
    )
    remote_led_wall_process.start()


if __name__ == "__main__":
    app()
