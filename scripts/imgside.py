#!/usr/bin/env python
#coding:utf-8

import rospy
import cv2
import numpy as np
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
    self.leftv=0
    self.rightv=0
    self.markers=[]
    self.lastarupdatetime=time.time()
    self.ar_sub=rospy.Subscriber("aruco_marker_publisher/markers", MarkerArray, self.set_arparam)
    self.ser=rospy.Service("get_speed_req",GetSpeedReq,self.setspeed)

  def relaymarker(self,x):
    dx=x+50/2
    if dx>0:
      self.leftv=dx+30
      self.rightv=30
    else:
      self.leftv=30
      self.rightv=-dx+30
    return 1

  def setspeed(self,req):
    resid=-1
    if req.req==1:
        beforez=1000 #比較用z
        for p in self.markers:
            x=p.pose.pose.position.x*100
            z=p.pose.pose.position.z*100
            if z>beforez:
                continue
            print("markerID:"+str(p.id))
            print("x:"+str(x))
            print("z:"+str(z))
            if (self.relaymarker(x) if p.id in range(10,19+1) else 0):
              continue
            theta=np.rad2deg(np.arctan(x/z))
            if theta<-10:
                self.leftv=30
                self.rightv=-30
                print("左回転")
            elif theta>10:
                self.leftv=-30
                self.rightv=30
                print("右回転")
            elif p.pose.pose.position.z*100<1500:
                print("move")
                resid=p.id
            else:
                self.leftv=50
                self.rightv=50
                print("まっすぐ")
        return GetSpeedReqResponse(resid,self.leftv,self.rightv)
    elif req.req==2:
        #最後にマーカーを取得してから1s経つとマーカー無しと返す
        elapsedtime=time.time()-self.lastarupdatetime
        if elapsedtime>1:
            return GetSpeedReqResponse(resid,0,0)
        else:
            for p in self.markers:
                resid=p.id
            return GetSpeedReqResponse(resid,0,0)

  def set_arparam(self,data):
    self.markers=data.markers
    self.lastarupdatetime=time.time()

def main():
  rospy.init_node('imgaxis',anonymous=True)
  ic=image_converter()
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")

if __name__=='__main__':
  main()
