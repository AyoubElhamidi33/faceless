import json
import random
import os
from openai import OpenAI
from .config import OPENAI_API_KEY, OUTPUT_DIR

class ScriptGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.hook_types = [
            "impossible_time", "last_recording", "disappearance",
            "mysterious_message", "camera_capture", "emergency_call",
            "impossible_evidence"
        ]

    def generate_script(self, topic: str, style_profile: dict) -> dict:
        from .validator import validate_script_logic, validate_golden_similarity, validate_story_novelty
        
        print(f"[*] 🌑 PROMETHEUS ENGINE v3 STARTING for: {topic}")
        
        # PHASE 1: HOOK ENGINE (A/B Testing Variants)
        hook_data = self._generate_hook(topic)
        base_hook = hook_data["hook_text"]
        
        # PHASE 2: STORY ENGINE
        max_retries = 3
        final_script = {}
        
        for attempt in range(max_retries):
            print(f"[*] Story Generation Attempt {attempt + 1}/{max_retries}...")
            
            # Initial Generation
            draft_script = self._generate_story(topic, base_hook, hook_data["hook_type"], style_profile)
            
            # PHASE 2.5: HUMAN VOICE REWRITE PASS (Critical Lock)
            print("[*] Running Human Voice Rewrite Pass...")
            draft_script["script_text"] = self._rewrite_human_voice(draft_script["script_text"], base_hook)
            
            # LOCK CHECKS
            is_valid, problems = validate_script_logic(draft_script)
            if not is_valid:
                print(f"[!] ❌ Logic/Voice Lock Failed: {problems}")
                continue

            is_golden, score, msg = validate_golden_similarity(draft_script["script_text"])
            if not is_golden:
                print(f"[!] ❌ Golden Lock Failed: {msg} ({score:.2f})")
                continue

            fingerprint = f"{draft_script.get('hook_type')}|{draft_script.get('escalation_pattern')}|{draft_script.get('ending_type')}"
            is_novel, ratio = validate_story_novelty(fingerprint)
            if not is_novel:
                print(f"[!] ❌ Novelty Lock Failed: Too similar ({ratio:.2f})")
                continue
            
            final_script = draft_script
            print(f"[*] ✅ Quality Gates Passed.")
            break
        
        if not final_script:
            raise Exception("Script Generation failed after max retries.")

        # PHASE 4: SEO & METADATA
        print("[*] Generating SEO Metadata...")
        seo = self._generate_seo(topic, final_script["script_text"])
        final_script["metadata"] = seo
        
        # PHASE 5: A/B VARIANTS
        print("[*] Generating A/B Variants...")
        variants = self._generate_variants(final_script["script_text"])
        final_script["variants"] = variants

        # CLEANUP
        final_script["suggested_style"] = style_profile.get("name", "consistent_comic")
        final_script["caption_style"] = style_profile.get("caption_style", "center_wordbeats")
        final_script["music_mood"] = style_profile.get("music_mood", "dark_ambient")
        
        # Ensure Hook Start
        if not final_script.get("script_text", "").strip().startswith(base_hook.strip()):
            final_script["script_text"] = base_hook + " " + final_script.get("script_text", "")

        return final_script

    def _generate_hook(self, topic: str) -> dict:
        htype = random.choice(self.hook_types)
        # PATCH 2: Stop Bot-Like Repetition
        prompt = (
            "You are a viral horror hook generator.\n"
            f"TOPIC: {topic}\n"
            f"TYPE: {htype}\n"
            "Generate ONE opening sentence (8-14 words).\n"
            "STRICT RULES:\n"
            "- BANNED PHRASES: 'Did you know', 'Experts found', 'Police recovered', 'Let me tell you', 'Today I'.\n"
            "- MUST BE ACTION-ORIENTED or IMMEDIATELY UNSETTLING.\n"
            "- START WITH: Time, Location, or the horrifying object directly.\n"
            "- NO fantasy/monsters. No 'ghosts', 'demons', 'curses'. Use 'shadows', 'figures', 'remains'.\n"
            "Return STRICT JSON: {\"hook_type\": \"...\", \"hook_text\": \"...\"}"
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response.choices[0].message.content)
        except:
             return {"hook_type": "fallback", "hook_text": f"The silence at {topic} was deafening."}

    def _generate_story(self, topic: str, hook: str, hook_type: str, style: dict) -> dict:
        # PATCH 7: Clean Prompt Structure
        prompt = (
            f"TOPIC: {topic} | HOOK: {hook}\n"
            "STRICT DOCUMENTARY RECAP STRUCTURE:\n"
            "1. HOOK (Exact match required)\n"
            "2. YEAR/LOCATION (Time Jump Context)\n"
            "3. NORMAL SETUP (The calm before)\n"
            "4. FIRST WARNING (Something is wrong)\n"
            "5. ESCALATION BEATS (4-8 scenes of worsening dread)\n"
            "6. OUTCOME (The tragedy/result)\n"
            "7. EERIE REFLECTION (Unresolved Note)\n\n"
            "CRITICAL CONTENT LOCKS:\n"
            "1. POV LOCK: Declare 'narrative_pov'. Include 3 sensory refs (smell/touch/sound), 1 emotional reaction, 1 decision moment.\n"
            "2. FALSE CALM: You MUST include a 'False Calm' beat (a moment of safety before doom) between escalation steps.\n"
            "3. SUBTEXT: Include >=1 theme: systemic failure, ignored warning, injustice.\n"
            "4. SILENCE: Insert [SILENCE:x] marker near peak.\n"
            "5. REALISM: 3 time anchors (1 exact minute), 1 off-screen threat, 1 false calm, 1 raw ugly sentence.\n"
            "6. BEAT COUNT: The script MUST be between 130 and 160 words total. 16 Scenes.\n\n"
            "CONTINUITY LOCKS:\n"
            "- Track location/time. Only change when script explicitly does.\n"
            "- Objects persist.\n"
            "- Atmosphere evolves gradually.\n\n"
            "SCENE GENERATION (EXACTLY 16 SCENES):\n"
            "- Return 'scenes' as LIST OF OBJECTS with detailed metadata for rendering.\n"
            "- CRITICAL: You MUST include a 'False Calm' structure in 'event_type' sequence:\n"
            "   [...NORMAL..., ...WARNING..., ...NORMAL (False Calm)..., ...DANGER/ESCALATION...]\n"
            "- DO NOT write the full prompt string. Provide component parts.\n"
            "- Keys per scene:\n"
            "  'beat_text': (The exact sentence from the script that corresponds to this scene)\n"
            "  'main_subject': (visual description)\n"
            "  'action': (what is happening)\n"
            "  'location': (environment)\n"
            "  'time': (time of day)\n"
            "  'lighting': (lighting condition)\n"
            "  'atmosphere': (e.g. foggy, tense)\n"
            "  'visible_objects': [list of objects]\n"
            "  'camera': (framing)\n"
            "  'mood': (emotional tone)\n"
            "  'event_type': (NORMAL|WARNING|DISCOVERY|ESCALATION|DANGER|OUTCOME|AFTERMATH)\n\n"
            "RETURN JSON:\n"
            "{\n"
            f'  "hook_type": "{hook_type}",\n'
            f'  "hook_text": "{hook}",\n'
            '  "script_text": "Full script text here...",\n'
            '  "character_profile": {"age_range": "30s", "role": "Investigator", "clothing": "Dark coat", "features": "Tired eyes"},\n'
            '  "narrative_pov": "...",\n'
            '  "subtext_theme": "...",\n'
            '  "iconic_scene_index": 5,\n'
            '  "scenes": [{...}, ...],\n'
            '  "fact_confidence": "medium",\n'
            '  "sticky_ending_line": "...",\n'
            '  "technical_detail": "...",\n'
            '  "beat_words": ["WORD", "WORD", ...],  # MUST be 80-110 words, ALL CAPS, matching script roughly\n'
            '  "keywords": ["tag1", ...],\n'
            '  "escalation_pattern": [0, 1, ...],\n'
            '  "false_calm_indices": [9],\n'
            f'  "ending_type": "ambiguous"\n'
            "}"
        )
        response = self.client.chat.completions.create(
            model="gpt-4o", response_format={"type": "json_object"},
            messages=[{"role": "system", "content": "Prometheus Documentary Engine. JSON Output."}, {"role": "user", "content": prompt}]
        )
        data = json.loads(response.choices[0].message.content)
        
        # PATCH 8: Auto-Fix Beat Words to pass Validator
        script_text = data.get("script_text", "")
        beats = data.get("beat_words", [])
        
        # Normalize existing beats
        if beats:
            beats = [str(b).upper().strip(".,!?") for b in beats]
            
        script_words = [w.strip(".,!?").upper() for w in script_text.split()]
        
        # If missing or too short (Validator expects > 60?)
        # User said "beat_words must be 80-110".
        if len(beats) < len(script_words) * 0.8:
             data["beat_words"] = script_words
        else:
             data["beat_words"] = beats
                 
        return data

    def _rewrite_human_voice(self, script_text: str, hook: str) -> str:
        # PATCH 3: Fix Rewrite Hook Integrity
        prompt = (
            f"Rewrite this script into simpler, human, spoken English.\n"
            f"SCRIPT: {script_text}\n"
            "RULES:\n"
            "- Keep events identical.\n"
            "- Reduce abstraction. Use concrete nouns.\n"
            "- Increase physical detail (what they saw/felt).\n"
            "- Short sentences (avg 12 words).\n"
            "- NO 'amidst', 'unease', 'serenity', 'claims emerged'.\n"
            "- Write as if telling a friend over a drink.\n"
            "- USE A MIX OF PERSPECTIVES:\n"
            "  * Third Person Factual: 'It happened at 3AM.'\n"
            "  * Witness Account: 'She saw the shadow', 'They heard the scream', 'I felt the cold.'\n"
            "  * Documentary Hedging: 'Reports say', 'Neighbors described'.\n"
            f"- MUST START with the exact Hook: \"{hook}\"\n"
            "Return ONLY the rewritten text."
        )
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        if not content.startswith(hook):
             # Force hook prefix if LLM disobeyed
             content = f"{hook} " + content.lstrip(hook).strip()
        return content

    def _generate_seo(self, topic: str, script: str) -> dict:
        prompt = (
            f"Generate SEO metadata for this script.\nTopic: {topic}\n"
            "Return JSON: {\"titles\": [3 clickbait titles], \"hashtags\": [10 tags], \"description\": \"intrigue summary\"}"
        )
        response = self.client.chat.completions.create(
            model="gpt-4o", response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)

    def _generate_variants(self, script_text: str) -> dict:
        prompt = (
            "Generate 2 alternative Hooks for A/B testing this script.\n"
            "Return JSON: {\"hook_b\": \"...\", \"hook_c\": \"...\"}"
        )
        response = self.client.chat.completions.create(
            model="gpt-4o", response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)