# reference: https://gist.github.com/lbussy/9e81cbcc617952f1250e353bd42e7775
from os import getuid, system
from sys import exit
from time import sleep

from gpiozero import Button

stopPin = 15
stopButton = Button(stopPin)  # defines the button as an object and chooses GPIO pin


def isRoot():
    if getuid() != 0:
        return False
    else:
        return True


def main():
    print("\nMonitoring pin {} for reboot signal.".format(stopPin))
    print("Ctrl-C to quit.\n")

    try:
        while True:
            if stopButton.is_pressed:
                sleep(0.5)
                if stopButton.is_pressed:
                    system("shutdown now -h")
            sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt.")

    finally:
        pass

    return


if __name__ == "__main__":
    if not (isRoot()):
        print("\nScript must be run as root.")
        exit(1)
    else:
        main()
        exit(0)
