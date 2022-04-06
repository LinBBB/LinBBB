# encoding:utf-8
import os
import sys
import pymysql
import xlwt
import cv2
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QRegExp
from PyQt5.QtGui import QFont, QIcon, QRegExpValidator,QPalette,QPixmap

from gui_ui.user import *


# user用户显示窗口
class userControl(Ui_UserZone,QWidget):
    def __init__(self,ID,IDtoClass):
        super(userControl, self).__init__()
        self.setupUi(self)


        # 传入学生的参数
        self.userId.setText(ID)
        self.classNum.setText(IDtoClass)
        self.userclassNum.setText(IDtoClass)

        self.initUI()

    def initUI(self):
        # 页面基础属性设置
        self.windowNature()

        # 设置背景图片
        self.Setting_Background()
        # 设置固定大小
        self.setFixedSize(800, 450)
        # 设置信号槽
        self.signalSetting()

        # 个人信息--->页面基本属性
        self.userPersonalInit()

        # 更新头像
        self.showUserImage()

        # 班级课表---》表格刷新
        self.userLessons_tableFresh()

        # 签到日志--->表格显示
        self.freshSignLog_auto()


    # 设置背景图片
    def Setting_Background(self):
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap("gui_image/Student.jpg")))
        self.setPalette(window_pale)


    # 页面基础属性设置
    def windowNature(self):
        # 窗体名称
        self.setWindowTitle("智能考勤系统")
        # 设置所有窗体的图标
        self.setWindowIcon(QIcon("gui_image/lin.png"))  # 设置当前窗体图标
        # 设置提示框内容
        self.setToolTip("大家好,欢迎来到学生端")


    # 信号槽连接
    def signalSetting(self):
        # 选项卡点击事件
        self.treeWidget.clicked.connect(self.onTreeClicked)
        # 个人信息页面---->更新面部数据按钮
        self.updateButton.clicked.connect(self.collectUserFaceData)
        # 个人信息页面----> 重置密码按钮
        self.saveChange.clicked.connect(self.userPasswordChange)
        # 个人信息页面---->“更换头像”按钮
        self.updateUserImage.clicked.connect(self.update2UserImage)
        # 个人信息页面---->“注销账号”按钮
        self.deleteMyself.clicked.connect(self.deleteUserAccount)
        # 班级课表页面---->“刷新”按钮
        self.freshLessons.clicked.connect(self.userLessons_tableFreshButton)
        # 班级课表页面---->“导出表格”按钮
        self.userLesson2Excel.clicked.connect(self.userLessons_save2ExcelButton)
        # 签到日志页面---->“刷新”按钮
        self.freshRecordButton.clicked.connect(self.freshSignLog_All)
        # 签到日志页面---->“导出表格”按钮
        self.userSignLog2Excel.clicked.connect(self.userSignLog_save2ExcelButton)


    # 个人信息页的基本设置
    def userPersonalInit(self):
        # 初始化重置密码框属性
        self.userPasswordInit()
        # 进入用户页面，个人信息页面--LCD初始化
        self.Lcd2show_userClassSum()
        # 显示姓名，性别
        self.showNameAndGenger()

        # 显示用户头像
        self.showUserImage()


    # 个人信息页LCD显示方法
    def Lcd2show_userClassSum(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
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
        rows = cursor.execute(sql, user_class)
        # 存在该班级词条
        if (rows):
            sql = 'select classNumber from classtable where majorNumber = %s '
            cursor.execute(sql, user_class)
            # 获取存储的密码
            row = cursor.fetchone()
            # 带数字元组转字符串
            row2 = ' '.join(map(str, row))
            self.classSum.setText(row2)
        else:
            QMessageBox.about(self, "发生错误", "未检索到该班级的信息！")

        # 关闭游标
        cursor.close()

        # 释放数据库资源
        conn.close()

    # 显示姓名和性别
    def showNameAndGenger(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
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

        # 查看是否存在该班级
        sql = 'select *from information_schema.tables where table_name=%s'
        rows = cursor.execute(sql, user_class)
        # 存在该班级词条
        if (rows):
            sql = 'select userName,gender from `%s`' % user_class  + ' where id_num = %s '
            cursor.execute(sql, user_Id)
            # 获取存储的密码
            row = cursor.fetchone()
            # 设置中文名
            self.userId_2.setText(row[0])
            self.userId_3.setText(row[1])

        else:
            QMessageBox.about(self, "发生错误", "未检索到该班级的信息！")

        # 关闭游标
        cursor.close()

        # 释放数据库资源
        conn.close()


    # 重置密码输入框基本属性初始化方法
    def userPasswordInit(self):
        # 重置密码提示
        # 框内文字
        self.passswordReset1.setPlaceholderText('请输入新的密码:')
        # 悬停提示
        #self.passswordReset1.setToolTip('首字母大写，6到10位数字字母。')
        # 框内文字
        self.passswordReset2.setPlaceholderText('请再次确认密码！')
        # 悬停提示
        self.passswordReset2.setToolTip('请再次确认密码！')
        # 初次加载页面时按钮无效化
        self.check_input()
        # 输入框1输入变化时检测状态
        self.passswordReset1.textChanged.connect(self.check_input)
        # 输入框1输入变化时检测状态
        self.passswordReset2.textChanged.connect(self.check_input)
        # 设置密码文本输入框校验器
        # password_val = QRegExpValidator(QRegExp("^[A-Z][0-9A-Za-z]{10}$"))
        # self.passswordReset1.setValidator(password_val)
        # self.passswordReset2.setValidator(password_val)
        # 设置重置密码框1输入时明文显示，控件焦点转移后掩码显示
        self.passswordReset1.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        #self.passswordReset2.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        # 设置重置密码框2以掩码显示
        self.passswordReset2.setEchoMode(QLineEdit.Password)


    # 检查文本输入框方法
    def check_input(self):
        # 当密码输入框1,2均有内容时，设置保存修改为可点击状态，或者不可点击。
        if self.passswordReset1.text() and self.passswordReset2.text():
            self.saveChange.setEnabled(True)
        else:
            self.saveChange.setEnabled(False)


    # 侧边栏选项卡点击事件
    def onTreeClicked(self):
        item = self.treeWidget.currentItem()
        # 获取当前序号
        index_top = self.treeWidget.indexOfTopLevelItem(item)
        # 根据节点序号直接调用page页面
        self.stackedWidget.setCurrentIndex(index_top)

    # 更新面部数据
    def collectUserFaceData(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 打开摄像头
        cam = cv2.VideoCapture(0+ cv2.CAP_DSHOW)
        # 设置图片大小
        cam.set(3, 640)
        cam.set(4, 480)
        # 调用CascadeClassifier分类器
        face_detector = cv2.CascadeClassifier('./haarcascades/haarcascade_frontalface_default.xml')

        # 人脸编号
        face_id = user_Id
        # 开始前操作提示
        QMessageBox.about(self,"提示","即将开始录入，请将正对摄像区域中央！")
        # 计数器
        count = 0

        while (True):
            # 摄像头获取视频流
            ret, img = cam.read()
            # 视频竖屏显示
            # img = cv2.flip(img, -1)
            # 图像灰度化
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 调用detectMultiScale()函数检测
            faces = face_detector.detectMultiScale(gray, 1.3, 5)
                # (image,scaleFactor,minNeighbors)
                    # image表示的是要检测的输入图像
                    # scaleFactor表示每次图像尺寸减小的比例
                    # minNeighbors表示每一个目标至少要被检测到3次才算是真的目标(因为周围的像素和不同的窗口大小都可以检测到人脸)
            # 摄像区域内有人脸的情况
            for (x, y, w, h) in faces:
                # 框出人脸
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                # 计数器加1
                count += 1
                # 保存图片的文件夹路径
                path = "./userImg2train/"  + str(user_class)
                # 检测一个文件夹是否存在
                folder = os.path.exists(path)
                # 不存在则新建该文件夹
                if not folder:
                    os.makedirs(path)
                # 图片保存至本地文件夹
                cv2.imwrite( path+"/" + str(face_id) + '_' + str(count) + ".jpg", gray[y:y + h, x:x + w])
                # 显示
                cv2.imshow('image', img)
            # 'ESC'键退出
            k = cv2.waitKey(20) & 0xff
            if k == 27:
                break
            elif count >= 100:  # 拍摄100张图片
                break

        # 在班级数据库中标注该用户面部数据已存入
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
        rows = cursor.execute(sql, user_class)
        # 找到该班级的表单
        if (rows):
            # 在该班级的表中检索该名用户的信息
            sql = 'select * from `%s`  ' % user_class + '  where id_num = %s'
            row = cursor.execute(sql, user_Id)
            checked = "是"
            # 找到该名用户的信息
            if (row):
                # 更新密码字段信息
                sql = 'update `%s`' % user_class + ' set checked = %s where id_num = %s'
                cursor.execute(sql, (checked, user_Id))
                QMessageBox.about(self,"提示","同学人脸信息已保存,checked")
                # 提交修改
                conn.commit()
                # 关闭游标
                cursor.close()
                # 释放数据库资源
                conn.close()
            else:
                QMessageBox.warning(self, '发生错误', '该用户不存在！')
        else:
            QMessageBox.warning(self, '发生错误', '该班级表单不存在！')
        # 解除摄像头占用
        cam.release()
        # 关闭OpenCV所有窗口
        cv2.destroyAllWindows()

        # 重新训练该班级的数据样本
        self.trainUserClassData()

    # 训练该班级的检测样本
    def trainUserClassData(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 面部数据所在路径
        path = './userImg2train' + '/' +user_class


        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier("./haarcascades/haarcascade_frontalface_default.xml")

        # 得到路径path下的所有文件，返回list列表形式
        allImg2List = os.listdir(path)
        # 倒着数第四位'.'为分界线,按照'.'左边的数字从小到大排序
        allImg2List.sort(key=lambda x: int(x[:-4]))
        # 拼接路径
        imagePaths = [os.path.join(path,f) for f in allImg2List]

        # 新建存放图片/id的空列表
        # 训练要用的两个参数
        faceSamples = []
        ids = []

        for imagePath in imagePaths:
            # PIL库convert函数L模式，对图片灰度值转化
            PIL_img = Image.open(imagePath).convert('L')
            # PIL image转 Numpy array 图片转数组
            img_numpy = np.array(PIL_img,'uint8')
            # 将图片的路径拆分并获取id
            id = int(os.path.split(imagePath)[-1].split("_")[0])
            faces = detector.detectMultiScale(img_numpy)
            # 将图片和id都添加到list列表中
            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)
        # 完成后提示
        QMessageBox.about(self,"提示","正在同步到检测样本！请稍等！")
        print("\n [INFO] 正在重新训练样本数据。请稍候...")
        # 训练样本
        recognizer.train(faceSamples,np.array(ids))
        # 训练样本模型保存路径
        model2path = './userTrainer2save/' + user_class + '/'
        # 检测是一个文件夹是否存在
        folder = os.path.exists(model2path)
        # 不存在则新建
        if not folder:
            os.makedirs(model2path)
        else:
            pass
        # 保存模型
        recognizer.write(model2path + user_class +  '_trainer.yml')
        # 打印样本中用户的数量
        print("\n [INFO] 样本该班级的学生数量: {0} 。".format(len(np.unique(ids))))
        # 完成后提示
        QMessageBox.about(self,"提示","同步检测样本成功!")

    # 重置密码
    def userPasswordChange(self):
        # 验证密码格式合法性
        self.check_password()
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 密码格式合法，密码框未被清空
        if (self.passswordReset1.text() and self.passswordReset2.text()):
            user_password2Save = self.passswordReset1.text()
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
            sql = 'select * from information_schema.tables where table_name = %s'
            rows = cursor.execute(sql,user_class)

            # 找到该班级的表单
            if (rows):
                # 在该班级的表中检索该名用户的信息
                sql = 'select * from `%s`' %user_class + ' where id_num = %s'
                row = cursor.execute(sql,user_Id)
                # 找到该名用户的信息
                if (row):
                    # 更新密码字段信息
                    sql = 'update `%s` ' %user_class + ' set password = %s where id_num =%s'
                    cursor.execute(sql,(user_password2Save,user_Id))
                    # 提交修改
                    conn.commit()
                    # 关闭游标
                    cursor.close()
                    # 释放数据库资源
                    conn.close()
                    # 提示信息
                    QMessageBox.about(self, "提示", "修改成功！")
                else:
                    QMessageBox.warning(self,"发生错误","该用户不存在！")
            else:
                QMessageBox.warning(self,'发生错误',"该班级表单不存在")

    # 跟新用户头像
    def update2UserImage(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 打开摄像头
        cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        # 设置图片大小
        cam.set(3,640)
        cam.set(4,480)
        # 调用CascadeClassifier分类器
        face_detector = cv2.CascadeClassifier('./haarcascades/haarcascade_frontalface_default.xml')
        # 人脸编号
        face_id = user_Id
        # 开始前提示
        QMessageBox.about(self,"提示",'即将开始录入,请将正对摄像区域中央!')
        # 保存头像的文件路径
        path = "./userHeadImg/" + str(user_class)
        # 退出整个while循环标志
        endFlag = 0
        while True:
            # 摄像头获取视频流
            ret,img = cam.read()
            # 调用detectMultiScale()分类器
            faces = face_detector.detectMultiScale(img,1.3,5)
            for (x,y,w,h) in faces:
                # 框出人脸
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),thickness=2)
                # 显示
                cv2.imshow('userImage',img)
                # 空格键退出,每帧停留时间20ms
                k = cv2.waitKey(20) & 0xff
                if k==32:   # 空格32,Esc27
                    # 检测所属班级头像文件夹是否存在
                    folder = os.path.exists(path)
                    # 不存在则新建文件夹，存在保存头像(覆盖旧头像)
                    if not folder:
                        QMessageBox.warning(self,"警告","还没有该班级的文件夹,点击确定创建")
                        os.mkdir(path)
                        QMessageBox.about(self,"提示","已创建，请重新录入!")
                        break
                    else:
                        # 图片保存至本地文件夹
                        cv2.imwrite(path + "/" + str(face_id) + ".jpg",img[y:y + h , x:x + w])
                    endFlag = 1 # 直接退出整个while循环
                    break # 退出当前for循环
                elif k==27:
                    break # 跳出当前for循环
            if endFlag:
                # 完成后提示
                QMessageBox.about(self,"提示","更新成功!")
                break

            # 无人脸时，正常显示视频流
            cv2.imshow('userImage',img)
            k = cv2.waitKey(20) & 0xff
            if (k == 27) or (k== 32) :  # 空格32,Esc27
                break

        # 解除摄像头占用
        cam.release()
        cv2.destroyAllWindows()
        # 更新头像
        self.showUserImage()


    # 检查输入密码合法性方法
    def check_password(self):
        password_1 = self.passswordReset1.text()
        password_2 = self.passswordReset2.text()
        # 密码位数检测
        if len(password_1) < 6:
            QMessageBox.warning(self,"警告","密码位数小于6")
            # 清空2次输入的密码
            self.passswordReset1.setText("")
            self.passswordReset2.setText("")
        else:
            # 检测两次密码结果是否相同
            if password_1 == password_2:
                pass
            else:
                QMessageBox.warning(self,"警告","两次密码输入结果不一致")
                self.passswordReset1.setText("")
                self.passswordReset2.setText("")

    # 显示用户头像
    def showUserImage(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 保存头像的文件路径
        path = './userHeadImg/' + str(user_class)
        # 存在头像则显示
        if os.path.exists(path + "/" + user_Id + '.jpg'):
            self.headImage.setAlignment((Qt.AlignCenter))
            self.headImage.setPixmap(QPixmap(path + "/" +user_Id +".jpg"))
        else:
            self.headImage.setPixmap(QPixmap("./gui_img/lin.png"))

    # 注销账号部分
    def deleteUserAccount(self):
        # 询问
        deleteUserAccount_result = QMessageBox.question(self,"不可恢复操作:","请再次确认是否注销此账号?",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if deleteUserAccount_result == QMessageBox.Yes:
            # 截取用户ID
            user_Id = self.userId.text()
            # 截取班级编号
            user_class = user_Id[0:10]
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
            rows = cursor.execute(sql, user_class)
            # 找到该班级的表单
            if (rows):
                # 在该班级的表中检索该名用户的信息
                sql = 'select * from `%s`  ' % user_class + '  where id_num = %s'
                row = cursor.execute(sql, user_Id)
                if (row):
                    # 删除已有数据记录
                    sql_delete = 'delete  from `%s`' % user_class + 'where id_num = %s'
                    cursor.execute(sql_delete, user_Id)
                    # 提交修改
                    conn.commit()
                    # 关闭游标
                    cursor.close()
                    # 释放数据库资源
                    conn.close()
                    # 提示信息
                    QMessageBox.about(self, "提示", "注销成功！")
                    # 关闭用户界面
                    self.close()
                else:
                    QMessageBox.warning(self,"发生错误","未找到该用户的表单")
            else:
                QMessageBox.warning(self,"发生错误","未找到该班级的表单!")
        else:
            # 忽略本次操作
            pass



    ###################班级课表
    # 班级课表---表格刷新按钮方法
    def userLessons_tableFreshButton(self):
        self.userLessons_tableFresh()
        # 刷新成功
        QMessageBox.about(self,"提示","刷新成功！")

    # 班级课表--刷新表格
    def userLessons_tableFresh(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
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
        sql = ' select * from lessontable where toClass = %s '
        cursor.execute(sql,user_class)

        # 保存所有信息
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        row = cursor.rowcount

        # 该班级不存在任何课程
        if row == 0:
            QMessageBox.about(self,"提示","该班级没有开设任何课程,请联系管理员老师增设课程")
            return
        else:
            pass


        # 取得字段数，用于设置表格的列数
        vol = len(rows[0])

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # 创建(row,vol）大小的表格
        self.tableWidget.setRowCount(row)
        self.tableWidget.setColumnCount(vol)

        # 设置表头名称
        self.tableWidget.setHorizontalHeaderLabels(['班级编号', '课程名称', '开课日期', '结课日期','一周课表','上课时间','下课时间'])

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
              temp_data = rows[i][j]  # 临时记录，不能直接插入表格
              data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
              self.tableWidget.setItem(i, j, data)

    # 班级课表--------》导出表格按钮方法
    def userLessons_save2ExcelButton(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]

        # 保存Excel位置
        save2path = './save2Excel/' + user_class +'_lessontable.xls'
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
        sql = ' select * from lessontable where toClass = %s '
        cursor.execute(sql, user_class)
        # 重置游标的位置
        cursor.scroll(0, mode='absolute')
        # 搜取所有结果
        results = cursor.fetchall()

        # 获取MYSQL里面的数据字段名称
        fields = cursor.description
        # 新建工作簿
        workbook = xlwt.Workbook()

        # 置参数cell_overwrite_ok=True, 可以覆盖原单元格中数据。
        sheet_name = user_class + '_lessontable'
        sheet = workbook.add_sheet(sheet_name, cell_overwrite_ok=True)

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
        # 提示刷新成功
        QMessageBox.about(self, "提示", "导出成功！")


    #################签到日志#####################

    # 签到日志页-------->刷新+提示框
    def freshSignLog_All(self):
        self.freshSignLog_auto()
        QMessageBox.about(self,"提示","刷新成功")

    # 自动刷新所有，页面初始化时
    def freshSignLog_auto(self):
        # 刷新签到记录
        self.freshSignRecord_table()
        # 刷新-迟到记录
        self.freshlateRecord_table()
        # 刷新请假记录
        self.freshfreeRecord_table()
        # 刷新-LCD显示
        self.freshCountSum()

    # 刷新出勤记录
    def freshSignRecord_table(self):

        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 保存该班级签到数据的表单名
        signUpSheetName = str(user_class) + "_signdata"


        # 判断班级签到表单是否存在，不存在则建立(为了第一次登录做准备)
        #self.classSignUpSheetInit()


        # 成功签到位
        successSignState = '1'

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

        # 获取班级信息表单内容 以"课程+日期+状态"来消除当天重复状态记录的影响
        sql = "select * from %s " % signUpSheetName + "where (userId = %s) and (signState = %s)"
        cursor.execute(sql,(user_Id,successSignState ))

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 没有，则退出
        if (rows == 0):
            # 释放游标
            cursor.close()
            # 关闭连接，释放数据库资源
            conn.close()
            return
        else:
            pass

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount
        # 设置表格的列数
        vol = 4

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()
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
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data1 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data2 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data3 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data4 = rows[i][5]

            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            Success_Sign_Person_LessonName_list.append(str(temp_data1))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            Success_Sign_Person_classlocation_list.append(str(temp_data2))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            Success_Sign_Person_signDate_list.append(str(temp_data3))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            Success_Sign_Person_signTime_list.append(str(temp_data4))

        # 数据插入二维数组
        # 4个一维列表 组成矩阵 每个列表作为一个列向量
        form_4XN_Matrix = np.matrix(
            [Success_Sign_Person_LessonName_list, Success_Sign_Person_classlocation_list, Success_Sign_Person_signDate_list, Success_Sign_Person_signTime_list])
        # 4XN矩阵 置换为 NX4矩阵
        form_NX4_Matrix = np.transpose(form_4XN_Matrix)
        # 矩阵转数组
        form_NX4_Array = np.array(form_NX4_Matrix)

        # 创建(row,vol)大小的表格
        self.signRecord.setRowCount(rowsum)
        self.signRecord.setColumnCount(vol)

        # 设置表头名称
        self.signRecord.setHorizontalHeaderLabels([ '课程名称', '签到地点', '签到日期', '签到时间'])

        # 将表格变为禁止编辑
        self.signRecord.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.signRecord.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.signRecord.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.signRecord.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX4_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.signRecord.setItem(i, j, data)

    # 签到日志页---->刷新-迟到记录
    def freshlateRecord_table(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 保存该班级签到数据的表单名
        signUpSheetName = str(user_class) + "_signdata"

        # 迟到状态位
        lateSignState = '2'

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

        # 获取班级信息表单内容 以"课程+日期+状态"来消除当天重复状态记录的影响
        sql = "select * from %s " % signUpSheetName + "where (userId = %s) and (signState = %s)"
        cursor.execute(sql,(user_Id,lateSignState ))

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 没有，则退出
        if (rows == 0):
            # 释放游标
            cursor.close()
            # 关闭连接，释放数据库资源
            conn.close()
            return
        else:
            pass

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 设置表格的列数
        vol = 4

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->课程名称 LessonName
        Late_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        Late_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        Late_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        Late_Sign_Person_signTime_list = []

        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data1 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data2 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data3 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data4 = rows[i][5]

            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            Late_Sign_Person_LessonName_list.append(str(temp_data1))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            Late_Sign_Person_classlocation_list.append(str(temp_data2))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            Late_Sign_Person_signDate_list.append(str(temp_data3))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            Late_Sign_Person_signTime_list.append(str(temp_data4))

        # 数据插入二维数组
        # 4个一维列表 组成矩阵 每个列表作为一个列向量
        form_4XN_Matrix = np.matrix(
            [Late_Sign_Person_LessonName_list, Late_Sign_Person_classlocation_list, Late_Sign_Person_signDate_list, Late_Sign_Person_signTime_list])
        # 4XN矩阵 置换为 NX4矩阵
        form_NX4_Matrix = np.transpose(form_4XN_Matrix)
        # 矩阵转数组
        form_NX4_Array = np.array(form_NX4_Matrix)

        # 创建(row,vol)大小的表格
        self.lateRecord.setRowCount(rowsum)
        self.lateRecord.setColumnCount(vol)

        # 设置表头名称
        self.lateRecord.setHorizontalHeaderLabels([ '课程名称', '签到地点', '签到日期', '签到时间'])

        # 将表格变为禁止编辑
        self.lateRecord.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.lateRecord.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.lateRecord.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.lateRecord.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX4_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.lateRecord.setItem(i, j, data)

    # 刷新请假记录
    def freshfreeRecord_table(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 保存该班级签到数据的表单名
        signUpSheetName = str(user_class) + "_signdata"

        # 请假状态位
        lateSignState = '3'

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

        # 获取班级信息表单内容 以"课程+日期+状态"来消除当天重复状态记录的影响
        sql = "select * from %s " % signUpSheetName + "where (userId = %s) and (signState = %s)"
        cursor.execute(sql,(user_Id,lateSignState ))

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 没有，则退出
        if (rows == 0):
            # 释放游标
            cursor.close()
            # 关闭连接，释放数据库资源
            conn.close()
            return
        else:
            pass

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 设置表格的列数
        vol = 4

        # 释放游标
        cursor.close()

        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->课程名称 LessonName
        Late_Sign_Person_LessonName_list = []

        # list列表,保存-->考勤地点 classlocation
        Late_Sign_Person_classlocation_list = []

        # list列表,保存-->签到日期 signDate
        Late_Sign_Person_signDate_list = []

        # list列表,保存-->签到时间 signTime
        Late_Sign_Person_signTime_list = []

        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 课程名称 LessonName，不能直接存入list
            temp_data1 = rows[i][2]
            # 临时记录 考勤地点 classlocation，不能直接存入list
            temp_data2 = rows[i][3]
            # 临时记录 签到日期 signDate，不能直接存入list
            temp_data3 = rows[i][4]
            # 临时记录 签到时间 signTime，不能直接存入list
            temp_data4 = rows[i][5]

            # 课程名称 LessonName 存入Success_Sign_Person_LessonName_list列表
            Late_Sign_Person_LessonName_list.append(str(temp_data1))
            # 考勤地点 classlocation 存入Success_Sign_Person_classlocation_list列表
            Late_Sign_Person_classlocation_list.append(str(temp_data2))
            # 签到日期 signDate 存入Success_Sign_Person_signDate_list列表
            Late_Sign_Person_signDate_list.append(str(temp_data3))
            # 签到时间 signTime 存入Success_Sign_Person_signTime_list列表
            Late_Sign_Person_signTime_list.append(str(temp_data4))

        # 数据插入二维数组
        # 4个一维列表 组成矩阵 每个列表作为一个列向量
        form_4XN_Matrix = np.matrix(
            [Late_Sign_Person_LessonName_list, Late_Sign_Person_classlocation_list, Late_Sign_Person_signDate_list, Late_Sign_Person_signTime_list])
        # 4XN矩阵 置换为 NX4矩阵
        form_NX4_Matrix = np.transpose(form_4XN_Matrix)
        # 矩阵转数组
        form_NX4_Array = np.array(form_NX4_Matrix)

        # 创建(row,vol)大小的表格
        self.lateRecord_2.setRowCount(rowsum)
        self.lateRecord_2.setColumnCount(vol)

        # 设置表头名称
        self.lateRecord_2.setHorizontalHeaderLabels([ '课程名称', '签到地点', '签到日期', '签到时间'])

        # 将表格变为禁止编辑
        self.lateRecord_2.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置表格整行选中
        self.lateRecord_2.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 使表宽度自适应
        self.lateRecord_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 使表高度自适应
        self.lateRecord_2.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 数据插入表格
        for i in range(rowsum):
            for j in range(vol):
                temp_data = form_NX4_Array[i][j]  # 临时记录，不能直接插入表格
                data = QTableWidgetItem(str(temp_data))  # 转换后可插入表格
                self.lateRecord_2.setItem(i, j, data)


    # 签到日志页---->刷新-LCD显示
    def freshCountSum(self):
        #######################################刷新-出勤次数
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 保存该班级签到数据的表单名
        signUpSheetName = str(user_class) + "_signdata"

        # 成功签到位
        successSignState = '1'
        # 迟到状态位
        lateSignState = '2'
        # 请假状态位
        freeSignState = '3'

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

        # 获取班级信息表单内容 以"课程+日期+状态"来消除当天重复状态记录的影响
        sql = "select * from %s " % signUpSheetName + "where (userId = %s) and (signState = %s)"
        cursor.execute(sql,(user_Id,successSignState ))

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            self.signCountSum.setText("0" + "次")

        else:
            pass

        # 释放游标
        cursor.close()
        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->课程名称字段-lessonName
        lessonName_tempor_list = []

        # list列表,保存-->签到日期-signDate
        signDate_tempor_list = []

        # list列表,保存-->课程名称+签到日期
        lessonName_signDate_tempor_list = []

        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 课程名称字段-lessonName，不能直接存入list
            temp_data1 = rows[i][2]
            # 临时记录 签到日志-signDate，不能直接存入list
            temp_data2 = rows[i][4]

            # 课程名称字段-lessonName 存入lessonName_tempor_list列表
            lessonName_tempor_list.append(str(temp_data1))
            # 签到日志-signDate 存入signDate_tempor_list列表
            signDate_tempor_list.append(str(temp_data2))

        # 拼接2个list表的字符串
        for i in range(rowsum):
            lessonName_signDate_tempor_list.append(lessonName_tempor_list[i] + signDate_tempor_list[i])

        # list ---> set
        lessonName_signDate_tempor_set = set(lessonName_signDate_tempor_list)

        # 集合内元素个数
        signCount_Sum = len(lessonName_signDate_tempor_set)

        # 刷新显示 "出勤次数"lcd
        #self.signCountSum.setStyleSheet("border: 2px solid black; color: black; ")
        self.signCountSum.setText(str(signCount_Sum) + "次")

        #######################################刷新-迟到次数
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

        # 获取班级信息表单内容 以"课程+日期+状态"来消除当天重复状态记录的影响
        sql = "select * from %s " % signUpSheetName + "where (userId = %s) and (signState = %s)"
        cursor.execute(sql,(user_Id,lateSignState ))

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            self.lateCountSum.setText("0" + "次")

        else:
            pass

        # 释放游标
        cursor.close()
        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->课程名称字段-lessonName
        lessonName_tempor_list = []

        # list列表,保存-->签到日期-signDate
        signDate_tempor_list = []

        # list列表,保存-->课程名称+签到日期
        lessonName_signDate_tempor_list = []

        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 课程名称字段-lessonName，不能直接存入list
            temp_data1 = rows[i][2]
            # 临时记录 签到日志-signDate，不能直接存入list
            temp_data2 = rows[i][4]

            # 课程名称字段-lessonName 存入lessonName_tempor_list列表
            lessonName_tempor_list.append(str(temp_data1))
            # 签到日志-signDate 存入signDate_tempor_list列表
            signDate_tempor_list.append(str(temp_data2))

        # 拼接2个list表的字符串
        for i in range(rowsum):
            lessonName_signDate_tempor_list.append(lessonName_tempor_list[i] + signDate_tempor_list[i])

        # list ---> set
        lessonName_signDate_tempor_set = set(lessonName_signDate_tempor_list)

        # 集合内元素个数
        lateCount_Sum = len(lessonName_signDate_tempor_set)

        # 刷新显示 "迟到次数"lcd
        #self.lateCountSum.setStyleSheet("border: 2px solid black; color: black; ")
        self.lateCountSum.setText(str(lateCount_Sum) + "次")

        #######################################刷新-请假次数
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

        # 获取班级信息表单内容 以"课程+日期+状态"来消除当天重复状态记录的影响
        sql = "select * from %s " % signUpSheetName + "where (userId = %s) and (signState = %s)"
        cursor.execute(sql,(user_Id,freeSignState ))

        # 获取所有符合条件的字段
        rows = cursor.fetchall()

        # 取得记录个数，用于设置表格的行数
        rowsum = cursor.rowcount

        # 没有，则退出
        if (rowsum == 0):

            self.freeCountSum.setText("0次")

        else:
            pass

        # 释放游标
        cursor.close()
        # 关闭连接，释放数据库资源
        conn.close()

        # list列表,保存-->课程名称字段-lessonName
        lessonName_tempor_list = []

        # list列表,保存-->签到日期-signDate
        signDate_tempor_list = []

        # list列表,保存-->课程名称+签到日期
        lessonName_signDate_tempor_list = []

        # 签到数据存入列表
        for i in range(rowsum):
            # 临时记录 课程名称字段-lessonName，不能直接存入list
            temp_data1 = rows[i][2]
            # 临时记录 签到日志-signDate，不能直接存入list
            temp_data2 = rows[i][4]

            # 课程名称字段-lessonName 存入lessonName_tempor_list列表
            lessonName_tempor_list.append(str(temp_data1))
            # 签到日志-signDate 存入signDate_tempor_list列表
            signDate_tempor_list.append(str(temp_data2))

        # 拼接2个list表的字符串
        for i in range(rowsum):
            lessonName_signDate_tempor_list.append(lessonName_tempor_list[i] + signDate_tempor_list[i])

        # list ---> set
        lessonName_signDate_tempor_set = set(lessonName_signDate_tempor_list)

        # 集合内元素个数
        freeCount_Sum = len(lessonName_signDate_tempor_set)

        # 刷新显示 "请假次数"lcd
        #self.freeCountSum.setStyleSheet("border: 2px solid black; color: black; ")
        self.freeCountSum.setText(str(freeCount_Sum) + "次")

        # 出勤次数 signCount_Sum
        # 迟到次数 lateCount_Sum
        # 请假次数 freeCount_Sum
        # 总次数 Count_Sum
        Count_Sum = signCount_Sum + lateCount_Sum + freeCount_Sum
        if Count_Sum == 0:
            QMessageBox.warning(self,"警告","你没有任何签到记录")
            return
        else:
            pass
        # 除 100%格式显示 显示前两位
        Percent = int((signCount_Sum/Count_Sum)*100)

        # 刷新显示 "出勤率"lcd
        self.signPercent.setStyleSheet("border: 2px solid black; color: black; ")
        self.signPercent.setText(str(Percent) + "%")

    # 签到日志页---->导出表格方法
    def userSignLog_save2ExcelButton(self):
        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 保存该班级签到数据的表单名
        signUpSheetName = str(user_class) + "_signdata"

        # 保存Excel位置
        save2path = './save2Excel/' + user_class + "_StudentSigndata"

        # 不存在该路径则创建
        if os.path.exists(save2path):
            pass
        else:
            os.makedirs(save2path)


        # 初始化状态位
        signStateInit ='0'

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

        # 获取签到信息表单内容
        sql = " select * from %s " % signUpSheetName + " where (userId = %s) and (signState != %s) "
        cursor.execute(sql, (user_Id,signStateInit))

        # 重置游标的位置
        cursor.scroll(0, mode='absolute')

        # 搜取所有结果
        results = cursor.fetchall()

        # 获取MYSQL里面的数据字段名称
        fields = cursor.description

        # 新建工作簿
        workbook = xlwt.Workbook()

        # 签到表格名称
        sheet_name = user_Id + '_signdata'

        # 置参数cell_overwrite_ok=True, 可以覆盖原单元格中数据。
        sheet = workbook.add_sheet(sheet_name, cell_overwrite_ok=True)

        # 写上字段信息
        for field in range(0, len(fields)):
            sheet.write(0, field, fields[field][0])

        # 获取并写入数据段信息
        row = 1
        col = 0
        for row in range(1, len(results) + 1):
            for col in range(0, len(fields)):
                sheet.write(row, col, u'%s' % results[row - 1][col])
        '''
        # 设置一个字典用于保存列宽数据
        dims = {}
        # 遍历表格数据，获取自适应列宽数据
        for row in sheet.rows:
            for cell in row:
                if cell.value:
                    # 遍历整个表格，把该列所有的单元格文本进行长度对比，找出最长的单元格
                    # 在对比单元格文本时需要将中文字符识别为1.7个长度，英文字符识别为1个，这里只需要将文本长度直接加上中文字符数量即可
                    # re.findall('([\u4e00-\u9fa5])', cell.value)能够识别大部分中文字符
                    cell_len = 0.7 * len(re.findall('([\u4e00-\u9fa5])', str(cell.value))) + len(str(cell.value))
                    dims[cell.column] = max((dims.get(cell.column, 0), cell_len))
        for col, value in dims.items():
            # 设置列宽，get_column_letter用于获取数字列号对应的字母列号，最后值+2是用来调整最终效果的
            sheet.column_dimensions[get_column_letter(col)].width = value + 2
        '''

        #保存至Excel文件夹下
        workbook.save(save2path + '/' +user_Id + "_signdata.xls")
        # 提示刷新成功
        QMessageBox.about(self, "提示", "导出成功！")


    # 检查是否存在该班级的签到数据表单
    def classSignUpSheetInit(self):

        # 获取用户ID
        user_Id = self.userId.text()
        # 截取班级编号
        user_class = user_Id[0:10]
        # 保存该班级签到数据的表单名
        signUpSheetName = str(user_class) + "_signdata"

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
            sql = 'create table `mytest`.`%s` ' % signUpSheetName + ' ( `userId` char(255) NOT NULL,`userName` char(255) NULL,`lessonName` char(255) NULL,`classlocation` char(255) NULL,  `signDate` date NULL,  `signTime` time(0) NULL,  `signState` char(255) NULL DEFAULT NULL, PRIMARY KEY (`userId`)   )'
            cursor.execute(sql)

        # 提交修改
        conn.commit()
        # 关闭游标
        cursor.close()
        # 释放数据库资源
        conn.close()


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    # 传入python的命令行代码参数
    app = QApplication(sys.argv)
    # 实例化用户界面
    user_first = userControl()
    user_first.show()
    sys.exit(app.exec_())
