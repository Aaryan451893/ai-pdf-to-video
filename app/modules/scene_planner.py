# modules/scene_planner.py
def plan(scenes, total_audio_seconds):
    # Flatten dialog
    utterances = []
    for si, sc in enumerate(scenes):
        for d in sc["dialogue"]:
            utterances.append({"scene": si, "who": d["who"], "text": d["line"]})
    # Allocate time by char length
    lens = [max(1, len(u["text"])) for u in utterances]
    total = sum(lens)
    t = 0.0
    for i,u in enumerate(utterances):
        dur = total_audio_seconds * (lens[i] / total)
        u["start"] = t
        u["end"] = t + dur
        t += dur
    return utterances
