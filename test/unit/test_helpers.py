import json


def setup_request(app, ctx=None, request={}, headers=None):
    if ctx is not None:
        ctx.pop()
    new_ctx = app.test_request_context(data=json.dumps(request), content_type='application/json', headers=headers)
    new_ctx.push()
    return new_ctx

