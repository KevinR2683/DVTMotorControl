import tkinter as tk
import time
import threading

class MotorControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DVT Lab Test Program Selection")

        # Test Name
        self.label_test_name = tk.Label(root, text="Test Name")
        self.label_test_name.grid(row=0, column=0, padx=10, pady=10)

        self.entry_test_name = tk.Entry(root)
        self.entry_test_name.grid(row=0, column=1, padx=10, pady=10)

        # Max Cycle Count
        self.label_max_cycle_count = tk.Label(root, text="Max Cycle Count")
        self.label_max_cycle_count.grid(row=0, column=2, padx=10, pady=10)

        self.entry_max_cycle_count = tk.Entry(root)
        self.entry_max_cycle_count.grid(row=0, column=3, padx=10, pady=10)

        # Positive Force Value
        self.label_positive_force = tk.Label(root, text="Positive Force(ft-lbs)")
        self.label_positive_force.grid(row=1, column=0, padx=10, pady=10)

        self.entry_positive_force = tk.Entry(root)
        self.entry_positive_force.grid(row=1, column=1, padx=10, pady=10)

        # Negative Force Value
        self.label_negative_force = tk.Label(root, text="Negative Force(ft-lbs)")
        self.label_negative_force.grid(row=1, column=2, padx=10, pady=10)

        self.entry_negative_force = tk.Entry(root)
        self.entry_negative_force.grid(row=1, column=3, padx=10, pady=10)
        
        # Test Status
        self.label_test_status = tk.Label(root, text="Test Status: Not Running", bg="red", fg="white")
        self.label_test_status.grid(row=3, column=2, columnspan=2, padx=10, pady=10)

        # Cycle Counter
        self.label_cycle_counter = tk.Label(root, text="Current Cycle: 0")
        self.label_cycle_counter.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Motor Direction
        self.label_motor_direction = tk.Label(root, text="Motor Direction: None")
        self.label_motor_direction.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Checkbox to control Clockwise and Counter-Clockwise buttons
        self.checkbox_control = tk.Checkbutton(root, text="Enable Motor Control", command=self.update_button_state)
        self.checkbox_control.grid(row=4, column=2, columnspan=2, padx=10, pady=10)

        # Test Selection Area (Drop-down Menu)
        self.label_test_selection = tk.Label(root, text="Test Selection:")
        self.label_test_selection.grid(row=6, column=1, padx=10, pady=10, sticky=tk.W)

        self.test_options = ["None", "Lifetime", "CARLL", "Center Structure CARLL", "BFALTA", "Torsion", "Side Push", "Gear Box Testing"]
        self.selected_test = tk.StringVar()
        self.selected_test.set("None")
        self.test_dropdown = tk.OptionMenu(root, self.selected_test, *self.test_options)
        self.test_dropdown.grid(row=6, column=2, padx=10, pady=10, sticky=tk.W)

        # Buttons (initially disabled)
        self.button_start_test = tk.Button(root, text="Start Test", command=self.start_test)
        self.button_start_test.grid(row=8, column=1, padx=10, pady=10)
        self.button_start_test.config(activebackground="green")

        self.button_end_test = tk.Button(root, text="End Test", command=self.stop_test, state=tk.DISABLED)
        self.button_end_test.grid(row=8, column=2, padx=10, pady=10)

        self.button_rotate_clockwise = tk.Button(root, text="Rotate Clockwise", command=self.rotate_clockwise, state=tk.DISABLED)
        self.button_rotate_clockwise.grid(row=9, column=1, padx=10, pady=10)

        self.button_rotate_counterclockwise = tk.Button(root, text="Rotate Counter-Clockwise", command=self.rotate_counterclockwise, state=tk.DISABLED)
        self.button_rotate_counterclockwise.grid(row=9, column=2, padx=10, pady=10)

        # Motor Direction Indicator
        self.label_motor_direction = tk.Label(root, text="Motor Direction: None")
        self.label_motor_direction.grid(row=10, column=1, columnspan=2, padx=10, pady=10)

        # Motor Status Indicator
        self.label_motor_status = tk.Label(root, text="Motor Status: Not Running", bg="red", fg="white")
        self.label_motor_status.grid(row=11, column=1, columnspan=2, padx=10, pady=10)

        # Countdown Labels
        self.label_clockwise_countdown = tk.Label(root, text="Clockwise: --")
        self.label_clockwise_countdown.grid(row=14, column=1, padx=10, pady=10)

        self.label_counterclockwise_countdown = tk.Label(root, text="Counter-Clockwise: --")
        self.label_counterclockwise_countdown.grid(row=14, column=2, padx=10, pady=10)

        # Initialize variables
        self.current_cycle = 0
        self.max_cycle_count = 10  # Example max cycle count
        self.test_running = False
        self.stop_flag = False
        self.last_cycle_time = time.time()
        self.motor_thread = None
        self.active_test = "None"
        self.motor_control_enabled = False

    def update_button_state(self):
        self.motor_control_enabled = not self.motor_control_enabled
        if self.motor_control_enabled:
            self.button_rotate_clockwise.config(state=tk.NORMAL)
            self.button_rotate_counterclockwise.config(state=tk.NORMAL)
        else:
            self.button_rotate_clockwise.config(state=tk.DISABLED)
            self.button_rotate_counterclockwise.config(state=tk.DISABLED)

    def rotate_clockwise(self):
        if self.test_running and self.motor_control_enabled:
            control_motor('clockwise', 'rotate')
            self.label_motor_direction.config(text="Motor Direction: Clockwise")
            self.update_cycle_counter()
        elif not self.test_running:
            self.label_test_status.config(text="Error: Test is not running.")
        else:
            self.label_test_status.config(text="Error: Motor control is disabled.")

    def rotate_counterclockwise(self):
        if self.test_running and self.motor_control_enabled:
            control_motor('counter-clockwise', 'rotate')
            self.label_motor_direction.config(text="Motor Direction: Counter-Clockwise")
            self.update_cycle_counter()
        elif not self.test_running:
            self.label_test_status.config(text="Error: Test is not running.")
        else:
            self.label_test_status.config(text="Error: Motor control is disabled.")

    def start_test(self):
        test_name = self.entry_test_name.get()
        max_cycle_count = self.entry_max_cycle_count.get()
        if test_name and max_cycle_count:
            try:
                max_cycle_count = int(max_cycle_count)
                self.current_cycle = 0
                self.max_cycle_count = max_cycle_count
                self.label_cycle_counter.config(text=f"Current Cycle: {self.current_cycle}")
                self.test_running = True
                self.label_test_status.config(text="Test Status: Running", bg="green")
                self.label_motor_direction.config(text="Motor Direction: None")
									  
																
                self.button_end_test.config(state=tk.NORMAL)

                self.motor_thread = threading.Thread(target=self.run_test)
                self.motor_thread.start()
            except ValueError:
                self.label_test_status.config(text="Error: Max Cycle Count must be an integer.")
        else:
            self.label_test_status.config(text="Error: Please enter both Test Name and Max Cycle Count.")

    def stop_test(self):
			
        self.test_running = False
        self.stop_flag = True					
        self.label_test_status.config(text="Test Status: Not Running", bg="red")
        self.label_motor_direction.config(text="Motor Direction: None")			  
        self.button_end_test.config(state=tk.DISABLED)
        if self.motor_thread and self.motor_thread.is_alive():
            self.motor_thread.join()
        # Add logic to stop the test

    def update_cycle_counter(self):
        self.current_cycle += 1
        self.label_cycle_counter.config(text=f"Current Cycle: {self.current_cycle}")

    def run_test(self):
        while self.test_running and self.current_cycle < self.max_cycle_count:
            if self.stop_flag:
                break
            # Rotate motor clockwise
            self.label_motor_direction.config(text="Motor Direction: Clockwise")
																	  
            for i in range(5, 0, -1):
                self.label_clockwise_countdown.config(text=f"Clockwise: {i}")
                time.sleep(1)
            # Wait for 1 second
            time.sleep(1)

            # Rotate motor counterclockwise
            self.label_motor_direction.config(text="Motor Direction: Counter-Clockwise")
																					 
            for i in range(5, 0, -1):
                self.label_counterclockwise_countdown.config(text=f"Counter-Clockwise: {i}")
                time.sleep(1)
            # Wait for 1 second
            time.sleep(1)

            # Update cycle counter
            self.update_cycle_counter()

        self.stop_test()

def control_motor(direction, action):
    # Placeholder function to control the motor.
    # Replace this with actual code to control your motor.
    print(f"Motor {action} {direction}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MotorControlApp(root)
    root.mainloop()
