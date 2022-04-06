from PyQt5.QtCore import QThread, QDateTime,QCoreApplication
from PyQt5.QtGui import QFocusEvent
from adminLoad import *
from userLoad import *
from gui_ui.Login import *
from gui_ui.register import *

class Login_Page(Ui_Login, QWidget):
    def __init__(self):
        super(Login_Page, self).__init__()
        self.setupUi(self)
        self.InitUI()

    # 初始化窗口函数
    def InitUI(self):
        # 设置窗口标题
        self.setWindowTitle("人脸识别考勤系统")
        # 设置背景图片
        self.Setting_Background()
        # 设置固定大小
        self.setFixedSize(800, 450)
        # 设置图标
        app.setWindowIcon(QIcon("gui_image/lin3.png"))
        # 显示时间
        self.Show_Time()
        # 初始化文本框
        self.Init_LineEdit()
        # 初始化复选框
        self.Init_CheckBook()
        # 初始化按钮
        self.Init_Button()


    # 显示时间
    def Show_Time(self):
        self.time = Time()
        self.time.updae_date.connect(self.Update_Time)
        self.time.start()

    def Update_Time(self, data):
        # 实时显示时间
        self.Time_Label.setText(data)
        self.Time_Label.setFont(QFont("Roman tomes", 12, QFont.Bold))

    # 设置背景图片
    def Setting_Background(self):
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap("gui_image/Login_page.png")))
        self.setPalette(window_pale)

    # 文本框的初始化
    def Init_LineEdit(self):
        # 设置提示语
        self.User_lineEdit.setPlaceholderText("输入用户账号")
        # 限制用户账号12位
        # user_lineEdit = QRegExpValidator(QRegExp("^[0-9]{12}$"))
        # self.User_lineEdit.setValidator(user_lineEdit)

        self.Password_lineEdit.setPlaceholderText("输入密码")
        self.Password_lineEdit.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        # 只要文本框发生变化，就会调用check_input函数
        self.User_lineEdit.textChanged.connect(self.Input_Check)
        self.Password_lineEdit.textChanged.connect(self.Input_Check)

    # 当两个文本框有内容时登录按钮才亮
    def Input_Check(self):
        # 当两个文本框有内容时，登录按钮才能按
        if (self.User_lineEdit.text() and self.Password_lineEdit.text()) and (
                self.Admin.isChecked() or self.Student.isChecked()):
            self.Login_Button.setEnabled(True)
        else:
            self.Login_Button.setEnabled(False)

    # 初始化复选框
    def Init_CheckBook(self):

        # 绑定文本框变化槽函数
        self.Admin.toggled.connect(self.Input_Check)
        self.Student.toggled.connect(self.Input_Check)

        # 绑定信号槽函数
        self.Rember.stateChanged.connect(self.Remember_Password)
        self.autologin.stateChanged.connect(self.Auto_Login)

    # 初始化按钮(绑定登录函数的槽函数)
    def Init_Button(self):

        self.Login_Button.setEnabled(False)
        # 登录按钮点击绑定槽函数
        self.Login_Button.clicked.connect(self.Login)
        # 注册按钮绑定槽函数
        self.Register_Buton.clicked.connect(self.Register_Func)
        # 退出按钮绑定槽函数
        self.Exit_Button.clicked.connect(self.close)

    # 记住密码
    def Remember_Password(self):
        # 记住密码功能选中
        if self.Rember.isChecked():
            User_Data = [self.User_lineEdit.text(), self.Password_lineEdit.text()]
            # 写入.pkl文件
            with open("autoLoginFile/login.pkl", "wb") as f:
                pickle.dump(User_Data, f)

    # 自动登录方法
    def Auto_Login(self):
        if self.autologin.isChecked():
            data = [self.User_lineEdit.text(), self.Password_lineEdit.text()]
            # 删除原有.pkl文件
            os.remove("autoLoginFile/auto.pkl")
            # 新建.pkl文件
            with open("autoLoginFile/auto.pkl", "wb") as f:
                pickle.dump(data, f)
        else:
            # 清空.pkl文件
            with open("autoLoginFile/auto.pkl", "wb") as f:
                pickle.dump(0, f)

    # 登录时保存登录状态设置
    def Save_LoginState(self):
        self.Remember_Password()
        self.Auto_Login()

    ############################按钮槽函数#################
    def Login(self):

        # 登录时保存文本框内容到自动登录文件
        self.Save_LoginState()

        # 获取用户输入的用户账号及密码
        ID = self.User_lineEdit.text()
        password = self.Password_lineEdit.text()

        # 获取用户输入的班级号
        IDtoClass = ID[0:10]

        # 判断是老师登录还是学生登录

        # 如果是管理员登录，判断管理员的账号和密码
        if (self.Admin.isChecked()):
            # 管理员登录
            if (ID == 'Lin' and password == '123456'):
                # 关闭登录页面
                #self.close()
                QMessageBox.about(self,"欢迎","欢迎进入管理员老师页面！")
                # 跳转到管理员页面
                self.jump2admin()
                # 管理员页面关闭后退出本函数
                return
            else:
                # 不是管理员
                QMessageBox.about(self, "提示", "管理员账户或密码错误！")

            print("我是管理员登陆")

        elif (self.Student.isChecked()):
            # 建立数据库连接
            coon = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='123456',
                db='mytest',
                charset='utf8'
            )
            # 拿到游标
            cursor = coon.cursor()

            # 检索数据库---是否存有该班级词条
            sql = 'select * from information_schema.tables where table_name = %s '
            rows = cursor.execute(sql, IDtoClass)
            if (rows):
                # 数据库已经存在该班级的表
                sql = 'select * from `%s` ' % IDtoClass + ' where id_num = %s '
                row = cursor.execute(sql, ID)

                # 该表中已经存在该名用户的基础信息
                if (row):
                    # 存在该用户
                    # 查询该用户密码
                    sql = 'select password from `%s`' % IDtoClass + ' where id_num = %s'
                    cursor.execute(sql, ID)
                    # 获取存储的密码
                    row = cursor.fetchone()
                    # 带数字元组字符串
                    row2 = ' '.join(map(str, row))
                    if (row2 == password):
                        QMessageBox.about(self, '提示', '登陆成功!欢迎进入学生页面！')
                        # 关闭登陆注册页面
                        #self.close()
                        # 跳转用户界面
                        self.jump2user()


                    else:
                        QMessageBox.about(self, '提示', '密码错误')
                # 不存在该用户
                else:
                    QMessageBox.about(self, '提示', '该用户不存在!请先注册')
            # 数据库中不存在该班级的表
            else:
                # 查询管理员是否已建立该班级词条
                sql = 'select * from classtable where majorNumber = %s '
                rows = cursor.execute(sql, IDtoClass)
                # 班级已建立但未初始化
                if (rows):
                    # 弹出提示框
                    QMessageBox.about(self, '提示', '请先注册！')
                else:
                    # 管理员未开放该班级
                    QMessageBox.warning(self, '提示', '请联系管理员增设该班级')

            print("学生端登陆")

    def Register_Func(self):
        register_page = Register_Page()
        register_page.exec()


    # 跳转管理员页面方法
    def jump2admin(self):
        # 创建模态对话框
        admin2show_dialog = QDialog()
        # 设置对话框名称
        admin2show_dialog.setWindowTitle('管理员页面')
        # 设置窗体的图标
        admin2show_dialog.setWindowIcon(QIcon("./gui_image/lin.png"))
        admin2show_dialog.setFixedSize(800,450)
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap("gui_image/Teacher.jpg")))
        admin2show_dialog.setPalette(window_pale)
        # 垂直布局
        v_layout = QVBoxLayout(admin2show_dialog)
        # 实例化管理员界面
        adminfirst = adminControl()
        # 班级管理表单加入垂直布局
        v_layout.addWidget(adminfirst)
        # 模态窗口关闭返回主窗口窗口
        admin2show_dialog.exec()
        #用户界面关闭后，显示新的登录注册框
        self.show()

    # 跳转用户页面方法
    def jump2user(self):
        # 获取登录用户ID
        ID = self.User_lineEdit.text()
        # 获取用户输入的班级号
        IDtoClass = ID[0:10]

        # 初始化学生页面
        self.userfirst = userControl(ID,IDtoClass)

        # # 个人信息页-----个人ID
        # self.userfirst.userId.setText(ID)
        # # 个人信息页-----班级编号
        # self.userfirst.classNum.setText(IDtoClass)
        #
        # # 个人信息页-----个人头像
        # self.userfirst.showUserImage()
        #
        # # 班级课表页-----班级号
        # self.userfirst.userclassNum.setText(IDtoClass)
        # 显示用户界面
        self.userfirst.show()


# 显示时间的类
class Time(QThread):
    # 每隔一秒发送时间数据
    updae_date = pyqtSignal(str)

    # 改写run函数
    def run(self) -> None:
        while True:
            data = QDateTime.currentDateTime()
            currentTime = data.toString("yyyy-MM-dd hh:mm:ss dddd")
            self.updae_date.emit(str(currentTime))
            time.sleep(1)




"""        学生注册页面              """
class Register_Page(Ui_Register_Form,QDialog):
    def __init__(self):
        super(Register_Page, self).__init__()
        self.setupUi(self)
        # 调用初始化函数
        self.InitUi()
        self.show()

    def InitUi(self):
        self.setWindowTitle("学生用户注册")
        self.setWindowIcon(QIcon("./gui_image/clock.png"))
        self.setFixedSize(800,470)

        # 文本框初始化
        self.Init_Line()
        # 按钮初始化
        self.Init_Button()

    # 初始化文本框
    def Init_Line(self):
        # 文本框内容变化时绑定输入检查函数
        self.ID_line.textChanged.connect(self.Input_Check)
        self.Password_Line.textChanged.connect(self.Input_Check)
        self.Check_Line.textChanged.connect(self.Input_Check)
        self.Chinese.textChanged.connect(self.Input_Check)
        self.English.textChanged.connect(self.Input_Check)
        self.man.clicked.connect(self.Input_Check)
        self.girl.clicked.connect(self.Input_Check)
        # 设置密码显示方式
        self.Password_Line.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.Check_Line.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        # 注册提示
        self.ID_line.setPlaceholderText('输入学生的学号')
        self.Password_Line.setPlaceholderText('请输入密码')
        self.Check_Line.setPlaceholderText('请再次确认密码！')
        self.Chinese.setPlaceholderText('中文名')
        self.English.setPlaceholderText('英文名')

    # 只有内容充足，注册按钮才为点击状态
    def Input_Check(self):
        if (self.man.isChecked() or self.girl.isChecked()):
            gender = True
        else:
            gender = False

        if (self.ID_line.text() and self.Password_Line.text()
                and self.Check_Line.text() and self.Chinese.text() and self.English.text() and gender):
            self.Register_button.setEnabled(True)
        else:
            self.Register_button.setEnabled(False)

    # 判断学生用户密码的合法性
    def check_password(self):
        password1 = self.Password_Line.text()
        checkpassword = self.Check_Line.text()

        # 密码位数检测
        if len(password1) < 6:
            QMessageBox.warning(self,"警告","密码位数小于6")
            self.Password_Line.setText("")
            self.Check_Line.setText("")
        else:
            # 检查两次密码是否相同
            if password1 == checkpassword:
                pass
            else:
                QMessageBox.warning(self, "警告", "两次输入的密码不一致")
                # 清空密码文本框
                self.Password_Line.setText("")
                self.Check_Line.setText("")

    # 按钮初始化
    def Init_Button(self):
        self.Register_button.setEnabled(False)
        self.Register_button.clicked.connect(self.To_Register)
        self.Exit_button.clicked.connect(self.close)

    # 注册方法
    def To_Register(self):
        # 判断密码合理性
        self.check_password()
        # 先获取注册用户的学号，检查用户是否存在
        ID = self.ID_line.text()
        # 获取注册用户输入的班级号
        IDtoClass = ID[0:10]

        # 暂存表单信息
        id_line_tempor = self.ID_line.text()  # 用户ID
        Chinese_tempor = self.Chinese.text()  # 中文名
        English_tempor = self.English.text()  # 英文名
        password = self.Check_Line.text()     # 密码

        if self.man.isChecked():
            gender = "男"
        elif self.girl.isChecked():
            gender = "女"
        else:
            gender = '0'
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

        # 检查数据库是否存在该班级的信息
        sql = 'select *from information_schema.tables where table_name = %s'
        rows = cursor.execute(sql,IDtoClass)
        # 如果存在该班级
        if (rows):
            sql = 'select *from `%s` '%IDtoClass + ' where id_num = %s'
            row = cursor.execute(sql,ID)
            # 该表中是否已经存在改名用户信息
            if (row):
                QMessageBox.warning(self,"警告","该同学已存在!")
            else:
                # 不存在则插入该学生的信息
                sql_insert = 'insert into `%s` ' %IDtoClass +'(id_num,userName,userEnglishName,password,gender,checked) values(%s,%s,%s,%s,%s,%s)'
                cursor.execute(sql_insert,(id_line_tempor,Chinese_tempor,English_tempor,password,gender,"否"))



                # 弹出提示框
                QMessageBox.about(self,"提示","注册成功！")

        else:
            # 该数据库不存在该班级的表
            # 查询管理员是否已建立该班级
            sql = 'select * from classtable where majorNumber = %s '
            rows = cursor.execute(sql,IDtoClass)
            if (rows):
                # 存在该班级
                # 新建一张表
                sql = 'create table `mytest`.`%s` ' % IDtoClass + ' (`id_num` char(255)  NOT NULL,  `userName` char(255)NULL,`userEnglishName` char(255)NULL,`gender` char(255) NULL, `password` char(255) NULL, `checked` char(255) NULL )'
                cursor.execute(sql)
                # 该用户为第一位用户
                # 插入该学生的信息
                sql_insert = 'insert into `%s` ' %IDtoClass + '(id_num,userName,userEnglishName,password,gender,checked) values(%s,%s,%s,%s,%s,%s)'
                cursor.execute(sql_insert,(id_line_tempor,Chinese_tempor,English_tempor,password,gender,"否"))
                # 弹出提示框
                QMessageBox.about(self,"提示","注册成功!")

            else:
                # 老师没有开放该班级
                QMessageBox.warning(self,"提示","管理员老师没有增设该班级!")


        # 提交修改
        conn.commit()
        cursor.close()
        conn.close()







if __name__ == "__main__":

    # 适应不同分辨率
    QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    login_page = Login_Page()
    login_page.show()

    sys.exit(app.exec_())
