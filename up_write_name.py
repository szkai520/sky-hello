import re
import urllib.request
import urllib.parse
import os
import time


def handle_request(page, url):
    new_url = url + str(page) + '.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    }
    request = urllib.request.Request(url=new_url, headers=headers)
    return request


def get_text(content_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    }
    request = urllib.request.Request(content_url, headers=headers)
    text_html = urllib.request.urlopen(content_url).read().decode()
    content_pattern = re.compile(r'<li><p>(.*?)</p></li>')
    title_pattern = re.compile(r'<h1>(.*?)</h1>')
    content = content_pattern.findall(text_html)
    # print(content)
    title = title_pattern.findall(text_html)
    return (title, content)


def parse_content(content):
    pattern = re.compile(r'<h3><a href="(/lizhi/qianming/\d+\.html)">(.*?)</a></h3>', re.S)
    info = pattern.findall(content)
    for u, t in info:
        content_url = "http://www.yikexun.cn" + u
        title = t
        text = get_text(content_url)
        string = '<h1>%s</h1>\n%s \n' % text
        with open('lizhi.html', 'a', encoding='utf8')as f:
            f.write(string)


def main():
    url = 'http://www.yikexun.cn/lizhi/qianming/list_50_'
    start_page = int(input('请输入起始页码'))
    end_page = int(input('请输入结束页码'))
    for page in range(start_page, end_page + 1):
        request = handle_request(page, url)
        content = urllib.request.urlopen(request).read().decode()
        parse_content(content)


if __name__ == '__main__':
    main()
