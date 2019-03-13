# coding=utf-8
from flask import request
from flask import abort
from flask import jsonify
from flask import make_response
from flask import current_app

from info import redis_store
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from info import constants
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
    # 4. 保存图片验证码内容到redis
    try:
        redis_store.setex("ImageCode_" + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))

    # 5. 返回图片验证码
    resp = make_response(image)
    # 设置返回的content_type
    resp.headers['Content_Type'] = 'image/jpg'
    return resp
