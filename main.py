import cv2
import numpy as np
import video_code
import SelectPoints
import OpticalFlow_GF
import OpticalFlow_points
import Show_data
import Back_video

#主函数
def main():
      camera,fps = video_code.video_choose()#视频导入
      string = input('请选择：1.任意选点；2.规整选点;3.轮廓选点:')
      if string=='1':
         point = SelectPoints.select_area(camera)  # 在第一帧选择点
         str = input('显示第几个点的数据？请输入数字:')
         pointdata,t = OpticalFlow_points.gf_point(str,camera,point)      #估计某点的光流
         Show_data.fft_data(fps,pointdata,t)
      elif string=='2':
         str = input('请输入步长:')
         OpticalFlow_GF.gf_select(str,camera) #全局稠密光流
      elif string == '3':
         SelectPoints.select_area(camera)  # 在第一帧选择框
         SelectPoints.outline(camera)
         str = input('显示第几个轮廓的数据？请输入数字:')
         pointdata,t,x,y,A,B,tup1,tup2 = SelectPoints.outline_data(camera,str)
         Show_data.fft_data(fps, pointdata, t)
         Back_video.filter(fps,x,A,B,t)      #设置阈值，滤波
         Back_video.backvideo(x,y,tup1,tup2)   #映射到原视频中
      camera.release()
      cv2.destroyAllWindows()



if __name__ == '__main__':
      main()