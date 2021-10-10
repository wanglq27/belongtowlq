import cv2

def video_choose():
    camera = cv2.VideoCapture('VID604.mp4') # 读取视频
    fps = camera.get(cv2.CAP_PROP_FPS)# 获取视频帧率
    print('视频帧率：%f fps' %fps)

   #判断视频是否成功打开
    if (camera.isOpened()):
      print('视频已打开')
    else:
      print('视频打开失败!')
   # # 测试用,查看视频size
    size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
       int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print ('视频尺寸:'+repr(size))

    return  camera,fps

