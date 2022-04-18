from sanic import response

from .models import Users


def query_user(pk):
    user = Users.query(pk=pk)
    return response.json({"user": str(user)})
