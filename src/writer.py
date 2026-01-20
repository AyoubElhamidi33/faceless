import json
import random
import os
from openai import OpenAI
from .config import OPENAI_API_KEY, OUTPUT_DIR

class TopicEngine:
    def __init__(self, channel_config: dict):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.niche = channel_config.get("niche", "horror")
        self.state_file = os.path.join(OUTPUT_DIR, "topic_state.json")
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {"used_topics": []}

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_fresh_topic(self) -> str:
        print("[*] TopicEngine: Fetching fresh topic...")
        # 1. Generate batch
        prompt = (
            f"Generate 10 specific, viral, and shocking video topics for the niche '{self.niche}'. "
            "Focus on 'unknown facts', 'dark history', 'glitch in the matrix', or 'unexplained disappearances'. "
            "Return ONLY a raw JSON list of strings."
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a viral content strategist. Output JSON only."},
                    {"role": "user", "content": prompt}
                ]
            )
            data = json.loads(response.choices[0].message.content)
            candidates = data.get("topics", data.get("list", []))
            
            # 2. Filter used
            for topic in candidates:
                if topic not in self.state["used_topics"]:
                    self.state["used_topics"].append(topic)
                    self._save_state()
                    print(f"[*] TopicEngine: Selected '{topic}'")
                    return topic
            
            # Fallback if all used (recursive retry could be added here, but simple return for now)
            print("[!] Warning: All generated topics were used. Returning random from batch.")
            return candidates[0] if candidates else "The Disappearance of Flight 19"

        except Exception as e:
            print(f"[!] TopicEngine Error: {e}")
            return "The Dyatlov Pass Incident"

class ScriptGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.hook_types = [
            "impossible_time", "last_recording", "disappearance",
            "mysterious_message", "camera_capture", "emergency_call",
            "impossible_evidence"
        ]

    def generate_script(self, topic: str, style_profile: dict) -> dict:
        print(f"[*] 🌑 PROMETHEUS ENGINE STARTING for: {topic}")
        
        # PHASE 1: HOOK ENGINE
        hook_data = self._generate_hook(topic)
        raw_hook = hook_data.get("hook_text")
        hook_type = hook_data.get("hook_type")
        
        # PHASE 2: HOOK VALIDATION
        validated_hook = self._validate_hook(raw_hook)
        print(f"[*] Validated Hook: {validated_hook}")

        # PHASE 3: STORY ENGINE
        final_script = self._generate_story(topic, validated_hook, hook_type, style_profile)
        print("[*] Full Story Generated.")
        
        # Force the hook text to be the first line if it isn't already handled by GPT
        if not final_script.get("script_text").strip().startswith(validated_hook.strip()):
            final_script["script_text"] = validated_hook + " " + final_script["script_text"]

        return final_script

    def _generate_hook(self, topic: str) -> dict:
        # We enforce a specific "Did you know" structure now
        prompt = (
            "You are a viral horror hook generator.\n"
            f"TOPIC: {topic}\n"
            "Generate ONE opening sentence. \n"
            "STRICT RULE: MUST START WITH 'Did you know that' or 'Do you know'.\n"
            "Example: 'Did you know that on Halloween 1981, a radio station broadcasted a recording of a man dying live on air?'\n"
            "Rules: 10-16 words. Shocking fact. Real documented case feel.\n"
            "Return STRICT JSON: {\"hook_type\": \"did_you_know\", \"hook_text\": \"...\"}"
        )
        response = self.client.chat.completions.create(
            model="gpt-4o", response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)

    def _validate_hook(self, hook_text: str) -> str:
        prompt = (
            f"Evaluate this hook: \"{hook_text}\"\n"
            "Check: Starts with 'Did you know' or 'Do you know'? Shocking? Clear?\n"
            "If weak or missing the start phrase, rewrite ONCE. Return ONLY the final hook sentence."
        )
        response = self.client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip('"')

    def _generate_story(self, topic: str, hook: str, hook_type: str, style: dict) -> dict:
        prompt = (
            f"TOPIC: {topic} | HOOK: {hook}\n"
            "STRICT VIRAL STRUCTURE:\n"
            "1. HOOK (Use existing 'Did you know...')\n"
            "2. DATE/LOCATION (e.g., 'On November 3rd, 1998, in a small town in Ohio...')\n"
            "3. THE STRANGE EVENT (What happened?)\n"
            "4. ESCALATION (Chain of worse events)\n"
            "5. UNRESOLVED END (No closure)\n"
            "GLOBAL RULES: Serious, investigative, no gore/fantasy (unless realistic), ~60s.\n"
            "VISUALS: Generate **12-15 SCENES** (Rapid pacing).\n"
            "RETURN JSON:\n"
            "{\n"
            f'  "hook_type": "{hook_type}",\n'
            f'  "hook_text": "{hook}",\n'
            '  "script_text": "Full story...",\n'
            '  "scenes": ["Exact 12-15 consistent comic book visual prompts identifying The Detective character"],\n'
            '  "beat_words": ["40-90 short tension words for captions"],\n'
            '  "keywords": ["tag1", "tag2"],\n'
            f'  "suggested_style": "{style.get("name", "consistent_comic")}",\n'
            f'  "caption_style": "{style.get("caption_style", "typewriter")}",\n'
            f'  "music_mood": "{style.get("music_mood", "analog_drone")}"\n'
            "}"
        )
        response = self.client.chat.completions.create(
            model="gpt-4o", response_format={"type": "json_object"},
            messages=[{"role": "system", "content": "Prometheus Engine. JSON Output."}, {"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)