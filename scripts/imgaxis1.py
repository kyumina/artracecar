#!/usr/bin/env python
#coding:utf-8

import rospy
import cv2
import numpy as np
#rosとopencvの画像の相互変換
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from bluetank.msg import Speed
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
    self.image_pub = rospy.Publisher("image_topic_2",Image)
    self.speed_pub = rospy.Publisher("speed",Speed)
    self.bridge=CvBridge()
    #self.image_sub = rospy.Subscriber("cv_camera/image_raw", Image, self.callback)
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
      speed_msg=Speed()
      if x<-100:
        speed_msg.left_speed=-30
        speed_msg.right_speed=30
      elif x>100:
        speed_msg.left_speed=30
        speed_msg.right_speed=-30
      elif p.pose.pose.position.z*100<9:
        #左回転
        if p.id == 0:
          speed_msg.left_speed=-30
          speed_msg.right_speed=30
        #停止
        elif p.id == 1:
          speed_msg.left_speed=0
          speed_msg.right_speed=0
      else:
        speed_msg.left_speed=50
        speed_msg.right_speed=50
      self.speed_pub.publish(speed_msg)


  #@stop_watch
  #def callback(self,data):
  #  try:
  #    cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
  #  except CvBridgeError as e:
  #    print(e)

  #  #========================
  #  # YOU INPUT ANY CODE
  #  #========================

  #  #CONVERT BLACK WHITE
  #  cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
  #  yokohiki=100
  #  tatehiki=250
  #  cv_image=cv_image[tatehiki:480, 0+yokohiki:640-yokohiki]
  #  thresh=200
  #  max_pixel=255
  #  ret, cv_image = cv2.threshold(cv_image,thresh,max_pixel,cv2.THRESH_BINARY)

  #  #SEARCH AR
  #  if len(self.markers):
  #    #今回はmarkeridが0とわかっている
  #    for p in self.markers:
  #      print(p.pose.pose.orientation)


  #  #GET HOW RAD AXIS CAR
  #  X=[]
  #  Y=[]
  #  for y,yoko in enumerate(cv_image[::30]):
  #    plus=0
  #    count=0
  #    for i,x in enumerate(yoko):
  #      if x==255:
  #        plus+=i
  #        count+=1
  #    if count>0:
  #      center=(plus/count,y*30)
  #      cv2.circle(cv_image, center, 20, 255/2)
  #      X.append(480-tatehiki-center[1])
  #      Y.append(center[0]-320+yokohiki)
  #  A=np.array([X,np.ones(len(X))])
  #  A = A.T
  #  try:
  #    a,b = np.linalg.lstsq(A,Y)[0]
  #    cv_image=cv2.line(cv_image,(int(b+320-yokohiki),480-tatehiki),(int(a*(480-tatehiki)+b)+320-yokohiki,0),100,5)
  #    cv2.circle(cv_image,(int(b+320-yokohiki),480-tatehiki), 50, 255/2)
  #    cv2.circle(cv_image, (int(a*(480-tatehiki)+b)+320-yokohiki,0), 50, 255/2)

  #  except:
  #    print("math failed")
  #    self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "8UC1"))
  #    return
  #  try:
  #    self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "8UC1"))
  #  except Exception as e:
  #    print(e)

  #  #AXIS TO SPEED & PUBLISH
  #  speed_msg=Speed()
  #  print(b)
  #  if -50<b<50:
  #    speed_msg.right_speed=50
  #    speed_msg.left_speed=50
  #  else:
  #    handle = b/5-a/5
  #    if handle>0:
  #      speed_msg.right_speed=0
  #      speed_msg.left_speed=int(b/5-a/5)
  #    else:  
  #      speed_msg.right_speed=-int(b/5-a/5)
  #      speed_msg.left_speed=0
  #  self.speed_pub.publish(speed_msg)

def main():
  rospy.init_node('imgaxis',anonymous=True)
  ic=image_converter()
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")

if __name__=='__main__':
  main()
