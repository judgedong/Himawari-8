'''
Created on 2017年4月28日

@author: Judge
'''
import os
import requests
import threading
import shutil
import json
import platform
from sys import argv
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta


#生成路径
def getPath(t, x, y):
    return "%s/%s/%02d/%02d/%02d%02d00_%s_%s.png" \
    % (cdn+base, t.year, t.month, t.day, t.hour, (t.minute // 10) * 10, x, y)
#下载图片,各种异常处理
def getImgData(sess,path):
    try:
        r = sess.get(path)
        if r.status_code!=200:
            #缓存找不到这个文件,尝试直接从主站获取
            print('缓存无此文件!!!')
            path = path.replace(cdn,'')
            imgData = getImgData(sess,path)
        else:
            imgData = r.content
        #文件内容为空,尝试重新获取
        if imgData == "":
            print('获取图像失败,尝试重新获取')
            imgData = getImgData(sess,path)
    #连接失败,尝试重新获取数据
    except BaseException as e:
        print('获取图像失败,尝试重新获取')
        imgData = getImgData(sess,path)
    return imgData
#下载图片
def getImgs(time,x,y):
    start = datetime.now()
    path = getPath(time,x,y)
    imgData = getImgData(sess,path)
    tempPng = Image.open(BytesIO(imgData))
    tempPng.save("%s%s%02d%02d-%02d%02d00_%s_%s.png" % (rootPath,time.year,time.month,time.day,time.hour,(time.minute // 10) * 10,y,x), 'PNG')
    png.paste(tempPng, (width*x, height*y, width*(x+1), height*(y+1)))
    end = datetime.now()
    if platform.system()=='Windows':
        print('%02d-%02d下载完成,耗时%.5f秒' % (x,y,(end-start).microseconds/1000000))

#从接口获取最后的版本信息
def getlatest():
    url = 'http://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json'
    response = requests.request("GET", url)
    data = json.loads(response.text)
    time =  datetime.strptime(data['date'],'%Y-%m-%d %H:%M:%S')
    return time




#############################################################################################





#倍数
scale = 8
cdn = 'http://res.cloudinary.com/pxbfhhmjiwol5sox5dfpxwgfbfluhcnuczb0u72muxyymndv5pp6oqnshp7skhtglsiy27an4meeiwk8un9vwbmb3zwqboq1ds0e/image/fetch/'
base = 'http://himawari8-dl.nict.go.jp/himawari8/img/D531106/%sd/550' % (scale)

#文件操作的根目录
if platform.system()=='Windows':
    rootPath =  'f://earth/'
else:
    rootPath =  '/root/earth/'
wallpaperPath= rootPath+'wallpaper/'
oldwallpaperPath= rootPath+'wallpaper-old/'
oldTemp = rootPath+'temp-old/'

#宽高应该是固定的
width = 550
height = 550


#拼接后的图像
png = Image.new('RGB', (width*scale, height*scale))
#单个图像
tempPng = Image.new('RGB', (width, height))
#请求的session
sess = requests.Session()


#增加指定时间的参数
if len(argv) > 1:
    try:
        time =  datetime.strptime(argv[1]+" "+argv[2],'%Y-%m-%d %H:%M:%S')
    except BaseException as e:
        print('参数错误!!!!')
        os._exit(0)
else:
    #从当前时间推算最后的图片不精确,尝试从api获取最后的版本,cloudinary的cdn还有延迟
    time = getlatest() - timedelta(minutes=0)
print(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")+' 获取====>>'+datetime.strftime(time, "%Y-%m-%d %H:%M:%S")+' ========>>Start!')



#初始化路径,移动老文件
#如果目录不存在,则创建
if not os.path.exists(wallpaperPath):
    os.makedirs(wallpaperPath)
if not os.path.exists(oldwallpaperPath):
    os.makedirs(oldwallpaperPath)
if not os.path.exists(oldTemp):
    os.makedirs(oldTemp)
#移动wallpaperPath下的所有文件到oldwallpaperPath
for x in os.listdir(wallpaperPath):
    shutil.move(os.path.join(wallpaperPath, x),os.path.join(oldwallpaperPath, x))
#移动rootPath下的所有文件到oldTemp
for x in os.listdir(rootPath):
    if os.path.isfile(os.path.join(rootPath, x)):
        if platform.system()=='Windows':
            shutil.move(os.path.join(rootPath, x),os.path.join(oldTemp, x))
        else:#linux系统下就不保存Temp了
            os.remove(os.path.join(rootPath, x))

#谜之多线程
threads = []
for x in range(scale):
    for y in range(scale):
        tt = threading.Thread(target=getImgs,args=(time,x,y,))
        threads.append(tt)
for t in threads:
    t.setDaemon(True)
    t.start()
for t in threads:
    t.join()
#谜之多线程

#换完壁纸吱一声
if platform.system()=='Windows':
    txt=Image.new('RGBA', png.size, (0,0,0,0))
    fnt=ImageFont.truetype("c:/Windows/fonts/Tahoma.ttf", 20)
    d=ImageDraw.Draw(txt)
    d.text((txt.size[0]-190,txt.size[1]-25), datetime.strftime(time, "%Y-%m-%d %H:%M:%S"),font=fnt, fill=(255,255,255,127))
    out=Image.alpha_composite(png, txt)
    out.save("%swallpaper/%s%02d%02d-%02d%02d00.png" % (rootPath,time.year,time.month,time.day,time.hour,(time.minute // 10) * 10), 'PNG')
    import winsound
    winsound.PlaySound("*", winsound.SND_ALIAS)
else:
    png.save("%swallpaper/%s%02d%02d-%02d%02d00.webp" % (rootPath,time.year,time.month,time.day,time.hour,(time.minute // 10) * 10), 'WEBP')
print(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")+' 获取====>>'+datetime.strftime(time, "%Y-%m-%d %H:%M:%S")+' ========>>Done!!')
