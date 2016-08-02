#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 8/2/16 3:32 PM
# @Author  : jiuyue
# @Site    : 
# @File    : tinySpider01.py
# @Software: PyCharm
# @Version : 1.0

#
# Try to catch the pictures on http://www.gaoxiaogif.com/qqbiaoqing/
# The first time to write a spider
# Cannot keep working after interruption, no error handler, no multiprocess
# No other complex module, just urllib with python3
#

import urllib.request
import os
import re

SAVETO = './pic/'  # the path where you want to save these pictures
BASEURL = 'http://www.gaoxiaogif.com'  # home page

regStrs = [
    # regex string to catch the second level page name and url on the home page.
    r'<li><a href="(.*?)"(?:.*?)target="_blank"(?:"?)><i class=".*"></i>(.*)</a>(?:.*?)</li>',

    # regex string to catch the second level page name and url on second level page.
    # because the information on the home page is incomplete, so we have to catch
    # them on second level page
    r'<li><a href="(.*?)"><i class="icon-angle-right"></i>(.*?)</a>(?:.*?)</li>',

    # regex string to catch the picture's name and url on second level page
    r'<span><img src="(.*?)" alt="(.*?)"></span></a>',

    # regex string to catch the next page on second level page
    r'(?:<a href=".*?">.*?</a>)*<a href="(.*?)">下一页</a>',
]

urlToBeSpider = set()  # save the page that will be visited : (url, name)
urlVisited = set()  # save the page that have been visited before


def save_pic_to_file(fullUrl, dirname, filename):
    """Save the pic to local
    the fullUrl is the full url of the picture, dirname is the name of the dir you want to save this picture and
    the filename is the name of the picture

    :param fullUrl: str
    :param dirname: str
    :param filename: str
    :return: None
    """
    suf = fullUrl.split('.')[-1]
    path = SAVETO + dirname + '/' + filename + '.' + suf
    if not os.path.exists(SAVETO + dirname):
        os.mkdir(SAVETO + dirname)

    print('Save picture ', filename, ' to ', path, ' ...', end='\t')
    with open(path, 'wb') as fileToSave:
        fileToSave.write(get_page_raw_context(fullUrl))
    print('Done')


def get_page_raw_context(url):
    """Get the raw context of the page
    Just return the raw context of the page without encoding or something like that.

    :param url: str
    :return: str
    """
    try:
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        """:type: http.client.HTTPResponse"""
        urlVisited.add(url)
        return response.read()
    except urllib.request.URLError as e:
        print(e.reason)
        return None


def get_page_context(url):
    """Get the context after decoding of the page
    Get the context of the page. The context has been decoded.

    :param url:
    :return: str
    """
    context = get_page_raw_context(url)
    if context is None:
        return None
    context = context.decode("gbk")
    urlVisited.add(url)
    return context


def get_type_list(url):
    """Get the type information
    Get the type information. A list of tuple will be returned
    :return: list(tuple(str, str))
    """
    print("Try to get the type information ...", end='\t')
    context = get_page_context(BASEURL + url)  # We start at this page
    if context is None:
        print("Can't get ", BASEURL, " page！")
        return

    reg = re.compile(regStrs[0])
    mt = reg.findall(context)
    if mt is None:
        print("regex match failed")
        return None
    print("Success")
    return mt


def visit_second_level_page(url, name):
    """Visit second level page
    Visit second level page, 3 things to be done:
    1. catch type information and save it
    2. catch url of the pictures on this page
    3. catch the next page's url and visit it

    :param url: str
    :param name: str
    :return: None
    """
    print("Try to catch second level page ", url, "...", end='\t')
    my_url = BASEURL + url
    if my_url in urlVisited:
        print("Visited, pass")
        return

    context = get_page_context(my_url)
    if context is None:
        print("Can't get ", my_url, " page！")
        return
    print("Success")

    # catch the type information
    reg1 = re.compile(regStrs[1])
    mt = reg1.findall(context)
    urlToBeSpider.update(mt)

    # catch the pictures
    reg2 = re.compile(regStrs[2])
    mt2 = reg2.findall(context)
    for pic_url in mt2:
        if pic_url[0].startswith("http"):
            save_pic_to_file(pic_url[0], name, pic_url[1])
        else:
            save_pic_to_file(BASEURL + pic_url[0], name, pic_url[1])

    # get the url of the next page
    reg3 = re.compile(regStrs[3])
    mt3 = reg3.search(context)
    if mt3 is None:  # the last page has no next page
        return
    else:
        next_page_url = mt3.group(1)
        if next_page_url == '#self':  # prevent from visiting itself
            return
        if next_page_url.startswith("http"):
            visit_second_level_page(next_page_url, name)  # keep visiting next page
        else:
            visit_second_level_page(BASEURL + next_page_url, name)


if __name__ == "__main__":

    urlToBeSpider.update(get_type_list('/qqbiaoqing/'))
    while len(urlToBeSpider) != 0:
        tmpTuple = urlToBeSpider.pop()
        if tmpTuple[0].count('/') != 2:
            visit_second_level_page(*tmpTuple)
        else:
            get_type_list(tmpTuple[0])

    print(len(urlToBeSpider))
