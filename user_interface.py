import tkinter as tk
import pandas as pd
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import time
from threading import Lock

# Load the data
try:
    data = pd.read_csv("AAPL_data.csv", index_col=0, parse_dates=True, skiprows=1)
    data.columns = data.columns.str.strip()  # Clean column names
    data.index = pd.to_datetime(data.index, errors='coerce')  # Ensure index is datetime
    data = data.dropna()  # Drop rows with invalid datetime
    print("Data loaded successfully")
except Exception as e:
    print(f"Error loading data: {e}")

# Create the main window
root = tk.Tk()
root.title("Bar Replay App")

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, fill=tk.X)

# Create Start, Pause/Play, Stop, Forward, Rewind, Buy, Sell, Clear Indicators, and Trend Line buttons
start_button = tk.Button(button_frame, text="Start", command=lambda: start_replay())
pause_play_button = tk.Button(button_frame, text="Pause", command=lambda: toggle_pause_play())
stop_button = tk.Button(button_frame, text="Stop", command=lambda: stop_replay())
forward_button = tk.Button(button_frame, text="Forward", command=lambda: forward())
rewind_button = tk.Button(button_frame, text="Rewind", command=lambda: rewind())
buy_button = tk.Button(button_frame, text="Buy", command=lambda: set_mode("buy"), bg="green", fg="white")
sell_button = tk.Button(button_frame, text="Sell", command=lambda: set_mode("sell"), bg="red", fg="white")
clear_button = tk.Button(button_frame, text="Clear Indicators", command=lambda: clear_indicators())
trend_button = tk.Button(button_frame, text="Trend Line", command=lambda: set_mode("trend"))
delete_annotation_button = tk.Button(button_frame, text="Delete Annotation", command=lambda: delete_annotation())

start_button.pack(side=tk.LEFT, padx=5, pady=5)
pause_play_button.pack(side=tk.LEFT, padx=5, pady=5)
stop_button.pack(side=tk.LEFT, padx=5, pady=5)
forward_button.pack(side=tk.LEFT, padx=5, pady=5)
rewind_button.pack(side=tk.LEFT, padx=5, pady=5)
buy_button.pack(side=tk.LEFT, padx=5, pady=5)
sell_button.pack(side=tk.LEFT, padx=5, pady=5)
clear_button.pack(side=tk.LEFT, padx=5, pady=5)
trend_button.pack(side=tk.LEFT, padx=5, pady=5)
delete_annotation_button.pack(side=tk.LEFT, padx=5, pady=5)

# Create a canvas for the chart
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Variables to control the replay and annotations
is_running = False
is_paused = False
current_index = 0
mode = None
annotations = []  # Store annotations
trend_points = []  # Store points for the trend line
buy_sell_annotations = []  # Store buy/sell annotations (arrows)
selected_annotation = None  # Keep track of the annotation to be deleted
lock = Lock()  # Thread lock for shared resources
replay_thread = None  # Store the replay thread to ensure proper shutdown

def update_chart():
    global current_index, selected_annotation
    ax.clear()

    # Plot the chart
    try:
        mpf.plot(data.iloc[:current_index], type='candle', style='charles', ax=ax)
    except Exception as e:
        print(f"Error while plotting the chart: {e}")

    # Reapply all stored annotations except the selected one for deletion
    for annotation in annotations:
        if annotation != selected_annotation:
            if annotation["type"] == "trend":
                x1, y1, x2, y2 = annotation["coords"]
                ax.plot([x1, x2], [y1, y2], color="blue", linewidth=2)
            else:
                ax.annotate(annotation["label"], xy=annotation["xy"], xytext=annotation["xytext"],
                            arrowprops=dict(facecolor=annotation["color"], arrowstyle='->', lw=2), fontsize=12, color=annotation["color"])

    # Draw buy/sell markers
    for ann in buy_sell_annotations:
        ax.annotate(ann["label"], xy=ann["xy"], xytext=(ann["xy"][0], ann["xy"][1] + 5),
                    arrowprops=dict(facecolor=ann["color"], arrowstyle='->', lw=2), fontsize=12, color=ann["color"])

    canvas.draw()

def replay():
    global current_index, is_running, is_paused, replay_thread
    while True:
        with lock:
            if not is_running:
                break
            if not is_paused and current_index < len(data):
                current_index += 1
                update_chart()
            elif current_index >= len(data):  # Stop when reaching the end of data
                is_running = False
                break
        time.sleep(0.5)  # Reduce update frequency to prevent overloading

def start_replay():
    global is_running, is_paused, current_index, replay_thread
    with lock:
        if not is_running:
            is_running = True
            is_paused = False
            current_index = 0  # Reset to the beginning
            forward_button.config(state=tk.DISABLED)  # Disable forward button during replay
            replay_thread = threading.Thread(target=replay, daemon=True)
            replay_thread.start()
        else:
            print("Replay is already running")

def toggle_pause_play():
    global is_paused
    with lock:
        if is_running:
            is_paused = not is_paused
            pause_play_button.config(text="Play" if is_paused else "Pause")
            if is_paused:  # Re-enable forward button when paused
                forward_button.config(state=tk.NORMAL)
            else:  # Disable forward button when playing
                forward_button.config(state=tk.DISABLED)

def stop_replay():
    global is_running, is_paused, current_index, replay_thread
    with lock:
        is_running = False
        is_paused = False
        current_index = 0  # Reset to start
        forward_button.config(state=tk.NORMAL)  # Enable forward button when stopped
        if replay_thread is not None and replay_thread.is_alive():
            replay_thread.join()  # Ensure the thread has stopped before continuing
    update_chart()
    pause_play_button.config(text="Pause")

def forward():
    global current_index
    with lock:
        if current_index < len(data) - 1:  # Stay within bounds
            current_index += 1
            update_chart()

def rewind():
    global current_index, is_paused
    with lock:
        if current_index > 0:  # Stay within bounds
            current_index -= 1
            update_chart()
        is_paused = True  # Pause after rewinding
        pause_play_button.config(text="Play")

def set_mode(new_mode):
    global mode
    with lock:
        mode = new_mode
        print(f"Mode set to {mode}")

def clear_indicators():
    global annotations, trend_points, buy_sell_annotations
    with lock:
        annotations = []
        trend_points = []
        buy_sell_annotations = []  # Clear buy/sell markers
    update_chart()

def delete_annotation():
    global annotations, selected_annotation

    if selected_annotation is None:
        print("No annotation selected for deletion")
        return

    # Remove the selected annotation from the list
    annotations = [ann for ann in annotations if ann != selected_annotation]
    selected_annotation = None

    # Update the chart to reflect the deletion
    update_chart()

def on_click(event):
    global mode, trend_points, selected_annotation, buy_sell_annotations

    if event.xdata is None or event.ydata is None:
        return

    with lock:
        if mode == "trend":
            trend_points.append((event.xdata, event.ydata))
            if len(trend_points) == 2:
                x1, y1 = trend_points[0]
                x2, y2 = trend_points[1]
                dx = x2 - x1
                dy = y2 - y1
                extension_factor = 2
                x2_extended = x2 + extension_factor * dx
                y2_extended = y2 + extension_factor * dy
                annotations.append({"type": "trend", "coords": [x1, y1, x2_extended, y2_extended]})
                trend_points = []
                # Reset mode after drawing trendline
                mode = None
                print(f"Trendline drawn from ({x1}, {y1}) to ({x2_extended}, {y2_extended})")
        elif mode == "buy" or mode == "sell":
            buy_sell_annotations.append({"label": "Buy" if mode == "buy" else "Sell",
                                         "xy": (event.xdata, event.ydata), "color": "green" if mode == "buy" else "red"})
            print(f"{mode.capitalize()} annotation added at {event.xdata}, {event.ydata}")
        else:
            # Check if we're in deletion mode
            clicked_annotation = None
            click_threshold = 0.5  # Increased threshold for easier selection

            for annotation in annotations:
                if annotation["type"] == "trend":
                    x1, y1, x2, y2 = annotation["coords"]
                    # Check if click is near the trend line
                    if is_point_near_line((event.xdata, event.ydata), (x1, y1), (x2, y2), click_threshold):
                        clicked_annotation = annotation
                        break

            if clicked_annotation:
                selected_annotation = clicked_annotation
                print(f"Annotation selected: {selected_annotation}")
            else:
                print("No annotation clicked")

    update_chart()

def is_point_near_line(point, line_start, line_end, threshold):
    """Helper function to check if a point is near a line"""
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end

    # Line equation parameters
    dx = x2 - x1
    dy = y2 - y1
    line_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    if line_length == 0:
        return False

    # Perpendicular distance formula
    distance = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / line_length

    return distance < threshold

# Bind the click event for adding/removing annotations
fig.canvas.mpl_connect('button_press_event', on_click)

# Start the Tkinter event loop
root.mainloop()
