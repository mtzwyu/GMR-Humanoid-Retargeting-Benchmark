# Phân tích tư thế pkl + render 1 khung hình chỉ định bằng MuJoCo (offscreen)
# python analyze_pose.py <pkl> <xml> <out_png> <frame_index>
import sys, pickle
import numpy as np
import mujoco as mj
import imageio.v2 as imageio

pkl, xml, out_png, fi = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
d = pickle.load(open(pkl, "rb"))
root = np.asarray(d["root_pos"], dtype=float)
rot = np.asarray(d["root_rot"], dtype=float)      # xyzw
dof = np.asarray(d["dof_pos"], dtype=float)

m = mj.MjModel.from_xml_path(xml)
data = mj.MjData(m)

def qadr(name):
    j = mj.mj_name2id(m, mj.mjtObj.mjOBJ_JOINT, name)
    return m.jnt_qposadr[j]

names = {}
candidates = {
    "waist_pitch": ["waist_pitch_joint", "Waist", "waist_pitch"],
    "hip_pitch_L": ["left_hip_pitch_joint", "Left_Hip_Pitch", "LeftHipPitch"],
    "hip_pitch_R": ["right_hip_pitch_joint", "Right_Hip_Pitch", "RightHipPitch"],
    "knee_L": ["left_knee_joint", "Left_Knee_Pitch", "LeftKnee"],
    "knee_R": ["right_knee_joint", "Right_Knee_Pitch", "RightKnee"],
    "ankle_pitch_L": ["left_ankle_pitch_joint", "Left_Ankle_Pitch", "LeftAnklePitch"],
    "ankle_pitch_R": ["right_ankle_pitch_joint", "Right_Ankle_Pitch", "RightAnklePitch"],
}
joint_names = [mj.mj_id2name(m, mj.mjtObj.mjOBJ_JOINT, i) or "" for i in range(m.njnt)]
for label, cand in candidates.items():
    for c in cand:
        if c in joint_names:
            names[label] = c
            break

print(f"file={pkl}\nxml={xml}\nframes={dof.shape[0]} dof={dof.shape[1]}")
print("joints:", ", ".join(j for j in joint_names if j))
for label, jname in names.items():
    a = qadr(jname) - 7
    print(f"{label:14s} mean={np.degrees(dof[:, a]).mean():8.2f} deg  std={np.degrees(dof[:, a]).std():6.2f}")
print(f"root_z         mean={root[:,2].mean():.3f} m  min={root[:,2].min():.3f}  max={root[:,2].max():.3f}")
print(f"root_y         mean={root[:,1].mean():.3f} m  min={root[:,1].min():.3f}  max={root[:,1].max():.3f}")
q = rot / np.linalg.norm(rot, axis=1, keepdims=True)
dot = np.abs(np.sum(q[:-1] * q[1:], axis=1))
print(f"quat |dot| min={dot.min():.4f}  mean={dot.mean():.4f}  frames={len(q)}")

# render khung hình chỉ định
fi = min(fi, dof.shape[0] - 1)
data.qpos[0:3] = root[fi]
data.qpos[3:7] = [q[fi][3], q[fi][0], q[fi][1], q[fi][2]]   # xyzw -> wxyz
data.qpos[7:7 + dof.shape[1]] = dof[fi]
mj.mj_forward(m, data)
r = mj.Renderer(m, height=720, width=960)
cam = mj.MjvCamera()
cam.type = mj.mjtCamera.mjCAMERA_FREE
cam.lookat[:] = [root[fi][0], root[fi][1], 0.9]
cam.distance = 2.6
cam.azimuth = 135.0
cam.elevation = -12.0
r.update_scene(data, camera=cam)
img = r.render()
imageio.imwrite(out_png, img)
print(f"rendered frame {fi} -> {out_png}")
