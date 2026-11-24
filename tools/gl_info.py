# In thong tin OpenGL context ma MuJoCo dung (de tra loi: render la GPU that hay software).
# Dung: python tools\gl_info.py
import os
import mujoco
from OpenGL import GL

print("mujoco", mujoco.__version__, "| MUJOCO_GL =", os.environ.get("MUJOCO_GL", "(khong dat)"))

ctx = mujoco.GLContext(640, 480)
ctx.make_current()
vendor = GL.glGetString(GL.GL_VENDOR)
renderer = GL.glGetString(GL.GL_RENDERER)
version = GL.glGetString(GL.GL_VERSION)
print("GL_VENDOR   =", vendor.decode() if vendor else None)
print("GL_RENDERER =", renderer.decode() if renderer else None)
print("GL_VERSION  =", version.decode() if version else None)
ctx.free()
