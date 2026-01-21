import json
import os
import time
from openai import OpenAI
from .config import OPENAI_API_KEY, OUTPUT_DIR

class TopicEngine:
    def __init__(self, channel_config: dict):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.niche = channel_config.get("niche", "horror")
        self.state_file = os.path.join(OUTPUT_DIR, "topic_state.json")
        self.blacklist = [
            "Flight 19", "Dyatlov Pass", "Elisa Lam", "MH370", "Titanic", "Bermuda Triangle"
        ]
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {"used_topics": [], "candidates": []}

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_fresh_topic(self) -> str:
        print("[*] TopicEngine v2: Fetching fresh topic...")
        
        # 1. Check local cache first
        if self.state.get("candidates"):
            while self.state["candidates"]:
                candidate = self.state["candidates"].pop(0)
                if not self._is_blacklisted(candidate) and candidate not in self.state["used_topics"]:
                    self._mark_used(candidate)
                    return candidate
        
        # 2. Generate new batch
        print(f"[*] TopicEngine v2: Cache empty. Generating batch for '{self.niche}'...")
        new_topics = self._generate_batch()
        
        # 3. Filter & Deduplicate
        valid_topics = []
        for t in new_topics:
            if not self._is_blacklisted(t) and t not in self.state["used_topics"]:
                valid_topics.append(t)
        
        if not valid_topics:
            print("[!] Warning: All generated topics were duplicates or blacklisted.")
            # FATAL: Do not repeat.
            # But during dev, we might need a fallback.
            # User Rule: "If exhausted: regenerate, DO NOT random reuse"
            # So we retry generation once recursively.
            print("[*] Retrying generation once...")
            new_topics_2 = self._generate_batch()
            for t in new_topics_2:
                if not self._is_blacklisted(t) and t not in self.state["used_topics"]:
                    valid_topics.append(t)
            
            if not valid_topics:
                raise RuntimeError("Topic Exhaustion: No new unique topics found.")

        # 4. Update Cache
        self.state["candidates"].extend(valid_topics)
        self._save_state()
        
        # 5. Return first
        chosen = self.state["candidates"].pop(0)
        self._mark_used(chosen)
        return chosen

    def _mark_used(self, topic):
        print(f"[*] TopicEngine: Selected '{topic}'")
        self.state["used_topics"].append(topic)
        self._save_state()

    def _is_blacklisted(self, topic):
        for bad in self.blacklist:
            if bad.lower() in topic.lower():
                return True
        return False

    def _generate_batch(self):
            prompt = (
                f"Generate 50 specific, true historical events for the niche '{self.niche}'.\n"
                "CRITICAL RULES FOR 'TRAGIC_HUMAN_IRONY':\n"
                "1. FOCUS ON THE INDIVIDUAL: Every topic must revolve around a specific person or small crew (e.g., Kevin Carter, The Piper Alpha Shift Manager, The Radium Girls).\n"
                "2. THE FATAL FLAW: The story must have a 'Twist of Fate'—a small mistake, a moral dilemma, or a cruel irony that led to disaster.\n"
                "3. NO SUPERNATURAL: Absolutely NO ghosts, cryptids, aliens, or 'unexplained mysteries'. Only hard, brutal reality.\n"
                "4. FORMAT: JSON object with a single key 'topics'.\n"
                "5. EXAMPLES OF GOOD TOPICS:\n"
                "   - 'Hisashi Ouchi: The man kept alive against his will for 83 days.'\n"
                "   - 'Franz Reichelt: The tailor who jumped off the Eiffel Tower to prove his suit worked.'\n"
                "   - 'Vasili Arkhipov: The one man who refused to launch a nuke and saved the world.'\n"
                "   - 'The Byford Dolphin Incident: The most brutal decompression accident in history.'\n"
            )
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You are a researcher for a 'Dark History' channel. You find ironic, tragic true stories."},
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.choices[0].message.content
                data = json.loads(content)
                
                if "topics" in data: return data["topics"]
                return []
            except Exception as e:
                print(f"[!] TopicEngine Batch Error: {e}")
                return []
