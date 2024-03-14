import time
from django.core.management.base import BaseCommand
import pyautogui
def get_current_position():
    return pyautogui.position()

def calculate_distance(p1, p2):
    return ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)**0.5

def calculate_speed(distance, elapsed_time):
    if elapsed_time == 0:
        return 0
    return distance / elapsed_time
class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):



        print("Move the mouse to change the position.")
        print("Press Ctrl+C to exit.")

        start_time = time.time()  # Initialize start_time outside the loop

        try:
            last_position = get_current_position()

            while True:
                current_position = get_current_position()

                if current_position != last_position:
                    distance = calculate_distance(last_position, current_position)
                    elapsed_time = time.time() - start_time
                    speed = calculate_speed(distance, elapsed_time)

                    print(f"Position: {current_position}, Distance: {distance:.2f} pixels, Speed: {speed:.2f} pixels per second")

                    last_position = current_position
                    start_time = time.time()

                time.sleep(0.1)  # Adjust the sleep duration as needed

        except KeyboardInterrupt:
            print("\nProgram terminated by user.")


