from svc.manager import create_sse_app


app = create_sse_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, threaded=True)
