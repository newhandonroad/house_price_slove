import requests
from requests.exceptions import RequestException
import re
import json
#result.txt  存放该区域所有楼盘的 ID 和 名字（运行price.py获得后复制进来）
#result1.txt 存放该区域所有楼盘的详细信息，包括名字和三商
#result3.txt 存放百强企业名单
#result2.txt 存放经过百强企业名单筛选后的所有楼盘的名字
#result4.txt 存放筛选完成后，楼盘最新动态的日期和动态网址
def  get_one_page(url):
    try:
        response = requests.get(url)  #获取这个URL
        if response.status_code == 200: #200表示获取成功
            return response.text
        return None
    except RequestException:
        return None
def parse_one_page(html): #对楼盘取 名字 和 开发商信息
    pattern = re.compile('text-l">\n\s+(.*?)\n',re.S)  #此处写正则
    items = re.findall(pattern,html)
    for item in items:

        yield {
            ab+' '+cd : item  #格式：当前楼盘名cd  +  开发商等信息
        }

def parse_two_page(html): #对楼盘取动态，时间+ID1和ID2，然后把两个ID拼接起来
    pattern = re.compile('loupan-name">(.*?)</span>.*?最新.*?-time">(.*?)</div>.*?loupan|loupan-name">(.*?)</span>',re.S)  #此处写正则
    items = re.findall(pattern,html)  # re.findall返回所有字符串，并且是以list的形式
    print(len(items))             #备份   loupan-name">(.*?)</span>.*?最新.*?-time">(.*?)</div>.*?loupan\/(.*?)\/dongtai\/(.*?)\.html|loupan-name">(.*?)</s(\w)(\w)(\w)>
    if(len(items)==1):
        for item in items:
         yield {
             'name':item[0],
            'time' : item[1],  #格式：
           # '动态ID1':item[2],
           # '动态ID2':item[3],
             '       ':item[2]

        }
    elif(len(items)==0):
          items = ('!!!','1','11')
          print(items)
         # yield {

        #    '!!!!!!!!' : item
       #   }

def parse_three_page(html): #对楼盘最新动态取出内容
    pattern = re.compile('-main">(.*?)</div>',re.S)  #此处写正则
    items = re.findall(pattern,html)
    for item in items:

        yield {
            '动态' : item  #格式：

        }

def write_to_file(content,path): #第一个参数是传入内容，第二个是path
    with open(path,'a+',encoding='utf-8') as f :#此处考虑 要追加内容写a 覆盖就w
         f.write(json.dumps(content,ensure_ascii=False)+'\n')
         f.close()



def main():
    global cd  #这一块程序实现：打开 result ， 读取 id  和 名字，并且生成了后续url，和字符串a和cd，a用来生成url
    global ab # ID也需要复用
    for line in open("result.txt", 'r',encoding='utf-8'):     # 对每一行的数字进行合成url操作
        pattern = re.compile('"(\d+)', re.S)  # 取出ID
        name_a=re.compile('"name": "(.*?)"', re.S)   #取出名字
        dig = re.findall(pattern, line)
        name_b=re.findall(name_a, line)
        ab=''.join(dig) #将之前保存下来的txt中的数字添加到字符串后，相当于变成字符串了
        cd = ''.join(name_b)  # cd是每次百强信息的当前楼盘
        oneurl='https://sh.focus.cn/loupan/'+ab+'/xiangqing.html' #  楼盘的详细信息页面，用来看百强的
        twourl='https://sh.focus.cn/loupan/'+ab+'/dongtai/'       #  楼盘的动态页面
        threeurl='https://sh.focus.cn/loupan/'+ab+'/huxing/'      #  楼盘的户型数据
        print(oneurl)#可以考虑将url也输出，方便直接点击查找

        #下面这一块程序：将楼盘的详细信息网址打开，抓取每个楼盘的三商信息，共五条，存入result1.txt中
        print('START_SECOND')
        html = get_one_page(oneurl)
        for item in parse_one_page(html):
            write_to_file(item,'result1.txt')
        print('success to write')

        #下面这一块程序：将楼盘的动态页面打开，抓取每一条数据的最新日期（后续应该要添加判断：如何确定正则匹配出内容了）
        #我感觉这一块可以取出时间，网址，然后附在result1后面。
        #分析：
     #   print('START_THRID')
    #    html = get_one_page(twourl)  # 生成result4结果
     #   for item in parse_two_page(html):
     #       write_to_file(item, 'result4.txt')
    #    print('success to write')

    #下面这一块程序：取出result1的楼盘信息（三商+名字）对百强进行比对，如果是百强，就将数据存为result2.txt
    #也就是说，result2.txt是result1.txt的筛选版本，去除了非百强企业
    fa = open('result1.txt',encoding='utf-8')
    a = fa.readlines()  # a 是当前楼盘信息
   # print(len_a)
    fa.close()
    fb = open('result3.txt',encoding='utf-8')
    b = fb.readlines()   # b　是百强企业，用于检测Ａ中是否存在百强企业的名字
    fb.close()
  #  ff=open('result4.txt',encoding='utf-8') #4也跟着删除
   # f = ff.readlines()    # f 是result4里面取出来的所有楼盘，跟着a删除当前行，相比result1来说，少了一些没有动态的楼盘
  #  ff.close()

    flag = 0 # 初始化为0
  #  abc_count=-1
  #  abc_count1=0
    for a111 in a[:]:
      #  print(a111)
      #  abc_count=abc_count+1
        for b111 in b:
            b111=b111.strip('\n')
            if a111.find(b111) >= 0:
               # print('结果存在')
                flag=1
        if flag == 1 :                     #现在百强对比就是一条一条删的
         #   print('符合百强要求')
            flag = 0
        else : #没有任意一条符合百强的
            a.remove(a111)
        #    if((abc_count+1)%5==0):
         #       abc_count1=int((abc_count+1)/5-1) #目前仍存在问题：删除的过于少了
        #        if(len(f)>=abc_count):
         #          f.pop(abc_count1)
        #    abc_count = abc_count -1
            flag=0
    fc = open('result2.txt', 'w',encoding='utf-8') #result2 是保存筛选出来的百强的
    fc.writelines(a)
    fc.close()
  #  fg = open ('result6.txt', 'w+',encoding='utf-8') #result6是百强楼盘的
  #  fg.writelines(f)
  #  fg.close()

    #这一块代码的内容：对result2删除重复的数据，只保留第五个数据，即楼盘名字+开发商
   # c1=a #将c1赋值为删选出来的百强企业，后续使用c1作为基础List
  #  fd = open('result2.txt', encoding='utf-8')
  #  c1 = fd.readlines()  # a 是当前楼盘信息
   # 下列代码是只保留一个品牌商（需要哪些到时候考虑）
   # d=len(c1)-1
  #  while d > -1:
   #     if (d+1)%5 != 0:
   #          c1.pop(d)  # 删除除了第五行的倍数
   #          d = d -1
   #     else :
   #         d = d - 1
    #下列代码用于实现：提取动态，并插入到list c1 中
  #  print(len(c1))
 #   c3=['start']
    #fd = open('result2.txt', encoding='utf-8')
  #  id_name_xq = fd.readlines()  # 格式为 ID+名字+详情 （经过百强筛选的） 类型：list
    for id_name_xq in open('result2.txt', encoding='utf-8'):
       id_name_xq_id = re.compile('"(\d+)', re.S)  # 取出ID
       dig_id = re.findall(id_name_xq_id, id_name_xq)
       if(dig_id):
            dig_id_char = ''.join(dig_id)  # 将取出的ID变为字符串格式
       else:
           dig_id_char = ''.join('!!!!!!!!')
       foururl = 'https://sh.focus.cn/loupan/' + dig_id_char + '/dongtai/'  # 楼盘的动态页面
       html = get_one_page(foururl)  # 生成result4结果
       for item in parse_two_page(html):
          write_to_file(item, 'result4.txt')
    print('success to write')
#上面这个模块  缺少对 没有动态的校验


    '''
    nn=0 #用于下面循环计数
    for line in open("result6.txt", 'r',encoding='utf-8'):     # 对每一行的数字进行合成url操作
        id1 = re.compile('ID1".*?"(\d+)"', re.S)  # 取出ID1
        id2 = re.compile('ID2": "(\d+)"', re.S)   #取出ID2
        time = re.compile('time": "(.*?)"', re.S)   #取出time
        id11 = re.findall(id1, line)
        id22=re.findall(id2, line)
        time1=re.findall(time,line)
        id111 = ''.join(id11)  # 将id1添加到字符串后，相当于变成字符串了
        id222= ''.join(id22)  # 将id2添加到字符串后，相当于变成字符串了
        time2=''.join(time1)  # 将时间信息变为字符串
        foururl = 'https://sh.focus.cn/loupan/' + id111 + '/dongtai/'+ id222 +'.html'  # 构造楼盘点进去的动态
        newline = time2 +'        '+ foururl  #构造为要输出的内容：时间+网址
        #newline是正常显示的
    
#最后需要将所有内容拼接到一个文本文档
#内容形式为： 楼盘名字+时间+网址
#              c1    +  newline

        c2=(newline.join(c1[nn]))  #此时C1是个list,所以都是一个完整的list加一个newline
        nn += 1
        f=open("result5.txt",'a+',encoding='utf-8')
        f.writelines(c1[nn-1]+newline+'\n')
        f.close()
    print(nn)
     #   c3.append(c1)
      #  c3.append(newline)
      #  c3.append('\n')
  #  print(c3)
  #  write_to_file(c2, 'result5.txt')
'''
if __name__ == '__main__':
    main()