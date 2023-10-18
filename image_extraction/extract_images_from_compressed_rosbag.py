import tqdm
import rosbag  # only python2.7 (http://wiki.ros.org/kinetic/Installation/Ubuntu)
import numpy as np

import cv2
import matplotlib.pyplot as plt
import os
import argparse
import rospy
import datetime

parser = argparse.ArgumentParser()
parser.add_argument(dest='target_dir', type=str, help="The path to the files' directory.")
parser.add_argument(dest='in_file', type=str, help="The name of the input file.")
parser.add_argument(dest='offset', type=int, help="How many hours to offset")
args = parser.parse_args()

## Step1 - Read .rosbag
bag = rosbag.Bag(os.path.join(args.target_dir, args.in_file))

## Step2 - Read Compressed Images Packets
print(' - start_time        : ', bag.get_start_time())
print(' - end_time          : ', bag.get_end_time())

topics = ['/port_0/camera_0/image_raw/compressed', '/port_0/camera_1/image_raw/compressed']

for idx, (topic, msg, t) in enumerate(bag.read_messages(topics=topics)):
    print(t)

    if topic == '/port_0/camera_0/image_raw/compressed':
        prefix = 'STREETDRONE.FRONTCAM_IMG.'
    elif topic == '/port_0/camera_1/image_raw/compressed':
        prefix = 'STREETDRONE.REARCAM_IMG.'

    img = cv2.imdecode(np.fromstring(msg.data, np.uint8), cv2.IMREAD_COLOR)
    dt1 = datetime.datetime.utcfromtimestamp(t.to_sec())
    dt1 = dt1 + datetime.timedelta(hours=args.offset)

    t_str = dt1.strftime('%Y-%m-%dT%H%M%S.%f').split('.')[0]
    t_ms = (int(round(float(dt1.strftime('%Y-%m-%dT%H%M%S.%f').split('.')[1]), -3)) / 1000)
    if t_ms == 1000:
        t_ms = 0
    timestamp = t_str + '.' + str(t_ms).zfill(3)

    filename = os.path.join(args.target_dir, prefix + timestamp + ".png")
    # Note that imwrite detects extension for writing
    cv2.imwrite(filename, img)
    print('Written file {0}'.format(filename))
