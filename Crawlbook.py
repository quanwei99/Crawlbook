import json
import os
import shutil
import threading
import time

import img2pdf
import requests

Headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/80.0.3987.106 Safari/537.36",
    'Cookie': "_gid=411660808478; _gidv=959fa96d058dfa0ee387cc72d7f51fc3; acw_tc=3ccdc16815823556702652687e232d5dc3d6b34a6ce65f72946424b94878f8; ssxmod_itna=QqjxnQitDtdCwwDlRD+rFxcjDRBzD0Wjx32rmGx0vIeiODUoxn+2bo5YHKBw3VDQCUERrta5RGj4xaGC+r4GLDmKjxCAYxiiDC40rD74irDDxD3Db4KDSCxG6uDm4i3pxGeD+3VPGCD4qDBDD=fD7QDILQ4REjlAfNHQm6xRL+33qDMieGXRGTi3d0tVeeSWgdDzdaDtM=H3k=qx0PTQiPtQi4CFi+x0645nhhkScYqYG5=3xLmHA+CTtfbUA4DGf4iUYL3eD===; ssxmod_itna2=QqjxnQitDtdCwwDlRD+rFxcjDRBzD0Wjx32rmDnF8cuxDsCGDL7aQH=0=maZbqAp3BRlbBQGCI6B5RhaYnl74E3OKCAqENwKnS9OW2tTMBLtH4FyLvu9gTo=6qa87/Tp8afmfh8ms2N44d0Vnb0O+8xCK3fQYwieL0v55CRHjWtQhQfxTDi5GWLxIgr6KQWfW+n/be5tzon3AovHYcNIfq0PLioA7uikdPipD8Di/j4ZIhn+KbiGEo3SbwSUCq09Af6RIh9E2IGUEcOX2xmIlc58A1Gnqdxn5SrIY1ReymwXFmwNOSzqmo9lAQYdgrqqmvxFfiZN8mhx2eqD+POQmrIQm0IAohAe4Aihl0PEPhi35BrwjYqiNwe3q0dsDeH/AOOetlYdbKKjoOIIiPRjrfmifVaQtBv6=mmidgZowEevZukRYwQdmCQylD7xmQY=FOmQBrWOejzqflWgmYzlrE7NqYPq3pmZFjBoB+wChetQeagmvlFvfGfEWj/LTGmtW=V7jvAp=Bmdtf+OGmPPKBH/m4DQFtUgDlhaL0vjGQ0htR0vOuTK1XmK5D08DiQiYD==; PHPSESSID=dh8im06lg230m21sq9votfla6b; Hm_lvt_a84b27ffd87daa3273555205ef60df89=1582805268,1583235482,1583235517,1583236732; Hm_lpvt_a84b27ffd87daa3273555205ef60df89=1583236816"
}

url = "https://lib-nuanxin.wqxuetang.com/v1/read/initread?bid=194080"
book_url = "http://img.bookask.com/book/read/194080/"

getcmd = os.getcwd()
img_path = ""
pdf_path = ""
book_title = ""
pages = 0

thread_count = 5


def init():
    global img_path, pdf_path
    print("Start!!!")

    img_path = getcmd + "\\book\\img\\"
    pdf_path = getcmd + "\\book\\pdf\\"
    # if os.path.exists(img_path):
    #     shutil.rmtree(img_path)
    #     time.sleep(0.1)
    # else:
    #     pass
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)


def get_information():
    global book_title, pages
    print("访问：" + url)
    data = requests.get(url, headers=Headers).text
    js = json.loads(data)
    print(js)
    book_id = js["data"]["bid"]
    book_title = js["data"]["name"]
    pages = int(js["data"]["pages"])
    print("书籍id:" + book_id + "---" + "书籍名称：" + book_title + "---" + "页数:", pages)


def down_load():
    threading_list = []
    for i in range(thread_count):
        t = threading.Thread(target=load_img, args=(i,))
        t.start()
        threading_list.append(t)

    for i in threading_list:
        i.join()


def load_img(count):
    # print(threading.current_thread())
    thread_page = int(pages / thread_count)
    # print(thread_page)
    l = thread_page * count + 1
    if count == thread_count - 1:
        r = pages
    else:
        r = thread_page * (count + 1)

    for page in range(l, r + 1):
        urls = book_url + str(page) + ".jpeg"

        local_path = img_path + "/" + str(page) + ".jpeg"
        if os.path.exists(local_path) and os.path.getsize(local_path) != 0:
            print("已存在" + str(page) + "页图片，跳过")
            continue

        with open(local_path, "wb") as f:
            while 1:
                try:
                    content = requests.get(urls, timeout=10).content
                    break
                except Exception:
                    print("访问出错,重新访问")
                    time.sleep(1)

            f.write(content)
        print("第" + str(page) + "页正在下载完成")
        time.sleep(0.1)
    print("图片下载完成！！")


def img_to_pdf():
    file = pdf_path + "\\" + book_title + ".pdf"
    with open(file, "wb") as f:
        lst = list()
        for i in range(1, int(pages) + 1):
            lst.append(img_path + "\\" + str(i) + ".jpeg")
        pdf2 = img2pdf.convert(lst)
        f.write(pdf2)
    print(book_title + ",已成功转换为pdf")


if __name__ == "__main__":
    init()
    get_information()
    down_load()
    img_to_pdf()
