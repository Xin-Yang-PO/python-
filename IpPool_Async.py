"""
creates an IP pool by asynchronous programming
"""
import time
import aiohttp
import asyncio
import pandas
from lxml import etree
from fake_useragent import UserAgent

# slove: RuntimeError: Event loop is closed
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
url_get = 'http://www.kxdaili.com/dailiip/1/{}.html'


class Get_Ip(object):
    """
    get the (ip:port) and save: first get the html, next get the ip and port, and save by csv
    """

    def __init__(self, url, page):
        """
        :param url: visit url
        :param page: page of the html data
        """
        self.url = url
        self.page = page
        self.headers = {'User-Agent': UserAgent().random}

    async def get_save_html(self):  # asynchronous function declaration, build coroutine
        """
        first we should get the html and save as file.txt
        """
        # (with...as...) and (async with...as...) have the same function,
        # but one is used for synchronous functions and one is used for asynchronous functions,
        # they can both release resources when they're done, protection system
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.url, headers=self.headers) as response:  # get html
                # print(type(await response.text()))
                # print(await response.text())
                with open('txt/Async_Response_Page{}.txt'.format(self.page),
                          'w',
                          encoding='utf-8') as f:  # save html, txt
                    f.write(await response.text())  # (await) tell program it is a wait-able object

    async def get_save_ip(self):
        """
        next we should extract ip, port, anony, agree and save it
        """
        # should wait some time, the latter is running much faster than the former
        await asyncio.sleep(0.3)
        with open('txt/Async_Response_Page{}.txt'.format(self.page),
                  'r',
                  encoding='utf-8') as f:
            txt = f.read()
        # xpath to extract element, or re
        element = etree.HTML(txt)
        ip = element.xpath('//*[@class="active"]/tbody/tr/td[1]/text()')
        port = element.xpath('//*[@class="active"]/tbody/tr/td[2]/text()')
        anony = element.xpath('//*[@class="active"]/tbody/tr/td[3]/text()')
        agree = element.xpath('//*[@class="active"]/tbody/tr/td[4]/text()')
        # create a two-dimensional array
        dataframe = pandas.DataFrame({'IP': ip, 'PORT': port, 'ANONY': anony, 'AGREE': agree})
        # a: add, no modification
        dataframe.to_csv('csv/Async_IP.csv', mode='a', index=False)


class Test_Ip(object):
    """
    test the useful ip and save: first is read the data from file.csv, next use the url to tset it and save it
    """

    def __init__(self):
        self.test_url = 'http://httpbin.org/ip'
        self.file_path = 'csv/Async_IP.csv'
        self.headers = {'User-Agent': UserAgent().random}
        self.ip_list = []
        self.port_list = []
        self.anony_list = []
        self.agree_list = []

    def get_data(self):
        """
        :return:[0]ip, [1]port, [2]anony, [3]agree
        """
        data = pandas.read_csv(self.file_path)
        (ip, port, anony, agree) = (data['IP'].tolist(), data['PORT'].tolist(),
                                    data['ANONY'].tolist(), data['AGREE'].tolist())
        return ip, port, anony, agree

    async def test(self, ip, port, anony, agree):
        proxy = 'http://{0}:{1}'.format(ip, port)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url=self.test_url, headers=self.headers, proxy=proxy,
                                       timeout=aiohttp.ClientTimeout(total=10)) as response:
                    print(response.status)
                    if response.status == 200:
                        if ip in await response.text():
                            print(f'\033[0;32m{proxy} is effective\033[0m')
                            self.ip_list.append(ip)
                            self.port_list.append(port)
                            self.anony_list.append(anony)
                            self.agree_list.append(agree)
                        else:
                            print(f'\033[0;31m{proxy} is not effective\033[0m')
                    else:
                        print(f'\033[0;31m{proxy} is not effective\033[0m')
            except Exception as e:
                print(f'\033[0;31m{proxy} Error:\033[0m', e)

    def save(self):
        """
        save the available proxy
        """
        dataframe = pandas.DataFrame({'IP': self.ip_list, 'PORT': self.port_list,
                                      'ANONY': self.anony_list, 'AGREE': self.agree_list})
        dataframe.to_csv('csv/Async_Available_IP.csv', mode='a', index=False)

    async def main(self):
        """
        main funcion, run function
        """
        tasks = [asyncio.ensure_future(self.test(ip=ip, port=port, anony=anony, agree=agree))
                 for ip, port, anony, agree in zip(self.get_data()[0], self.get_data()[1],
                                                   self.get_data()[2], self.get_data()[3])]
        '''for ip, port in zip(self.get_data()[0], self.get_data()[1]):
            task = asyncio.create_task(self.test(ip=ip, port=port))
            tasks.append(task)'''
        await asyncio.gather(*tasks)
        self.save()


start = time.perf_counter()


async def run_get():
    """
    asynchronous programming requires a function to mobilize
    """
    for i in range(1, 5, 1):
        task_1 = asyncio.ensure_future(Get_Ip(url_get.format(i), page=i).get_save_html())
        task_2 = asyncio.ensure_future(Get_Ip(url_get.format(i), page=i).get_save_ip())
        await task_1
        await task_2


asyncio.run(run_get())
asyncio.run(Test_Ip().main())
end = time.perf_counter()
# 12.1423935s
print(f'Time consuming:{end - start}')
