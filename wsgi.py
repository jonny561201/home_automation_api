from svc.manager import app

app.run(host='0.0.0.0', port=5000, ssl_context=('certificate.crt', 'private.key'))
