# app/modules/video_gen.py
import math
import numpy as np
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, CompositeVideoClip
from moviepy.video.VideoClip import VideoClip

# ---------- text helpers for Pillow >=10 ----------
def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return (bbox[2]-bbox[0], bbox[3]-bbox[1])

def _wrap_text(text: str, draw: ImageDraw.ImageDraw, font, max_width: int) -> List[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip() if cur else w
        tw, _ = _text_size(draw, test, font)
        if tw <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def _nice_font(size: int):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

# ---------- avatar drawing ----------
def draw_avatar(draw: ImageDraw.ImageDraw, center: tuple[int,int], env: float, role: str):
    if role == "Teacher":
        head, body = (30,30,120), (50,50,160)
    else:
        head, body = (120,30,30), (160,50,50)

    x, y = center
    head_r = 56
    y += int(4 * env)  # subtle bob
    # head
    draw.ellipse([x-head_r, y-head_r, x+head_r, y+head_r], fill=head)
    # body
    bw, bh = 110, 160
    draw.rounded_rectangle([x-bw//2, y+head_r-10, x+bw//2, y+head_r-10+bh], radius=18, fill=body)
    # eyes
    eye_off, e, ey = 24, 8, y-8
    draw.ellipse([x-eye_off-e, ey-e, x-eye_off+e, ey+e], fill=(255,255,255))
    draw.ellipse([x+eye_off-e, ey-e, x+eye_off+e, ey+e], fill=(255,255,255))
    pr = 3
    draw.ellipse([x-eye_off-pr, ey-pr, x-eye_off+pr, ey+pr], fill=(0,0,0))
    draw.ellipse([x+eye_off-pr, ey-pr, x+eye_off+pr, ey+pr], fill=(0,0,0))
    # mouth (opens with env)
    mw = 34
    mh = int(6 + env * 24)
    draw.ellipse([x-mw, y+22, x+mw, y+22+mh], fill=(0,0,0))

def generate_video(
    audio_file: str,
    scenes: List[Dict],
    output_file: str = "lecture.mp4",
    fps: int = 24,
    W: int = 1280,
    H: int = 720,
):
    """
    scenes: [
      {"title": "...", "keyline": "...",
       "dialogue": [{"who":"Teacher","line":"..."}, {"who":"Student","line":"..."}]
      }, ...
    ]
    """
    # ----- Load audio -----
    try:
        audio = AudioFileClip(audio_file)
    except Exception as e:
        raise FileNotFoundError(f"Could not load audio '{audio_file}': {e}")
    duration = max(1.0, audio.duration)
    total_frames = max(1, int(duration * fps))

    # ----- Flatten dialog + proportionally assign timings -----
    utterances = []
    for si, sc in enumerate(scenes or []):
        for d in sc.get("dialogue", []):
            utterances.append({"scene": si, "who": d["who"], "text": d["line"]})
    if not utterances:
        utterances = [{"scene": 0, "who": "Teacher", "text": "No dialog provided."}]

    char_counts = [max(1, len(u["text"])) for u in utterances]
    total_chars = sum(char_counts)
    seg_durations = [duration * (c / total_chars) for c in char_counts]

    starts = []
    t = 0.0
    for d in seg_durations:
        starts.append(t)
        t += d
    # clamp last to exact duration
    if starts:
        seg_durations[-1] += (duration - (starts[-1] + seg_durations[-1]))

    # ----- build simple audio envelope for mouth sync -----
    env = np.zeros(total_frames, dtype=float)
    try:
        sr = 22050
        samples = audio.to_soundarray(fps=sr)
        if samples.ndim == 2:
            samples = samples.mean(axis=1)
        N = len(samples)
        chunk = max(1, N // total_frames)
        for i in range(total_frames):
            s = i * chunk
            e = min(N, (i + 1) * chunk)
            ch = samples[s:e]
            if len(ch) > 0:
                env[i] = float(np.sqrt(np.mean(ch ** 2)))
        if env.max() > 0:
            env /= env.max()
    except Exception:
        # fallback rhythmic envelope
        for i in range(total_frames):
            env[i] = 0.5 + 0.5 * math.sin(2 * math.pi * (i / total_frames) * 3)

    # ----- fonts -----
    title_font = _nice_font(40)
    key_font   = _nice_font(32)
    bubble_font= _nice_font(28)
    ui_font    = _nice_font(20)

    def make_frame(tsec: float):
        fi = min(total_frames - 1, int(tsec * fps))

        # background gradient
        base = np.zeros((H, W, 3), dtype=np.uint8)
        for y in range(H):
            r = int(35 + 70 * y / H + 15 * math.sin(tsec / 6))
            g = int(55 + 85 * y / H + 10 * math.cos(tsec / 5))
            b = int(120 + 45 * y / H + 20 * math.sin(tsec / 4))
            base[y, :, 0] = np.clip(r, 0, 255)
            base[y, :, 1] = np.clip(g, 0, 255)
            base[y, :, 2] = np.clip(b, 0, 255)

        img = Image.fromarray(base)
        draw = ImageDraw.Draw(img)

        # find current utterance index
        u_idx = 0
        for i, st in enumerate(starts):
            if tsec >= st:
                u_idx = i
        u_idx = min(u_idx, len(utterances) - 1)
        u = utterances[u_idx]
        sc = scenes[u["scene"]] if scenes else {"title": "Scene", "keyline": ""}

        # right card with title & key line (minimal text)
        card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        bx0, by0, bx1, by1 = int(W * 0.55), int(H * 0.08), int(W * 0.95), int(H * 0.45)
        cd.rounded_rectangle([bx0, by0, bx1, by1], radius=18, fill=(255, 255, 255, 225))
        img = Image.alpha_composite(img.convert("RGBA"), card).convert("RGB")
        draw = ImageDraw.Draw(img)

        draw.text((bx0 + 20, by0 + 16), sc.get("title", ""), font=title_font, fill=(20, 20, 40))
        maxw = bx1 - bx0 - 40
        key_lines = _wrap_text(sc.get("keyline", ""), draw, key_font, maxw)
        y = by0 + 70
        for ln in key_lines[:3]:
            draw.text((bx0 + 20, y), ln, font=key_font, fill=(30, 30, 60))
            y += 36

        # avatars
        envv = float(env[fi])
        teacher_pos = (int(W * 0.22), int(H * 0.46))
        student_pos = (int(W * 0.38), int(H * 0.56))
        draw_avatar(draw, teacher_pos, envv if u["who"] == "Teacher" else 0.15 * envv, "Teacher")
        draw_avatar(draw, student_pos, envv if u["who"] == "Student" else 0.15 * envv, "Student")

        # speech bubble
        bubble_w = int(W * 0.48)
        bubble_h = int(H * 0.28)
        bubble_x = int(W * 0.06) if u["who"] == "Teacher" else int(W * 0.26)
        bubble_y = int(H * 0.08) if u["who"] == "Teacher" else int(H * 0.40)

        bub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bub)
        bd.rounded_rectangle([bubble_x, bubble_y, bubble_x + bubble_w, bubble_y + bubble_h],
                             radius=18, fill=(255, 255, 255, 235))
        img = Image.alpha_composite(img.convert("RGBA"), bub).convert("RGB")
        draw = ImageDraw.Draw(img)

        # speech text
        tw_max = bubble_w - 32
        lines = _wrap_text(u["text"], draw, bubble_font, tw_max)
        ty = bubble_y + 16
        for ln in lines[:6]:  # keep concise
            draw.text((bubble_x + 16, ty), ln, font=bubble_font, fill=(10, 10, 25))
            ty += 30

        # progress bar
        p = max(0.0, min(1.0, tsec / duration))
        px0, px1, py = int(W * 0.08), int(W * 0.92), int(H * 0.92)
        draw.rectangle([px0, py - 6, px1, py + 6], fill=(220, 220, 220))
        draw.rectangle([px0, py - 6, int(px0 + (px1 - px0) * p), py + 6], fill=(50, 120, 200))
        label = f"Scene {u['scene'] + 1}/{len(scenes)} • {u['who']}"
        draw.text((px0, py + 10), label, font=_nice_font(18), fill=(240, 240, 240))

        return np.array(img, dtype=np.uint8)

    base = VideoClip(make_frame, duration=duration)
    video = CompositeVideoClip([base]).with_audio(audio)
    video.write_videofile(output_file, fps=fps, codec="libx264", audio_codec="aac", threads=4)
