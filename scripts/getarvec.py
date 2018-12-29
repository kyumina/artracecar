#!/usr/bin/env python
#coding:utf-8

import rospy
import cv2
import numpy as np
import tf
from geometry_msgs.msg import Vector3
from imgaxis.srv import *
from aruco_msgs.msg import MarkerArray
from aruco_msgs.msg import Marker

#measure time
import time
from functools import wraps

def stop_watch(func) :
  @wraps(func)
  def wrapper(*args, **kargs) :
    start = time.time()
    result = func(*args,**kargs)
    process_time =  time.time() - start
    print("{0} is {1}s".format(func.__name__,process_time))
    return result
  return wrapper

class image_converter:
  def __init__(self):
    self.markers=[]
    self.ar_sub=rospy.Subscriber("aruco_marker_publisher/markers", MarkerArray, self.set_arparam)

  def set_arparam(self,data):
    self.markers=data.markers
    for p in self.markers:
      #車体をARの方向に向ける
      x=p.pose.pose.position.x*100
      z=p.pose.pose.position.z*100
      print("markerID:"+str(p.id))
      print("x:"+str(x))
      print("z:"+str(z))
      print("seata:"+str(np.rad2deg(np.arctan(x/z))))
      quaternion=p.pose.pose.orientation
      e = tf.transformations.euler_from_quaternion((quaternion.x, quaternion.y, quaternion.z, quaternion.w))
      print "x={},y={},z={}".format(np.rad2deg(e[0]),np.rad2deg(e[1]),np.rad2deg(e[2]))

def main():
  rospy.init_node('imgaxis',anonymous=True)
  ic=image_converter()
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")

if __name__=='__main__':
  main()
