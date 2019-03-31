import requests,json,csv
import execjs
requests.packages.urllib3.disable_warnings()


class Spider_exam(object):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}

    def get_des_psswd(self,message):
        def get_js(self):
            f = open("md5.js", 'r', encoding='utf-8')  # 打开JS文件
            line = f.readline()
            htmlstr = ''
            while line:
                htmlstr = htmlstr + line
                line = f.readline()
            return htmlstr

        jsstr = get_js(self)
        ctx = execjs.compile(jsstr)  # 加载JS文件
        return (ctx.call('hex_md5', message))  # 调用js方法  第一个参数是JS的方法名，后面的data和key是js方法的参数

    def get_des_title(self,message):
        def get_js(self):
            f = open("as.js", 'r', encoding='utf-8')  # 打开JS文件
            line = f.readline()
            htmlstr = ''
            while line:
                htmlstr = htmlstr + line
                line = f.readline()
            return htmlstr

        jsstr = get_js(self)
        ctx = execjs.compile(jsstr)  # 加载JS文件
        return (ctx.call('aesDecrypt', message))  # 调用js方法  第一个参数是JS的方法名，后面的data和key是js方法的参数

    def login(self,username,passwd):

        #loginurl:https://slb-user.ksbao.com/api/user/userlogin
        url='https://slb-user.ksbao.com/api/user/userlogin'
        data={'username': '',#明文
        'password': '',#MD5加密
        'userAgent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'clientType': 'web_pc',
        'clientver': 'wide.ksbao.com'}
        data['username']=username
        passwd=Spider_exam().get_des_psswd(passwd)
        data['password']=passwd
        response=requests.post(url,data,verify=False)
        response.encoding="utf-8"
        userInfo=[(json.loads(response.text))['data']['guid'],(json.loads(response.text))['data']['appID']]
        return userInfo

    def down_info(self,guid,appid,cptID):#cptID 默认为1
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        data_url="https://slb-exam.ksbao.com/api/exam/getChapterTestEx"
        data={'appID': '1192',#get user`s appid
        'cptID': '1',#循环递增
        'guid': '',#login_get_guid
        'clientver': 'wide.ksbao.com'}

        data['appID']=appid
        data['guid']=guid
        data['cptID']=cptID

        respond=requests.post(data_url,data=data,headers=header,verify=False)
        return respond.text

    def list_item(self,items):
        item_list=json.loads(items)
        list_all=[]
        for x in item_list['data']['test']['StyleItems'][0]["TestItems"]:#列表题循环
            list_option={
                'A':'',
                'B':'',
                'C':'',
                'D':'',
                'E':''
            }
            title=Spider_exam().get_des_title(str(x['Title']))
            a=0
            for o in x["SelectedItems"]:#选项循环
                if a==0:
                    list_option['A']=o["Content"]

                if a==1:
                    list_option['B']=o["Content"]

                if a==2:
                    list_option['C']=o["Content"]

                if a==3:
                    list_option['D']=o["Content"]

                if a==4:
                    list_option['E']=o["Content"]
                    break
                a=a+1
            list_option["Title"]=title
            list_all.append(list_option)
        return list_all

    def get_cptID(self,guid,appID):
        #url:https://slb-exam.ksbao.com/api/chapterMenu/getCptStatistics?guid=guid&appID=appID&clientver=wide.ksbao.com  get
        url="https://slb-exam.ksbao.com/api/chapterMenu/getCptStatistics?guid="+guid+"&appID="+appID+"&clientver=wide.ksbao.com"#  get
        body=requests.get(url,verify=False)
        s=eval(body.text)
        list = []
        for x in s['data']:
            list.append(x['CptID'])
        return list

    def data_writer(self,item):
        with open('题库.csv', 'a', encoding='gbk', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(item)
            
if __name__=="__main__":
    exam=Spider_exam()
    username="13764819739"
    passwd="zz1797831629"
    userInfo=exam.login(username,passwd)
    catID=exam.get_cptID(userInfo[0],str(userInfo[1]))
    item=['题干','选项A','选项B','选项C','选项D','选项E']
    exam.data_writer(item)
    for a in catID:
        print(a)
        exam_data=exam.down_info(userInfo[0],userInfo[1],str(a))
        t=exam.list_item(exam_data)
        for b in t:
            item = [b['Title'], b['A'], b['B'], b['C'], b['D'], b['E']]
            exam.data_writer(item)

    print('完毕')
    #print(exam.get_cptID("HV5FN6qmNlrjUC11g2m3z9cSGB7tMrOk52745310","1192"))
