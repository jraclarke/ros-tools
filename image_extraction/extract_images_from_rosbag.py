#!/usr/bin/env python
"""
Read image topics from a bagfile and output them to a png (can be changed) with a timestamp 
and topic as the name.
Works for either compressed or uncompressed image topics.

Todo:
Error handling.
"""
import tqdm
import rosbag  # only python2.7 (http://wiki.ros.org/kinetic/Installation/Ubuntu)
import numpy as np
import cv2
import os
import argparse
import rospy
import datetime
from cv_bridge import CvBridge

parser = argparse.ArgumentParser()
parser.add_argument(dest='target_dir', type=str, help="The path to the bag files' directory.")
parser.add_argument(dest='in_file', type=str, help="The name of the input file.")
parser.add_argument(dest='offset', type=int, help="How many hours to offset")
parser.add_argument(dest='topics', type=str, help="csv of image topics to output images for.")
parser.add_argument("--compressed", action="store_true", help="Input image topics are compressed")
parser.set_defaults(compress=False)
args = parser.parse_args()

bridge = CvBridge()

# Read rosbag
bag = rosbag.Bag(os.path.join(args.target_dir, args.in_file))

print(' - start_time        : ', bag.get_start_time())
print(' - end_time          : ', bag.get_end_time())

topics = args.topics.split(',')

for idx, (topic, msg, t) in enumerate(bag.read_messages(topics=topics)):

    if args.compressed:
        img = cv2.imdecode(np.fromstring(msg.data, np.uint8), cv2.IMREAD_COLOR)
    else:
        img = bridge.imgmsg_to_cv2(msg, "bgr8")

    dt1 = datetime.datetime.utcfromtimestamp(t.to_sec())
    dt1 = dt1 + datetime.timedelta(hours=args.offset)

    t_str = dt1.strftime('%Y-%m-%dT%H%M%S.%f').split('.')[0]
    t_ms = (int(round(float(dt1.strftime('%Y-%m-%dT%H%M%S.%f').split('.')[1]), -3)) / 1000)
    if t_ms == 1000:
        t_ms = 0
    timestamp = t_str + '.' + str(t_ms).zfill(3)

    filename = os.path.join(args.target_dir, timestamp + topic.replace('/', '.') + ".png")
    # Note that imwrite detects extension for writing
    cv2.imwrite(filename, img)
    print('Written file {0}'.format(filename))

