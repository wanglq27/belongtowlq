import matplotlib.pyplot as plt
import scipy as sci
import numpy as np
from scipy import signal
from matplotlib.pylab import mpl
'''
这部分是显示时域数据和频域数据的
参数：sampling_freq 视频的帧率
     A：某点的响应数据（此处是位移-时间数据）
     t:时间
'''
mpl.rcParams['font.sans-serif'] = ['SimHei']   #显示中文
mpl.rcParams['axes.unicode_minus']=False      #显示负号

def fft_data(sampling_freq,A,t):

    # 傅里叶变换
    fft_result_abs1 = np.abs(sci.fft.fft(A)) * 2 / len(t)
    f_idx1 = np.arange(len(t)) * sampling_freq / len(t)
    # 导出数据
    '''
    t1=t
    c=np.array(A1)
    c = c.astype(np.float32)
    A1=c.tolist()
    with open("rdata2.csv", 'w', newline='') as t:  # numline是来控制空的行数的
        writer = csv.writer(t)  # 这一步是创建一个csv的写入器
        writer.writerow(t1)  # 写入标签
        writer.writerow(A1)  # 写入样本数据
    '''

    # 带通滤波
    low = 2
    high = 28
    wn1 = 2 * low / sampling_freq
    wn2 = 2 * high / sampling_freq
    b, a = signal.butter(8, [wn1, wn2], 'bandpass')  # 配置滤波器 8 表示滤波器的阶数
    filtedData = signal.filtfilt(b, a, A)  # 过滤信号

    fft_result_abs2 = np.abs(sci.fft.fft(filtedData)) * 2 / len(t)
    f_idx2 = np.arange(len(t)) * sampling_freq / len(t)

    # 画图
    plt.close('all')
    plt.figure()
    plt.subplot(2, 2, 1)
    plt.plot(t, A)
    plt.title(U'原始时域信号')

    plt.subplot(2, 2, 2)
    plt.plot(f_idx1[range(int(len(t) / 2))], fft_result_abs1[range(int(len(t) / 2))])
    plt.title(U'原始信号频域分析')

    plt.subplot(2, 2, 3)
    plt.plot(t, filtedData)
    plt.title(U'滤波信号分析')

    plt.subplot(2, 2, 4)
    plt.plot(f_idx2[range(int(len(t) / 2))], fft_result_abs2[range(int(len(t) / 2))])
    plt.title(U'滤波信号频域分析')
    plt.show()