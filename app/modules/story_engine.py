# app/modules/story_engine.py
import re
from typing import List, Dict

def _sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text.strip())
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def _keyword_score(sent: str) -> float:
    stop = set("the a an to of for and or in on with is are was were be been being this that from into by it as at if then than when which who whom whose why how".split())
    words = [w.lower() for w in re.findall(r"[A-Za-z']+", sent)]
    content = [w for w in words if w not in stop and len(w) > 3]
    # favor mid-length sentences with more content words
    return 0.65*len(content) + 0.35*min(len(sent)/120, 1.0)

def summarize_core(text: str, max_points: int = 5) -> List[str]:
    sents = _sentences(text)
    if not sents:
        return []
    scored = [(i, _keyword_score(s), s) for i, s in enumerate(sents)]
    scored.sort(key=lambda x: x[1], reverse=True)

    picked, used = [], set()
    for idx, _, s in scored:
        # keep diversity by skipping near neighbors
        if any(abs(idx - j) <= 1 for j in used):
            continue
        picked.append(s)
        used.add(idx)
        if len(picked) >= max_points:
            break
    picked.sort(key=lambda s: sents.index(s))
    return picked

def generate_examples(points: List[str]) -> List[Dict]:
    scenes = []
    for k, p in enumerate(points, 1):
        concept = p
        example = (
            f"Imagine you run a small café. {concept} affects how you decide prices, "
            f"stock ingredients, and serve customers efficiently."
        )
        scenes.append({
            "title": f"Concept {k}",
            "keyline": f"{concept}",
            "dialogue": [
                {"who": "Teacher", "line": f"Key idea {k}: {concept}"},
                {"who": "Teacher", "line": f"Real-life example: {example}"},
                {"who": "Student", "line": "So if demand spikes later, we adjust prep and pricing?"},
                {"who": "Teacher", "line": "Exactly. We align supply with expected demand to reduce waste."},
                {"who": "Student", "line": "And we track waste to optimize inventory, right?"},
                {"who": "Teacher", "line": "Perfect summary! That’s the practical impact of this concept."}
            ]
        })
    return scenes

def build_script(raw_text: str, max_points: int = 5) -> Dict:
    points = summarize_core(raw_text, max_points=max_points)
    if not points:
        points = ["No content extracted from the source."]
    scenes = generate_examples(points)
    # narration focuses on the key points only (minimal text on screen later)
    narrative = " ".join(points)
    return {
        "points": points,
        "scenes": scenes,
        "narration_text": narrative
    }
