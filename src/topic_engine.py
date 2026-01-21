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
            f"Generate 100-150 specific, obscure, and unsettling historical events for the niche '{self.niche}'.\n"
            "RULES:\n"
            "- Focus on: Industrial disasters, strange disappearances, survival incidents, uncanny historical facts, all strictly within the '{self.niche}' theme.\n"
            "- NO: Mainstream myths (Area 51, Bigfoot), pure fantasy, or well-known unresolved mysteries (Zodiac).\n"
            "- FORMAT: JSON object with a single key 'topics'.\n"
            "- EXAMPLE: {{\"topics\": ['The Halifax Explosion 1917', 'The Centralia Mine Fire']}}"
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a historical archivist for a horror documentary channel. JSON only."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            # print(f"[DEBUG] Topic Batch Response: {content[:100]}...") 
            data = json.loads(content)
            
            # Smart extraction
            if "topics" in data: return data["topics"]
            if "list" in data: return data["list"]
            if "events" in data: return data["events"]
            
            # Fallback: check values if it's a list
            if isinstance(data, list): return data
            
            return []
        except Exception as e:
            print(f"[!] TopicEngine Batch Error: {e}")
            return []
