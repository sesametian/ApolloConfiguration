import requests
import json
#import pyapollos
# import ast
#from ApolloConf import *
from tkinter import *
import tkinter.messagebox
from tkinter import ttk
from tkinter import scrolledtext
import os,sys
# apollo_client = pyapollos.ApolloClient(app_id="test",cluster="default",config_server_url="http://172.20.3.32:10010")
# #apollo_client.start()
# a = apollo_client.get_value("message", namespace="application")
# print(a)
#print(apollo_client.get_value('content', namespace='test.txt'))
"""SSID=b3609b135f0945daa3c5faa40aa5a940; NG_TRANSLATE_LANG_KEY=zh-CN; JSESSIONID=E7FBC365C5E1E49D3EFE2839F1967BF4"""
"SSOTOKEN=fd12a2878e694e3daf7686c27f18d32e"
root= Tk()
root.title("同步配置工具") #界面的title
# file_path = os.path.dirname(__file__) #如果是py脚本文件使用该方法定位文件位置
file_path = os.path.dirname(sys.executable) #如果需要转成exe文件模式，使用该方法定位文件位置

frame1 = Frame(root) #使用Frame增加一层容器
frame1.pack(padx=50,pady=40)

label = Label(frame1,text="AppId：",font=("宋体",15),fg="blue").grid(row=0,padx=10,pady=5,sticky=N) #创建标签
labe2 = Label(frame1,text="获取环境：",font=("宋体",15),fg="blue").grid(row=1,padx=10,pady=5)
labe3 = Label(frame1,text="配置环境：",font=("宋体",15),fg="blue").grid(row=2,padx=10,pady=5)
e1 = Entry(frame1,font = ('Helvetica', '12'))
e2 = Entry(frame1,font = ('Helvetica', '12'))
e3 = Entry(frame1,font = ('Helvetica', '12'))
e1.grid(row=0,column=1,sticky=W)
e2.grid(row=1,column=1,sticky=W) #布置文本输入框
e3.grid(row=2,column=1,sticky=W)
labeltitle=Label(frame1,text="建议同时填写获取环境与配置环境",font=("宋体",10,'bold'),fg="red")
labeltitle.grid(row=3,column=1,sticky=NW)

header = {
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Authorization': 'b15fd1732b149caa02c73a50927250a323aad328',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 SLBrowser/7.0.0.10251 SLBChan/33'
         }

def check_app_isexist(appid): #查询某个app是否存在
    if isinstance(appid,str):
        param = {'appIds':appid}
        re = requests.get('http://config.qa.bx/openapi/v1/apps?', headers=header, params=param)
        if re.status_code==200:
            text.insert(INSERT,appid+'存在!\n')
        else:
            tkinter.messagebox.showerror('错误',"请输入字符类型的appid")
            return None

def get_namespaceName_list(evn,appid): #获取某个app在某个环境下所有namespace名称列表
    # Authorization中的token是在配置中心管理员权限中创建获得的，目前只有ApolloSim这个应用，如需其他应用，找宇阳开通，使用第三方应用‘feigongneng’
    url = 'http://config.qa.bx/openapi/v1/envs/%s/apps/%s/clusters/default/namespaces'%(evn,appid)
    re_namespaces = requests.get(url, headers=header)
    if re_namespaces.status_code != 200:
        tkinter.messagebox.showerror('错误',"获取namespace错误，请检查环境或appid是否正确")
    #print(re_namespaces.text)
    re_namesapace_list = json.loads(re_namespaces.text)
    #print(type(re_namesapace_list))
    namespaceName_list = []
    for namesapace in re_namesapace_list:
        #print(type(namesapace))
        namespaceName_list.append(namesapace['namespaceName'])
        #print('@@@@@@@',namespaceName_list)
    return namespaceName_list

def get_namespaces_items1(appid,namespaceName): #用公开接口获取namespace信息
    url = 'http://cfs.f.qa.bx:10010/configfiles/%s/default/%s'%(appid,namespaceName)
    re = requests.get(url)
    #print(re_g.text)
    return re.text

def get_namespaces_items(env,appid,namespaceName): #获取某个Namespace信息接口
    url = 'http://config.qa.bx/openapi/v1/envs/%s/apps/%s/clusters/default/namespaces/%s'%(env,appid,namespaceName)
    re = requests.get(url, headers=header)
    #print(re.text)
    items = json.loads(re.text)
    #print('!!!!!!!!!!',items["items"])
    return items["items"]

def creat_namespaces(appid,namespaceName): #创建Namespace
    url = 'http://config.qa.bx/openapi/v1/apps/%s/appnamespaces'%appid
    data = {
		'name': namespaceName, #namespace的名字，如果是properties，去掉后缀.properties
		'appId': appid,
		'format': 'properties', #namespace的格式，如properties，xml
		'isPublic': 'turn', #是否是公共namespace
		'comment': "", #评论
		'dataChangeCreatedBy': 'co_tianchuan' #操作人，（执行操作的人，留痕）
		}
    re = requests.post(url,headers=header, json=data)
    if re.status_code==400:
        tkinter.messagebox.showerror('错误',"namespace已存在!")
        #print('namespace已存在')
        return None
    return re.text

def creat_items(env,appid,namespaceName,key,value): #新增配置接口
    url = 'http://config.qa.bx/openapi/v1/envs/%s/apps/%s/clusters/default/namespaces/%s/items' %(env,appid,namespaceName)
    IfNotExists = True
    value = value.strip()
    data = {   
        'key': key,
		'value': value,
		'comment': "", #评论
		'dataChangeCreatedBy': 'co_tianchuan', #操作人，（执行操作的人，留痕）
		'createIfNotExists':  IfNotExists #是否覆盖已存在的配置
        }
    re = requests.post(url,headers=header,json=data)
    # print(json.loads(re.text)['message'])
    if re.status_code == 200:
        return re.text
    elif re.status_code == 400 and json.loads(re.text)['message'] == 'item already exists':
        tkinter.messagebox.showerror('错误',"item已经存在！")
    else:
        tkinter.messagebox.showerror('错误',"上传配置错误!")
        # print('~~~~~~~~~~',re.status_code)
        # print(re.text)
        
def do_release(env,appid,namespaceName): #发布配置接口
    url = 'http://config.qa.bx/openapi/v1/envs/%s/apps/%s/clusters/default/namespaces/%s/releases' %(env,appid,namespaceName)
    import time
    title = time.strftime("%Y%m%d%H%M%S", time.localtime()) + "-release"
    data = {
    "releaseTitle":title, #时间戳加releases
    "releaseComment":"", #备注
    "releasedBy":"co_tianchuan" #创建人
            }
    re = requests.post(url,headers=header, json=data)
    return re.text

def Modify_item(env,appid,namespaceName,key,value): #修改配置
    url = 'http://config.qa.bx/openapi/v1/envs/%s/apps/%s/clusters/default/namespaces/%s/items/%s' %(env,appid,namespaceName,key)
    value = value.strip()
    data = {   
        'key': key, #需要修改的key
		'value': value, #需要修改的value
		'comment': "", #评论
		'dataChangeLastModifiedBy': 'co_tianchuan' #操作人，（执行操作的人，留痕）
        }
    re = requests.put(url,headers=header, json=data)
    if re.status_code == 200:
        text.insert(INSERT,'修改配置成功')
        text.insert(INSERT,'修改配置%s，新值为%s' %(key,value),'\n')
        #print('修改配置%s，新值为%s' %(key,value))
        return re.text
    else:
        text.insert(INSERT,'修改配置失败 错误码%s \n'% re.status_code)
        text.insert(INSERT,'错误信息%s\n' %re.text)
        return None

def delete_item(appid,namespaceName,key): #删除某个配置
    url = 'http://config.qa.bx/openapi/v1/envs/sitz/apps/%s/clusters/default/namespaces/%s/items/%s' %(appid,namespaceName,key)
    oper = {"operator":"co_tianchuan"}
    re = requests.delete(url,headers=header,params=oper)
    if re.status_code == 200:
        print("appid %s下的namespace:%s中key%s已被删除" %(appid,namespaceName,key))
    else:
        print("appid %s下的namespace:%s中key%s删除失败" %(appid,namespaceName,key))

def get_releases_latest(env,appid,namespaceName): #获取某个Namespace当前生效的已发布配置接口
    url = 'http://config.qa.bx/openapi/v1/envs/%s/apps/%s/clusters/default/namespaces/%s/releases/latest' %(env,appid,namespaceName)
    re = requests.get(url, headers=header)
    result = json.loads(re.text)['configurations']
    return str(result)

def get_config():
    appid = e1.get().strip()
    f_env = e2.get().strip()
    #t_env = e3.get()
    if not appid :
        tkinter.messagebox.showerror('错误',"请输入appid!")
    elif not f_env :
        tkinter.messagebox.showerror('错误',"请输入获取环境!")
    # elif not t_env :
    #     tkinter.messagebox.showerror('错误',"请输入配置环境!")
    else:
        check_app_isexist(appid)
        if not os.path.exists(os.path.join(file_path,appid)):
                os.mkdir(appid)
                #text.insert(INSERT,'文件位置'+os.path.join(file_path,appid)+'\n')
        else:
            pass
        for namespaceName in get_namespaceName_list(f_env,appid):
            item_path = os.path.join(file_path,appid,namespaceName)
            if not os.path.exists(item_path):
                os.mkdir(item_path)
            text.insert(INSERT,'获取'+namespaceName+'配置\n')
            conf_path = os.path.join(item_path,"config.txt")
            if os.path.exists(conf_path):
                os.remove(conf_path)
            for item in get_namespaces_items(f_env,appid,namespaceName):
                #print('~~~~~~',namespaceName,item)
                with open(item_path+"\config.txt",'a') as fp:
                    if item['key'] == 'content':
                        fp.write(str(item['key'])+'='+'\n'+str(item['value']))
                    elif item['key'] and item['value']:
                        fp.write(str(item['key'])+'='+str(item['value'])+"\n")

def creat_config():
    appid = e1.get().strip()
    #f_env = e2.get()
    t_env = e3.get().strip()
    # appid = "ApolloSim"
    # f_env = 1
    # t_env = 1
    if not appid :
        tkinter.messagebox.showerror('错误',"请输入appid!")
    # elif not f_env :
    #     tkinter.messagebox.showerror('错误',"请输入获取环境!")
    elif not t_env :
        tkinter.messagebox.showerror('错误',"请输入配置环境!")
    else:
        app_path = os.path.join(file_path,appid)
        for root,dirs,files in os.walk(app_path):
            for name in files:
                confile_path = os.path.join(root,name)
                namespaceName = os.path.split(root)[-1]
                # print(confile_path)
                # print(namespaceName)
                if os.path.exists(confile_path):
                    with open(confile_path,'r') as fp:
                        #all_text = fp.read()
                        for line in fp.readlines():
                            # print(line)
                            # print(line.strip() == 'content=')
                            # print(type(line))
                            # print(all_text)
                            if line.strip() == 'content=':
                                fp.seek(10)
                                #print(fp.read())
                                text_content = fp.read().strip()
                                creat_items(t_env,appid,namespaceName,'content',text_content)
                                text.insert(INSERT,'配置namespace:'+namespaceName+'\n')
                                text.insert(INSERT,'配置信息:content:'+text_content+'\n')
                                break
                            else:
                                #print('lllll',line)
                                key,value = line.split('=',1)
                                #print("*****",key,value)
                                creat_items(t_env,appid,namespaceName,key,value)
                                text.insert(INSERT,'配置namespace:'+namespaceName+'\n')
                                text.insert(INSERT,'配置信息:'+key+':'+value+'\n')

def modify_config():
    appid = e1.get().strip()
    #f_env = e2.get()
    t_env = e3.get().strip()
    # appid = "ApolloSim"
    # f_env = 1
    # t_env = 1
    if not appid :
        tkinter.messagebox.showerror('错误',"请输入appid!")
    # elif not f_env :
    #     tkinter.messagebox.showerror('错误',"请输入获取环境!")
    elif not t_env :
        tkinter.messagebox.showerror('错误',"请输入配置环境!")
    else:
        app_path = os.path.join(file_path,appid)
        for root,dirs,files in os.walk(app_path):
            for name in files:
                confile_path = os.path.join(root,name)
                namespaceName = os.path.split(root)[-1]
                # print(confile_path)
                # print(namespaceName)
                if os.path.exists(confile_path):
                    with open(confile_path,'r') as fp:
                        #all_text = fp.read()
                        for line in fp.readlines():
                            # print(line)
                            # print(line.strip() == 'content=')
                            # print(type(line))
                            # print(all_text)
                            if line.strip() == 'content=':
                                fp.seek(10)
                                #print(fp.read())
                                text_content = fp.read()
                                Modify_item(t_env,appid,namespaceName,'content',text_content)
                                text.insert(INSERT,'配置namespace:'+namespaceName+'\n')
                                text.insert(INSERT,'配置信息:content:'+text_content+'\n')
                                break
                            else:
                                #print('lllll',line)
                                key,value = line.split('=',1)
                                #print("*****",key,value)
                                Modify_item(t_env,appid,namespaceName,key,value)
                                text.insert(INSERT,'配置namespace:'+namespaceName+'\n')
                                text.insert(INSERT,'配置信息:'+key+':'+value+'\n')
            
def release_config():
    appid = e1.get().strip()
    #f_env = e2.get()
    t_env = e3.get().strip()
    # appid = "ApolloSim"
    # f_env = 1
    # t_env = 1
    if not appid :
        tkinter.messagebox.showerror('错误',"请输入appid!")
    # elif not f_env :
    #     tkinter.messagebox.showerror('错误',"请输入获取环境!")
    elif not t_env :
        tkinter.messagebox.showerror('错误',"请输入配置环境!")
    else:        
        app_path = os.path.join(file_path,appid)
        for root,dirs,files in os.walk(app_path):
            for name in files:
                confile_path = os.path.join(root,name)
                namespaceName = os.path.split(root)[-1]
                # print(confile_path)
                # print(namespaceName)
                if os.path.exists(confile_path):
                    do_release(t_env,appid,namespaceName)
                    text.insert(INSERT,'发布'+namespaceName+'配置成功\n')
                    text.insert(INSERT,'最新配置如下\n')
                    text.insert(INSERT,get_releases_latest(t_env,appid,namespaceName)+'\n')

def contrast_config():
    appid = e1.get().strip()
    f_env = e2.get().strip()
    t_env = e3.get().strip()
    # appid = "CCS-x-file"
    # f_env = 'sitf'
    # t_env = 'sitz'
    if not appid :
        tkinter.messagebox.showerror('错误',"请输入appid!")
    elif not f_env :
        tkinter.messagebox.showerror('错误',"请输入获取环境!")
    elif not t_env :
        tkinter.messagebox.showerror('错误',"请输入配置环境!")
    else:
        check_app_isexist(appid)
        f_namespace_list = get_namespaceName_list(f_env,appid)
        t_namespace_list = get_namespaceName_list(t_env,appid)
        contrast_list = list(set(f_namespace_list).symmetric_difference(set(t_namespace_list))) #两个集合的全部差集
        if contrast_list:
            text.insert(INSERT,'两个环境namespace不同，差异如下：'+'\n')
            text.insert(INSERT,str(contrast_list)+'\n')
        else:
            text.insert(INSERT,'两个环境namespace相同'+'\n')
            #check_app_isexist(appid)
            # print(f_namespace_list,t_namespace_list)
            for namespace in f_namespace_list:
                f_item_list = get_namespaces_items(f_env,appid,namespace)
                t_item_list = get_namespaces_items(t_env,appid,namespace)
                f_item_dic = {}
                t_item_dic = {}
                for f_item in f_item_list:
                    if f_item['key']:
                        f_item_dic[f_item['key']] = f_item['value']
                for t_item in t_item_list:
                    if t_item['key']:
                        t_item_dic[t_item['key']] = t_item['value']
                # print('FFFFFFFFF',f_item_list)
                # print('TTTTTTTTT',t_item_list)
                import dictdiffer
                for diff in list(dictdiffer.diff(f_item_dic, t_item_dic)):
                    text.insert(INSERT,'namespace:%s中，不同的内容'% namespace+str(diff)+'\n')
                
                # for f_item in f_item_list:
                #     for t_item in t_item_list:
                #         if f_item['key'] != t_item['key']:
                #             text.insert(INSERT,'获取环境%s与配置环境%s中namespace"%s"的key不同，分别是%s和%s' %(f_env,t_env,namespace,f_item['key'],t_item['key']) +'\n')
                #         elif f_item['value'] != t_item['value']:
                #             text.insert(INSERT,'获取环境%s与配置环境%s中namespace"%s"的key%s的值不同，分别是%s和%s' %(f_env,t_env,namespace,f_item['key'],f_item['value'],t_item['value']) +'\n')
                # text.insert(INSERT,'获取环境%s与配置环境%s中namespace"%s"下的配置一致' %(f_env,t_env,namespace) +'\n')
                     
# creat_items(t_env,appid,namespaceName,item['key'],item['value'])
# text.insert(INSERT,'配置信息：'+item['key']+':'+item['value']+'\n')
# do_release(t_env,appid,namespaceName)
# text.insert(INSERT,'发布'+namespaceName+'配置成功\n')
# text.insert(INSERT,'最新配置如下\n')
# text.insert(INSERT,get_releases_latest(t_env,appid,namespaceName)+'\n')

def quit_save():
    import time
    if not text.get("0.0","end").strip(): #如果窗口没有任何内容（没有做任何操作）就不保存，退出
        root.quit()
    else:
        savelog = ''
        nowtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()) #获取当前时间并格式化输出
        savelog = nowtime+"\n"+text.get("0.0","end") #获取文本框全部内容
        with open(file_path+"\%s.log" % nowtime[:10],'a',encoding='utf-8') as fp: #使用日期作为log文件名
            fp.write(savelog)
        root.quit()

def helpinf():
    tkinter.messagebox.showinfo('帮助',"""1.输入您要获取配置的AppID，以及获取配置的环境名（大小写均可）。
2.点击获取配置，就可获取相应的配置，在工具根目录下的dist文件夹下，生成与AppID一致的文件夹，其中子文件夹名为各namespace，其下为各namaspace的配置文件（config.txt）。
3.修改各配置文件中的配置项（请只修改key、value，文本形式的配置key默认为content，value中内容为文本内容）。
4.修改好配置后保存，填写AppId，和要配置的环境名，点击上传配置按钮，配置即上传到apollo，并没有发布。
5.填写AppId，和要配置的环境名，点击发布配置，已上传的配置即发布生效。
快捷键：
F1                查看帮助
                                             """)

def aboutinf():
    tkinter.messagebox.showinfo('关于',"您现在正在使用的是测试版本   by:田川")

frame1.bind_all("<F1>",lambda event:helpinf())
frame1.bind_all("<Alt-F4>",lambda event:quit_save())
menu=Menu(root)
submenu1=Menu(menu,tearoff=0)
menu.add_cascade(label='查看',menu=submenu1)
submenu1.add_command(label='退出', command=quit_save)
submenu2=Menu(menu,tearoff=0)
menu.add_cascade(label='帮助',menu=submenu2)
submenu2.add_command(label='查看帮助',command=helpinf)
submenu2.add_command(label='关于',command=aboutinf)
root.config(menu=menu)

text = scrolledtext.ScrolledText(frame1,width=50,height=10,font=("宋体",15)) #创建可滚动的文本显示框
text.grid(row=4,column=0,padx=40,pady=15,columnspan=4) #放置文本显示框

#text.insert(INSERT,'文件位置'+file_path+'\n')

button1= Button(frame1 ,text=" 获取配置 ",font=("宋体",13),width=10,command=get_config).grid(row=5,column=0,padx=15,pady=5) #创建按钮
button2= Button(frame1 ,text=" 上传配置 ",font=("宋体",13),width=10,command=creat_config).grid(row=5,column=1,padx=15,pady=5)
button3= Button(frame1 ,text=" 修改配置 ",font=("宋体",13),width=10,command=modify_config).grid(row=5,column=2,padx=15,pady=5) 
button3= Button(frame1 ,text=" 发布配置 ",font=("宋体",13),width=10,command=release_config).grid(row=6,column=0,padx=15,pady=5) 
button4= Button(frame1 ,text=" 对比配置 ",font=("宋体",13),width=10,command=contrast_config).grid(row=6,column=1,padx=15,pady=5)
button4= Button(frame1 ,text=" 退出 ",font=("宋体",13),width=10,command=quit_save).grid(row=6,column=2,padx=15,pady=5)

root.mainloop() #执行tk

# session = requests.session()
# url = "http://config.qa.bx/signin"
# header ={
#             'Connection': 'keep-alive',
#             'Content-Type': 'application/x-www-form-urlencoded',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 SLBrowser/7.0.0.10251 SLBChan/33'
#         }

# data = {
#     "username":"co_tianchuan",
#     "password":"830223tC",
#     "login-submit": "%E7%99%BB%E5%BD%95"
# }
# # tctest = requests.post(url, json=data, headers=header, allow_redirects=False)
# # print(tctest.cookies)

# re_signin = session.request("POST",url, json=data, headers=header, allow_redirects=False)
# print(re_signin.status_code)
# print(re_signin.text)
# cookic = requests.utils.dict_from_cookiejar(re_signin.cookies)
# print(cookic)

# #cookic = json.dumps(cookic)
# header_u ={
#             'Connection': 'keep-alive',
#             'Content-Type': 'application/json;charset=UTF-8',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 SLBrowser/7.0.0.10251 SLBChan/33'
#         }
# data_u = {
#     "id": 162785,
#     "namespaceId": 10755,
#     "key": "test",
#     "value": "test",
#     "lineNum": 1,
#     "dataChangeCreatedBy": "co_tianchuan",
#     "dataChangeLastModifiedBy": "co_tianchuan",
#     "dataChangeCreatedTime": "2021-11-30T11:07:13.000+0800",
#     "dataChangeLastModifiedTime": "2021-11-30T20:01:34.000+0800",
#     "isQuoteNamespace": 'false',
#     "tableViewOperType": "update",
#     "comment": ""
# }
# put_cookic = {"SSID":"b3609b135f0945daa3c5faa40aa5a940", "NG_TRANSLATE_LANG_KEY":"zh-CN","JSESSIONID":cookic['JSESSIONID']}
# #data_u = json.dumps(data_u)
# url_u = 'http://config.qa.bx/apps/ApolloSim/envs/SITF/clusters/default/namespaces/jspt.tctest/items'
# re_items = session.request("PUT",url_u, data=data_u, headers=header_u, cookies=put_cookic, allow_redirects=False)
# print(re_items.url)
# print(re_items.text)

# auth = ("co_tianchuan", "830223tC")
# re_g = requests.get('http://172.20.3.38:80/configfiles/ApolloSim/default/redis',verify=True)
# print(re_g.text)
# print(re_g.url)
# print(re_g)

# header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 SLBrowser/7.0.0.10251 SLBChan/33"}
# param = {"configText":"test = test\ndfsdf = sdfsfd\n","namespaceId":10755,"format":"properties"}
# put_test = requests.put("http://config.qa.bx/apps/ApolloSim/envs/SITF/clusters/default/namespaces/jspt.tctest/items",data=param,headers=header)
# print(put_test.url)

# tctest = requests.get('http://cfs.f.qa.bx:10010//notifications/v2?appId=ApolloSim&notifications=%s')
# print(tctest.url)
# print(tctest.text)

# envclusters = requests.get('http://172.20.3.38:80/openapi/v1/apps/ApolloSim/envclusters',auth=auth)
# print(envclusters.text)

# namespaces = requests.get('http://cfs.f.qa.bx:10010/openapi/v1/envs/SITF/apps/test/clusters/default/namespaces')
# print(namespaces.text)

# if __name__ == '__main__':
#     update_item()
    # text = get_namespaces_items1('ApolloSim','text.yml')
    # print(text)
    # re = requests.get('http://config.qa.bx/openapi/v1/envs/sitf/apps/ApolloSim/clusters/default/namespaces/text.yml', headers=header)
    # print(re.text)
    # data = {   
    #     'key': 'test',
	# 	'value': 'python',
	# 	'comment': "", #评论
	# 	'dataChangeCreatedBy': 'co_tianchuan', #操作人，（执行操作的人，留痕）
	# 	'createIfNotExists': 'true' #是否覆盖已存在的配置
    #     }
    # re = requests.post('http://config.qa.bx/openapi/v1/envs/sitz/apps/ApolloSim/clusters/default/namespaces/jspt.tctest/items', headers=header,json=data)
    # print(re.text)
    # contrast()
