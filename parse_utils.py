import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import re
import os


def get_namespace(tag):
    m = re.match(r'\{.*\}',tag)
    ns = m.group(0)
    return ns



def parse_jointAngle(_file):
  '''
  Get ZXY Joint Angle for every frame, get XZY Joint Angle for shoulder joint
  '''
  tree = ET.parse(_file)
  root = tree.getroot()
  ns = get_namespace(root.tag)
  
  subject = root.find(ns + 'subject')
  joints = subject.find(ns + 'joints')

  joints_name = []
  labels = []
  for joint in joints:
    joints_name.append(joint.attrib['label'])
    labels.append(joint.attrib['label'] + '_x')
    labels.append(joint.attrib['label'] + '_y')
    labels.append(joint.attrib['label'] + '_z')

  frames = subject.find(ns + 'frames')

  zxy = []
  xzy = []
  for frame in frames[3:]:
      jointAngle = frame.find(ns + "jointAngle")
      zxy.append([float(num) for num in jointAngle.text.split(' ')])

      jointAngleXZY = frame.find(ns + "jointAngleXZY")
      xzy.append([float(num) for num in jointAngleXZY.text.split(' ')])


  df_zxy = pd.DataFrame(np.array(zxy),columns=labels)
  df_xzy = pd.DataFrame(np.array(xzy),columns=labels)

  df_zxy
  df_zxy[['jRightShoulder_x','jRightShoulder_y','jRightShoulder_z','jLeftShoulder_x','jLeftShoulder_y','jLeftShoulder_z']] = df_xzy[['jRightShoulder_x','jRightShoulder_y','jRightShoulder_z','jLeftShoulder_x','jLeftShoulder_y','jLeftShoulder_z']]
  return df_zxy,joints_name

def parse_position(_file):
  tree = ET.parse(_file)
  root = tree.getroot()
  ns = get_namespace(root.tag)
  subject = root.find(ns + 'subject')

  sensors = subject.find(ns + 'segments')

  all_sensor = []
  for sensor in sensors:
    all_sensor.append(sensor.attrib['label'])

  pos = np.empty((len(all_sensor),3))
  frames = subject.find(ns + 'frames')
  for frame in frames[3:]:
    position = frame.find(ns + 'position')
    data = [float(num) for num in position.text.split(' ')]
    temp = np.empty((len(all_sensor),3))
    for i, d in enumerate(data):
      temp[i//3,i%3] = d
    pos = np.row_stack([pos,temp])

  pos = np.reshape(pos,(-1,len(all_sensor),3))
  return pos, all_sensor


class JointAngleData:
  def __init__(self,df,joints_name):
    self.df = df
    self.data = dict()
    self.initialize_joint_data(joints_name)


  def initialize_joint_data(self,joints_name):
    for joint in joints_name:
      self.data[joint] = self.get_jointAngle_np(joint)

  def get_jointAngle_np(self,name):
    temp =  self.df[[f'{name}_z',f'{name}_x',f'{name}_y']].to_numpy()


    if name == 'jL5S1':
      temp[:,0] =  -temp[:,0]

    if name in ['jLeftHip','jRightHip']:
      temp[:,0] =  - temp[:,0]
      temp[:,2] = -temp[:,2]

    if name in ['jRightElbow','jLeftElbow']:
      # temp[:,0] = - temp[:,0]
      temp[:,1] = -temp[:,1]
      temp[:,2] = -temp[:,2]
    

    if name in ['jLeftShoulder','jRightShoulder']:
      temp[:,0] = -temp[:,0]
      # temp[:,2] = -temp[:,2]
      # temp[:,1] = -temp[:,1]

    if name == 'jRightShoulder':
      temp[:,1] = -temp[:,1]


    return temp
