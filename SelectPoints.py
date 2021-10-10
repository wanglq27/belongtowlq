import cv2
import numpy as np
'''
这部分是选择单个点or感兴趣的区域 以及显示选择的roi
空格进入下一步
'''
#全局变量
right_up_num=0   #左键点击次数
left_up_num=0    #右键点击次数

#选点or选框
def select_area(camera):
     global img
     grabbed, img = camera.read() # 逐帧采集视频流
     cv2.namedWindow('Image')
     cv2.setMouseCallback('Image',OnMouseAction)
     while(1):
         cv2.imshow('Image',img)
         k=cv2.waitKey(10) & 0xFF
         if k==ord(' '): # 空格退出操作
            break
     cv2.destroyAllWindows() # 关闭页面
     return point1

#定义鼠标的点击事件，选择感兴趣的点or区域
def OnMouseAction(event,x,y,flags,params):
    global point1, point2,point3,point4,right_up_num,left_up_num
    if event == cv2.EVENT_LBUTTONDOWN:#左键点击
        right_up_num=right_up_num+1
        if right_up_num==1:
           x,y=int(x),int(y)
           point1 = [(x, y)]
           cv2.circle(img, point1[0], 2, (0, 0, 255), -1)
        else:
           for i in range(2,right_up_num+1):
              x,y=int(x),int(y)
              point1.append((x,y))
              cv2.circle(img, point1[right_up_num-1], 2, (0, 0, 255), -1)
    elif event==cv2.EVENT_LBUTTONUP: #松开左键
        if right_up_num==1:
           x,y=int(x),int(y)
           point2 = [(x, y)]
           cv2.circle(img, point2[0], 2, (0, 0, 255), -1)
           cv2.rectangle(img, point1[0], point2[0], (255, 0, 0), 1)
        else:
           for i in range(2,right_up_num+1):
              x,y=int(x),int(y)
              point2.append((x,y))
              cv2.circle(img, point2[right_up_num-1], 2, (0, 0, 255), -1)
              cv2.rectangle(img, point1[right_up_num-1], point2[right_up_num-1], (255, 0, 0), 1)
        #print("松开左键")
    elif event==cv2.EVENT_RBUTTONDOWN :
        print("右键点击：删除点")
        left_up_num=left_up_num+1
        if left_up_num==1:
           x,y=int(x),int(y)
           point3 = [(x, y)]
           cv2.circle(img1, point3[0], 2, (0, 0, 255), -1)
        else:
           for i in range(2,left_up_num+1):
              x,y=int(x),int(y)
              point3.append((x,y))
              cv2.circle(img1, point3[left_up_num-1], 2, (0, 0, 255), -1)
    elif event==cv2.EVENT_RBUTTONUP: #松开右键
        if left_up_num==1:
           x,y=int(x),int(y)
           point4 = [(x, y)]
           cv2.circle(img1, point4[0], 2, (0, 0, 255), -1)
           cv2.rectangle(img1, point3[0], point4[0], (255, 0, 0), 1)
        else:
           for i in range(2,left_up_num+1):
              x,y=int(x),int(y)
              point4.append((x,y))
              cv2.circle(img1, point4[left_up_num-1], 2, (0, 0, 255), -1)
              cv2.rectangle(img1, point3[left_up_num-1], point4[left_up_num-1], (255, 0, 0), 1)
    elif flags==cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON): # 按住左键拖曳
        print("左鍵拖曳")

'''
显示轮第一帧框选的轮廓
'''
def outline(camera):
    global img1
    grabbed, img1 = camera.read()  # 逐帧采集视频流
    cv2.namedWindow('Image1')
    cv2.setMouseCallback('Image1', OnMouseAction)
    for i in range(right_up_num):
        tup1 = point1[i]
        tup2 = point2[i]

        Video_choose = img1[tup1[1]:tup2[1], tup1[0]:tup2[0]]
        vc1 = img1[tup1[1]+2:tup2[1]-2, tup1[0]+5:tup2[0]-5]

        blured = cv2.blur(Video_choose, (5, 5))#均值滤波
        canny = cv2.Canny(blured, 64, 128)
        # 找到轮廓
        contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # 绘制轮廓cv2.drawContours(img[tup1[1]:tup2[1], tup1[0]:tup2[0]], contours, -1, (0, 255, 255), 1)

        # vc1轮廓
        blured = cv2.blur(vc1, (5, 5))  # 均值滤波
        canny = cv2.Canny(blured, 64, 128)
        contours1, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # 将vc1轮廓加入vc
        for i in range(len(contours1)):
            contours.append(contours1[i])

        #提取轮廓点
        for j in range(len(contours)):
            oline=contours[j]
            for m in range(oline.shape[0]):
                op=oline[m][0] #点的坐标
                cv2.circle(img1[tup1[1]:tup2[1], tup1[0]:tup2[0]],(op[0],op[1]),1,(0,255,255),-1)
    while (1):
        cv2.imshow("Image1", img1)
        k = cv2.waitKey(10) & 0xFF
        if k == ord(' '):  # 空格退出操作
            break
    cv2.destroyAllWindows()  # 关闭页面
'''
这部分是处理删除的点以及选择的某个轮廓数据
稠密光流跟踪轮廓点的光流
'''
def outline_data(camera,num):
    global tup1,tup2,x,y
    t = []  # 帧数
    x = []
    y = []
    num=int(num)
    tup1=point1[num-1]
    tup2 = point2[num - 1]
    grabbed, old_frame = camera.read()  # 逐帧采集视频流
    Video_choose = old_frame[tup1[1]:tup2[1], tup1[0]:tup2[0]]
    old_gray = cv2.cvtColor(Video_choose, cv2.COLOR_BGR2GRAY)
    blured = cv2.blur(Video_choose, (5, 5))  # 均值滤波
    canny = cv2.Canny(blured, 64, 128)
    # 找到轮廓
    contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # 提取轮廓点
    if left_up_num!=0:
       for i in range(left_up_num):
           tup3 = point3[i]
           tup4 = point4[i]
           #相对坐标
           b1x=tup3[0]-tup1[0]
           b1y=tup3[1]-tup1[1]
           b2x = tup4[0] - tup1[0]
           b2y = tup4[1] - tup1[1]
           if i==0:
              for j in range(len(contours)):
                 oline=contours[j]
                 for m in range(oline.shape[0]):
                    op=oline[m][0] #点的坐标
                    if not ((b1x < op[0] < b2x) and (b1y < op[1] < b2y)):
                      x.append(op[0])
                      y.append(op[1])
           if i!=0:
              j=0
              while j<len(x):
                 if ((b1x<x[j]<b2x) and (b1y < y[j] < b2y)):
                   del x[j]
                   del y[j]
                 else:
                   j = j + 1
    if left_up_num==0:
        for j in range(len(contours)):
          oline = contours[j]
          for m in range(oline.shape[0]):
              op = oline[m][0]  # 点的坐标
              x.append(op[0])
              y.append(op[1])

    i=1
    A = []
    B = []
    for j in range(len(x)):
        A.append([])
        B.append([])

    while True:
        ret, frame = camera.read()  # 逐帧采集视频流
        if not ret:
            break
        t.append(i)
        Video_choose1 = frame[tup1[1]:tup2[1], tup1[0]:tup2[0]]
        frame_gray = cv2.cvtColor(Video_choose1, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(old_gray, frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        old_gray = frame_gray
        fx, fy = flow[y, x].T  # 取选定网格点坐标对应的光流位移
        for n in range(len(x)):
            A[n].append(fx[n])
        for n in range(len(y)):
            B[n].append(fy[n])
        lines = np.vstack([x, y, x + fx, y + fy]).T.reshape(-1, 2, 2)  # 将初始点和变化的点堆叠成2*2的数组
        lines = np.int32(lines + 0.5)  # 忽略微小的假偏移，整数化
        cv2.polylines(frame[tup1[1]:tup2[1], tup1[0]:tup2[0]], lines, 0, (0, 255, 0))  # 以初始点和终点划线表示光流运动
        for (x1, y1), (x2, y2) in lines:
            cv2.circle(frame[tup1[1]:tup2[1], tup1[0]:tup2[0]], (x1, y1), 1, (0, 255, 0), -1)  # 在初始点（网格点处画圆点来表示初始点）
            #cv2.cv2.arrowedLine(frame[tup1[1]:tup2[1], tup1[0]:tup2[0]], (x1, y1), (x2,y2),(0, 255, 0), 1)
        cv2.imshow('Video_choose', frame)
        ch = cv2.waitKey(1)
        if ch == 27:
            break
        if ch == ord(' '):
            break
        i=i+1

    return A[5],t,x,y,A,B,tup1,tup2