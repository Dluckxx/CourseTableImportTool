from http import cookiejar
from bs4 import BeautifulSoup
import requests

username = ''
password = ''
url_index = 'http://jiaowu.sicau.edu.cn'
url_check = 'http://jiaowu.sicau.edu.cn/jiaoshi/bangong/check.asp'
url_course = 'http://jiaowu.sicau.edu.cn/xuesheng/gongxuan/gongxuan/kbbanji.asp'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
}
login_data = {
    'user': username,
    'pwd': password,
    'lb': 'S',
    'sign': ''
}

session = requests.session()
session.cookies = cookiejar.LWPCookieJar(filename="cookies.txt")

print('*' * 40)
print(' ' * 12, '课表生成脚本1.0')
print('*' * 40)

# 获取登陆sign
print('*' * 10, '获取登陆sign', '*' * 10)
response = session.get(url_index, headers=headers)
if response.status_code == 200:
    print('200 OK!')
else:
    print('error')
    exit(0)
soup = BeautifulSoup(response.content.decode(response.apparent_encoding), 'html.parser')
login_data['sign'] = soup.find(attrs={'name': 'sign'})['value']
print('sign:', login_data['sign'])

# 登陆，获取cookie
print('*' * 10, '发送登陆请求', '*' * 10)
response = session.post(url_check, headers=headers, data=login_data)
if response.status_code == 200:
    print('200 OK!')
else:
    print('error')
    exit(0)
soup = BeautifulSoup(response.content.decode(response.apparent_encoding), 'html.parser')
if soup.find('title').string == '四川农业大学教务管理系统':
    print('登陆成功！')
else:
    print('登陆失败，请重试！')
    exit(0)
session.cookies.save(ignore_discard=True, ignore_expires=True)
print('cookie已经保存到:', session.cookies.filename)

# 获取课表信息
print('*' * 10, '获取课表信息', '*' * 10)
response = session.get(url_course, headers=headers)
soup = BeautifulSoup(response.content.decode(response.apparent_encoding), 'html.parser')
print('获取到:', soup.title.string)
table = soup.find(name='table', attrs={'border': '1', 'bordercolor': '#000000'})
csv = ''
count = 0

# 处理文本
for tr in table.find_all('tr')[2:7]:
    # print('-' * 100)
    for td in tr.find_all('td'):
        if td.text == '上午' or td.text == '下午' or td.text == '晚上':
            continue
        for br in td.find_all('br'):
            br.extract()
        if len(td.text) > 10:
            count += 1
        csv += td.text.split('--')[0].replace('雅安校区：', ' ')
        csv += ','
    csv += '\n'

session.cookies.save(ignore_discard=True, ignore_expires=True)

print('生成文件', 'course.csv')
open('course.csv', 'w').write(csv)

response.close()
session.close()

print('Done!记录了{}门课程'.format(count))
