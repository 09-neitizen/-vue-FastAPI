# 发送邮箱验证码
class Setting():
    '''
    但是使用25号端口有一个问题，就是保密性不够好，数据都是明文传输，没有加密。
    现在一般都推荐使用SSL，Secure Socket Layer，465是默认的SMTP over SSL的端口号
    '''
    EMAIL_HOST = "smtp.163.com"  # SMTP服务器地址
    EMAIL_PORT = 465  # 端口： 一般情况下都为25
    EMAIL_HOST_USER = "ccnuhelper@163.com"  # 账号
    EMAIL_HOST_PASSWORD = "UFIQDASVMHNNSNCW"  # 密码 (注意：这里的密码指的是授权码)
    EMAIL_FROM = "ccnuhelper@163.com"  # 邮箱来自


