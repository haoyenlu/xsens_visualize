import os
import argparse
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from parse_utils import parse_position, parse_jointAngle
from animation import SegmentAnimation, JointAnimation

def parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data',type=str)
    parser.add_argument('--save',type=str)

    args = parser.parse_args()
    return args


def main(mvnx_file,save_folder):
    os.makedirs(save_folder,exist_ok=True)

    position, sensors = parse_position(mvnx_file)
    fig  = plt.figure()
    ax = plt.axes(projection='3d')
    ax.view_init(0, 30 ,0)

    obj = SegmentAnimation(ax)
    obj.fit(position)

    frames = position.shape[0]

    ani = animation.FuncAnimation(fig,obj.update,frames=frames)
    FFwriter = animation.FFMpegWriter(fps=60)
    ani.save(os.path.join(save_folder,'animation.mp4'), writer = FFwriter)



if __name__ == '__main__':
    args = parse_argument()

    main(args.data,args.save)
