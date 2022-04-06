# encoding:utf-8
"""
跳转到管理员局面了，

"""
import cv2
import pymysql
import xlwt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,pyqtSignal,QRegExp,QDateTime,QCoreApplication,QThread
from PyQt5.QtGui import QFont,QPixmap,QIcon,QRegExpValidator,QPalette
import numpy as np
import datetime
import time
import zipfile
import os
import sys
from gui_ui.admin import *
from gui_ui.window2showTable import *
import smtplib
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# admin 管理员页面
class adminControl(Ui_admin,QWidget):
    def __init__(self):
        super(adminControl, self).__init__()
        self.setupUi(self)
        self.initUI()

        # 显示窗体
        self.show()


    def initUI(self):

        # 页面基础属性设置
        self.windowNatrue()

        # 设置背景图片
        self.Setting_Background()

        # 考勤管理--输入属性初始化
        self.attendanceLineInit()

        # 班级管理--输入属性初始化
        self.classLineInit()

        # 课表管理---输入属性初始化
        self.lessonLineInit()

        # 数据分析----输入属性初始化
        self.AnalysisLineInit()

        # 设置信号槽
        self.signalSetting()

        # 显示时间
        self.Show_Time()


####################################基本窗体功能######################
    # 显示时间
    def Show_Time(self):
        self.time = Time()
        self.time.update_time.connect(self.Update_Time)
        self.time.start()

    def Update_Time(self,data):
        # 显示实时时间
        self.time_label.setText(data)
        self.time_label.setFont(QFont("Roman tomes", 8, QFont.Bold))

    # 页面基础属性设置
    def windowNatrue(self):
        # 窗体名称
        self.setWindowTitle("管理员页面")
        # 设置所有窗体图标
        self.setWindowIcon(QIcon("./gui_image/lin.png"))
        # 设置提示框内容
        self.setToolTip("欢迎来到管理员页面，我是林树斌")
        self.setFixedSize(800,450)

    # 设置背景图片
    def Setting_Background(self):
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap("gui_image/Teacher.jpg")))
        self.setPalette(window_pale)

    # 侧栏选项卡点击事件
    def onTreeClicked(self):
        item = self.treeWidget.currentItem()
        # 获取当前序号
        index_top = self.treeWidget.indexOfTopLevelItem(item)
        # 根据节点序号直接调用page页面
        self.stackedWidget.setCurrentIndex(index_top)

    # 信号槽连接
    def signalSetting(self):
        # 选项卡点击事件
        self.treeWidget.clicked.connect(self.onTreeClicked)

        # 考勤管理-------”考勤签到按钮
        self.Start_to_Attendence.clicked.connect(self.Attendence)

        # 考勤管理------个人请假按钮
        self.Free_Button.clicked.connect(self.personFreeApply_Func)


        # 考勤管理------确定按钮
        self.makesure_button.clicked.connect(self.MakeSure_Func)



        # 班级管理----》保存按钮
        self.classSaveSettings.clicked.connect(self.saveClassSettings)
        # 班级管理----》查看表单
        self.watchClass.clicked.connect(self.table2show)
        # 课表管理---》 保存按钮
        self.tableSaveSettings.clicked.connect(self.saveLessonSettings)
        # 课表管理---》查看表单
        self.watchTable.clicked.connect(self.lesson2show)
        # 统计分析---> 查询按钮
        self.findTheData.clicked.connect(self.find_freshData_Func)
        # 统计分析----> 刷新按钮
        self.freshAdminTable.clicked.connect(self.find_freshData_Func)
        # 统计分析----> 导出表格
        self.out2excel.clicked.connect(self.save2Excel)
        # 统计分析----> 发送至邮箱
        self.send2email.clicked.connect(self.send2email_Func)



###################################attendence考勤功能管理
    def attendanceLineInit(self):
        # 检测输入
        self.check_input()

        # 考勤班级编号----框内提示
        self.class_lineedit.setPlaceholderText("10位班级编号!")
        # 考勤班级编号限制8位纯数字
        class_val = QRegExpValidator(QRegExp("^[0-9]{10}$"))
        self.class_lineedit.setValidator(class_val)
        # 设置检查“考勤班级编号"输入框输入状态F
        self.class_lineedit.textChanged.connect(self.check_input)

        # 考勤课程---框内提示
        self.lesson_lineedit.setPlaceholderText("课程名称!")
        # 考勤课程限制中文输入
        lesson_val = QRegExpValidator(QRegExp("^[A-Z0-9-\u4e00-\u9fa5]{12}$"))
        self.lesson_lineedit.setValidator(lesson_val)
        # 设置检查”考勤课程“输入框输入状态
        self.lesson_lineedit.textChanged.connect(self.check_input)

        # 考勤地点---框内提示
        self.classroom.setPlaceholderText("教室号!")
        # 考勤班级编号限制输入8位纯数字
        classroom_val = QRegExpValidator(QRegExp("^[0-9A-Z-]{6}$"))
        self.classroom.setValidator(classroom_val)
        # 设置检查"考勤地点"输入框输入状态
        self.classroom.textChanged.connect(self.check_input)


    def check_input(self):
        # 当考勤班级及考勤地点输入框均有内容时，设置按钮为可点击状态，或者不可点击。
        if self.class_lineedit.text() and self.classroom.text() and self.lesson_lineedit.text():
            self.makesure_button.setEnabled(True)
        else:
            self.makesure_button.setEnabled(False)
            self.Start_to_Attendence.setEnabled(False)
            self.Free_Button.setEnabled(False)

    # 确定按钮
    def MakeSure_Func(self):
        # 考勤班级编号
        class2test_tempor = self.class_lineedit.text()
        # 考勤课程
        lesson2SignUp_tempor = self.lesson_lineedit.text()
        # 教学楼位置
        classBuilding_tempor = self.location_building.currentText()
        # 考勤班级教室
        classroom_tempor = self.classroom.text()
        # 考勤班级地点(教学楼+教室)
        classroom_Location_tempor = classBuilding_tempor + classroom_tempor

        # ”禁止请假“复选框状态
        if (self.banFree.isChecked() == True):
            banFreeApply_Flag = True
        else:
            banFreeApply_Flag = False

        # 判断是有该班级的人脸检测样本
        # 人脸检测样本的文件夹路径
        path = "./userTrainer2save/" + class2test_tempor + '/' + class2test_tempor +'_trainer.yml'
        # 检测该班级的人脸检测样本是否存在
        folder = os.path.exists(path)
        # 不存在
        if not folder:
            QMessageBox.about(self,"提示","没有该班级的人脸考勤样本")
            self.class_lineedit.setText("")
            self.classroom.setText("")
            return
        else:
            pass

        # 查询该班级今日是否有课
        ifExistlesson_Flag = self.ifTodayExistClass()
        if (ifExistlesson_Flag == 1):
            pass
        else:
            QMessageBox.about(self,"提示","该班级今日没有次课程的教学计划！")
            return

        # 签到前准备--->检测是否存在该班级的签到数据表单
        self.classSignUpSheetInit()

        # 查找classtable表  刷新·应到人数·数据
        self.Should_Arriave()

        # 刷新已签到表格和已到的表单
        # 查找14021702_signdata表查找状态为1
        self.Already_Arrive()

        # 刷新"迟到/请假人员"表格和人数
        self.LateAndFree()

        # 开放“考勤签到”功能
        self.Start_to_Attendence.setEnabled(True)

        # 开放或锁定“个人请假”功能
        if (banFreeApply_Flag == True):
            self.Free_Button.setEnabled(False)
            QMessageBox.about(self,"提示","设置成功！已开放考勤签到功能！")
        else:
            self.Free_Button.setEnabled(True)
            QMessageBox.about(self,"提示","已开放“考勤签到”“个人请假”功能")

    # 考勤按钮
    def Attendence(self):
        # 考勤班级编号
        class2test_tempor = self.class_lineedit.text()
        # 考勤课程
        lesson2SignUp_tempor = self.lesson_lineedit.text()
        # 教学楼位置
        classBuilding_tempor = self.location_building.currentText()
        # 考勤班级教室
        classroom_tempor = self.classroom.text()
        # 考勤班级地点(教学楼+教室)
        classroom_Location_tempor = classBuilding_tempor + classroom_tempor

        # 该班级的检测样本名称
        modelpath = './userTrainer2save/' + class2test_tempor + '/'+ class2test_tempor +'_trainer.yml'
        # 检测检测样本是否存在
        folder = os.path.exists(modelpath)
        # 不存在，提示报错
        if not folder:
            QMessageBox.about(self,"发生错误","未检索到该班级的检测模型！")
            return
        else:
            pass

        # 调用OpenCV的LBPHFaceRecognizer_create()函数
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        # 读入检测样本数据
        recognizer.read(modelpath)
        # haarcascade分类器路径
        cascadePath = "./haarcascades/haarcascade_frontalface_default.xml"
        # 调用haarcascade分类器
        faceCascade = cv2.CascadeClassifier(cascadePath)
        # 使用默认字体
        font = cv2.FONT_HERSHEY_SIMPLEX

        # 空列表，存储从数据库取出的学号
        numIndex = []
        # 空列表，存储从数据库取出的用户中文姓名
        names_Ch = []
        # 空列表，存储从数据库取出的用户英文姓名
        names_En = []

        ## 从数据库中拿到该班级的学号和对应的名字

        # 连接数据库
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()
        # 在数据库中检索该班级的表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql, class2test_tempor)
        # 存在该班级表单
        if (rows):
            # 获取该班级信息表单内存储的数据
            cursor.execute('select * from `%s`' %class2test_tempor)

            # 取出所有记录
            rows = cursor.fetchall()

            # 记录个数，确定表单的行数
            rowSum = cursor.rowcount

            # 释放游标
            cursor.close()

            # 关闭连接，释放数据库资源
            conn.close()

            # 数据存入学号和姓名的列表
            for i in range(rowSum):
                # 临时记录学号，不能直接存入
                temp_data1 = rows[i][0]
                # 临时记中文姓名，不能直接存入
                temp_data2 = rows[i][1]
                # 临时记录英文姓名，不能直接存入
                temp_data3 = rows[i][2]
                # 学号存入numIndex列表
                numIndex.append(str(temp_data1))
                # 姓名存入names_Ch列表
                names_Ch.append(str(temp_data2))
                # 姓名存入names_En列表
                names_En.append(str(temp_data3))
        else:
            QMessageBox.about(self, "发生错误", "未检索到该班级的信息！")


        # 打开摄像头
        cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)

        # 设置图像宽度
        cam.set(3, 330)
        # 设置图像高度
        cam.set(4, 230)

        # 设置可被检测为人脸图像的最小大小
        minW = 0.1 * cam.get(3)
        minH = 0.1 * cam.get(4)

        # 身份暂存变量，用于2次校验用户身份，身份默认为"unknown"
        face_tempor_save1 = 'unknown1'
        face_tempor_save2 = 'unknown2'

        # 分频计数标志
        timecounter = 0
        while True:
            # 读取摄像头图像
            ret, img = cam.read()
            # 摄像头彩色图像灰度化
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 分类器参数设置
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(int(minW), int(minH)),
            )

            # 退出while循环信号位
            break_sign = '0'

            # 检测到人脸时
            for (x, y, w, h) in faces:

                # 框出人脸
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # id保存返回的被测人脸的学号
                id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

                # 转换id,因为12位学号整数超过了
                # 因为12位数字超过了范围，要做转换
                id = 201863462912 + id


                # 存在达到置信度阈值的人脸样本，完美匹配为100
                if (confidence > 40):
                    # 获取当前学号所对应的用户姓名
                    user_identity_En = names_En[numIndex.index(str(id))]

                    # round()设置保留几位小数点，默认为保留整数
                    confidence = "  {0}%".format(round( confidence))

                # 在检测样本中，不存在能达到规定置信阈值的人脸样本
                else:
                    # 标注未知身份
                    user_identity_En = "unknown"

                    # 此时的人脸置信度
                    confidence = "  {0}%".format(round( confidence))


                # 分频计数器加一
                timecounter = timecounter + 1

                # 视频中标注用户英文名称
                cv2.putText(img, str(user_identity_En), (x + 5, y - 5), font, 1, (0, 0, 255), 2)
                # 视频中标注用户当前身份的置信度
                cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 0, 0), 1)

                # 分频判断，每15帧暂存一次人脸图像的检测结果，稳定结果
                if (timecounter % 15 == 0):
                    # 移位暂存用户信息
                    face_tempor_save2 = face_tempor_save1
                    # 录入第二次检测的用户信息(上一次检测后过了15帧图像数据)
                    face_tempor_save1 = user_identity_En

                # 分频计数器置零
                if timecounter >= 45:
                    timecounter=0

                # 检测到人脸时，正常显示框脸后的图像
                # cv2.imshow('identified', img)
                # 转换图片格式
                img2Label = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # QImage对象--->self.LabelImg
                self.LabelImg = QtGui.QImage(img2Label.data,
                                             img2Label.shape[1],  # 宽度 width
                                             img2Label.shape[0],  # 高度 height
                                             img2Label.shape[1] * 3,  # 宽度*深度 width*depth
                                             QtGui.QImage.Format_RGB888)
                # 将QImage对象转换为QPixmap对象
                self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.LabelImg))

                # Qlabel显示图像
                self.imageLabel.show()


                # 结果稳定时，弹出提示框，用户本人二次验证
                if (face_tempor_save1 == face_tempor_save2 != "unknown"):
                    # 保存此时用户的学号
                    user_identity_num = str(id)
                    # 保存此时的用户中文姓名
                    user_identity_Ch = names_Ch[names_En.index(str(face_tempor_save1))]
                    # 用户本人二次验证
                    faceresult = QMessageBox.question(self, "签到确认：", "请问您是" + str(user_identity_Ch) + "同学吗？",
                                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    # 检测结果通过用户本人的二次验证
                    if faceresult == QMessageBox.Yes:
                        # 确认身份后再获取签到时间
                        # 获取当期的日期
                        date = QDateTime.currentDateTime()
                        # 正则表达式筛选"年-月-日"
                        date_now = date.toString("yyyy-MM-dd")
                        # 正则表达式筛选"时:分:秒"
                        time_sign = date.toString("hh:mm:ss")
                        # 签到数据状态验证位，初值为0
                        signState_Init = '0'
                        # 保存该班级签到数据的表单名
                        signUpSheetName = str(class2test_tempor) + "_signdata"

                        # 建立数据库连接
                        conn = pymysql.connect(
                            host='localhost',
                            port=3306,
                            user='root',
                            password='123456',
                            db='mytest',
                            charset='utf8'
                        )
                        # 拿到游标
                        cursor = conn.cursor()
                        # 在数据库中检索该班级的表单
                        sql = "select * from information_schema.tables where table_name = %s "
                        rows = cursor.execute(sql,signUpSheetName)
                        # 存在该签到表单
                        if(rows):
                            # 判断是否重复签到
                            sql_test = 'select *from %s' %signUpSheetName + ' where userId = %s and lessonName =%s and signDate = %s and signState = %s'
                            rows2 = cursor.execute(sql_test,(user_identity_num,lesson2SignUp_tempor,date_now,'1'))

                            # 判断是否已经迟到
                            sql_test = 'select *from %s' %signUpSheetName + ' where userId = %s and lessonName =%s and signDate = %s and signState = %s'
                            rows3 = cursor.execute(sql_test,(user_identity_num,lesson2SignUp_tempor,date_now,'2'))

                            # 判断是否已经请假
                            sql_test = 'select *from %s' %signUpSheetName + ' where userId = %s and lessonName =%s and signDate = %s and signState = %s'
                            rows4 = cursor.execute(sql_test,(user_identity_num,lesson2SignUp_tempor,date_now,'3'))

                            # 如果已经签到
                            if (rows2 or rows3):
                                QMessageBox.about(self,"提示","今天这节课你已经签到了")
                                # 将QImage对象转换为QPixmap对象
                                self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.LabelImg))
                                # 移除Qlabel图像
                                self.imageLabel.setPixmap(QPixmap(""))
                                # Qlabel显示图像
                                self.imageLabel.show()
                                # 退出签到函数
                                return
                            elif rows4:
                                QMessageBox.about(self,'提示','这节课你已经请假，无法签到')
                                # 将QImage对象转换为QPixmap对象
                                self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.LabelImg))
                                # 移除Qlabel图像
                                self.imageLabel.setPixmap(QPixmap(""))
                                # Qlabel显示图像
                                self.imageLabel.show()
                                # 退出签到函数
                                return
                            else:
                                # 插入数据记录
                                sql_insert = 'insert into %s ' %signUpSheetName + '(userId,userName,lessonName,classlocation,signDate,signTime,signState) values(%s,%s,%s,%s,%s,%s,%s)'
                                cursor.execute(sql_insert, (user_identity_num, user_identity_Ch,lesson2SignUp_tempor, classroom_Location_tempor, date_now, time_sign, signState_Init))
                                # 提交修改
                                conn.commit()
                                QMessageBox.about(self,"提示","保存签到数据成功！")
                        # 未找到该班级的签到数据表单
                        else:
                            QMessageBox.about(self,'报错','未找到该班级的签到数据表单！')
                            # 将QImage对象转换为QPixmap对象
                            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.LabelImg))

                            # Qlabel显示图像
                            self.imageLabel.show()
                            # 退出签到函数
                            return

                        # 关闭游标
                        cursor.close()
                        # 释放数据库资源
                        conn.close()
                        # 退出信号
                        break_sign = '1'
                        # 退出内部循环
                        break
                    # 检测结果未通过用户本人的二次验证，用户--->“不是本人”
                    else:
                        # 移除label上的图片
                        self.imageLabel.setPixmap(QPixmap("./gui_image/detectFalse.png"))
                        # Qlabel显示图片
                        self.imageLabel.show()
                        # 退出本次签到
                        return

            # 未检测到人脸时，正常显示获取的图像
            # 转换图片格式
            img2Label = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # QImage对象--->self.LabelImg
            self.LabelImg = QtGui.QImage(img2Label.data,
                                         img2Label.shape[1],    # 宽度 width
                                         img2Label.shape[0],    # 高度 height
                                         img2Label.shape[1] * 3,     # 宽度*深度 width*depth
                                         QtGui.QImage.Format_RGB888)
            # 将QImage对象转换为QPixmap对象
            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.LabelImg))

            # Qlabel显示图像
            self.imageLabel.show()

            # 按空格键退出窗口
            k = cv2.waitKey(20) & 0xff
            if (k == 32) or (break_sign == '1' ):
                break

        # 解除摄像头占用
        cam.release()

        # 移除label上的图片
        self.imageLabel.setPixmap(QPixmap(""))

        # 每录入一条签到数据，校验一次用户签到状态----->判定用户签到有效性
        self.checkSignState()

        # 刷新应到人数
        self.Should_Arriave()

        # 刷新已签到和已到的label
        self.Already_Arrive()

        # 刷新迟到
        self.LateAndFree()

    # 个人请假按钮
    def personFreeApply_Func(self):
        # 考勤班级编号
        class2test_tempor = self.class_lineedit.text()
        # 考勤课程
        lesson2SignUp_tempor = self.lesson_lineedit.text()
        # 教学楼位置
        classBuilding_tempor = self.location_building.currentText()
        # 考勤班级教室
        classroom_tempor = self.classroom.text()
        # 考勤班级地点(教学楼+教室)
        classroom_Location_tempor = classBuilding_tempor + classroom_tempor

        # 该班级的检测样本名称
        modelpath = './userTrainer2save/' + class2test_tempor + '/'+ class2test_tempor +'_trainer.yml'
        # 检测检测样本是否存在
        folder = os.path.exists(modelpath)
        # 不存在，提示报错
        if not folder:
            QMessageBox.about(self,"发生错误","未检索到该班级的检测模型！")
            return
        else:
            pass

        # 调用OpenCV的LBPHFaceRecognizer_create()函数
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        # 读入检测样本数据
        recognizer.read(modelpath)
        # haarcascade分类器路径
        cascadePath = "./haarcascades/haarcascade_frontalface_default.xml"
        # 调用haarcascade分类器
        faceCascade = cv2.CascadeClassifier(cascadePath)
        # 使用默认字体
        font = cv2.FONT_HERSHEY_SIMPLEX

        # 签到成功状态位
        successSignState = '1'

        # 空列表，存储从数据库取出的学号
        numIndex = []
        # 空列表，存储从数据库取出的用户中文姓名
        names_Ch = []
        # 空列表，存储从数据库取出的用户英文姓名
        names_En = []

        ## 从数据库中拿到该班级的学号和对应的名字
        # 连接数据库
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()
        # 在数据库中检索该班级的表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql, class2test_tempor)
        # 存在该班级表单
        if (rows):
            # 获取该班级信息表单内存储的数据
            cursor.execute('select * from `%s`' %class2test_tempor)

            # 取出所有记录
            rows = cursor.fetchall()

            # 记录个数，确定表单的行数
            rowSum = cursor.rowcount

            # 释放游标
            cursor.close()

            # 关闭连接，释放数据库资源
            conn.close()

            # 数据存入学号和姓名的列表
            for i in range(rowSum):
                # 临时记录学号，不能直接存入
                temp_data1 = rows[i][0]
                # 临时记中文姓名，不能直接存入
                temp_data2 = rows[i][1]
                # 临时记录英文姓名，不能直接存入
                temp_data3 = rows[i][2]
                # 学号存入numIndex列表
                numIndex.append(str(temp_data1))
                # 姓名存入names_Ch列表
                names_Ch.append(str(temp_data2))
                # 姓名存入names_En列表
                names_En.append(str(temp_data3))

        else:
            QMessageBox.about(self, "发生错误", "未检索到该班级的信息！")


        # 打开摄像头
        cam = cv2.VideoCapture(0+ cv2.CAP_DSHOW)

        # 设置图像宽度
        cam.set(3, 330)
        # 设置图像高度
        cam.set(4, 230)

        # 设置可被检测为人脸图像的最小大小
        minW = 0.1 * cam.get(3)
        minH = 0.1 * cam.get(4)

        # 身份暂存变量，用于2次校验用户身份，身份默认为"unknown"
        face_tempor_save1 = 'unknown1'
        face_tempor_save2 = 'unknown2'

        timecounter = 0  # 分频计数标志

        while True:
            # 读取摄像头图像
            ret, img = cam.read()

            # 摄像头彩色图像灰度化
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 分类器参数设置
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(int(minW), int(minH)),
            )

            # 退出while循环信号位
            break_sign = '0'

            # 检测到人脸时
            for (x, y, w, h) in faces:
                # 框出人脸
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # id保存返回的被测人脸的学号
                id, confidence = recognizer.predict(gray[y:y + h, x:x + w])


                # 转换id,因为12位学号整数超过了
                # 因为12位数字超过了范围，要做转换
                id = 201863462912 + id


                # 存在达到置信度阈值的人脸样本，完美匹配为100
                if (confidence > 57):
                    # 获取当前学号所对应的用户姓名
                    user_identity_En = names_En[numIndex.index(str(id))]

                    # round()设置保留几位小数点，默认为保留整数
                    confidence = "  {0}%".format(round( confidence))
                # 在检测样本中，不存在能达到规定置信阈值的人脸样本
                else:
                    # 标注未知身份
                    user_identity_En = "unknown"

                    # 此时的人脸置信度
                    confidence = "  {0}%".format(round( confidence))

                # 分频计数器加一
                timecounter = timecounter + 1

                # 视频中标注用户英文名称
                cv2.putText(img, str(user_identity_En), (x + 5, y - 5), font, 1, (0, 0, 255), 2)

                # 视频中标注用户当前身份的置信度
                cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 0, 0), 1)

                # 分频判断，每15帧暂存一次人脸图像的检测结果，稳定结果
                if (timecounter % 15 == 0):
                    # 移位暂存用户信息
                    face_tempor_save2 = face_tempor_save1
                    # 录入第二次检测的用户信息(上一次检测后过了15帧图像数据)
                    face_tempor_save1 = user_identity_En

                # 分频计数器置零
                if timecounter >= 45:
                    timecounter=0


                # 检测到人脸时，正常显示框脸后的图像
                # 转换图片格式
                img2Label = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # QImage对象--->self.LabelImg
                self.LabelImg = QtGui.QImage(img2Label.data,
                                             img2Label.shape[1],  # 宽度 width
                                             img2Label.shape[0],  # 高度 height
                                             img2Label.shape[1] * 3,  # 宽度*深度 width*depth
                                             QtGui.QImage.Format_RGB888)
                # 将QImage对象转换为QPixmap对象
                self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.LabelImg))

                # Qlabel显示图像
                self.imageLabel.show()

                # 结果稳定时，弹出提示框，用户本人二次验证
                if (face_tempor_save1 == face_tempor_save2 != "unknown"):
                    # 保存此时用户的学号
                    user_identity_num = str(id)
                    # 保存此时的用户中文姓名
                    user_identity_Ch = names_Ch[names_En.index(str(face_tempor_save1))]
                    # 用户本人二次验证
                    faceresult = QMessageBox.question(self, "签到确认：", "请问您是" + str(user_identity_Ch) + "同学吗？",
                                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    # 检测结果通过用户本人的二次验证
                    if faceresult == QMessageBox.Yes:
                        # 确认身份后再获取签到时间
                        # 获取当期的日期
                        date = QDateTime.currentDateTime()
                        # 正则表达式筛选"年-月-日"
                        date_now = date.toString("yyyy-MM-dd")
                        # 正则表达式筛选"时:分:秒"
                        time_sign = date.toString("hh:mm:ss")
                        # 签到数据状态验证位，初值为0,请假为3
                        signState_Init = '3'
                        # 保存该班级签到数据的表单名
                        signUpSheetName = str(class2test_tempor) + "_signdata"

                        # 建立数据库连接
                        conn = pymysql.connect(
                            host='localhost',
                            port=3306,
                            user='root',
                            password='123456',
                            db='mytest',
                            charset='utf8'
                        )
                        # 拿到游标
                        cursor = conn.cursor()
                        # 在数据库中检索该班级的表单
                        sql = "select * from information_schema.tables where table_name = %s "
                        rows = cursor.execute(sql,signUpSheetName)
                        # 存在该签到表单
                        if(rows):

                            # 判断是否已经成功签到请假
                            sql_test = 'select *from %s' %signUpSheetName + ' where userId = %s and lessonName =%s and signDate = %s and signState = %s'
                            rows1 = cursor.execute(sql_test,(user_identity_num,lesson2SignUp_tempor,date_now,'3'))

                            # 判断是否已经成功签到
                            sql_test = 'select *from %s' %signUpSheetName + ' where userId = %s and lessonName =%s and signDate = %s and signState = %s'
                            rows2 = cursor.execute(sql_test,(user_identity_num,lesson2SignUp_tempor,date_now,'1'))

                            # 判断是否已经迟到
                            sql_test = 'select *from %s' %signUpSheetName + ' where userId = %s and lessonName =%s and signDate = %s and signState = %s'
                            rows3 = cursor.execute(sql_test,(user_identity_num,lesson2SignUp_tempor,date_now,'2'))

                            if(rows1):
                                QMessageBox.about(self,'提示','您已经请过假了！')
                                # 移除label上的图片
                                self.imageLabel.setPixmap(QPixmap(""))
                                # Qlabel显示图像
                                self.imageLabel.show()
                                return

                            elif(rows2):
                                QMessageBox.about(self,'提示','你已经成功签到，无法在这节课请假')
                                # 移除label上的图片
                                self.imageLabel.setPixmap(QPixmap(""))
                                # Qlabel显示图像
                                self.imageLabel.show()
                                return
                            elif(rows3):
                                QMessageBox.about(self,'提示','你已经迟到，无法在这节课请假')
                                # 移除label上的图片
                                self.imageLabel.setPixmap(QPixmap(""))
                                # Qlabel显示图像
                                self.imageLabel.show()
                                return

                            else:
                                pass

                            # 插入记录
                            # 插入数据记录
                            sql_insert = 'insert into %s ' %signUpSheetName + '(userId,userName,lessonName,classlocation,signDate,signTime,signState) values(%s,%s,%s,%s,%s,%s,%s)'
                            cursor.execute(sql_insert, (user_identity_num, user_identity_Ch,lesson2SignUp_tempor, classroom_Location_tempor, date_now, time_sign, signState_Init))
                            # 提交修改
                            conn.commit()
                            QMessageBox.about(self,"提示","请假成功！")
                        # 未找到该班级的签到数据表单
                        else:
                            QMessageBox.about(self,'报错','未找到该班级的签到数据表单！')
                            # 退出签到函数
                            return

                        # 关闭游标
                        cursor.close()
                        # 释放数据库资源
                        conn.close()
                        # 退出信号
                        break_sign = '1'
                        # 退出内部循环
                        break
                    # 检测结果未通过用户本人的二次验证，用户--->“不是本人”
                    else:
                        # 移除label上的图片
                        self.imageLabel.setPixmap(QPixmap(""))
                        # Qlabel显示图像
                        self.imageLabel.show()
                        return

            # 未检测到人脸时，正常显示获取的图像
            # 转换图片格式
            img2Label = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # QImage对象--->self.LabelImg
            self.LabelImg = QtGui.QImage(img2Label.data,
                                         img2Label.shape[1],  # 宽度 width
                                         img2Label.shape[0],  # 高度 height
                                         img2Label.shape[1] * 3,  # 宽度*深度 width*depth
                                         QtGui.QImage.Format_RGB888)
            # 将QImage对象转换为QPixmap对象
            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.LabelImg))

            # Qlabel显示图像
            self.imageLabel.show()

            # 按空格键退出窗口
            k = cv2.waitKey(20) & 0xff
            if (k == 32) or (break_sign == '1' ):
                break


        # 移除label上的图片
        self.imageLabel.setPixmap(QPixmap(""))

        # Qlabel显示图像
        self.imageLabel.show()

        # 解除摄像头占用
        cam.release()
        # 刷新"迟到请假人员"表格
        self.LateAndFree()
        time.sleep(0.2)



    # 判断该班级今天是否有课
    def ifTodayExistClass(self):
        # 考勤班级编号
        class2test_tempor = self.class_lineedit.text()
        # 考勤课程
        lesson2SignUp_tempor = self.lesson_lineedit.text()
        # 获取当期的日期和周几
        date = QDateTime.currentDateTime()
        # 正则表达式筛选出”周几“ “星期几”星期一
        weekday_tempor = date.toString("dddd")
        # 正则表达式筛选”年-月-日"2022-03-14
        date_now = date.toString("yyyy-MM-dd")
        # 中文列表
        weekday_chinese_list = ['星期一','星期二','星期三','星期四','星期五','星期六','星期日']
        # 数字列表
        weekday_number_list = ['1','2','3','4','5','6','7']
        # 译码，中文转数字 1
        weekday_now = weekday_number_list[weekday_chinese_list.index(weekday_tempor)]

        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()

        # 查询该班级课表，“班级编号”“课程名称"
        sql = 'select * from lessontable where toClass = %s' % class2test_tempor + ' and lessonName = %s'
        rows = cursor.execute(sql, lesson2SignUp_tempor)
        # 存在”班级编号“”课程名称“
        if (rows):
            # 查询开课日期
            sql = 'select dateStart from lessontable where toClass = %s' % class2test_tempor + ' and lessonName = %s'
            cursor.execute(sql,  lesson2SignUp_tempor)
            # 获取存储的数据('2000-01-01',)
            row = cursor.fetchone()
            # 带数字元组转字符串2000-01-01
            row1 = ' '.join(map(str,row))
            # 当前日期大于开课日期
            if (date_now>=row1):
                # 查询结课日期
                sql = 'select dateEnd from lessontable where toClass = %s' % class2test_tempor + ' and lessonName = %s'
                cursor.execute(sql, lesson2SignUp_tempor)
                # 获取存储的数据
                row2_tempor = cursor.fetchone()
                # 带数字元组转字符串
                row2 = ' '.join(map(str, row2_tempor))
                # 当前日期小于结课日期
                if (date_now <= row2):
                    # 查询有课的”周几“
                    sql = 'select lessonWeek from lessontable where toClass = %s' % class2test_tempor + ' and lessonName = %s'
                    cursor.execute(sql, lesson2SignUp_tempor)
                    # 获取存储的数据('5,6',)
                    row3_tempor = cursor.fetchone()
                    # 带数字元组转字符串5,6 <class 'str'>
                    row3 = ' '.join(map(str, row3_tempor))
                    # 判断当天是否有课的”周几“
                    if (weekday_now in row3):
                        return 1
                    else: # 今天没有课
                        return 0
                else:# 当前日期大于结课日期
                    return 0
            else:#当前日期小于开课日期
                return 0
        else:
            QMessageBox.about(self,"提示","该班级未安排此课程计划!")
            # 清空"考勤课程"输入框
            self.lesson2SignUp.setText("")

        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()


    # 检查是否存在该班级的签到数据表单
    def classSignUpSheetInit(self):
        # 班级编号
        class2test = self.majorNumber.text()
        # 保存该班级签到数据的表单名
        signUpSheetName = str(class2test) + "_signdata"
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()

        # 在数据库中检索该班级的表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql, signUpSheetName)

        # 存在该班级的签到表单
        if (rows):
            pass
        # 新建该班级的签到表单
        else:
            sql = 'create table `mytest`.`%s` ' % signUpSheetName + ' ( `userId` char(255) NOT NULL,`userName` char(255) NULL,`lessonName` char(255) NULL,`classlocation` char(255) NULL,  `signDate` date NULL,  `signTime` time(0) NULL,  `signState` char(255) NULL DEFAULT NULL )'
            cursor.execute(sql)

        # 提交修改
        conn.commit()
        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()

    # 刷新应到人数数据
    def Should_Arriave(self):
        # 考勤班级编号
        class2test_tempor = self.class_lineedit.text()
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()
        # 查询该班级
        sql = 'select * from classtable where majorNumber = %s '
        rows = cursor.execute(sql, class2test_tempor)
        # 存在该班级词条
        # 存在该班级词条
        if (rows):
            sql = 'select classNumber from classtable where majorNumber = %s '
            cursor.execute(sql, class2test_tempor)
            # 获取存储的数据
            row = cursor.fetchone()
            # 带数字元组转字符串
            row2 = ' '.join(map(str,row))
            # lcd控件显示班级人数
            self.should_lineeidt.setText(row2)
        else:
            QMessageBox.about(self,'发生错误','未检索到该班级的信息')

        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()

    # 刷新已签到表格和已到的表单
    def Already_Arrive(self):
        # 考勤班级编号
        class2test_tempor = self.class_lineedit.text()
        # 考勤课程
        lesson2Signup_tempor = self.lesson_lineedit.text()
        # 获取当前的日期
        date = QDateTime.currentDateTime()
        # 正则表达式筛选“年-月-日”2022-03-14
        date_now = date.toString("yyyy-MM-dd")
        # 字符串转换未datetime对象2022-03-14 00:00:00
        date_now_datetime = datetime.datetime.strptime(date_now,'%Y-%m-%d')
        # 截取date部分2022-03-14
        date_now_date = date_now_datetime.date()

        # 签到成功状态位
        successSignState = '1'

        # 保存该班级签到数据的表单名
        signUpSheetName = str(class2test_tempor) + '_signdata'

        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()

        # 判断签到数据的有效性,"0"--->初始状态/"1"--->签到成功/"2"--->迟到/"3"--->请假
        # 数据库中检索该班级的签到数据表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql, signUpSheetName)

        # 存在该班级的签到表单
        if (rows):
            # 检索 “今日”内属于该“课程”的签到状态为“1”的数据记录
            sql = "select *from %s " %signUpSheetName + " where signState = %s " %successSignState + " and lessonName = %s and signDate = %s "
            cursor.execute(sql,(lesson2Signup_tempor,date_now_date))
            # 取出所有记录
            rows = cursor.fetchall()
            # 记录个数，确定含该“课程名称”的行数
            rowSum = cursor.rowcount

            # 判断是否需要刷新
            if (rowSum==0):
                # 没有记录,清空“已签到人员"表格
                self.signup_tableWIgdet.clearContents()
                # 释放游标
                cursor.close()
                # 关闭连接，释放数据库资源
                conn.close()
                # 还未有成功签到的记录,不用刷新表格，直接退出函数
                return
            else:
                pass

            # 用于设置表格的列数,列数为3--->"编号""姓名""签到时间"
            volSum = 3

            # list列表，保存--->成功签到人员-学号
            successSign_PersonId_list = []

            # lsit列表，保存--->成功签到人员-姓名
            successSign_PersonName_list = []

            # list列表,保存-->成功签到人员-签到时间
            successSign_PersonTime_list = []

            # 签到数据存入列表
            for i in range(rowSum):
                # 临时记录 用户id userId，不能直接存入list
                temp_data0 = str(rows[i][0])
                # 取学号后两位数字
                temp_data1 = temp_data0[-2:]
                # 临时记录 人员-姓名，不能直接存入list
                temp_data2 = rows[i][1]
                # 临时记录 人员-签到时间，不能直接存入list
                temp_data3 = rows[i][5]

                # 人员-id 存入PersonId_list列表
                successSign_PersonId_list.append(str(temp_data1))
                # 人员-姓名 存入PersonName_list列表
                successSign_PersonName_list.append(str(temp_data2))
                # 人员-签到时间 存入PersonTime_list列表
                successSign_PersonTime_list.append(str(temp_data3))

            # 释放游标
            cursor.close()
            # 关闭连接，释放数据库资源
            conn.close()

            # 数据插入二维数组
            # 3个一维列表组成矩阵，每个列表作为一个列向量
            form_3XN_Matrix = np.matrix([successSign_PersonId_list,successSign_PersonName_list,successSign_PersonTime_list])

            # 3XN矩阵置换为NX3矩阵[['14' '啊斌' '16:15:32']]
            form_NX3_Matrix = np.transpose(form_3XN_Matrix)
            # 矩阵转数组[['14' '啊斌' '16:15:32']
            #  ['15' '啊明' '17:27:18']]
            form_NX3_Array = np.array(form_NX3_Matrix)

            # 集合内元素的个数---->已到人数
            # 设置为元组为了防止重复名字{'啊明', '啊斌'}
            successSign_PersonName_set = set(successSign_PersonName_list)

            people_already_show_Num = len(successSign_PersonName_set)

            # 创建(row,vol)大小的表格
            self.signup_tableWIgdet.setRowCount(rowSum)
            # 学号，姓名，签到时间3列
            self.signup_tableWIgdet.setColumnCount(volSum)
            # 设置表头名称
            self.signup_tableWIgdet.setHorizontalHeaderLabels(['学号','姓名','签到时间'])
            # 将表格变为禁止编辑
            self.signup_tableWIgdet.setEditTriggers(QAbstractItemView.NoEditTriggers)
            # 设置表格整行选中
            self.signup_tableWIgdet.setSelectionBehavior(QAbstractItemView.SelectRows)
            # 使表宽度自适应
            self.signup_tableWIgdet.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # 使表高度自适应 setSectionResizeMode()，表示均匀拉直表头。
            self.signup_tableWIgdet.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # 设置排序方式 sortItems(列，排序方式--->升序排列）
            self.signup_tableWIgdet.sortItems(0,Qt.AscendingOrder)

            # 数据插入表格
            for i in range(rowSum):
                for j in range(volSum):
                    temp_data = form_NX3_Array[i][j] # 临时记录，不能直接插入表格
                    # 转换后可插入表格
                    data = QTableWidgetItem(str(temp_data))
                    self.signup_tableWIgdet.setItem(i,j,data)


            # Lcd:"已到人数"Lcd---->显示-->已到人数
            self.already_lineedit.setText(str(people_already_show_Num))

        else:
            QMessageBox.warning(self,'报错','未找到该班级签到数据的存储表单!')
            # 退出函数
            return

    # 刷新"迟到请假人员”表格
    def LateAndFree(self):
        # 考勤班级编号
        class2test_tempor = self.class_lineedit.text()
        # 考勤课程
        lesson2SignUp_tempor = self.lesson_lineedit.text()
        # 获取当前的日期,获取今天的时间
        date = QDateTime.currentDateTime()
        # 正则表达式筛选"年-月-日"
        date_now = date.toString("yyyy-MM-dd")
        # 字符串转换为datetime对象
        date_now_datetime = datetime.datetime.strptime(date_now, '%Y-%m-%d')
        # 截取date部分
        date_now_date = date_now_datetime.date()

        # 迟到状态位
        lateSignState = '2'
        # 请假状态位
        freeSignState = '3'

        # 保存该班级签到数据的表单名
        signUpSheetName = str(class2test_tempor) + "_signdata"


        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()

        # 判断签到数据的有效性,"0"--->初始状态/"1"--->签到成功/"2"--->迟到/"3"--->请假
        # 数据库中检索该班级的签到数据表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql, signUpSheetName)

        # 存在该班级的签到数据表单
        if (rows):
            # 检索 “今日” 内属于该“课程”状态为‘2’的数据记录
            sql = "select * from %s " % signUpSheetName + " where (signState = %s " % lateSignState + " or  signState = %s " % freeSignState + " )and lessonName = %s  and signDate = %s"
            cursor.execute(sql, (lesson2SignUp_tempor, date_now_date))

            # 提出所有记录
            rows = cursor.fetchall()

            # 判断是否需要刷新
            if (rows == 0):
                # 没有记录，清空“迟到请假人员"表格
                self.lateOrfree_tableWidget.clearContents()
                # 还没有成功签到的记录，不用刷新表格，直接退出
                cursor.close()
                conn.close()
                return
            else:
                pass

            # 记录个数，确定含该”课程名称"的行数
            rowSum = cursor.rowcount

            # 用于设置表格的列数,列数为3--->"状态""编号""姓名""签到时间"
            volSum = 4

            # list列表,保存-->迟到请假人员-id
            LTSign_PersonId_list = []
            # list列表,保存-->迟到请假人员-签到时间
            LTSign_PersonName_list = []
            # list列表,保存-->迟到请假人员-签到时间
            LTSign_PersonTime_list = []
            # list列表,保存-->迟到请假人员-'数字'签到状态
            LTSign_PersonState_list_num = []

            # 签到数据存入列表
            for i in range(rowSum):
                # 临时记录 用户id userId，不能直接存入list
                temp_data0 = str(rows[i][0])
                # 取学号后2位数字
                temp_data1 = temp_data0[-2:]
                # 临时记录 人员-姓名，不能直接存入list
                temp_data2 = rows[i][1]
                # 临时记录 人员-签到时间，不能直接存入list
                temp_data3 = rows[i][5]
                # 临时记录 人员-签到状态，不能直接存入list
                temp_data4 = rows[i][6]

                # 人员-id 存入PersonId_list列表
                LTSign_PersonId_list.append(str(temp_data1))
                # 人员-姓名 存入PersonName_list列表
                LTSign_PersonName_list.append(str(temp_data2))
                # 人员-签到时间 存入PersonTime_list列表
                LTSign_PersonTime_list.append(str(temp_data3))
                # 人员-签到状态 存入PersonTime_list列表
                LTSign_PersonState_list_num.append(str(temp_data4))

            # 签到状态译码
            LTSign_PersonState_orign = ['2','3']
            LTSign_PersonState_translate = ['迟到','请假']
            # list列表,保存-->迟到请假人员-'中文'签到状态
            LTSign_PersonState_list_Ch = []

            # 签到状态 数字-->中文
            for i in range(rowSum):
                LTSign_PersonState_list_Ch.append(LTSign_PersonState_translate[LTSign_PersonState_orign.index(LTSign_PersonState_list_num[i])])

            # 释放游标
            cursor.close()
            # 关闭连接，释放数据库资源
            conn.close()

            # 数据插入二维数组
            # 4个一维列表组成矩阵，每个列表作为一个列向量
            form_4XN_Matrix = np.matrix(
                [LTSign_PersonState_list_Ch,LTSign_PersonId_list,LTSign_PersonName_list,LTSign_PersonTime_list]
            )
            # 4XN矩阵置换为NX4矩阵
            form_NX4_Matrix = np.transpose(form_4XN_Matrix)
            # 矩阵转数组
            form_NX4_Array = np.array(form_NX4_Matrix)

            # 集合内元素的个数------> 已到人数
            LTSign_PersonName_set = set(LTSign_PersonName_list)
            people_free_show_Num = len(LTSign_PersonName_set)

            # 创建(row,vol)大小的表格
            self.lateOrfree_tableWidget.setRowCount(rowSum)
            self.lateOrfree_tableWidget.setColumnCount(volSum)

            # 设置表头名称
            self.lateOrfree_tableWidget.setHorizontalHeaderLabels(['状态','学号','姓名','签到时间'])

            # 将表格变为禁止编辑
            self.lateOrfree_tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

            # 设置表格整行选中
            self.lateOrfree_tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

            # 使表宽度自适应
            self.lateOrfree_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            # 使表高度自适应
            self.lateOrfree_tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            # 设置排序方式 sortItems(列， 排序方式)
            self.lateOrfree_tableWidget.sortItems(0, Qt.AscendingOrder)

            # 数据插入表格
            for i in range(rowSum):
                for j in range(volSum):
                    temp_data = form_NX4_Array[i][j]
                    # 将数据转变成可以显示的数据格式
                    data = QTableWidgetItem(str(temp_data))
                    self.lateOrfree_tableWidget.setItem(i,j,data)

            # Lcd:"已到人数"Lcd---->显示-->迟到请假人数
            self.freeOrLate_lineedit.setText(str(people_free_show_Num))
        else:
            QMessageBox.warning(self,"报错","未找到该班级签到数据的存储表单!")
            # 退出函数
            return

    # 用户签到状态校验----》判断用户签到的有效性
    def checkSignState(self):
        # 获取该班级的签到属性
        # 考勤班级编号
        class2test_tempor = self.class_lineedit.text()
        # 考勤课程
        lesson2SignUp_tempor = self.lesson_lineedit.text()
        # 获取当天的日期
        date = QDateTime.currentDateTime()
        # 正则表达式筛选"年-月-日"
        date_now = date.toString("yyyy-MM-dd")
        # 字符串转换位datetime对象
        date_now_datetime = datetime.datetime.strptime(date_now, '%Y-%m-%d')
        # 截取date部分
        date_now_date = date_now_datetime.date()

        # 保存该班级签到数据的表单名
        signUpSheetName = str(class2test_tempor) + '_signdata'

        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()

        # 查询lessontable,检索该班级课表,"班级编号""课程名称"---->获取上下课时间
        # 检索lessontable中该班级此课程的词条记录
        sql = 'select * from lessontable where toClass = %s' % class2test_tempor + ' and lessonName = %s'
        rows = cursor.execute(sql,lesson2SignUp_tempor)
        # 存在该班级课程计划---->获取上下课时间
        if (rows):
            # 查询上课时间
            sql = 'select lessonBegin from lessontable where toClass = %s ' % class2test_tempor + ' and lessonName = %s'
            cursor.execute(sql,lesson2SignUp_tempor)
            # 获取存储的数据
            row1 = cursor.fetchone()
            # 带数字元组转字符串0:00:00
            lessonBegin_time = ' '.join(map(str, row1))
            # 字符串转换为time对象
            lessonBegin_time_datetime = datetime.datetime.strptime(lessonBegin_time,'%H:%M:%S')

            # 查询下课时间
            sql = 'select lessonEnd from lessontable where toClass = %s ' % class2test_tempor + ' and lessonName = %s '
            cursor.execute(sql,lesson2SignUp_tempor)
            # 获取存储的数据('2:00:00',)
            row2 = cursor.fetchone()
            # 带数字元组转字符串2:00:00
            lessonEnd_time = ' '.join(map(str, row2))
            # 字符串转换为time对象 转换未时分秒的time对象
            lessonEnd_time_datetime = datetime.datetime.strptime(lessonEnd_time, '%H:%M:%S')

        # 报错------>数据库中该班级没有此课程计划
        else:
            QMessageBox.warning(self,'发生错误','未检索到该班级课程的词条记录!')
            # 退出这个函数
            return

        # 获取签到的开始时间、签到结束时间
        # 查询数据库classtable,检索该班级课表,"班级编号"---->获取签到开始时间、签到结束时间
        # 检索数据库classtable表单中该班级的词条记录
        sql = 'select *from classtable where majorNumber = %s'
        rows = cursor.execute(sql,class2test_tempor)
        # 如果存在
        if (rows):
            # 查询签到开始时间
            sql = 'select signStart  from classtable where majorNumber = %s'
            cursor.execute(sql,class2test_tempor)
            # 获取存储的数据
            row_1 = cursor.fetchone()
            # 带数字元组转字符串,中文
            signStart_time = ' '.join(map(str, row_1))
            # 签到开始时间译码
            signStart_orginal = ['前20分钟','前15分钟','前10分钟','前5分钟']
            signStart_translate = ['20', '15', '10','5']

            # 查询签到结束时间
            sql = 'select signEnd from classtable where majorNumber = %s'
            cursor.execute(sql,class2test_tempor)
            # 获取存储的数据
            row_2 = cursor.fetchone()
            # 带数字元组转字符串，中文
            signEnd_time = ' '.join(map(str, row_2))
            # 签到结束时间译码
            signEnd_orginal = ['前5分钟', '前0分钟']
            signEnd_translate = ['5', '0']

            # 签到有效时间,datetime类 ,带默认年月日"1990.01.01"
            #1900-01-01-0:0:0 - 20minutes = 1899-12-31 23:40:00
            # 开课前20分钟签到 23:40:00
            signStart_val_datetime = lessonBegin_time_datetime - datetime.timedelta(minutes= int(signStart_translate[signStart_orginal.index(signStart_time)]))

            # 1900-01-01 01:55:00  = 2:0:0 - 5minutes
            # 下课前5分钟  01:55:00
            signEnd_val_datetime = lessonEnd_time_datetime - datetime.timedelta(minutes= int(signEnd_translate[signEnd_orginal.index(signEnd_time)]))

            # 签到有效时间,datetime类转time类 ,去除默认的年月日
            # 23:40:00
            signStart_val_time = signStart_val_datetime.time()
            # 01:55:00
            signEnd_val_time = signEnd_val_datetime.time()
        else:
            QMessageBox.warning(self,"发生错误","未检索到该班级的词条!")
            return

        # 判断签到数据的有效性,"0"--->初始状态/"1"--->签到成功/"2"--->迟到/"3"--->请假
        # 数据库中检索该班级的签到数据表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql,signUpSheetName)
        # 存在该班级的签到数据表单
        if (rows):
            # 查找当天的含该课程名称的词条
            sql = 'select * from %s ' %signUpSheetName +' where lessonName = %s and signDate = %s '
            cursor.execute(sql,(lesson2SignUp_tempor,date_now_date))

            # 取出所有记录
            rows = cursor.fetchall()

            # 记录个数，确定含该“课程名称”的行数
            rowSum = cursor.rowcount

            # 暂存签到时间的list列表
            signTime_list = []

            # 暂存签到状态的list列表,状态为"3"请假状态的数据不参与校验过程
            signTimeState_done_list = []

            # 输出签到状态的list列表
            signTimeState_list = []

            # 签到数据存入列表
            for i in range(rowSum):
                # 临时记录签到时间，不能直接存入list    signTime
                temp_data1 = rows[i][5]
                # 临时记录原有签到状态，不能直接存入list    signState
                temp_data2 = rows[i][6]
                # 签到时间存入signTime_list列表
                signTime_list.append(str(temp_data1))
                # 已有签到时间存入signTimeState_done_list列表
                signTimeState_done_list.append(str(temp_data2))

            # 实际签到开始时间：str(signStart_val_time)
            # 实际签到结束时间：str(signEnd_val_time)
            # 判断签到时间对应的签到状态 ，"0"--->初始状态/"1"--->签到成功/"2"--->迟到/"3"--->请假
            for i in range(rowSum):
                # 签到数据 转为 time类对象
                string2time = datetime.datetime.strptime(signTime_list[i], '%H:%M:%S').time()
                state2string = signTimeState_done_list[i]

                # 用time类对象进行比较

                # 还没到考勤时间 且 考勤状态不是请假
                if ( (string2time< signStart_val_time) and (state2string != '3') ):
                    # 保存初始状态为0,为无效签到信息
                    signTimeState_list.append('0')
                # 实际签到开始时间<=签到数据<=实际签到结束时间
                # 在考勤的开始时间和结束时间范围内
                elif ( (string2time >= signStart_val_time)  and (string2time <= signEnd_val_time ) and (state2string != '3')):
                    # 保存状态为1,为成功签到信息
                    signTimeState_list.append('1')
                # 签到数据>实际签到结束时间
                elif ( (string2time > signEnd_val_time) and (state2string != '3') ):
                    # 保存状态为2,为上课迟到信息
                    signTimeState_list.append('2')
                elif ( state2string == '3' ):
                    signTimeState_list.append('3')
                else:
                    # 错误状态，退出函数
                    return


            # 更新签到表单签到状态位
            for i in range(rowSum):
                sql = 'update `%s`' %signUpSheetName + ' set signState = %s ' %signTimeState_list[i] + 'where lessonName = %s and signTime = %s'
                cursor.execute(sql,(lesson2SignUp_tempor,signTime_list[i]))
                # 提交修改
                conn.commit()
        else:
            QMessageBox.warning(self,'报错','未找到该班级签到数据存储表单!')
            # 退出函数
            return

        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()


    ###########################classtable班级管理

    # 显示班级管理表单
    def table2show(self):
        # 创建模态对话框
        table2show_dialog = QDialog()
        # 设置对话框名称
        table2show_dialog.setWindowTitle("班级管理表单")
        # 设置窗体的图标
        table2show_dialog.setWindowIcon(QIcon("./gui_img/lin2.png"))
        # 垂直布局
        v_layout = QVBoxLayout(table2show_dialog)
        # 实例化班级管理表单
        table2show = classData2Show()
        # 班级管理表单加入垂直布局
        v_layout.addWidget(table2show)
        # 模态窗口关闭返回主窗口
        table2show_dialog.exec_()


    # 班级管理---保存设置                   (新建班级 或者  修改班级信息)
    def saveClassSettings(self):

        # 暂存表单信息
        majorNumber_tempor = self.majorNumber.text()
        className_tempor = self.className.text()
        classNumber_tempor = self.classNumber.text()
        signStart_tempor = self.signStart.currentText()
        signEnd_tempor = self.signEnd.currentText()


        # 检测数据库是否有classtable表单
        self.classtableInit()

        # 新建班级时候要顺便新建该班级的签到表单*********_signdata
        # 判断班级签到表单是否存在，不存在则建立(为了第一次登录做准备)
        self.classSignUpSheetInit()


        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor=conn.cursor()

        # 检索数据库classtable表--是否有该班级词条
        sql = 'select *from classtable where majorNumber = %s'
        rows = cursor.execute(sql,majorNumber_tempor)

        # 如果存在
        if rows:
            # 删除已有数据记录
            sql_delete = 'delete from classtable where majorNumber = %s'
            cursor.execute(sql_delete,majorNumber_tempor)
            # 插入数据记录
            sql_insert = 'insert into classtable(majorNumber,className,classNumber,signStart,signEnd) values(%s,%s,%s,%s,%s)'
            cursor.execute(sql_insert,(majorNumber_tempor,className_tempor,classNumber_tempor,signStart_tempor,signEnd_tempor))
        else:
            # 插入数据记录
            sql_insert = 'insert into classtable(majorNumber,className,classNumber,signStart,signEnd) values(%s,%s,%s,%s,%s)'
            cursor.execute(sql_insert,(majorNumber_tempor,className_tempor,classNumber_tempor,signStart_tempor,signEnd_tempor))

        # 提交修改
        conn.commit()
        # t弹出提示框
        QMessageBox.about(self,'提示','保存成功！')
        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()


    # 检测是否有classtable表单
    def classtableInit(self):
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 检索数据库是否存在classtable表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql,'classtable')
        # 如果存在
        if (rows):
            pass
        # 如果不存在，新建classtable
        else:
            sql = 'create table `mytest`.`classtable` ( `majorNumber` int(0) NOT NULL, `className` char(255) NOT NULL,`classNumber` int(0) not null,`signStart` char(255) not null,`signEnd` char(255) not null,PRIMARY KEY (`majorNumber`))'
            cursor.execute(sql)
        # 提交修改
        conn.commit()
        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()


    # 班级管理----输入属性初始化
    def classLineInit(self):
        # 班级编号输入8位纯数字
        majornum_val = QRegExpValidator(QRegExp("^[0-9]{10}$"))
        self.majorNumber.setValidator(majornum_val)
        # 框内提示文字
        self.majorNumber.setPlaceholderText("班级编号,10位纯数字输入")
        self.majorNumber.textChanged.connect(self.classTable_check_input)

        # 班级人数输入纯数字，上限3位数，首位输入非0
        classnum_val = QRegExpValidator(QRegExp("^[1-9][0-9]{2}$"))
        self.classNumber.setValidator(classnum_val)
        # 框内提示文字
        self.classNumber.setPlaceholderText('输入你的班级人数')
        self.classNumber.textChanged.connect(self.classTable_check_input)

        # 所带班级输入格式，中文输入+4位数字
        className_val = QRegExpValidator(QRegExp("^[\u4e00-\u9fa5][\u4e00-\u9fa5][0-9]{4}$"))
        self.className.setValidator(className_val)
        # 框内提示文字
        self.className.setPlaceholderText('如物联****')
        self.className.setToolTip('"输入格式：2位专业汉字简称+4位数字"')
        self.className.textChanged.connect(self.classTable_check_input)


    # 检查输入，输入不为空时，使能保存按钮
    def classTable_check_input(self):
        if (self.className.text() and self.majorNumber.text() and self.classNumber.text()):
            self.classSaveSettings.setEnabled(True)
        else:
            self.classSaveSettings.setEnabled(False)



    ###########################lessontable课表管理
    # 显示课表管理菜单
    def lesson2show(self):
        # 创建模态对话框
        lesson2show_dialog = QDialog()
        # 设置对话框名称
        lesson2show_dialog.setWindowTitle("课表管理菜单")
        # 设置窗体的图标
        lesson2show_dialog.setWindowIcon(QIcon("./gui_image/lin3.png"))
        # 垂直布局
        v_layout = QVBoxLayout(lesson2show_dialog)
        # 实例化课表管理菜单
        lesson2show = lessonData2Show()
        # 班级管理菜单加入垂直布局
        v_layout.addWidget(lesson2show)
        # 模态窗口关闭返回主窗口
        lesson2show_dialog.exec()


    # 课表管理----输入属性初始化
    def lessonLineInit(self):
        # 初始化，”熄灭“----保存按钮
        self.lessonTable_check_input()

        # 复选框改变时，检验按钮状态
        self.monday.stateChanged.connect(self.lessonTable_check_input)
        self.tuesday.stateChanged.connect(self.lessonTable_check_input)
        self.wednesday.stateChanged.connect(self.lessonTable_check_input)
        self.thursday.stateChanged.connect(self.lessonTable_check_input)
        self.friday.stateChanged.connect(self.lessonTable_check_input)
        self.saturday.stateChanged.connect(self.lessonTable_check_input)
        self.sunday.stateChanged.connect(self.lessonTable_check_input)

        # 课程名称输入框初始化
        # 课程名称，中文/英文/数字输入，上限12位
        lessonName_val = QRegExpValidator(QRegExp("^[0-9A-Za-z\u4e00-\u9fa5]{12}$"))
        self.lessonName.setValidator(lessonName_val)
        #框内提示文字
        self.lessonName.setPlaceholderText("课程全名!")
        self.lessonName.textChanged.connect(self.lessonTable_check_input)

        # 班级编号输入框初始化
        # 班级编号8位纯数字
        toClass_val = QRegExpValidator(QRegExp("^[0-9]{10}$"))
        self.toClass.setValidator(toClass_val)
        # 框内提示内容
        self.toClass.setPlaceholderText("10位班级编号!")
        self.toClass.textChanged.connect(self.lessonTable_check_input)

        # 设置日历控件允许弹出
        self.dateStart.setCalendarPopup(True)
        self.dateEnd.setCalendarPopup(True)

    # 课表管理--保存设置
    def saveLessonSettings(self):
        # 暂存表单信息
        lessonName_tempor = self.lessonName.text()      # 课程名称
        toClass_tempor = self.toClass.text()            # 班级编号
        dateStart_tempor =self.dateStart.date()         # 开课日期
        dateEnd_tempor = self.dateEnd.date()            # 结课日期
        lessonBegin_tempor = self.lessonBegin.time()    # 上课时间
        lessonEnd_tempor = self.lessonEnd.time()        # 下课时间

        # 正则表达式--转换日期、时间格式
        dateStart_tempor_final = dateStart_tempor.toString("yyyy-MM-dd")
        dateEnd_tempor_final = dateEnd_tempor.toString("yyyy-MM-dd")
        lessonBegin_tempor_final = lessonBegin_tempor.toString("hh:mm:ss")
        lessonEnd_tempor_final = lessonEnd_tempor.toString("hh:mm:ss")

        # 创建一个空列表
        lessonWeek = list()

        # 确定周几上课
        if (self.monday.isChecked()==True):              # 周一上课
            lessonWeek.append('1')
        if (self.tuesday.isChecked()==True):             # 周二上课
            lessonWeek.append('2')
        if (self.wednesday.isChecked()==True):           # 周三上课
            lessonWeek.append('3')
        if (self.thursday.isChecked()==True):            # 周四上课
            lessonWeek.append('4')
        if (self.friday.isChecked()==True):              # 周五上课
            lessonWeek.append('5')
        if (self.saturday.isChecked()==True):            # 周六上课
            lessonWeek.append('6')
        if (self.sunday.isChecked()==True):              # 周日上课
            lessonWeek.append('7')

        # list列表转字符串string
        lessonWeek_string = ','.join(lessonWeek)

        # 结课日期<<开课日期 ，弹出警告框
        if (dateStart_tempor_final >= dateEnd_tempor_final):
            QMessageBox.warning(self,"警告对话框","日期格式错误,请重新核对开课及结课日期!",QMessageBox.Yes,QMessageBox.Yes)
            # 退出函数
            return 0

        # 下课时间<<上课时间，弹出警告框
        if (lessonBegin_tempor_final >= lessonEnd_tempor_final):
            QMessageBox.warning(self,"警告框","时间格式错误，请重新核对上课及下课时间",QMessageBox.Yes,QMessageBox.Yes)
            # 退出函数
            return 0

        # 检查是否有lessontable表单
        self.lessontableInit()

        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 查询数据库是否已存在该“班级-课程”的词条
        sql = 'select *from lessontable where toClass = %s' %toClass_tempor + ' and lessonName = %s'
        rows = cursor.execute(sql,lessonName_tempor)

        # 如果有该班级的对应课程
        if rows != 0:
            QMessageBox.about(self,"提示",'该班级已有该课程的教学计划!')
            return
        else:
            # 插入数据记录
            sql_insert = 'insert into lessontable(toClass,lessonName,dateStart,dateEnd,lessonWeek,lessonBegin,lessonEnd) values(%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(sql_insert,(toClass_tempor,lessonName_tempor,dateStart_tempor_final,dateEnd_tempor_final,lessonWeek_string,lessonBegin_tempor_final,lessonEnd_tempor_final))

        # 提交修改
        conn.commit()
        # 弹出提示框
        QMessageBox.about(self,"提示","保存成功")
        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()


    # 检查是否有lessontable表单
    def lessontableInit(self):
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()
        # 检索数据库是否存在classtable表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql,'lessontable')
        # 如果存在
        if (rows):
            pass
        # 如果不存在，则新建lessontable
        else:
            sql = 'create table `mytest`.`lessontable`  (`toClass` int(0) NOT NULL,`lessonName` char(255) NOT NULL,`dateStart` date NULL, `dateEnd` date NULL,`lessonWeek` char(255) NULL,`lessonBegin` time(0) NULL, `lessonEnd` time(0) NULL, PRIMARY KEY (`toClass`, `lessonName`))'
            cursor.execute(sql)
        # 提交修改
        conn.commit()
        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()



    # 检查输入，输入不为空时，使能保存按钮
    def lessonTable_check_input(self):
        # 判断一周课表是否被点钟
        if (self.monday.isChecked()==True or self.tuesday.isChecked()==True or self.wednesday.isChecked()==True
        or self.thursday.isChecked()==True or self.friday.isChecked()==True or self.saturday.isChecked()==True
        or self.sunday.isChecked()==True):
            group_checked = True
        else:
            group_checked = False

        if (self.lessonName.text() and self.toClass.text() and group_checked):
            self.tableSaveSettings.setEnabled(True)
        else:
            self.tableSaveSettings.setEnabled(False)


    ##########################dataAnalysis统计分析

    # 数据分析----输入属性初始化
    def AnalysisLineInit(self):

        # 初始化，”熄灭“---保存按钮
        self.AnalysisTable_check_input()

        # 查询班级：纯数字输入，上限8位
        classNum2see_val = QRegExpValidator(QRegExp("^[0-9]{10}$"))
        self.classNum2see.setValidator(classNum2see_val)
        # 查询班级---》框内提示文字
        self.classNum2see.setPlaceholderText("请输入10位班级编号！")
        # 输入框改变时，校验按钮状态
        self.classNum2see.textChanged.connect(self.AnalysisTable_check_input)

        # 查询课程
        className2see_val = QRegExpValidator(QRegExp("^[0-9A-Za-z\u4e00-\u9fa5]{12}$"))
        self.className2see.setValidator(className2see_val)
        self.className2see.setPlaceholderText("请输入课程名称！")
        self.className2see.textChanged.connect(self.AnalysisTable_check_input)

        # 邮箱地址输入框初始化，邮箱地址输入合法性
        pat = r'^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$'
        excel2Email_val = QRegExpValidator(QRegExp(pat))
        self.excel2Email.setValidator(excel2Email_val)

        # 邮箱地址----》 框内提示文字
        self.excel2Email.setPlaceholderText("请输入邮箱地址！")
        self.excel2Email.textChanged.connect(self.AnalysisTable_check_input)

        # 设置日历控件允许弹出
        self.classDate2see.setCalendarPopup(True)


    # "查询“”刷新“按钮方法
    def find_freshData_Func(self):
        # 暂存待查询的班级编号
        classNum2see_tempor = self.classNum2see.text()
        # 暂存待查询的”查询日期“
        date2see_tempor = self.classDate2see.date()

        # 查询状态 初始未”0“ ----》 查询所有该班级字段
        mode2see = "0"

        dateOriginal_string = '2022-1-1'
        dateOriginal_date = datetime.datetime.strptime(dateOriginal_string,'%Y-%m-%d')

        # 判断显示状态
        if (date2see_tempor == dateOriginal_date and self.className2see.text()): # 课程填一个
            # 管理员设置”查询课程“ mode2see = "1"
            mode2see = "1"
            self.mode2see_1()
        elif (date2see_tempor != dateOriginal_date and self.className2see.text()): # 日期 课程
            mode2see = '2'
            self.mode2see_2()
        elif (date2see_tempor != dateOriginal_date and not(self.className2see.text())): # 日期填一个
            mode2see = "3"
            self.mode2see_3()
        else:
            self.mode2see_0()


    # "查询""刷新"--->mode2see = "0" --> 查询所有该班级字段
    def mode2see_0(self):
        # 暂存待查询的"班级编号"
        classNum2see_tempor = self.classNum2see.text()
        # 暂存待查询的"查询课程"
        className2see_tempor = self.className2see.text()
        # 暂存待查询的"查询日期"
        date2see_tempor = self.classDate2see.date()

        # 保存该班级签到数据的表单名
        signUpSheetName = str(classNum2see_tempor) + "_signdata"

        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 检索数据库是否存在signUpSheetName表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql,signUpSheetName)
        # 如果存在
        if(rows):
            pass
        # 如果不存在
        else:
            QMessageBox.about(self,'提示',"该班级的签到表单不存在！")
            return
        # 提交修改
        conn.commit()
        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()

        # 成功签到位
        successSignState = '1'
        # 迟到状态位
        lateSignState = '2'
        # 请假状态位
        freeSignState = '3'

        ##########################################签到记录表格
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->成功
        sql = "select * from %s " % signUpSheetName + "where (signState = %s) "
        cursor.execute(sql,successSignState )

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self,'提示','未检索到符合条件的"签到记录"！')

        else:
            pass


        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        Success_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        Success_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        Success_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        Success_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        Success_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        Success_Sign_Person_signTime_list = []

        # 取学号后2位
        temp_data1 = []
        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[-2:]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            Success_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            Success_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            Success_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            Success_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            Success_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            Success_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [Success_Sign_Person_userId_list, Success_Sign_Person_userName_list, Success_Sign_Person_LessonName_list, Success_Sign_Person_classlocation_list,Success_Sign_Person_signDate_list,Success_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.successSignData_Table.setRowCount(rowsum)
        self.successSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.successSignData_Table.setHorizontalHeaderLabels(['学号','姓名', '课程名称', '签到地点', '签到日期','签到时间'])

        # 将表格变为禁止编辑
        self.successSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.successSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.successSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.successSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.successSignData_Table.setItem(i, j,data)

        ##########################################迟到记录表格
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->迟到
        sql = "select * from %s " % signUpSheetName + "where (signState = %s) "
        cursor.execute(sql,lateSignState )

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self,'提示','未检索到符合条件的“迟到记录”！')
        else:
            pass


        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        late_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        late_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        late_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        late_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        late_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        late_Sign_Person_signTime_list = []

        # 取学号后2位
        temp_data1 = []
        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[-2:]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            late_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            late_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            late_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            late_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            late_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            late_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [late_Sign_Person_userId_list, late_Sign_Person_userName_list, late_Sign_Person_LessonName_list, late_Sign_Person_classlocation_list,late_Sign_Person_signDate_list,late_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.lateSignData_Table.setRowCount(rowsum)
        self.lateSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.lateSignData_Table.setHorizontalHeaderLabels(['学号','姓名', '课程名称', '签到地点', '签到日期','签到时间'])

        # 将表格变为禁止编辑
        self.lateSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.lateSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.lateSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.lateSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.lateSignData_Table.setItem(i, j,data)


        ##########################################迟到记录表格
       # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->请假
        sql = "select * from %s " % signUpSheetName + "where (signState = %s) "
        cursor.execute(sql,freeSignState )

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self,'提示','未检索到符合条件的“请假记录”！')

        else:
            pass

        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        free_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        free_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        free_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        free_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        free_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        free_Sign_Person_signTime_list = []

        # 取学号后2位
        temp_data1 = []
        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[8:10]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            free_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            free_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            free_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            free_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            free_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            free_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [free_Sign_Person_userId_list, free_Sign_Person_userName_list, free_Sign_Person_LessonName_list, free_Sign_Person_classlocation_list,free_Sign_Person_signDate_list,free_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.freeSignData_Table.setRowCount(rowsum)
        self.freeSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.freeSignData_Table.setHorizontalHeaderLabels(['学号','姓名', '课程名称', '签到地点', '签到日期','签到时间'])

        # 将表格变为禁止编辑
        self.freeSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.freeSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.freeSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.freeSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.freeSignData_Table.setItem(i, j,data)
    # "查询、刷新”----> mode2see = "1" --->设置了考勤课程
    def mode2see_1(self):
        # 暂存待查询的"班级编号"
        classNum2see_tempor = self.classNum2see.text()
        # 暂存待查询的"查询课程"
        className2see_tempor = self.className2see.text()
        # 暂存待查询的"查询日期"
        date2see_tempor = self.classDate2see.date()

        # 保存该班级签到数据的表单名
        signUpSheetName = str(classNum2see_tempor) + "_signdata"
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 检索数据库是否存在signUpSheetName表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql, signUpSheetName)
        # 如果存在
        if (rows):
            pass
        # 如果不存在
        else:
            QMessageBox.about(self, '提示', "该班级的签到表单不存在！")
            return
        # 提交修改
        conn.commit()
        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()

        # 成功签到位
        successSignState = '1'
        # 迟到状态位
        lateSignState = '2'
        # 请假状态位
        freeSignState = '3'

        ##########################################签到记录表格
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->成功
        sql = "select * from %s " % signUpSheetName + "where (signState = %s) and(lessonName = %s) "
        cursor.execute(sql, (successSignState, className2see_tempor))

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self, '提示', '没有人成功签到！')

        else:
            pass

        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        Success_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        Success_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        Success_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        Success_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        Success_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        Success_Sign_Person_signTime_list = []

        # 取学号后2位
        temp_data1 = []
        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[-2:]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            Success_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            Success_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            Success_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            Success_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            Success_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            Success_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [Success_Sign_Person_userId_list, Success_Sign_Person_userName_list,Success_Sign_Person_LessonName_list,Success_Sign_Person_classlocation_list,
             Success_Sign_Person_signDate_list, Success_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.successSignData_Table.setRowCount(rowsum)
        self.successSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.successSignData_Table.setHorizontalHeaderLabels(['学号', '姓名', '课程名称','签到地点', '签到日期', '签到时间'])

        # 将表格变为禁止编辑
        self.successSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.successSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.successSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.successSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.successSignData_Table.setItem(i, j, data)

        ##########################################迟到记录表格
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->迟到
        sql = "select * from %s " % signUpSheetName + "where (signState = %s) and(lessonName = %s) "
        cursor.execute(sql, (lateSignState, className2see_tempor))

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self, '提示', '没有迟到记录”！')

        else:
            pass

        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        late_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        late_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        late_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        late_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        late_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        late_Sign_Person_signTime_list = []

        # 取学号后2位
        temp_data1 = []
        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[8:10]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            late_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            late_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            late_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            late_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            late_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            late_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [late_Sign_Person_userId_list, late_Sign_Person_userName_list,late_Sign_Person_LessonName_list,late_Sign_Person_classlocation_list,
             late_Sign_Person_signDate_list, late_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.lateSignData_Table.setRowCount(rowsum)
        self.lateSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.lateSignData_Table.setHorizontalHeaderLabels(['学号', '姓名','课程名称','签到地点', '签到日期', '签到时间'])

        # 将表格变为禁止编辑
        self.lateSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.lateSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.lateSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.lateSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.lateSignData_Table.setItem(i, j, data)

        ##########################################迟到记录表格
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->请假
        sql = "select * from %s " % signUpSheetName + "where (signState = %s) and(lessonName = %s) "
        cursor.execute(sql, (freeSignState, className2see_tempor))

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self, '提示', '没有请假记录”！')
            return
        else:
            pass

        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        free_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        free_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        free_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        free_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        free_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        free_Sign_Person_signTime_list = []

        # 取学号后2位
        temp_data1 = []
        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[8:10]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            free_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            free_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            free_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            free_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            free_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            free_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [free_Sign_Person_userId_list, free_Sign_Person_userName_list, free_Sign_Person_LessonName_list,free_Sign_Person_classlocation_list,
             free_Sign_Person_signDate_list, free_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.freeSignData_Table.setRowCount(rowsum)
        self.freeSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.freeSignData_Table.setHorizontalHeaderLabels(['学号', '姓名', '课程名称', '签到地点', '签到日期','签到时间'])

        # 将表格变为禁止编辑
        self.freeSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.freeSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.freeSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.freeSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.freeSignData_Table.setItem(i, j, data)

    # "查询""刷新"--->mode2see = "2" --> 设置了考勤课程 考勤日期
    def mode2see_2(self):
        # 暂存待查询的"班级编号"
        classNum2see_tempor = self.classNum2see.text()
        # 暂存待查询的"查询课程"
        className2see_tempor = self.className2see.text()
        # 暂存待查询的"查询日期"
        date2see_tempor_1 = self.classDate2see.date()

        # 正则表达式筛选"年-月-日"
        date2see_tempor_2 = date2see_tempor_1.toString("yyyy-MM-dd")
        # 字符串转换为datetime对象
        date2see_tempor_3 = datetime.datetime.strptime(date2see_tempor_2, '%Y-%m-%d')
        # datetime对象 转 date类
        date2see_tempor = date2see_tempor_3.date()

        # 保存该班级签到数据的表单名
        signUpSheetName = str(classNum2see_tempor) + "_signdata"

        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 检查数据库是否存在signUpSheetName表单
        sql = "select * from information_schema.tables where table_name = %s"
        rows = cursor.execute(sql,signUpSheetName)

        # 如果存在
        if (rows):
            pass
        # 如果不存在
        else:
            QMessageBox.about(self,"提示","该班级的签到表单不存在！")
            return

        conn.commit()
        cursor.close()
        conn.close()

        # 成功签到位
        successSignState = '1'
        # 迟到状态位
        lateSignState = '2'
        # 请假状态位
        freeSignState = '3'

        ##########################################签到记录表格
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 获取班级信息表单内容 签到状态--->成功
        sql = "select * from %s " % signUpSheetName + " where signState = %s " % successSignState + "and lessonName = %s  and signDate = %s"
        cursor.execute(sql,(className2see_tempor,date2see_tempor))

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self,'提示','未检索到符合条件的“签到记录”！')

        else:
            pass


        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        Success_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        Success_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        Success_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        Success_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        Success_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        Success_Sign_Person_signTime_list = []

        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[-2:]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            Success_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            Success_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            Success_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            Success_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            Success_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            Success_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [Success_Sign_Person_userId_list, Success_Sign_Person_userName_list, Success_Sign_Person_LessonName_list,Success_Sign_Person_classlocation_list,Success_Sign_Person_signDate_list,Success_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.successSignData_Table.setRowCount(rowsum)
        self.successSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.successSignData_Table.setHorizontalHeaderLabels(['学号','姓名', '课程名称','签到地点', '签到日期', '签到时间'])

        # 将表格变为禁止编辑
        self.successSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.successSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.successSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.successSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.successSignData_Table.setItem(i, j,data)


        ##########################################迟到记录表格
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->迟到
        sql = "select * from %s " % signUpSheetName  + " where signState = %s " % lateSignState + "and lessonName = %s  and signDate = %s"
        cursor.execute(sql,(className2see_tempor,date2see_tempor) )
        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self,'提示','没有迟到记录！')

        else:
            pass

        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        late_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        late_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        late_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        late_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        late_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        late_Sign_Person_signTime_list = []

        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[8:10]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            late_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            late_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            late_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            late_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            late_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            late_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [late_Sign_Person_userId_list, late_Sign_Person_userName_list,late_Sign_Person_LessonName_list ,late_Sign_Person_classlocation_list,late_Sign_Person_signDate_list,late_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.lateSignData_Table.setRowCount(rowsum)
        self.lateSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.lateSignData_Table.setHorizontalHeaderLabels(['学号','姓名', '课程名称','签到地点', '签到日期', '签到时间'])

        # 将表格变为禁止编辑
        self.lateSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.lateSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.lateSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.lateSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.lateSignData_Table.setItem(i, j,data)




        ##########################################请假记录表格
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->请假
        sql = "select * from %s " % signUpSheetName + " where signState = %s " % freeSignState + "and lessonName = %s  and signDate = %s"
        cursor.execute(sql, (className2see_tempor, date2see_tempor))
        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount
        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self,'提示','没有请假记录！')

        else:
            pass
        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        free_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        free_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        free_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        free_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        free_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        free_Sign_Person_signTime_list = []

        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[8:10]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            free_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            free_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            free_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            free_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            free_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            free_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [free_Sign_Person_userId_list, free_Sign_Person_userName_list,free_Sign_Person_LessonName_list ,free_Sign_Person_classlocation_list,free_Sign_Person_signDate_list,free_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.freeSignData_Table.setRowCount(rowsum)
        self.freeSignData_Table.setColumnCount(vol)
        # 设置表头名称
        self.freeSignData_Table.setHorizontalHeaderLabels(['学号','姓名', '课程名称', '签到地点', '签到日期','签到时间'])

        # 将表格变为禁止编辑
        self.freeSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.freeSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.freeSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.freeSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.freeSignData_Table.setItem(i, j,data)

    # "查询""刷新"--->mode2see = "3" --> 设置了 考勤日期
    def mode2see_3(self):
        # 暂存待查询的"班级编号"
        classNum2see_tempor = self.classNum2see.text()
        # 暂存待查询的"查询课程"
        className2see_tempor = self.className2see.text()
        # 暂存待查询的"查询日期"
        date2see_tempor_1 = self.classDate2see.date()

        ### 分隔符 "/" --> "-" ###
        # 正则表达式筛选"年-月-日"
        date2see_tempor_2 = date2see_tempor_1.toString("yyyy-MM-dd")
        # 字符串转换为datetime对象
        date2see_tempor_3 = datetime.datetime.strptime(date2see_tempor_2, '%Y-%m-%d')
        # datetime对象 转 date类
        date2see_tempor = date2see_tempor_3.date()

        # 保存该班级签到数据的表单名
        signUpSheetName = str(classNum2see_tempor) + "_signdata"
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 检索数据库是否存在signUpSheetName表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql,signUpSheetName)
        # 如果存在
        if(rows):
            pass
        # 如果不存在
        else:
            QMessageBox.about(self,'提示',"该班级的签到表单不存在！")
            return
        # 提交修改
        conn.commit()
        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()

        # 成功签到位
        successSignState = '1'
        # 迟到状态位
        lateSignState = '2'
        # 请假状态位
        freeSignState = '3'

        ##########################################签到记录表格
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->成功
        sql = "select * from %s " % signUpSheetName + " where signState = %s " % successSignState + "and signDate = %s"
        cursor.execute(sql,date2see_tempor)

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self,'提示','未检索到符合条件的“签到记录”！')

        else:
            pass


        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        Success_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        Success_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        Success_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        Success_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        Success_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        Success_Sign_Person_signTime_list = []

        # 取学号后2位
        temp_data1 = []
        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[-2:]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            Success_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            Success_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            Success_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            Success_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            Success_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            Success_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [Success_Sign_Person_userId_list, Success_Sign_Person_userName_list, Success_Sign_Person_LessonName_list,Success_Sign_Person_classlocation_list,Success_Sign_Person_signDate_list,Success_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.successSignData_Table.setRowCount(rowsum)
        self.successSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.successSignData_Table.setHorizontalHeaderLabels(['学号','姓名', '课程名称','签到地点', '签到日期', '签到时间'])

        # 将表格变为禁止编辑
        self.successSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.successSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.successSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.successSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.successSignData_Table.setItem(i, j,data)

        ##########################################迟到记录表格
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->迟到
        sql = "select * from %s " % signUpSheetName  + " where signState = %s " % lateSignState + " and signDate = %s"
        cursor.execute(sql,date2see_tempor )

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self,'提示','没有迟到记录！')

        else:
            pass

        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        late_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        late_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        late_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        late_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        late_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        late_Sign_Person_signTime_list = []

        # 取学号后2位
        temp_data1 = []
        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[8:10]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            late_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            late_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            late_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            late_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            late_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            late_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [late_Sign_Person_userId_list, late_Sign_Person_userName_list, late_Sign_Person_LessonName_list,late_Sign_Person_classlocation_list,late_Sign_Person_signDate_list,late_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.lateSignData_Table.setRowCount(rowsum)
        self.lateSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.lateSignData_Table.setHorizontalHeaderLabels(['学号','姓名', '课程名称','签到地点', '签到日期', '签到时间'])

        # 将表格变为禁止编辑
        self.lateSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.lateSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.lateSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.lateSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.lateSignData_Table.setItem(i, j,data)


        ##########################################迟到记录表格
       # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 模式 0 --->写入相应MySQL语句
        # 获取班级信息表单内容 签到状态--->请假
        sql = "select * from %s " % signUpSheetName + " where signState = %s " % freeSignState + " and signDate = %s"
        cursor.execute(sql,date2see_tempor)

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            QMessageBox.about(self,'提示','没有“请假记录”！')

        else:
            pass


        # 设置表格的列数
        vol = 6

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->用户id userId
        free_Sign_Person_userId_list = []

        # list列表,保存-->用户姓名 userName
        free_Sign_Person_userName_list = []

        # list列表,保存-->课程名称 LessonName
        free_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        free_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        free_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        free_Sign_Person_signTime_list = []

        # 取学号后2位
        temp_data1 = []
        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 用户id userId，不能直接存入list
            temp_data0 = str(rows[i][0])
            # 取学号后2位数字
            temp_data1 = temp_data0[-2:]
            # 临时记录 用户姓名 userName，不能直接存入list
            temp_data2 = rows[i][1]
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data3 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data4 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data5 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data6 = rows[i][5]

            # 用户id userId 存入Success_Sign_Person_userId_list列表
            free_Sign_Person_userId_list.append(str(temp_data1))
            # 用户姓名 userName 存入Success_Sign_Person_userName_list列表
            free_Sign_Person_userName_list.append(str(temp_data2))
            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            free_Sign_Person_LessonName_list.append(str(temp_data3))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            free_Sign_Person_classlocation_list.append(str(temp_data4))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            free_Sign_Person_signDate_list.append(str(temp_data5))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            free_Sign_Person_signTime_list.append(str(temp_data6))

        # 数据插入二维数组
        # 6个一维列表 组成矩阵 每个列表作为一个列向量
        form_6XN_Matrix = np.matrix(
            [free_Sign_Person_userId_list, free_Sign_Person_userName_list, free_Sign_Person_LessonName_list,free_Sign_Person_classlocation_list,free_Sign_Person_signDate_list,free_Sign_Person_signTime_list])
        # 6XN矩阵 置换为 NX6矩阵
        form_NX6_Matrix = np.transpose(form_6XN_Matrix)
        # 矩阵转数组
        form_NX6_Array = np.array(form_NX6_Matrix)

        # 创建(row,vol)大小的表格
        self.freeSignData_Table.setRowCount(rowsum)
        self.freeSignData_Table.setColumnCount(vol)

        # 设置表头名称
        self.freeSignData_Table.setHorizontalHeaderLabels(['学号','姓名', '课程名称', '签到地点', '签到日期','签到时间'])

        # 将表格变为禁止编辑
        self.freeSignData_Table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.freeSignData_Table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.freeSignData_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.freeSignData_Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX6_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.freeSignData_Table.setItem(i, j,data)




    # 保存签到数据到Excel表格
    def save2Excel(self):
        # 暂存待查询的班级编号
        classNum2see_tempor = self.classNum2see.text()

        # 保存该班级签到数据的表单名
        signUpSheetName = str(classNum2see_tempor) + '_signdata'

        # 保存Excel位置
        save2path = './save2Excel/' + classNum2see_tempor + "_ClassSigndata" + '/' + signUpSheetName + '.xls'

        # 判断该文件路径是否存在,如果没有就创建
        if os.path.exists(save2path):
            pass
        else:
            os.mkdir('./save2Excel/' + classNum2see_tempor + "_ClassSigndata")


        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()
        # 检索数据库是否存在signUpSheetName表单
        sql = 'select * from information_schema.tables where table_name = %s '
        rows = cursor.execute(sql,signUpSheetName)
        # 如果存在
        if (rows):
            pass
        else:
            QMessageBox.about(self,"提示","该班级的签到表单不存在!")
            return

        conn.commit()
        cursor.close()
        conn.close()

        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()
        # 获取表格数据
        sql = 'select * from %s'%signUpSheetName
        count = cursor.execute(sql)

        # 重置游标的位置
        cursor.scroll(0, mode='absolute')

        # 搜取所有结果
        results = cursor.fetchall()

        # 获取MYSQL里面的数据字段名称
        fields = cursor.description

        # 新建工作簿
        workbook = xlwt.Workbook()

        # 置参数cell_overwrite_ok=True, 可以覆盖原单元格中数据。
        sheet = workbook.add_sheet(signUpSheetName, cell_overwrite_ok=True)

        # 写上字段信息
        for field in range(0, len(fields)):
            sheet.write(0, field, fields[field][0])

        # 获取并写入数据段信息
        row = 1
        col = 0
        for row in range(1, len(results) + 1):
            for col in range(0, len(fields)):
                sheet.write(row, col, u'%s' % results[row - 1][col])

        #保存至Excel文件夹下
        workbook.save(save2path)

        # 弹出提示框
        QMessageBox.about(self,'提示',"导出成功！")

    # 发送至邮箱
    def send2email_Func(self):
        # 压缩'./savw2Excel'文件夹，并保存在同级目录下，命名为ExcelData
        self.fileSaveZip2Path()

        zipFilePath = os.path.join(sys.path[0], "ExcelData.zip")
        # zip文件所在的绝对路径。sys.path[0]获取的是脚本所在绝对目录。

        # 保存授权码的txt文件
        txtpath = './autoLoginFile/QMailSMTP.txt'

        # 保存授权码的pkl文件
        picklepath = './autoLoginFile/QMailSMTP.pkl'

        # 检测一个文件夹是否存在
        folder = os.path.exists(txtpath)
        # 列表infFromTxt
        infFromTxt = []
        # txtpath不存在则滤过
        if not folder:
            pass
        # 存在则保存其中信息
        else:
            # 导入txt文件
            with open('autoLoginFile/QMailSMTP.txt', 'r') as f:
                for line in f.readlines():
                    # 去掉列表中的每一个元素的换行符
                    infFromTxt_tempor = line.strip('\n')
                    infFromTxt.append(infFromTxt_tempor)


            # 保存用户账号，二进制格式
            with open('autoLoginFile/QMailSMTP.pkl', 'wb') as f:
                pickle.dump(infFromTxt,f)

        # 检索本地是否保存授权码的pkl文件
        if (os.path.exists(picklepath)):
            # 导入pkl文件信息
            with open('autoLoginFile/QMailSMTP.pkl', 'rb') as f:
                infFromPkl = pickle.load(f)

        else:
            # 不存在授权码的pkl文件
            QMessageBox(self,'提示','你未添加开启了STMP服务的邮箱账号和授权码!')
            # 退出函数
            return

        to_mails = self.excel2Email.text()  # 收件人邮箱，添加多个收件人，中间用‘,'隔开

        from_mail = str(infFromPkl[0]) # 发件人邮箱
        mail_pass = str(infFromPkl[1]) # 授权码

        # 编写邮件内容，本内容用的是'plain',也可以使用'html'格式
        msg = MIMEText(
            """尊敬的管理员，你好：
            这是今日份的Excel报表!
            请查收！
        祝好。
                    啊斌先生"""
        ,"plain","utf-8")
        content_part = msg

        # 添加附件(zip文件)
        zipFile = zipFilePath # 需发文件路径
        zip = MIMEApplication(open(zipFile,'rb').read())
        zip.add_header('Content-Disposition','attachment',filename='SignupData.zip')  # 设置附件信息

        m = MIMEMultipart()
        m.attach(content_part) # 添加邮件正文内容
        m.attach(zip)   # 添加附件到邮件信息中

        m['Subject'] = '今日份Excel表单'     #邮件主题
        m['From'] = from_mail  # 发件人
        m['To'] = to_mails  # 收件人

        try:
            server = smtplib.SMTP('smtp.qq.com')
            # 登陆邮箱(参数1：发件人邮箱,参数2：邮箱授权码)
            server.login(from_mail,mail_pass)
            # 发送邮箱(参数1：发件人邮箱，参数2：若干收件人邮箱，参数3：把邮件内容格式改为str）
            server.sendmail(from_mail,to_mails.split(','),m.as_string())
            QMessageBox.about(self,"提示","发送成功!")
            server.quit()
        except smtplib.SMTPException as e:
            print('error:',e) #打印错误
            QMessageBox.about(self,"提示","发生错误")


    def fileSaveZip2Path(self):
        # sys.path[0]是D:\newPycharm\QT学习\
        #zipFilePath是D:\newPycharm\QT学习\ExcelData.zip
        # 保存的路径
        zipFilePath = os.path.join(sys.path[0],'ExcelData.zip')

        # 创建空的zip文件(ZipFile类型)。参数w表示写模式。zipfile.ZIP_DEFLATE表示需要压缩，文件会变小。ZIP_STORED是单纯的复制，文件大小没变。
        zipFile = zipfile.ZipFile(zipFilePath,"w",zipfile.ZIP_DEFLATED)

        absDir = os.path.join(sys.path[0],"save2Excel")
        # 要压缩的文件夹绝对路径。

        # 开始压缩。如果当前工作目录跟脚本所在目录一样，直接运行这个函数。
        # 执行这条压缩命令前，要保证当前工作目录是脚本所在目录(absDir的父级目录)。否则会报找不到文件的错误。
        self.writeAllFileToZip(absDir,zipFile)


    # 递归读取absDir文件夹中所有文件，并塞进zipFile文件中。参数absDir表示文件夹的绝对路径。
    def writeAllFileToZip(self,absDir,zipFile):
        for f in os.listdir(absDir):
            absFile = os.path.join(absDir,f)  # 子文件的绝对路径
            if os.path.isdir(absFile):      # 判断是文件夹，继续深度读取
                relFile = absFile[len(os.getcwd()) + 1:]  # 改成相对路径，否则解压zip是/User/xxx开头的文件。
                zipFile.write(relFile)   # 在zip文件中创建文件夹
                self.writeAllFileToZip(absFile,zipFile)
            else: # 判断是普通文件，直接写到zip文件中
                # 改成相对路径
                relFile = absFile[len(os.getcwd()) +1:]
                zipFile.write(relFile)
        return



    # 检查输入，输入不为空时，使能按钮
    def AnalysisTable_check_input(self):
        # 查询班级输入框，无输入，熄灭”查询“”刷新“按钮
        if (self.classNum2see.text()):
            self.findTheData.setEnabled(True)
            self.freshAdminTable.setEnabled(True)
            self.out2excel.setEnabled(True)
        else:
            self.findTheData.setEnabled(False)
            self.freshAdminTable.setEnabled(False)
            self.out2excel.setEnabled(False)

        # 查询邮箱地址输入框，无输入，熄灭查询和刷新按钮
        if (self.excel2Email.text()):
            self.send2email.setEnabled(True)
        else:
            self.send2email.setEnabled(False)


# 显示时间的lei
class Time(QThread):
    # 每隔一秒发送时间数据
    update_time = pyqtSignal(str)
    # 改写run函数
    def run(self) -> None:
        while True:
            data = QDateTime.currentDateTime()
            currentTime = data.toString("yyyy-MM-dd hh:mm:ss dddd")
            self.update_time.emit(str(currentTime))
            time.sleep(1)


# 显示----》 查看班级管理表单-窗口
class classData2Show(Ui_Table2show,QWidget):
    def __init__(self):
        super(classData2Show, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        # 页面基础属性设置
        self.classdata2show_windowNature()
        # 按钮功能初始化
        self.buttonEnale()
        # 刷新表格数据
        self.dataFresh()


    # 页面基础属性设置
    def classdata2show_windowNature(self):
        # 窗体名称
        self.setWindowTitle("智能考勤系统")
        # 设置所有窗体的图标
        self.setWindowIcon(QIcon("./gui_img/lin3.png"))
        # 设置提示框内容
        self.setToolTip('欢迎来到管理员页面')
        self.setFixedSize(800,450)



    # 检测输入设置，按钮初始化时调用
    def data2deleteTest(self):
        if (self.data2Delete.text()):
            self.button2Delete.setEnabled(True)
        else:
            self.button2Delete.setEnabled(False)



    # 按钮设置
    def buttonEnale(self):
        # 删除按钮初始状态
        self.data2deleteTest()
        # 未输入数据时，删除按钮不使能
        self.data2Delete.textChanged.connect(self.data2deleteTest)
        # 班级编号输入8位纯数字
        data2Delete_val = QRegExpValidator(QRegExp("^[0-9]{10}$"))
        self.data2Delete.setValidator(data2Delete_val)
        # 框内提示文字
        self.data2Delete.setPlaceholderText("请输入该班级编号")
        # 数据刷新显示
        self.Fresh.clicked.connect(self.dataFresh)
        # 删除某行数据
        self.button2Delete.clicked.connect(self.dataDelete)
        # 导出至Excel表格
        self.save2excel.clicked.connect(self.save2Excel)


    # 数据刷新显示
    def dataFresh(self):

        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()

        # 获取班级信息表单内容
        cursor.execute('select *from classtable')
        rows = cursor.fetchall()
        #print(rows[0])('13021701', '计科1701', '26', 'Id-Num', '前10分钟', '前0分钟')

        # 取得记录个数,用于设置表格的行数
        row = cursor.rowcount

        # 取得字段数，用于设置表格的列数
        vol = len(rows[0])

        # 释放游标
        cursor.close()
        # 关闭连接，释放数据库资源
        conn.close()

        # 创建（row，vol）大小的表格
        self.tableWidget.setRowCount(row)
        self.tableWidget.setColumnCount(vol)

        # 设置表头名称
        self.tableWidget.setHorizontalHeaderLabels(['班级编号', '班级名称', '班级人数','签到开始时间','签到结束时间'])

        # 将表格变为禁止编辑
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 使表宽度自适应
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 使表高度自适应
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)


        # 数据插入
        for i in range(row):
            for j in range(vol):
                temp_data = rows[i][j]
                # 转换格式
                data = QTableWidgetItem(str(temp_data))
                self.tableWidget.setItem(i,j,data)

    # 删除某行数据
    def dataDelete(self):
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 暂存待删除的数据
        data2Delete_tempor = self.data2Delete.text()

        # 查询数据库是否已存在该词条
        sql = 'select *from classtable where majorNumber = %s '
        rows = cursor.execute(sql,data2Delete_tempor)

        # 存在该班级数据
        if rows:
            # 删除已有记录
            sql_delete = 'delete from classtable where majorNumber = %s'
            cursor.execute(sql_delete,data2Delete_tempor)
            #提交修改
            conn.commit()
            #弹出提示框
            QMessageBox.about(self,"提示","删除成功")

            # 刷新表格
            self.dataFresh()

            # 关闭游标
            cursor.close()
            #释放数据库资源
            conn.close()
        else:
            QMessageBox.warning(self,"警告对话框","班级不存在,请重新核对班级编号")

    # 保存classtable数据到Excelbiaoge
    def save2Excel(self):

        # 保存位置
        save2path = './save2Excel/classtable.xls'


        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()
        # 获取表格数据 个数
        count = cursor.execute('select *from classtable')

        # 重置游标的位置
        cursor.scroll(0,mode='absolute')

        # 搜取所有结果
        results = cursor.fetchall()

        # 获取MYSql里面的数据字段名称
        fields = cursor.description

        # 新建工作簿
        workbook = xlwt.Workbook()

        # 置参数cell_overwrite_ok = True,可以覆盖原单元格中数据
        sheet = workbook.add_sheet('classtable',cell_overwrite_ok=True)

        # 写上字段信息
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])

        # 获取并写入数据段信息
        row = 1
        col = 0
        for row in range(1,len(results) + 1):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s' % results[row - 1][col])

        # 保存至Excel文件夹下
        workbook.save(save2path)

        # 弹出提示框
        QMessageBox.about(self,"提示","导出成功!")


# 显示----》 查看课表管理菜单--窗口
class lessonData2Show(Ui_Table2show,QWidget):
    def __init__(self):
        super(lessonData2Show, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        # 页面基础属性设置
        self.lessondata2show_windowNatrue()
        # 按钮功能初始化
        self.buttonEnable()
        # 刷新表格数据
        self.dataFresh()

    # 页面基础属性设置
    def lessondata2show_windowNatrue(self):
        # 窗体名称
        self.setWindowTitle("查看课表")
        # 设置窗体图标
        self.setWindowIcon(QIcon("./gui_image/lin3.png"))
        # 设置提示框内容
        self.setToolTip("欢迎来到课表管理菜单")
        self.setFixedSize(800,450)

    # 按钮设置
    def buttonEnable(self):
        # 删除按钮初始状态
        self.data2deleteTest()
        # 未输入数据时，删除按钮不使能
        self.data2Delete.textChanged.connect(self.data2deleteTest)
        # 班级编号+课程名称
        #data2Delete_val = QRegExpValidator(QRegExp("[0-9\u4e00-\u9fa5]{25}$"))
        #self.data2Delete.setValidator(data2Delete_val)
        # 框内提示文字
        self.data2Delete.setPlaceholderText("如:2018118211高等数学")
        # 数据刷新显示
        self.Fresh.clicked.connect(self.dataFresh)
        # 删除某行数据
        self.button2Delete.clicked.connect(self.dataDelete)
        # 导出至Excel表格
        self.save2excel.clicked.connect(self.save2Excel)


    # 检测输入设置，按钮初始化调用
    def data2deleteTest(self):
        if (self.data2Delete.text()):
            self.button2Delete.setEnabled(True)
        else:
            self.button2Delete.setEnabled(False)

    # 数据刷新显示
    def dataFresh(self):
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()

        # 获取班级信息表单内容
        cursor.execute('select * from lessontable')
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格行数
        row = cursor.rowcount

        # 取得字段数，用于设置表格的列数
        vol = len(rows[0])

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # 创建(row,vol)大小的表格
        self.tableWidget.setRowCount(row)
        self.tableWidget.setColumnCount(vol)

        # 设置表头名称
        self.tableWidget.setHorizontalHeaderLabels(['班级编号', '课程名称', '开课日期', '结课日期','星期','上课时间','下课时间'])
        # 将表格变为禁止编辑
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置表格整行选中
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 使表宽度自适应
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 使表高度自适应
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(row):
            for j in range(vol):
                temp_data = rows[i][j]
                data = QTableWidgetItem(str(temp_data))
                self.tableWidget.setItem(i,j,data)

    # 删除某行数据
    def dataDelete(self):
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )

        # 拿到游标
        cursor = conn.cursor()

        # 暂存待删除数据
        data2Delete_tempor = self.data2Delete.text()

        # 暂存班级编号
        data2Delete_classNum = data2Delete_tempor[0:10]

        # 暂存课程名称
        data2Delete_className = data2Delete_tempor[10:]

        # 查询数据库是否已存在该班级词条
        sql = 'select * from lessontable where toClass =%s ' %data2Delete_classNum + ' and lessonName = %s'
        try:
            rows = cursor.execute(sql,data2Delete_className)
        except:
            QMessageBox.about(self,"提示","输入格式错误")
            return

        # 存在该班级数据
        if rows:
            # 删除已有数据记录
            sql_delete = 'delete from lessontable where toClass = %s ' % data2Delete_classNum + ' and lessonName = %s'
            cursor.execute(sql_delete,data2Delete_className)

            # 提交修改
            conn.commit()

            #弹出提示框
            QMessageBox.about(self,"提示",'删除成功!')
            # 刷新数据
            self.dataFresh()
            # 关闭游标
            cursor.close()
            # 释放数据库资源
            conn.close()
        else:
            QMessageBox.warning(self,"警告对话框","输入错误，请重新核对输入信息!")

    # 保存lessontable数据到Excelbiaoge
    def save2Excel(self):
        # 保存Excel位置
        save2path = './save2Excel/Teacher_lessontable.xls'
        # 建立数据库连接
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='mytest',
            charset='utf8'
        )
        # 拿到游标
        cursor = conn.cursor()
        # 获取表格数据
        count = cursor.execute('select * from lessontable')
        # 重置游标的位置
        cursor.scroll(0, mode='absolute')
        # 搜取所有结果
        results = cursor.fetchall()
        # 获取MYSQL里面的数据字段名称
        fields = cursor.description
        # 新建工作簿
        workbook = xlwt.Workbook()

        # 置参数cell_overwrite_ok=True, 可以覆盖原单元格中数据。
        sheet = workbook.add_sheet('Teacher_lessontable', cell_overwrite_ok=True)

        # 写上字段信息
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])

        # 获取并写入数据段信息
        for row in range(1,len(results)+1 ):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s' % results[row - 1][col])



        # 保存至Excel文件夹下
        workbook.save(save2path)
        # 弹出提示框
        QMessageBox.about(self,'提示',"导出成功！")

if __name__ == '__main__':
    # 适应不同分辨率
    QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    # 传入python的命令行代码参数
    app = QApplication(sys.argv)
    # 显示管理员页面
    adminfirst = adminControl()
    # 界面结束时结束程序
    sys.exit(app.exec_())