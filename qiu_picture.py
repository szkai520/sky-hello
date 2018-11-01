import re
import urllib.parse
import urllib.request
import os


def handle_request(url, page):
    new_url = url + str(page) + '/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    }
    request = urllib.request.Request(url=new_url, headers=headers)
    return request


# <img src="//pic.qiushibaike.com/system/pictures/12120/
# 121201241/medium/N7BZ91EGZV68RT87.jpg" alt="你长得真像你爸">
def download_image(content):
    pattern = re.compile(r'<div class="thumb">.*?<img src="(.*?)" .*?>.*?</div>', re.S)
    lt = pattern.findall(content)
    for link in lt:
        image_url = 'http:' + link
        dirname = 'qiutu'
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        filename = image_url.split('/')[-1]
        filepath = dirname + '/ ' + filename
        print('%s图片正在下载' % filename)
        urllib.request.urlretrieve(image_url, filepath)
        print('%s图片结束下载' % filename)


def main():
    url = 'https://www.qiushibaike.com/pic/page/'
    start_page = int(input('请输入起始页码'))
    end_page = int(input('请输入结束页码'))
    for page in range(start_page, end_page + 1):
        print('第%s开始下载' % page)
        #  生成对象
        request = handle_request(url, page)
        #  发送请求对象，获取相应内容
        content = urllib.request.urlopen(request).read().decode()
        #  解析内容，提取所有的图片链接
        download_image(content)
        print('第%s结束下载' % page)


if __name__ == '__main__':
    main()
