import re
import math

class WorldState:
    def __init__(self, style_profile):
        self.main_character = style_profile.get("character_bible", "Generic character")
        self.palette = style_profile.get("palette_bible", "Muted colors")
        self.camera_base = style_profile.get("camera_bible", "Cinematic")
        self.known_objects = set()

class StoryState:
    def __init__(self):
        self.current_location = "Unknown Location"
        self.current_time_offset = 0 # minutes
        self.current_atmosphere = "Normal"
        self.visible_objects = []
        self.event_type = "NORMAL"

EVENT_LIGHTING = {
    "NORMAL": "Natural cinematic lighting, soft shadows",
    "WARNING": "Dim lighting, long unsettled shadows, atmospheric gloom",
    "ESCALATION": "High contrast, harsh noir lighting, stark shadows",
    "DANGER": "Chaotic lighting, intense highlights, deep blacks, rim lighting",
    "AFTERMATH": "Cold, desaturated diffuse light, flat contrast, melancholic"
}

def build_storyboard(script_json, style_profile):
    script_text = script_json.get("script_text", "")
    # Split into beats (sentences), simple regex
    raw_beats = [s.strip() for s in re.split(r'[.!?]+', script_text) if s.strip()]
    
    total_beats = len(raw_beats)
    beats_per_scene = max(1, math.ceil(total_beats / 16))
    
    world = WorldState(style_profile)
    state = StoryState()
    
    writer_scenes = script_json.get("scenes", [])
    if writer_scenes and isinstance(writer_scenes[0], dict):
        state.current_location = writer_scenes[0].get("location", "Location 1")
    
    final_scenes = []
    
    for i in range(16):
        # 0. Deterministic Beat Assignment
        start = i * beats_per_scene
        end = min(start + beats_per_scene, total_beats)
        scene_beats = raw_beats[start:end]
        beat_text = " ".join(scene_beats)
        
        # 1. Deterministic Time Updates
        state.current_time_offset += 2 # +2 mins per scene default
        
        # 2. Deterministic Event Flow Curve
        if i < 4: state.event_type = "NORMAL"
        elif i < 7: state.event_type = "WARNING"
        elif i < 11: state.event_type = "ESCALATION"
        elif i < 15: state.event_type = "DANGER"
        else: state.event_type = "AFTERMATH"
        
        # 3. Location/Object Continuity from Writer Suggestions
        # We trust the Writer's location changes but enforce persistence if writer is vague
        if i < len(writer_scenes) and isinstance(writer_scenes[i], dict):
             suggested_loc = writer_scenes[i].get("location")
             if suggested_loc and suggested_loc != state.current_location:
                 state.current_location = suggested_loc
             
             new_objs = writer_scenes[i].get("visible_objects", [])
             state.visible_objects = list(set(state.visible_objects + new_objs)) # Accumulate

        # 4. Construct Scene Data (V4 Schema)
        lighting_prompt = EVENT_LIGHTING.get(state.event_type, EVENT_LIGHTING["NORMAL"])
        
        scene_data = {
            "beat_text": beat_text,
            "main_subject": f"{world.main_character}",
            "action": f"Scene {i+1} action based on: {beat_text[:50]}...", 
            "location": state.current_location,
            "time": f"T+{state.current_time_offset}m",
            "atmosphere": state.event_type.capitalize(),
            "visible_objects": state.visible_objects,
            "camera": world.camera_base,
            "mood": state.event_type,
            "event_type": state.event_type,
            "lighting": lighting_prompt, # PATCH 6: Hard Override
            "assigned_beats": scene_beats
        }
        
        # Override with Writer's specifics if they exist (subject, action, camera)
        if i < len(writer_scenes) and isinstance(writer_scenes[i], dict):
            scene_data["main_subject"] = writer_scenes[i].get("main_subject", scene_data["main_subject"])
            scene_data["action"] = writer_scenes[i].get("action", scene_data["action"])
            if writer_scenes[i].get("camera"):
                 scene_data["camera"] = writer_scenes[i].get("camera")
            
        final_scenes.append(scene_data)
        
    return final_scenes
