from sanic import Blueprint

from api.extensions.mysql import service as mysql
from api.utils import Response

user_bp = Blueprint("user", url_prefix="/user")


@user_bp.route("/<pk:int>")
async def get_user(request, pk):
    data = await mysql.query_user(pk)
    return Response.status(data)
