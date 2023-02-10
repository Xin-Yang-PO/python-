"""
Create an Ip pool by synchronous programming
"""
import time
from lxml import etree
import pandas
from fake_useragent import UserAgent
import requests

url_ = 'http://www.kxdaili.com/dailiip/1/{}.html'


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

    def get_save_html(self):
        """
        first we should get the html and save as file.txt
        """
        response = requests.get(self.url, headers=self.headers)
        with open('txt/Sync_Response_Page{}.txt'.format(self.page),
                  'w',
                  encoding='utf-8') as f:
            f.write(response.text)

    def get_save_ip(self):
        """
        next we should extract ip, port, anony, agree and save it
        """
        time.sleep(0.5)
        with open('txt/Sync_Response_Page{}.txt'.format(self.page),
                  'r',
                  encoding='utf-8') as f:
            txt = f.read()
        # using regular expressions, (.*)greedy mode
        element = etree.HTML(txt)
        ip = element.xpath('//*[@class="active"]/tbody/tr/td[1]/text()')
        port = element.xpath('//*[@class="active"]/tbody/tr/td[2]/text()')
        anony = element.xpath('//*[@class="active"]/tbody/tr/td[3]/text()')
        agree = element.xpath('//*[@class="active"]/tbody/tr/td[4]/text()')
        # create a two-dimensional array
        dataframe = pandas.DataFrame({'IP': ip, 'PORT': port, 'ANONY': anony, 'AGREE': agree})
        # a: add, no modification
        dataframe.to_csv('csv/Sync_IP.csv', mode='a', index=False)


class Test_Ip(object):
    """
    test the useful ip and save: first is read the data from file.csv, next use the url to tset it and save it
    """

    def __init__(self):
        self.test_url = 'http://httpbin.org/ip'
        self.file_path = 'csv/Sync_IP.csv'
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

    def test(self, ip, port, anony, agree):
        proxy = {'http':'http://{0}:{1}'.format(ip, port)}
        try:
            response = requests.get(self.test_url, headers=self.headers, timeout=10,
                                    proxies=proxy)
            print(response.status_code)
            if response.status_code == 200:
                if ip in response.text:
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
            print(f'\033[0;31m{proxy}Error:\033[0m', e)

    def save(self):
        """
        save the available proxy
        """
        dataframe = pandas.DataFrame({'IP': self.ip_list, 'PORT': self.port_list,
                                      'ANONY': self.anony_list, 'AGREE': self.agree_list})
        dataframe.to_csv('csv/Sync_Available_IP.csv', mode='a', index=False)

    def main(self):
        """
        main funcion, run function
        """
        for ip, port, anony, agree in zip(self.get_data()[0], self.get_data()[1],
                                          self.get_data()[2], self.get_data()[3]):
            self.test(ip=ip, port=port, anony=anony, agree=agree)
        self.save()


start = time.perf_counter()


def run():
    """
    run function
    """
    for i in range(1, 5, 1):
        task_1 = (Get_Ip(url_.format(i), page=i).get_save_html())
        task_2 = (Get_Ip(url_.format(i), page=i).get_save_ip())


run()
Test_Ip().main()
end = time.perf_counter()
# 188.87630800000002s
print(f'Time consuming:{end - start}')
