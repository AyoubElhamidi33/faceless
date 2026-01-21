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
            "- BANNED PHRASES: 'Experts found', 'Police recovered', 'Let me tell you', 'Today I'.\n"
            "- MUST BE ACTION-ORIENTED or IMMEDIATELY UNSETTLING.\n"
            "- START WITH: 'Did you know...' followed by a shocking statistic or irony.\n"
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
        # PROMETHEUS UPDATE: "Structure-Only" Logic (No Examples)
        prompt = (
            f"TOPIC: {topic} | HOOK: {hook}\n"
            "ROLE: You are an expert Viral Storyteller for a 'Dark History' channel. You do not write fiction; you write brutal, rhythmic facts.\n\n"
            "THE NARRATIVE BLUEPRINT (Strict Rules):\n"
            "1. THE HOOK (0:00): Start with 'Did you know...' followed by the tragic irony or specific death count. Stop the scroll instantly.\n"
            "2. THE ANCHOR (0:05): Ground the viewer. State the YEAR, the LOCATION, and the PROTAGONIST'S FULL NAME. Establish the routine before the disaster.\n"
            "3. THE PIVOT (0:15): The exact moment safety turns to danger. You MUST start this sentence with 'But' or 'However'. This is the fatal mistake or discovery.\n"
            "4. THE ESCALATION (0:30): A rapid-fire sequence of physical actions. Use sensory verbs (smelled smoke, heard the snap, felt the heat). Describe the mechanical failure or moral choice in detail.\n"
            "5. THE IMPACT (0:50): The final toll. State the number of victims, the suicide, or the specific lasting consequence. End on a heavy, resonant note.\n\n"
            "THE VISUAL BLUEPRINT (Director Mode):\n"
            "- CHARACTER SHEET: Define the protagonist's look (e.g., 'Robert, 40s, orange jumpsuit, soot-stained face'). Use this EXACT phrase in every scene.\n"
            "- CINEMATOGRAPHY: Describe the camera angle (Low Angle, Wide Master, Extreme Close-up) and lighting (Red Alarm Light, Cold Blue Moonlight) for every panel.\n"
            "- TONE: Gritty, Realistic, High Contrast Noir.\n\n"
            "CONSTRAINTS:\n"
            "- NO FLUFF: Adjectives must be physical (e.g., 'burning', 'frozen'), not emotional (e.g., 'scary', 'spooky').\n"
            "- PACING: Sentences must be breathable (under 12 words on average).\n"
            "- TRUTH: Use real historical names and numbers. No generic 'workers' or 'people'.\n\n"
            "OUTPUT FORMAT:\n"
            "Return a JSON object with this schema:\n"
            "{\n"
            "  \"hook_text\": \"...\",\n"
            "  \"script_text\": \"...\",\n"
            "  \"scenes\": [\n"
            "    {\n"
            "      \"beat_text\": \"...\",\n"
            "      \"visual_prompt\": \"[CAMERA] [LIGHTING] [CHARACTER] [ACTION]\",\n"
            "      \"event_type\": \"NORMAL\" | \"WARNING\" | \"DANGER\" | \"ESCALATION\" | \"AFTERMATH\"\n"
            "    }\n"
            "  ],\n"
            "  \"narrative_pov\": \"Third Person Objective\",\n"
            "  \"fact_confidence\": \"high\",\n"
            "  \"beat_words\": [\"LIST\", \"OF\", \"ALL\", \"WORDS\", \"IN\", \"SCRIPT\"]\n"
            "}"
        )
        
        response = self.client.chat.completions.create(
            model="gpt-4o", response_format={"type": "json_object"},
            messages=[{"role": "system", "content": "Prometheus Documentary Engine. JSON Output."}, {"role": "user", "content": prompt}]
        )
        data = json.loads(response.choices[0].message.content)
        
        # Auto-Fix Beat Words (System Stability)
        script_text = data.get("script_text", "")
        beats = data.get("beat_words", [])
        if beats:
            beats = [str(b).upper().strip(".,!?") for b in beats]
        script_words = [w.strip(".,!?").upper() for w in script_text.split()]
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