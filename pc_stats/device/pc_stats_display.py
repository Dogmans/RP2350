import sys
import uselect

from lcd_1in28 import LCD_1inch28


def parse_arg(arg):
    """Parse argument as int or return as string."""
    try:
        return int(arg)
    except ValueError:
        return arg


def execute_command(lcd, line):
    """Parse CSV command and execute on lcd object."""
    parts = line.strip().split(',')
    if not parts:
        return
    
    cmd = parts[0]
    args = [parse_arg(arg) for arg in parts[1:]]
    
    try:
        # Handle special method name mappings
        if cmd == "circle":
            # MicroPython FrameBuffer doesn't have circle, draw with ellipse or skip
            # For now, use hline/vline to approximate or just skip
            pass
        else:
            method = getattr(lcd, cmd)
            method(*args)
    except Exception:
        pass


def main():
    lcd = LCD_1inch28()
    lcd.set_bl_pwm(40000)

    poller = uselect.poll()
    poller.register(sys.stdin, uselect.POLLIN)

    while True:
        if poller.poll(100):
            line = sys.stdin.readline()
            if line:
                execute_command(lcd, line)


if __name__ == "__main__":
    main()
