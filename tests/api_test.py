import pytest
from sanic import Sanic
from sanic import response


@pytest.fixture
def app():
    sanic_app = Sanic(__name__)
    TestManager(sanic_app)

    @sanic_app.get("/")
    def basic(request):
        return response.text("foo")

    return sanic_app


def test_basic_test_client(app):
    request, response = app.test_client.get("/")

    assert response.body == b"foo"
    assert response.status == 200