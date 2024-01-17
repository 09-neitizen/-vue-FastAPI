from random import Random
import smtplib
from email.header import Header  # 用来对Email标题进行编码
from email.mime.text import MIMEText  # 负责构造文本
from email.mime.image import MIMEImage  # 负责构造图片
from email.mime.multipart import MIMEMultipart  # 负责将多个对象集合起来
from email.mime.base import MIMEBase  # 添加附件的时候用到
from email.utils import parseaddr, formataddr

# parseaddr：将带姓名的Email格式作为参数，给parseaddr函数，得到name姓名和addr纯email
# formataddr：将name和addr转换成标准Email地址格式


# smtplib模块主要负责发送邮件
# email模块主要负责构造邮件
'''
MIMEText：（MIME媒体类型）内容形式为纯文本、HTML页面。
MIMEImage：内容形式为图片。
MIMEMultupart：多形式组合，可包含文本和附件。

每一类对应的导入方式：
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
'''

my_email = "ccnuhelper@163.com"


# sendmail函数是不使用编码后的，带姓名的Email地址字符串的，而是使用纯Email地址
# 函数小工具
# 合并了 parseaddr和formataddr功能
# 输入以（发件人/收件人的昵称<xxxxx@163.com>）编写的Email地址
# 得到直接可以在MIMEText中使用字符串
def _format_addr(s):
    """
    合并了 parseaddr和formataddr功能
    :param s: 邮箱
    :return: 纯Email地址
    """
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def get_msg(content, subject, to, my_email=my_email):
    """
    获取邮件内容，特定格式
    :param content: 邮件内容
    :param subject: 邮件主题
    :param to: 邮件发给谁
    :param my_email: 邮件发送者
    :return: 邮件格式
    """
    msg = MIMEText(content, 'html', 'utf-8')
    msg['To'] = _format_addr(to)  # 发送到哪里
    msg['From'] = _format_addr(my_email)  # 自己的邮件地址
    msg['Subject'] = Header(subject, "utf-8")  # 邮件主题
    return msg.as_string()


# 生成随机字符串
def random_str(randomlength=6):
    """
    随机字符串
    :param randomlength: 字符串长度
    :return: String 类型字符串
    """
    code = ''
    chars = '0123456789'
    # chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        code += chars[random.randint(0, length)]
    return code


# 发送电子邮件
def send_code_email(receiver_email, send_type="register"):
    """
    发送电子邮件
    :param receiver_email: 发送给谁
    :param send_type: 发送的邮件用途
    :return: String 返回code
    """
    # 将给用户发的信息保存在数据库中
    code = random_str(8)
    # 创建 smtp对象,并连接
    smtp = smtplib.SMTP_SSL("smtp.163.com", 465)
    # 如果为注册类型
    if send_type == "register":
        email_title = "注册激活"
        # email_body = "请点击下面的链接激活你的账号:http://127.0.0.1:8000/active/{0}".format(code)
        email_body = '''
<div >
    <div >
        <div  style="opacity: 1;">
            <div style="max-width: 980px;
                margin: 64px auto;
                opacity: 0.87;
                padding: 24px 32px;
                box-shadow: 0 2px 2px 0 rgba(0, 0, 0, .14), 0 3px 1px -2px rgba(0, 0, 0, .2), 0 1px 5px 0 rgba(0, 0, 0, .12);
                border-radius: 2px;
                background: white">
                <p style="font-weight: bold;color: #2196F3;font-size: 28px;" align="center">CCNUHelper </p>
                <h2 style="margin: 0 0 16px 0" align="center">注册激活验证  验证码:</h2>
                <p align="center"><b style="color: #946CE6;font-size: 48px" >{}</b></p>
                <br>
                <div align="center">
                    <font face="'Nunito', sans-serif" color="#585858" style="font-size: 24px; line-height: 32px;" >
                    <span style="font-family: 'Nunito', Arial, Tahoma, Geneva, sans-serif; color: #aaaaaa; font-size: 16px; line-height: 32px;" >
                        (如果您从未请求发送邮箱验证码，请忽略此邮件)
                    </span>
                    </font>
                </div><br>
                <div align="center">
                    <span style="color: rgb(0, 0, 0); font-size: 10px;" >有效时间为</span>
                    <span style="color: rgb(0, 0, 0);">
                        <strong>
                        <span style="color: rgb(78, 164, 220); font-size: 10px;">2分钟</span>
                        </strong>
                        <span style="font-size: 10px;">，请及时验证</span>
                    </span>
                </div>
                <div align="center">
                    <span style="color: rgb(0, 0, 0); font-size: 10px;">请不要向其他人提供此验证码, 这可能使您的账户遭受攻击</span>
                </div>
                <div align="center">
                    <span style="color: rgb(0, 0, 0); font-size: 10px;">这是系统自动发送的邮件，请不要回复此邮件</span>
                </div>    
                <p align="center">
                    <span style="font-family: 'Nunito', Arial, Tahoma, Geneva, sans-serif; color: #1a1a1a; font-size: 17px; line-height: 20px;">
                        <a href="" target="_blank" 
                            style="font-family: 'Nunito', Arial, Tahoma, Geneva, sans-serif; 
                            color: #1a1a1a; font-size: 17px; 
                            line-height: 20px; 
                            text-decoration: none;" 
                            rel="noopener">访问官网
                        </a> &nbsp; | &nbsp; 
                        <a href="" target="_blank" 
                            style="font-family: 'Nunito', Arial, Tahoma, Geneva, sans-serif; 
                            color: #1a1a1a; font-size: 17px; 
                            line-height: 20px; 
                            text-decoration: none;" 
                            rel="noopener">用户中心
                        </a>
                    </span>
                </p>
        </div>
    </div>
</div>'''.format(code)
        # 发送邮件
        #  smtplib.SMTP([host[, port[, local_hostname[, timeout]]]])

        # 邮箱登录
        try:
            smtp.login("ccnuhelper@163.com", "UFIQDASVMHNNSNCW")
            msg = get_msg(email_body, email_title, receiver_email)
            smtp.sendmail(my_email, receiver_email, msg)
            smtp.quit()
        except smtplib.SMTPException:
            smtp.quit()
            return None
    if send_type == "retrieve":
        email_title = "找回密码"
        email_body = '''
<div >
    <div >
        <div  style="opacity: 1;">
            <div style="max-width: 980px;
                margin: 64px auto;
                opacity: 0.87;
                padding: 24px 32px;
                box-shadow: 0 2px 2px 0 rgba(0, 0, 0, .14), 0 3px 1px -2px rgba(0, 0, 0, .2), 0 1px 5px 0 rgba(0, 0, 0, .12);
                border-radius: 2px;
                background: white">
                <p style="font-weight: bold;color: #2196F3;font-size: 28px;" align="center">CCNUHelper </p>
                <h2 style="margin: 0 0 16px 0" align="center">找回密码验证  验证码:</h2>
                <p align="center"><b style="color: #946CE6;font-size: 48px" >{}</b></p>
                <br>
                <div align="center">
                    <font face="'Nunito', sans-serif" color="#585858" style="font-size: 24px; line-height: 32px;" >
                    <span style="font-family: 'Nunito', Arial, Tahoma, Geneva, sans-serif; color: #aaaaaa; font-size: 16px; line-height: 32px;" >
                        (如果您从未请求发送邮箱验证码，请忽略此邮件)
                    </span>
                    </font>
                </div><br>
                <div align="center">
                    <span style="color: rgb(0, 0, 0); font-size: 10px;" >有效时间为</span>
                    <span style="color: rgb(0, 0, 0);">
                        <strong>
                        <span style="color: rgb(78, 164, 220); font-size: 10px;">2分钟</span>
                        </strong>
                        <span style="font-size: 10px;">，请及时验证</span>
                    </span>
                </div>
                <div align="center">
                    <span style="color: rgb(0, 0, 0); font-size: 10px;">请不要向其他人提供此验证码, 这可能使您的账户遭受攻击</span>
                </div>
                <div align="center">
                    <span style="color: rgb(0, 0, 0); font-size: 10px;">这是系统自动发送的邮件，请不要回复此邮件</span>
                </div>    
                <p align="center">
                    <span style="font-family: 'Nunito', Arial, Tahoma, Geneva, sans-serif; color: #1a1a1a; font-size: 17px; line-height: 20px;">
                        <a href="" target="_blank" 
                            style="font-family: 'Nunito', Arial, Tahoma, Geneva, sans-serif; 
                            color: #1a1a1a; font-size: 17px; 
                            line-height: 20px; 
                            text-decoration: none;" 
                            rel="noopener">访问官网
                        </a> &nbsp; | &nbsp; 
                        <a href="" target="_blank" 
                            style="font-family: 'Nunito', Arial, Tahoma, Geneva, sans-serif; 
                            color: #1a1a1a; font-size: 17px; 
                            line-height: 20px; 
                            text-decoration: none;" 
                            rel="noopener">用户中心
                        </a>
                    </span>
                </p>
        </div>
    </div>
</div>
'''.format(code)
        # 发送邮件
        try:
            smtp.login("ccnuhelper@163.com", "UFIQDASVMHNNSNCW")
            msg = get_msg(email_body, email_title, receiver_email)
            smtp.sendmail(my_email, receiver_email, msg)
            smtp.quit()
        except smtplib.SMTPException:
            smtp.quit()
            return None
    return code
