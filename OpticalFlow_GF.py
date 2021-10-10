import  cv2
import numpy as np
'''
这部分是全局光流估计，计算速度慢
后续可以改为只有结构部分进行估计，要加上SelectPoints
'''
# 稠密光流网格
def draw_flow(flow, mask, step):
    step = int(step)
    h, w = mask.shape[:2]
    y, x = np.mgrid[step / 2:h:step, step / 2:w:step].reshape(2, -1).astype(
        'int64')  # 以网格的形式选取二维图像上等间隔的点，这里间隔为16，reshape成2行的array
    fx, fy = flow[y, x].T  # 取选定网格点坐标对应的光流位移
    lines = np.vstack([x, y, x + fx, y + fy]).T.reshape(-1, 2, 2)  # 将初始点和变化的点堆叠成2*2的数组
    lines = np.int32(lines + 0.5)  # 忽略微小的假偏移，整数化
    cv2.polylines(mask, lines, 0, (0, 255, 0))  # 以初始点和终点划线表示光流运动
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(mask, (x1, y1), 1, (0, 255, 0), -1)  # 在初始点（网格点处画圆点来表示初始点）
    return mask


# BGR显示
def draw_hsv(flow):
    h, w = flow.shape[:2]
    fx, fy = flow[:, :, 0], flow[:, :, 1]
    ang = np.arctan2(fy, fx) + np.pi  # 得到运动的角度
    v = np.sqrt(fx * fx + fy * fy)  # 得到运动的位移长度
    hsv = np.zeros((h, w, 3), np.uint8)  # 初始化一个0值空3通道图像
    hsv[..., 0] = ang * (180 / np.pi / 2)  # B通道为角度信息表示色调
    hsv[..., 1] = 255  # G通道为255饱和度
    hsv[..., 2] = np.minimum(v * 4, 255)  # R通道为位移与255中较小值来表示亮度
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)  # 将得到的HSV模型转换为BGR显示
    return bgr


def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:, :, 0] += np.arange(w)
    flow[:, :, 1] += np.arange(h)[:, np.newaxis]
    res = cv2.remap(img, flow, None, cv2.INTER_LINEAR)  # 图像几何变换（线性插值），将原图像的像素映射到新的坐标上去
    return res


def viz_flow(flow):
    # 色调H：用角度度量，取值范围为0°～360°，从红色开始按逆时针方向计算，红色为0°，绿色为120°,蓝色为240°
    # 饱和度S：取值范围为0.0～1.0
    # 亮度V：取值范围为0.0(黑色)～1.0(白色)
    h, w = flow.shape[:2]
    hsv = np.zeros((h, w, 3), np.uint8)
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv[..., 0] = ang * 180 / np.pi / 2
    hsv[..., 1] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    # flownet是将V赋值为255, 此函数遵循flownet，饱和度S代表像素位移的大小，亮度都为最大，便于观看
    # 也有的光流可视化讲s赋值为255，亮度代表像素位移的大小，整个图片会很暗，很少这样用
    hsv[..., 2] = 255
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr

# 稠密光流法
def gf_select(step,camera):
    ret, prev = camera.read()  # 读取视频第一帧作为光流输入的当前帧֡
    prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(prev)
    show_hsv = False
    show_glitch = False
    cur_glitch = prev.copy()

    while True:
        ret, img = camera.read()  # 读取视频的下一帧作为光流输入的当前帧
        if ret == True:  # 判断视频是否结束
            if cv2.waitKey(10) == 27:
                break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            # Farnback光流法
            prevgray = gray  # 计算完光流后，将当前帧存储为下一次计算的前一帧
            imgg = cv2.add(img, draw_flow(flow, mask, step))
            cv2.imshow('flow', imgg)
            if show_hsv:
                cv2.imshow('flow HSV', draw_hsv(flow))
            if show_glitch:
                cur_glitch = warp_flow(cur_glitch, flow)
                cv2.imshow('glitch', cur_glitch)

            ch = 0xFF & cv2.waitKey(1)
            if ch == ord(' '):
                break
            if ch == 27:
                break
            if ch == ord('1'):
                show_hsv = not show_hsv
                print('HSV flow visualization is', ['off', 'on'][show_hsv])
            if ch == ord('2'):
                show_glitch = not show_glitch
                if show_glitch:
                    cur_glitch = img.copy()
                print('glitch is', ['off', 'on'][show_glitch])
        else:
            break
    cv2.destroyAllWindows()
