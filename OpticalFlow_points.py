import cv2
import numpy as np
'''
以选择的点为中心取上下左右十个像素的矩形范围 step选择矩形范围
稠密光流估计矩形区域内四个中间位置的光流进行计算
返回值可以是A1-A4任意一个
eg：感觉这样不是很合理？还要思考下需要计算的点！
'''
def gf_point(str,camera,point):
      A1 = [] #区域点
      A2 = []
      A3 = []
      A4 = []
      t = []   #帧数
      num = int(str)
      step = 10
      tup = point[num-1]
      grabbed, old_frame = camera.read() # 逐帧采集视频流
      Video_choose = old_frame[tup[1]-10:tup[1]+10,tup[0]-10:tup[0]+10]
      old_gray = cv2.cvtColor(Video_choose, cv2.COLOR_BGR2GRAY)
      mask = np.zeros_like(Video_choose)
      i=1
      while True:
            ret, frame = camera.read() # 逐帧采集视频流
            if not ret:
               break
            t.append(i)
            Video_choose1=frame[tup[1]-10:tup[1]+10,tup[0]-10:tup[0]+10]
            frame_gray=cv2.cvtColor(Video_choose1, cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(old_gray, frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            old_gray = frame_gray
            # 绘制线
            h, w = mask.shape[:2]
            y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1).astype('int64')#以网格的形式选取二维图像上等间隔的点，这里间隔为10，reshape成2行的array
            fx, fy = flow[y,x].T#取选定网格点坐标对应的光流位移
            A1.append(fx[0])
            A2.append(fx[1])
            A3.append(fx[2])
            A4.append(fx[3])
            lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)#将初始点和变化的点堆叠成2*2的数组
            lines = np.int32(lines + 0.5)#忽略微小的假偏移，整数化
            cv2.polylines(mask, lines, 0, (0, 255, 0))#以初始点和终点划线表示光流运动
            for (x1, y1), (x2, y2) in lines:
                  cv2.circle(mask, (x1, y1), 1, (0, 255, 0), -1)#在初始点（网格点处画圆点来表示初始点）
            vc=cv2.add(Video_choose1,mask)
            cv2.imshow('Video_choose', vc)
            ch = cv2.waitKey(5)
            if ch == 27:
               break
            if ch == ord(' '):
               break
            i=i+1
      cv2.destroyAllWindows()

      return A1,t