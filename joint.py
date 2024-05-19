from operator import add
import numpy as np

class Joint:
  def __init__(self,name,position,rotate_with_parent=True):
    self.original_position = position
    self.position = position # position relative to parent
    self.children = []
    self.rotation = np.eye(3) # joint rotation frame after parent rotation
    self.parent = None
    self.name = name
    self.rotate_with_parent = rotate_with_parent


  def rotate(self,angle,axes = 'zxy'): # 3 dimension - fixed frame rotation (not relative)
    RM = np.eye(3)
    for i in range(len(axes)):
      RM = self.R(axes[i],angle[i]) @ RM

    R_isb = self.R('x',angle=90)

    RM = RM @ self.rotation


    for child in self.children:
      isb_pos = (R_isb.T @  RM  @ R_isb).dot(child.original_position)
      child.position = isb_pos
      child.rotation = RM if child.rotate_with_parent else np.eye(3)

  def R(self,axis="x",angle=90):
    rad = np.deg2rad(angle)
    if axis == 'x':
      R = np.array([[1,           0,             0],
                    [0, np.cos(rad),  -np.sin(rad)],
                    [0, np.sin(rad),   np.cos(rad)]])

    elif axis == 'y':
      R = np.array([[ np.cos(rad),           0,  np.sin(rad)],
                    [           0,           1,           0],
                    [ - np.sin(rad),           0, np.cos(rad)]])

    elif axis =='z':
      R = np.array([[ np.cos(rad),   -np.sin(rad),    0],
                    [ np.sin(rad),    np.cos(rad),    0],
                    [           0,              0,    1]])
    else:
      raise IOError("axis has to be x, y, or z")
    return R


  def get_link_length(self):
    distance = 0
    for i,j in zip(self.get_position(),self.parent.get_position()):
      distance += np.power(i-j,2)
    return np.sqrt(distance)

  def get_position(self):
    return list(map(add,self.parent.get_position(), self.position)) if self.parent is not None else self.position

  def set_child(self,child):
    self.children.append(child)
    child.parent = self

    

class Skeleton:
  def __init__(self):
    self.joints, self.head = self.initialize_joint()

  def initialize_joint(self):
    joints = dict()
    joints['jL5S1'] = Joint('jL5S1',position=[0,0,0])
    joints['jL4L3'] = Joint('jL4L3',position=[0,0,0.3])
    joints['jL1T12'] = Joint('jL1T12',position=[0,0,0.3])
    joints['jT9T8'] = Joint('jT9T8',position=[0,0,0.3])
    joints['jT1C7'] = Joint('jT1C7',position=[0,0,0.3])
    joints['jC1Head'] = Joint('jC1Head',position=[0,0,0.3])

    joints['jL5S1'].set_child(joints['jL4L3'])
    joints['jL4L3'].set_child(joints['jL1T12'])
    joints['jL1T12'].set_child(joints['jT9T8'])
    joints['jT9T8'].set_child(joints['jT1C7'])
    joints['jT1C7'].set_child(joints['jC1Head'])

    joints['jRightT4Shoulder'] = Joint('jRightT4Shoulder',position=[0,-0.1,0.2])
    joints['jRightShoulder'] = Joint('jRightShoulder',position=[0,-0.3,0])
    joints['jRightElbow'] = Joint('jRightElbow',position=[0,0,-0.7])
    joints['jRightWrist'] = Joint('jRightWrist',position=[0,0,-0.7])
    joints['jRightHand'] = Joint('jRightHand',position=[0,0,-0.2])

    joints['jT9T8'].set_child(joints['jRightT4Shoulder'])
    joints['jRightT4Shoulder'].set_child(joints['jRightShoulder'])
    joints['jRightShoulder'].set_child(joints['jRightElbow'])
    joints['jRightElbow'].set_child(joints['jRightWrist'])
    joints['jRightWrist'].set_child(joints['jRightHand'])



    joints['jLeftT4Shoulder'] = Joint('jLeftT4Shoulder',position=[0,0.1,0.2])
    joints['jLeftShoulder'] = Joint('jLeftShoulder',position=[0,0.3,0])
    joints['jLeftElbow'] = Joint('jLeftElbow',position=[0,0,-0.7])
    joints['jLeftWrist'] = Joint('jLeftWrist',position=[0,0,-0.7])
    joints['jLeftHand'] = Joint('jLeftHand',position=[0,0,-0.2])

    joints['jT9T8'].set_child(joints['jLeftT4Shoulder'])
    joints['jLeftT4Shoulder'].set_child(joints['jLeftShoulder'])
    joints['jLeftShoulder'].set_child(joints['jLeftElbow'])
    joints['jLeftElbow'].set_child(joints['jLeftWrist'])
    joints['jLeftWrist'].set_child(joints['jLeftHand'])
    

    joints['jRightHip'] = Joint('jRightHip',position=[0,-0.3,0])
    joints['jRightKnee'] = Joint('jRightKnee',position=[0,0,-1])
    joints['jRightAnkle'] = Joint('jRightAnkle',position=[0,0,-1])
    joints['jRightBallFoot'] = Joint('jRightBallFoot',position=[0.3,0,0])

    joints['jL5S1'].set_child(joints['jRightHip'])
    joints['jRightHip'].set_child(joints['jRightKnee'])
    joints['jRightKnee'].set_child(joints['jRightAnkle'])
    joints['jRightAnkle'].set_child(joints['jRightBallFoot'])

    joints['jLeftHip'] = Joint('jLeftHip',position=[0,0.3,0])
    joints['jLeftKnee'] = Joint('jLeftKnee',position=[0,0,-1])
    joints['jLeftAnkle'] = Joint('jLeftAnkle',position=[0,0,-1])
    joints['jLeftBallFoot'] = Joint('jLeftBallFoot',position=[0.3,0,0])

    joints['jL5S1'].set_child(joints['jLeftHip'])
    joints['jLeftHip'].set_child(joints['jLeftKnee'])
    joints['jLeftKnee'].set_child(joints['jLeftAnkle'])
    joints['jLeftAnkle'].set_child(joints['jLeftBallFoot'])

    return joints, joints['jL5S1']

  def rotate_all(self,angle_data,frame=0):

    def recurrent_rotate(root):
      if root.name in angle_data:
        if root.name not in ['jLeftShoulder','jRightShoulder']:
          root.rotate(angle_data[root.name][frame],axes='zxy')
        else:
          root.rotate(angle_data[root.name][frame],axes='xzy')


        for child in root.children:
          recurrent_rotate(child)

    recurrent_rotate(self.head)