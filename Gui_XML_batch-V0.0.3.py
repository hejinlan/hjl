#!/usr/bin/python
# -*- coding: UTF-8 -*-
#--hejinlan-2021-03-16

from tkinter import *
from tkinter.messagebox import *
from tkinter import filedialog
from xml.etree.ElementTree import ElementTree,Element
from xml.dom.minidom import parse
import time
import os

root = Tk()                    
root.title("处理ts翻译文件小工具")

#获取指定文件夹下的指定类型文件
def Dirfile(srcdir ,file_ext):
    filelist = []
    dstlist = []
    filelist.append(srcdir)
    while len(filelist) != 0:
        tmpdir = filelist.pop()
        if os.path.isdir(tmpdir):
            tmpvec = os.listdir(tmpdir)
            for tmpitem in tmpvec:
                filelist.append(tmpdir + "/" + tmpitem)
        else:
            if os.path.isfile(tmpdir):
                if os.path.splitext(tmpdir)[1] == file_ext:
                    dstlist.append(tmpdir)
    return dstlist
#打印文件夹下指定类型的文件名称
def writeFileNmeToText(nameLst):
    contentfolderText.delete(1.0, 'end')
    for name in nameLst:
        strName = str(name) + "\n"
        contentfolderText.insert(END, strName)

#日志动态打印
def write_log_to_Text(logmsg):
    global logLineNum
    logLineNum= 0
    current_time = get_current_time()
    logmsg_in = str(current_time) +" " + str(logmsg) + "\n"      #换行
    msgText.insert(END, logmsg_in)
    logLineNum = logLineNum + 1
    
def readXml(in_path):
    domTree = parse(in_path)
    # 文档根元素
    rootNode = domTree.documentElement
    print(rootNode.nodeName)
    return rootNode

var = IntVar()
def isV5NBFile(fileName):
    domTree = parse(fileName)
    # 文档根元素
    rootNode = domTree.documentElement
    msgLst = rootNode.getElementsByTagName("message")
    var.set(0)
    for msg in msgLst:
        if msg.hasAttribute("id") :
            var.set(1)
	    return
    
def updateXML_MsgID(fileName,txtFileName,savePathName):
    domTree = parse(fileName)
    # 文档根元素
    rootNode = domTree.documentElement
    msgLst = rootNode.getElementsByTagName("message")
    dataList = []
    dataList = open_read_txtFile(txtFileName)
    print(dataList)
    for msg in msgLst:
        if msg.hasAttribute("id") :
            msgID = msg.getAttribute("id")

            for lst in dataList:
                lstMsg = lst.split(",")
                idMsg= lstMsg[0]
                srcTrans = lst[len(lstMsg[0])+1:len(lst)]
                srcTrans= eval(srcTrans)

                if idMsg == msgID:

                    translation = msg.getElementsByTagName("translation")[0]
                    if len(translation.childNodes) > 0:
                        translation.childNodes[0].data = srcTrans
                    break
           
    with open(savePathName, 'w',encoding='utf-8') as f:
        domTree.writexml(f, addindent='', encoding='utf-8')
    write_log_to_Text("INFO: .ts File Conversion  success . Path: " + savePathName)
    
def updateXML(fileName,txtFileName,savePathName):
    domTree = parse(fileName)
    # 文档根元素
    rootNode = domTree.documentElement
    sources = rootNode.getElementsByTagName("source")
    dataList = []
    dataList = open_read_txtFile(txtFileName)
    
    for src in sources:
        if len(src.childNodes) <= 0 :
            write_log_to_Text("ERROR:请选择V5兼容相应的.ts文件！")
            return
        srcData = src.childNodes[0].data
        for lst in dataList:
           lstSrc = lst.split(",")
           srcId= lstSrc[0]
           srcMsg = lst[len(lstSrc[0])+1:len(lst)]
           srcMsg= eval(srcMsg)
           if srcId == srcData:
               pn = src.parentNode
               translation = pn.getElementsByTagName("translation")[0]
               if len(translation.childNodes) > 0:
                   translation.childNodes[0].data = srcMsg               
               break		
           
    with open(savePathName, 'w',encoding='utf-8') as f:
        domTree.writexml(f, addindent='', encoding='utf-8')
        
    write_log_to_Text("INFO: .ts File Conversion  success . Path: " + savePathName)    
		
#获取当前时间
def get_current_time():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return current_time

def getSaveFileName(txtFilename):
    listStr0 = fileText.get().split('/')
    listStr1 = listStr0[len(listStr0)-1].split('_');
    listStr2 = txtFilename.split('_');
    listStr3 = listStr2[len(listStr2)-1].split('.');
    listStr = otherText.get().split('/')
    st=""

    if len(listStr) > 1:
        st = "/" if listStr[1] !=''  else  ""
        
    savefileName = otherText.get() + st + listStr1[0] +'_'+listStr3[0]+".ts"
    return savefileName
    
def open_read_txtFile(fileTextName):
    print('read {name} context!'.format(name=fileTextName))
    dataList = []
    f = open(fileTextName, encoding='UTF-8-sig')
    while True:
        context = f.readline()
        if not context:
            break        
        #context = context.strip('\n').split()
        context = context.strip('\n')
        dataList.append(context)
    
    return dataList

    
def onFileCallBack():
  fileText['state'] = 'normal'  
  Folderpath = filedialog.askdirectory();
  filepath = filedialog.askopenfilename();
  fileText.delete(0, END)
  fileText.insert(0,filepath)
  fileText['state'] = 'readonly'

  if filepath != "":
      write_log_to_Text("INFO:open : "+ filepath + " file success")
  else :
      write_log_to_Text("ERROR:请选择具体.ts文件！")
     
def onOtherCallBack():
  otherText['state'] = 'normal'  
  Folderpath = filedialog.askdirectory();
  otherText.delete(0, END)
  otherText.insert(0,Folderpath)
  otherText['state'] = 'readonly'
  if Folderpath != "":
      write_log_to_Text("INFO:open : "+ Folderpath + " Folder success")
  else :
      write_log_to_Text("ERROR:请选择内容文件夹！")
  Dirfile(Folderpath,".txt")
  writeFileNmeToText(Dirfile(Folderpath,".txt"))

def onStartCallBack():
    xmlFilePath = fileText.get()
    isV5NBFile(xmlFilePath)
    for txtFileName in Dirfile(otherText.get(),".txt"):
        if var.get() == 1 :
            updateXML_MsgID(xmlFilePath,txtFileName,getSaveFileName(txtFileName))
        else:
            updateXML(xmlFilePath,txtFileName,getSaveFileName(txtFileName))
            
#UI部分代码         
label_file=Label(text='模板文件名:')
label_other=Label(text='内容文件夹:')
fileText =  Entry(root, bd =2,width=75)

otherText =  Entry(root, bd =2,width=75)

contentfolderText=Text(root,width= 95,height=15)

# row,column,sticky
label_file.grid(row=0,column=0,sticky=W) #一个有sticky,一个没有sticky，以作区分
label_other.grid(row=1,column=0)
# rowspan,columnspan
fileText.grid(row=0,column=1)
otherText.grid(row=1,column=1)
contentfolderText.grid(row=2,column=0,columnspan=3)

btnFile = Button(root, text ="选择模板文件", bg="lightblue", width=15,command = onFileCallBack)
btnother = Button(root, text ="选择内容文件夹", bg="lightblue", width=15,command = onOtherCallBack)
btnSave = Button(root, text ="批量生成文件", bg="lightgreen", width=15,command = onStartCallBack) 
btnFile.grid(row=0,column=2)
btnother.grid(row=1,column=2)

btnSave.grid(row=5,column=0,columnspan= 3)

#信息显示
msgText=Text(root,width= 95,height=20)
msgText.grid(row=6,column=0,columnspan= 3)

root.mainloop()                 # 进入消息循环
