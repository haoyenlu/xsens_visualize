import numpy as np


class SegmentAnimation:
  def __init__(self,ax,lcolor="#3498db", rcolor="#e74c3c"):
    self.I = np.array([1,2,3,4,5,6,5,12,13,14,5,8,9,10,1,20,21,22,1,16,17,18]) -1
    self.J = np.array([2,3,4,5,6,7,12,13,14,15,8,9,10,11,20,21,22,23,16,17,18,19]) -1
    self.LR  = np.array([1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0], dtype=bool)
    self.ax = ax
    self.lcolor = lcolor
    self.rcolor = rcolor

    vals = np.zeros((23,3))
    self.plots = []
    for i in range(len(self.I)):
      x = np.array( [vals[self.I[i], 0], vals[self.J[i], 0]] )
      y = np.array( [vals[self.I[i], 1], vals[self.J[i], 1]] )
      z = np.array( [vals[self.I[i], 2], vals[self.J[i], 2]] )
      self.plots.append(self.ax.plot(x, y, z, lw=2, c=lcolor if self.LR[i] else rcolor))

    self.ax.set_xlabel('x')
    self.ax.set_ylabel('y')
    self.ax.set_zlabel('z')

  def fit(self, pos):
    self.pos = pos


  def update(self,frame):
    vals = self.pos[frame]

    for i in range( len(self.I) ):
      x = np.array( [vals[self.I[i], 0], vals[self.J[i], 0]] )
      y = np.array( [vals[self.I[i], 1], vals[self.J[i], 1]] )
      z = np.array( [vals[self.I[i], 2], vals[self.J[i], 2]] )
      self.plots[i][0].set_xdata(x)
      self.plots[i][0].set_ydata(y)
      self.plots[i][0].set_3d_properties(z)
      self.plots[i][0].set_color(self.lcolor if self.LR[i] else self.rcolor)

    r = 0.5;
    xroot, yroot, zroot = vals[0,0], vals[0,1], vals[0,2]
    self.ax.set_xlim3d([-r+xroot, r+xroot])
    self.ax.set_zlim3d([-r+zroot, r+zroot])
    self.ax.set_ylim3d([-r+yroot, r+yroot])

    self.ax.set_aspect('equal')




class JointAnimation:
  def __init__(self,skeleton,ax):
    self.ax = ax
    self.skeleton = skeleton
    self.animation = None
    self.plots = dict()

  def init_skeleton(self):
    for name,joint in self.skeleton.joints.items():
      self.plots[joint] = dict()
      for child in joint.children:
        x,y,z = [joint.get_position()[0],child.get_position()[0]], \
                [joint.get_position()[1],child.get_position()[1]], \
                [joint.get_position()[2],child.get_position()[2]]

        self.plots[name][child.name] = self.ax.plot(x,y,z)

  def init_plot(self):
    self.ax.set_xlabel('x')
    self.ax.set_ylabel('y')
    self.ax.set_zlabel('z')

    self.ax.set_xlim3d([-1.5, 1.5])
    self.ax.set_zlim3d([-1.5, 1.5])
    self.ax.set_ylim3d([-1.5, 1.5])

    self.ax.set_aspect('equal')

  def animation_data(self,data):
    self.animation = data

  def update(self,i):
    assert self.animation is not None

    self.skeleton.rotate_all(self.animation,i)

    for name,joint in self.skeleton.joints.items():
      for child in joint.children:
        x,y,z = [joint.get_position()[0],child.get_position()[0]], \
                [joint.get_position()[1],child.get_position()[1]], \
                [joint.get_position()[2],child.get_position()[2]]

        self.plots[name][child.name][0].set_xdata(x)
        self.plots[name][child.name][0].set_ydata(y)
        self.plots[name][child.name][0].set_3d_properties(z)


