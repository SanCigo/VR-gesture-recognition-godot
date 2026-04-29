# VR Gesture Recognition for Godot

A 3D gesture recognition module for VR in Godot, using the [$P Point-Cloud Recognizer](https://depts.washington.edu/acelab/proj/dollar/pdollar.html) algorithm adapted for 3D space.

**Demonstration video:** https://youtu.be/tnYyMb3XGeg

---

## Dependencies

- [Godot Oculus Quest Toolkit](https://github.com/NeoSpark314/godot_oculus_quest_toolkit) — provides the VR runtime, controller input, and UI components used throughout this project.

---

## How It Works

A tracked object (`Position3D`) is attached as a child of each `ARVRController` node. As the controller moves, its 3D position is sampled into a point array. When tracking ends, the array is normalized and compared against stored gesture templates using the $P cloud-matching algorithm. The best-matching template name and a confidence score are returned.

### Algorithm Overview

1. **Resample** — the raw point path is resampled to a fixed number of equidistant points (`NumPoints = 32`).
2. **Scale** — the cloud is scaled to fit a unit bounding box.
3. **Translate** — the cloud is centred at the origin.
4. **Match** — the processed candidate cloud is compared against every stored template using the greedy cloud-distance algorithm. The template with the lowest distance score wins.

---

## Modes

The system has two node variants that can be placed in the scene:

### Developer Mode (`scenes/tracked_object/developer/`)

Use this during development to record, name, and manage gesture templates.

- **Add gestures** — creates new templates and saves them to disk automatically.
- **Delete gestures** — clears all stored templates from disk.
- **Custom names** — optional VR keyboard support lets you name each gesture; without it, gestures are named `template_1`, `template_2`, etc.
- Exported inspector property `load_previous_data` can be enabled to reload previously saved templates on startup.

### Gameplay Mode (`scenes/tracked_object/gameplay/`)

Use this in the shipped game. It has no add/delete UI and only loads the templates that were saved in Developer mode.

- Automatically loads templates from `user://p_c_data.dat` on startup.
- Forwards every recognition result to the `action_manager` node.

To switch between modes, set the `Mode` export property on the tracked object node in the Godot Inspector (`Developer` or `Gameplay`).

---

## How to Use

### 1. Recording Gestures (Developer Mode)

1. Open the project and run in Developer mode on your headset.
2. **Press the Index Trigger** on either controller to start tracking. Any 3D movement of the controller is recorded.
3. **Release the Index Trigger** to stop tracking.
   - If **Add Mode** is active, the movement is saved as a new template.
   - Otherwise, the system attempts to recognise the movement against existing templates.
4. To enter Add Mode, press the **Add** button on the VR UI panel:
   - If `custom_names` is disabled, the gesture is automatically named `template_1`, `template_2`, etc.
   - If `custom_names` is enabled, a VR keyboard appears — type the desired name and confirm.
5. Press **Cancel** to exit Add Mode without recording.
6. Press **Delete** to clear all stored gesture templates.

### 2. Recognising Gestures (both modes)

1. In Idle state, **press and hold the Index Trigger** to begin tracking.
2. Perform your gesture movement.
3. **Release the Index Trigger** — the system recognises the gesture and displays the matched name and confidence score on the UI label.
4. The result is also forwarded to the `action_manager` node, which executes the bound function.

### 3. Tracking Types

The `Tracking_type` export property controls how tracking starts and stops:

| Value | Behaviour |
|-------|-----------|
| `Buttons` | Tracking starts when the Index Trigger is held and stops when it is released. |
| `Velocity` | Tracking starts automatically when controller velocity ≥ 1 m/s and stops when velocity drops below 1 m/s. |

---

## Gesture Persistence (Save / Load)

Gesture templates are persisted using Godot's `user://` data directory.

| File | Path | Description |
|------|------|-------------|
| `p_c_data.dat` | `user://p_c_data.dat` | Binary file containing all recorded gesture point clouds. |

- **Saving** — every time a new gesture is added in Developer mode, the full template list is written to `user://p_c_data.dat` using Godot's `File.store_var()`.
- **Loading** — Gameplay mode loads this file on startup (`_ready()`). Developer mode loads it when the `load_previous_data` export property is enabled.
- **Deleting** — the Delete button in Developer mode overwrites the file with an empty array.

On Oculus Quest / Android, `user://` resolves to the app's internal storage directory. On desktop, it resolves to the OS user data folder reported by `OS.get_user_data_dir()`.

---

## Binding Gestures to Game Actions

Recognised gestures are forwarded to the `action_manager` node (`scripts/action_manager.gd`). Edit this file to map gesture names to game functions.

```gdscript
# action_manager.gd
var actions_list = {
    "template_1": funcref(self, "action_a"),
    "template_2": funcref(self, "action_b"),
    "template_3": funcref(self, "action_c")
}

func action_a(controller):
    # Called when "template_1" is recognised
    pass
```

**Rules:**
- The keys in `actions_list` must exactly match the gesture names used when recording in Developer mode.
- Each function receives the `controller_id` of the controller that performed the gesture.

### Two-Handed Gestures

The action manager supports two-handed combinations. If the **same gesture name** is recognised by both the left controller (`controller_id = 1`) and the right controller (`controller_id = 2`) within the same action stack frame (their IDs sum to 3), the action is triggered once as a two-handed gesture. Otherwise each hand fires its bound action independently.

---

## Export Variables (Inspector Properties)

These properties can be set in the Godot Inspector on the tracked object node:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Mode` | Enum | `Developer` | `Developer` enables template management UI; `Gameplay` loads-only. |
| `Tracking_type` | Enum | `Buttons` | `Buttons` uses the index trigger; `Velocity` uses controller speed. |
| `ignore_Y_orientation` | bool | `true` | When `true`, gestures are matched independently of the player's horizontal rotation, making recognition consistent regardless of which direction the player is facing. |
| `custom_names` | bool | `false` | *(Developer only)* When `true`, a VR keyboard is shown to name each gesture. When `false`, gestures are auto-named sequentially. |
| `load_previous_data` | bool | `false` | *(Developer only)* When `true`, previously saved templates are loaded from disk at startup. |

---

## Project Structure

```
scenes/
  game/
    main.tscn              # Main scene entry point
    vr_player.tscn         # VR player rig with both controllers
    vr_player.gd           # Shows/hides VR keyboard on add press
  tracked_object/
    developer/
      Q_recog_tracked_obj_dev.tscn   # Developer mode scene
      tracked_obj_dev.gd             # Dev mode logic (add/delete/save/recognize)
    gameplay/
      Q_recog_tracked_obj_game.tscn  # Gameplay mode scene
      tracked_obj_game.gd            # Gameplay mode logic (load/recognize only)

scripts/
  GameMain.gd              # Initialises VR and loads the main scene
  action_manager.gd        # Maps gesture names to game functions
  vr_player.gd             # (unused stub)
``` 
