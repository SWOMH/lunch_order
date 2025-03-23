from authx import AuthX, AuthXConfig

auth_config = AuthXConfig()
auth_config.JWT_SECRET_KEY = "SECRET_KEY"
auth_config.JWT_ACCESS_COOKIE_NAME = "from_website"
auth_config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=auth_config)

"""
jvt использовать пока не планировал, но, может, все же буду
Пока не определился просто до конца что это все же будет, а эта заготовка чтобы не забыть 
"""