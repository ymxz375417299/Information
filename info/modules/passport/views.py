# coding=utf-8
import re
import random
from datetime import datetime 

from flask import request
from flask import abort
from flask import jsonify
from flask import make_response
from flask import current_app
from flask import session

from info import redis_store
from info import db
from info import constants
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from info.libs.yuntongxun.sms import CCP
from info.models import User # 数据库模型
from . import passport_blu



@passport_blu.route('/image_code')
# 因为在蓝图中已经添加的url前缀，所以路由不是/passport/image_code
def get_image_code():
    """
    生成图片验证码
    1. 获取参数
    2. 判断参数是否有值
    3. 生成图片验证码
    4. 保存图片验证码内容到redis
    5. 返回图片验证码
    """
    # 1. 获取参数
    # arg: 取得url中？后面的参数（查询字符串）
    code_id = request.args.get('code_id', '')  # 默认值""
    # 2. 判断是否有值
    if not code_id:
        return abort(403)  # 主动抛出异常
    # 3. 生成图片验证码
    name, text, image = captcha.generate_captcha()
    current_app.logger.debug('图片验证码：%s' % text)
    # 4. 保存图片验证码内容到redis
    try:
        redis_store.setex("ImageCode_" + code_id,
                          constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))

    # 5. 返回图片验证码
    resp = make_response(image)
    # 设置返回的content_type
    resp.headers['Content_Type'] = 'image/jpg'
    return resp


@passport_blu.route('/smscode', methods=['POST'])
def send_sms():
    """
    1. 接受参数： 手机号，图片验证码内容，图片验证码id
    2. 校验参数（是否有值，是否符合规则） 
    3. 通过传入的图片编码核对redis真实性
    4. 进行验证码内容的比对，如果不一致，返回验证码错误
    5. 生成随机短信验证码并发送短信
    6. redis保存短信验证码内容
    7. 返回发送成功响应
    """

    # 1. 接受参数并判断是否有值
    # 取到请求值的内容，但是默认是字符串转成json方便处理
    # param_dict = json.loads(request.data)
    param_dict = request.json
    mobile = param_dict.get('mobile')
    image_code = param_dict.get('image_code')
    image_code_id = param_dict.get('image_code_id')

    # 2. 校验参数（是否有值，是否符合规则）
    if not all((mobile, image_code, image_code_id)):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 2.1 手机号是否合法
    if not re.match('^1[35678]\d{9}$', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号不合法')
    # 3. 通过传入的图片编码核对redis真实性
    try:
        real_image_code = redis_store.get('ImageCode_' + image_code_id)
        # 如果能够取出值，删除redis中的缓存内容
        if real_image_code:
            redis_store.delete('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取图片验证码失败')
    # 3.1 虽然redis成功取出来了。但是也有空值可能
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='验证码已过期')
    # 4. 进行验证码内容的比对，如果不一致，返回验证码错误
    if image_code.upper() != real_image_code.upper():
        # 验证码输出错误
        return jsonify(errno=RET.DATAERR, errmsg='验证码错误')
    # 4.1 TODO补： 校验手机号码是否已注册
    # 5. 生成随机短信验证码并发送短信
    sms_code = '%06d' % random.randint(0, 999999)
    current_app.logger.debug('短信验证码内容：%s' % sms_code)
    result = CCP().send_template_sms(mobile, [sms_code,
                                              constants.SMS_CODE_REDIS_EXPIRES/60], '1')
    if result != 0:
        # 成功返回0
        return jsonify(errno=RET.THIRDERR, errmsg='第三方发错出错')
    # 6. redis保存短信验证码内容
    try:
        
        redis_store.setex("SMS_%s" % mobile, 
                          constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存短信验证码失败')
    # 7. 返回发送成功响应
    return jsonify(errno=RET.OK, errmsg='发送成功')


@passport_blu.route('/register', methods=['POST'])
def register():
    """
    注册接口
    1. 获取参数
    2. 判断参数是否有值
    3. 判断参数是否合法（手机号）
    4. 从redis中获取指定手机号对应的短信验证码 
    5. 校验验证码
    6. 初始化user模型， 添加数据至数据库
    7. 保存当前的用户状态
    6. 返回注册结果
    """
    
    # 1. 获取参数
    json_data = request.json
    mobile = json_data.get('mobile')
    sms_code = json_data.get('smscode')
    password = json_data.get('password')
    # 2. 判断参数是否合法（手机号）
    if not re.match('^1[35678]\d{9}$', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号不合法')
    # 3. 判断参数是否有值
    if not all((mobile, sms_code, password)):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 4. 从redis中获取指定手机号对应的短信验证码 
    try:
        real_sms_code = redis_store.get('SMS_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取本地验证码失败')
    
    # 4.1 短信验证码过期
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码过期')
    # 5. 校验验证码
    if sms_code != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')
    # 6. 删除验证码
    try:
        redis_store.delete('SMS_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
    # 6. 初始化user模型， 添加数据至数据库
    user = User()
    # 刚注册没有昵称，默认使用手机号作为昵称
    user.mobile = mobile
    user.nick_name = mobile
    # 在User类使用装饰器进行加密，这里不做修改
    user.password = password
    # 记录一下用户最后一次登录时间
    user.last_time = datetime.now()
    # 添加数据
    try:
        # 创建会话，并把实例的模型user添加进去
        db.session.add(user)
        # 提交事务
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnno=RET.DBERR, errmsg='数据保存失败')
    # 7. 保存session当前的用户状态
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    # 6. 返回注册结果
    return jsonify(errno=RET.OK, errmsg='OK')


@passport_blu.route('/login', methods=["POST"])
def login():
    """
    登录接口
    1. 获取参数
    2. 校验参数和合法性
    3. 从数据库查询出指定个的用户
    4. 保存用户登录状态
    5. 返回结果return
    """
    # 1. 获取参数
    json_data = request.json
    mobile = json_data.get('mobile')
    password = json_data.get('password')
    # 2. 校验参数和合法性
    if not re.match('^1[35678]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号不合法")
    if not all((mobile, password)):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误") 
    # 3. 从数据库查询出指定个的用户
    try:
        # 获取的是User对象，不过是通过过滤后的结果
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据错误')
    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    # 4. 校验密码
    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg='密码错误')


    # 5. 保存用户登录状态
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    
    # 6. 记录最后一次 登录时间，不用user.add 因为user是获取的数据结果， 肯定是有值的
    user.last_login = datetime.now()

    # 7. 如果在视图函数中，对模型身上的属性有修改，那么需要commit到数据库保存
    # 但是其实可以用自己写的db.session.commit(), 前提是对SQLalchemyu有相关配置
    # 提交数据库修改
    try:
        db.session.commit()
    except Exception as e:
        current.logger.error(e)

    # 8 登录成功
    return jsonify(errno=RET.OK, errmsg='OK')
