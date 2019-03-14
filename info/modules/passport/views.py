# coding=utf-8
import re
import random
from flask import request
from flask import abort
from flask import jsonify
from flask import make_response
from flask import current_app

from info import redis_store
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from info import constants
from info.libs.yuntongxun.sms import CCP
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
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
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
        
        redis_store.setex("SMS_%s" % mobile, sms_code,
                          constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存短信验证码失败')
    # 7. 返回发送成功响应
    return jsonify(errno=RET.OK, errmsg='发送成功')
