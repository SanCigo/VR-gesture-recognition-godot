import json
import os
import matplotlib.pyplot as plt

def main():
    if not os.path.exists("p_c_data.json"):
        print("Could not find p_c_data.json. Please run the Godot JSON exporter first.")
        return

    with open("p_c_data.json", "r") as f:
        gestures = json.load(f)

    if not gestures:
        print("The JSON file is empty. No gestures found.")
        return

    for gesture in gestures:
        name = gesture["name"]
        points = gesture["points"]
        
        x = [p["x"] for p in points]
        y = [p["y"] for p in points]
        z = [p["z"] for p in points]
        
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot the path sequence
        ax.plot(x, y, z, marker='o', linestyle='-', markersize=4, label="Path", color="blue")
        
        # Highlight start (Green) and end (Red) points
        ax.scatter(x[0], y[0], z[0], color='green', s=100, label='Start', zorder=5)
        ax.scatter(x[-1], y[-1], z[-1], color='red', s=100, label='End', zorder=5)
        
        ax.set_title(f"Gesture Template: {name}")
        ax.set_xlabel('X Axis (Meters)')
        ax.set_ylabel('Y Axis (Meters)')
        ax.set_zlabel('Z Axis (Meters)')
        
        # Keep aspect ratio roughly equal if desired, scaling dynamically
        ax.legend()
        
        # Show interactive window (closes when you hit X, then moves to next gesture)
        print(f"Displaying {name}...")
        plt.show()

if __name__ == "__main__":
    main()
