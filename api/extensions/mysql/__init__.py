from tortoise.contrib.sanic import register_tortoise

from .models import Users


class MySqlExt(object):
    def __init__(self, app):
        self.app = app

        register_tortoise(
            app,
            db_url=app.config["MYSQL_URL"],
            modules={"models": ["Users"]},
            generate_schemas=True
        )
