from sanic import response


class Response:
    @staticmethod
    def simple_status():
        return response.json({
            "status": "ok"
        })

    @staticmethod
    def success_status(data):
        return response.json({
            "code": 200,
            "status": "SUCCESS",
            "data": data
        })

    @staticmethod
    def error_status(code, message):
        return response.json({
            "code": code,
            "status": "ERROR",
            "message": message
        })

    @staticmethod
    def task_status(task_id, status):
        return response.json({
            "code": 200,
            "status": "SUCCESS",
            "data": {
                "task_id": task_id,
                "status": status
            }
        })
