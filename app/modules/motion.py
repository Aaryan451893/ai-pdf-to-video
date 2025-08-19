# modules/motion.py
import numpy as np

def pose_track(role, duration, fps=12):
    # Return a list of OpenPose-like keypoint arrays per frame
    frames = int(duration*fps)
    track = []
    for f in range(frames):
        t = f/frames
        # base neutral pose
        pts = base_neutral_pose()
        # simple gestures
        if role == "Teacher":
            # wave right hand slowly
            pts["RWrist"][0] += 10*np.sin(2*np.pi*t)
        else:
            # nod head
            pts["Nose"][1] += 3*np.sin(2*np.pi*1.5*t)
        track.append(pts)
    return track

def base_neutral_pose():
    # Minimal skeleton dict with x,y coords (0..1 screen)
    return {
      "Nose":[0.4,0.35], "Neck":[0.4,0.45],
      "RShoulder":[0.45,0.45], "RElbow":[0.48,0.50], "RWrist":[0.50,0.55],
      "LShoulder":[0.35,0.45], "LElbow":[0.32,0.50], "LWrist":[0.30,0.55],
      "RHip":[0.42,0.65], "RKnee":[0.42,0.78], "RAnkle":[0.42,0.92],
      "LHip":[0.38,0.65], "LKnee":[0.38,0.78], "LAnkle":[0.38,0.92],
    }
