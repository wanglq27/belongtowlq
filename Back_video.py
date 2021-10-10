import scipy as sci
import cv2
import numpy as np
from scipy import signal
'''
计算阈值，过滤掉一些振动过大or不动的点
在模态频率附近进行带通滤波，再映射到原视频中
'''
def filter(freq,x,A,B,t):
    # 求阈值
    global C,D,Pxy
    r = 0
    Anew = []
    Bnew = []
    C = []
    D = []
    Pxy = []  # 幅值
    for n in range(len(x)):
        fft_result_abs = np.abs(sci.fft.fft(A[n])) * 2 / len(t)  # 求x方向的幅值
        fft_result_abs1 = np.abs(sci.fft.fft(B[n])) * 2 / len(t)  # 求y方向的幅值
        xy = pow(fft_result_abs, 2) + pow(fft_result_abs1, 2)
        Pxy.append(pow(xy, 0.5))
    for n in range(len(Pxy)):  # 平方后求和
        r = pow(Pxy[n], 2) + r
    r = r / len(x)
    R = pow(r, 0.5)
    Ra = max(R)
    for n in range(len(x)):
        if ((Pxy[n] >= 0.5 * Ra).any() and (Pxy[n] <= 5 * Ra).any()):
            Anew.append(A[n])
            Bnew.append(B[n])

    # 带通滤波x
    for n in range(len(Anew)):
        wn1 = 2 * 20.6 / freq
        wn2 = 2 * 24.6 / freq
        b, a = signal.butter(8, [wn1, wn2], 'bandpass')  # 配置滤波器 8 表示滤波器的阶数
        filtedData = signal.filtfilt(b, a, Anew[n])  # 过滤信号
        filtedData1 = signal.filtfilt(b, a, Bnew[n])  # 过滤信号
        C.append(filtedData)
        D.append(filtedData1)


def num2color(values):
   """将数值映射为颜色"""
   vmax=max(Pxy[2])
   vmin=min(Pxy[2])
   f=(vmax-vmin)/6
   if (values>=vmin) and (values<=vmin+f):
       return (201,252,189)#
   if (values > vmin+f) and (values <= vmin+2*f):
       return (0,252,124)#天蓝
   if (values > vmin+2*f) and (values <= vmin+3*f):
       return (34,139,34)#红色
   if (values > vmin + 3 * f) and (values <= vmin + 4 * f):
       return (0, 255, 255)  # 红色
   if (values > vmin + 4 * f) and (values <= vmin + 5 * f):
       return (0, 97, 255)  # 红色
   if (values > vmin+5*f) and (values <= vmax):
       return (0,0,255)#红色

def backvideo(x,y,tup1,tup2):
    cap = cv2.VideoCapture('VID604.mp4')
    i = 0
    while True:
        fx = []
        fy = []
        ret, frame = cap.read()  # 逐帧采集视频流
        if not ret:
            break
        # 绘制线
        contours = []
        for n in range(len(C)):
            contours.append([])
        for j in range(len(C)):
            fx.append(C[j][i])
            fy.append(D[j][i])
            l1 = np.hstack((x[j], y[j]))
            l2 = np.hstack((x[j] + fx[j] * 15, y[j] + fy[j] * 15))
            lines = np.vstack((l1, l2))  # 将初始点和变化的点堆叠成2*2的数组
            lines = np.int32(lines + 0.5)  # 忽略微小的假偏移，整数化
            # cv2.polylines(frame[tup1[1]:tup2[1], tup1[0]:tup2[0]], [lines], 0, num2color(Pxy[j][i]),2)  # 以初始点和终点划线表示光流运动
            for (x1, y1), (x2, y2) in [lines]:
                cv2.cv2.arrowedLine(frame[tup1[1]:tup2[1], tup1[0]:tup2[0]], (x1, y1), (x2, y2), num2color(Pxy[j][i]),
                                    1, 8)
            contours[j] = [[np.int32(x[j] + fx[j] * 8), np.int32(y[j] + fy[j] * 8)]]
        cv2.imshow('BACK', frame)
        ch = cv2.waitKey(1)  # z/1ms==1000z/s
        if ch == 27:
            break
        if ch == ord(' '):
            break
        if i != len(C[0]) - 1:
            i = i + 1
        else:
            break
