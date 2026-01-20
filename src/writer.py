import json
import os
from openai import OpenAI
from .config import OPENAI_API_KEY

class ScriptGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_script(self, topic: str) -> dict:
        """
        Agentic workflow to generate a script about the given topic.
        Returns a dictionary with script_text, scenes, and keywords.
        """
        print(f"[*] generating script for topic: {topic}")
        
        # Step 1: Draft
        draft = self._generate_draft(topic)
        print("[*] Draft generated.")

        # Step 2: Critique
        critique = self._critique_script(draft)
        print("[*] Critique received.")

        # Step 3: Final Polish
        final_script = self._finalize_script(draft, critique)
        print("[*] Final script generated.")
        
        return final_script

    def _generate_draft(self, topic: str) -> str:
        prompt = (
            f"Write a 60-second viral short video script about '{topic}'. "
            "Focus on 'Suspense' and 'Visual Storytelling'. "
            "The tone should be engaging and tailored for TikTok/Reels. "
            "Keep it under 160 words ideally."
        )
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a world-class scriptwriter for viral short-form content."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def _critique_script(self, draft: str) -> str:
        prompt = (
            "Act as a Viral Content Producer. Critique the following script's Hook (first 3 seconds). "
            "Is it boring? Does it drag? Be harsh and specific. "
            f"Script: \n{draft}"
        )
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a critical viral content producer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def _finalize_script(self, draft: str, critique: str) -> dict:
        prompt = (
            f"Original Script: \n{draft}\n\n"
            f"Critique: \n{critique}\n\n"
            "Based on the critique, rewrite the script to be absolute fire. "
            "Then, provide the output STRICTLY in the following JSON format:\n"
            "{\n"
            '  "script_text": "The full spoken text...",\n'
            '  "scenes": ["Detailed image prompt for scene 1", "Detailed image prompt for scene 2", ... (exactly 8 scenes)],\n'
            '  "keywords": ["tag1", "tag2", ...]\n'
            "}"
        )
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a JSON-outputting machine. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    # Test
    gen = ScriptGenerator()
    result = gen.generate_script("The Mystery of the Mary Celeste")
    print(json.dumps(result, indent=2))
