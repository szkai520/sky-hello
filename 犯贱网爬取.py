import threading
import time
from queue import Queue
import requests
from lxml import etree
import json

# 用来存放采集线程
g_crawl_list = []
# 用来存放解析线程
g_parser_list = []

g_flag = True

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
}


class CrawlThread(threading.Thread):
    def __init__(self, name, page_queue, data_queue):
        super(CrawlThread, self).__init__()
        self.name = name
        self.page_queue = page_queue
        self.data_queue = data_queue
        self.url = 'http://www.fanjian.net/jiantu-{}'

    def run(self):
        print("%s-----线程启动" % self.name)
        while True:
            # 判断采集线程何时推出
            if self.page_queue.empty():
                break
            # 从队列中取出页码
            page = self.page_queue.get()
            # print(page)
            # 拼接url，发送请求
            url = self.url.format(page)
            r = requests.get(url, headers=HEADERS)
            # print(r)
            # 将相应内容存放到data_queue中
            self.data_queue.put(r.text)
        print("%s-----线程结束" % self.name)


class ParserThread(threading.Thread):
    def __init__(self, name, data_queue, fp, lock):
        super(ParserThread, self).__init__()
        self.name = name
        self.data_queue = data_queue
        self.fp = fp
        self.lock = lock

    def run(self):
        print("%s-----解析线程开始" % self.name)
        while True:
            # 判断解析线程何时推出
            if g_flag == False:
                break
            # 从data_queue中取出一页数据
            try:
                data = self.data_queue.get(True, 5)
                # print(data)
                # 解析内容
                self.parse_content(data)
            except Exception as e:
                break
        print("%s-----解析线程结束" % self.name)

    def parse_content(self, data):
        tree = etree.HTML(data)
        # 找到所有的li列表
        li_list = tree.xpath('//ul[@class="cont-list"]/li')
        # print(li_list)
        items = []
        for li in li_list:
            # 获取标题
            title = li.xpath('.//h2/a/text()')[0]
            # print(title)
            # 获取图片url
            image_url = li.xpath('.//div[contains(@class,"cont-list-main")]//img/@data-src')
            # print(image_url)
            item = {
                '标题': title,
                '链接': image_url
            }
            items.append(item)
        # 写到文件中
        self.lock.acquire()
        self.fp.write(json.dumps(items, ensure_ascii=False) + '\n')
        self.lock.release()


def create_queue():
    # 创一个页码队列
    page_queue = Queue()
    for page in range(1, 11):
        page_queue.put(page)
    # 创一个内容队列
    data_queue = Queue()
    return page_queue, data_queue


def create_crwal_thread(page_queue, data_queue):
    crawl_name = ['采集线程1号', '采集线程2号', '采集线程3号', ]
    for name in crawl_name:
        # 创建采集线程
        tcrawl = CrawlThread(name, page_queue, data_queue)
        # 保存到列表中
        g_crawl_list.append(tcrawl)


def create_parser_thread(data_queue, fp, lock):
    parser_name = ['解析线程1号', '解析线程2号', '解析线程3号', ]
    for name in parser_name:
        # 创建解析线程
        tparser = ParserThread(name, data_queue, fp, lock)
        # 保存到列表中
        g_parser_list.append(tparser)


def main():
    # 创建队列
    page_queue, data_queue = create_queue()
    # 打开文件
    fp = open('jian.json', 'a', encoding='utf8')
    # 创建线程锁
    lock = threading.Lock()
    # 创建采集线程
    create_crwal_thread(page_queue, data_queue)
    time.sleep(3)
    # 创建解析线程
    create_parser_thread(data_queue, fp, lock)

    # 启动所有采集线程
    for tcrawl in g_crawl_list:
        tcrawl.start()
    # 启动所有解析线程
    for tparser in g_parser_list:
        tparser.start()

    while True:
        if page_queue.empty():
            break
    while True:
        if data_queue.empty():
            global g_flag
            g_flag = False
            break

    # 主线程等待子线程结束
    for tcrawl in g_crawl_list:
        tcrawl.join()
    for tparser in g_parser_list:
        tparser.join()

    # 关闭文件
    fp.close()
    print('主线程子线程全部结束')


if __name__ == '__main__':
    main()
