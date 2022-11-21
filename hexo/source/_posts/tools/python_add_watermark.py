from PIL import Image
import os

def add_img_watermark(img_path,watermark_path,out_path):
    # 获取原图
    img = Image.open(img_path).convert('RGB')
    img_w, img_h = img.size
    # 文件名称
    img_name = img_path.split('/')[-1]
    
    # 获取水印图片
    watermark = Image.open(watermark_path).convert('RGBA')
    # 将水印按照原图比例制作缩略图
    watermark.thumbnail((img_w/6, img_h/6))
    watermark_w,watermark_h = watermark.size
    
    r, g, b, a = watermark.split()
    
    # 设定水印位置：右下角
    x = img_w-watermark_w
    y = img_h-watermark_h
    img.paste(watermark, (x, y), mask=a)
    
    # 显示
    img.show()
    # 保存
    out_path = os.path.join(out_path,img_name)
    print('保存路径：',out_path)
    img.save(out_path)


if __name__=="__main__":
    # 水印图片
    watermarkPath = '/Users/workerspace/github/cmeng001.github.io/hexo/source/image/watermark/watermark_tm.jpeg'
    
    # 原文件地址
    imgPath = '/Users/workerspace/github/cmeng001.github.io/hexo/source/image'
    imgPath = imgPath+'/markdown/dividing_line.jpg'
    
    img_hosting_path = '/Users/workerspace/github/image-hosting/img'

    
    # 处理图床地址
    path_array = imgPath.split('image')[1].split('/')
    for path in path_array:
        if '.' not in path:
            img_hosting_path = os.path.join(img_hosting_path,path)
    if not os.path.exists(img_hosting_path):
        os.makedirs(img_hosting_path)

    add_img_watermark(imgPath,watermarkPath,img_hosting_path)


    







