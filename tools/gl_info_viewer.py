# In GL_VENDOR / GL_RENDERER cua context OpenGL ma CUA SO viewer MuJoCo dung
# (launch_passive -> GLFW/WGL), de phan biet render GPU that hay software.
# Dung: python tools\gl_info_viewer.py
import mujoco
import mujoco.viewer as mjv
from OpenGL import GL

m = mujoco.MjModel.from_xml_string("<mujoco><worldbody><geom type='sphere' size='.1'/></worldbody></mujoco>")
d = mujoco.MjData(m)

viewer = mjv.launch_passive(m, d)
vendor = GL.glGetString(GL.GL_VENDOR)
renderer = GL.glGetString(GL.GL_RENDERER)
version = GL.glGetString(GL.GL_VERSION)
print("viewer (launch_passive) GL_VENDOR   =", vendor.decode() if vendor else None)
print("viewer (launch_passive) GL_RENDERER =", renderer.decode() if renderer else None)
print("viewer (launch_passive) GL_VERSION  =", version.decode() if version else None)
viewer.close()
