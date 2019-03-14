# conding=utf-8

from .CCPRestSDK import REST


# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID                                                                                                                                    
_accountSid = ''
# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN                                                                                                                                  
_accountToken = ''
# 请使用管理控制台首页的APPID或自己创建应用的APPID                                                                                                                                                                  
_appId = ''
# 说明：请求地址，生产环境配置成app.cloopen.com                                                                                                                                                                     
_serverIP = ''
# 说明：请求端口 ，生产环境为8883
_serverPort = "8883" 
# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'  

class CCP(object):
    """发送短信的辅助类，并保证全局单例"""
    def __new__(cls, *args, **kwargs):
        # 实例化时，会先经过__new__的方法，判断是否已存在类属性_instance, _instance是类CCP的唯一对象，即单例
        if not hasattr(CCP, '_instance'):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            # 实例化云通讯的REST类
            cls._instance.rest = REST(_serverIP, _serverPort, _softVersion)
            # 调用REST的方法，初始化账户
            cls._instance.rest.setAccount(_accountSid, _accountToken)
            # 调用REST的方法，初始化应用id，appid
            cls._instance.rest.setAppId(_appId)
        return cls._instance

    def send_template_sms(self, to, datas, temp_id):
        """发送短信"""
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        # 如果云通讯发送短信成功，返回的字典数据result中statuCode的值为"000000"则成功
        if result.get('statusCode') == '000000':
            # 返回0，表示发送短信成功
            return 0 
        else:
            # 返回-1，表示发送失败
            return -1

if __name__ == "__main__":
    ccp = CCP()
    # 注意： 测试的短信模板编号为1
    #参数1: 发送给谁的手机号
    #参数2: ['内容', 有效时间单位分钟]
    #参数3: 模板编号1 【云通讯】您使用的是云通讯短信模板，您的验证码是{1}，请于{2}分钟内正确输入
    ccp.send_template_sms('', ['666666', 5], 1)

