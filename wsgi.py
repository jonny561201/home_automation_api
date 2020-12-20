from svc.manager import app

if __name__ == '__main__':
    app.run(ssl_context=('certificate.crt', 'private.key'))
