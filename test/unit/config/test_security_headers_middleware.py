from flask import Response

from svc.config.security_headers_middleware import add_security_headers


def test_add_security_headers__should_add_default_src_content_security_policy_header():
    response = Response()
    add_security_headers(response)

    assert "default-src 'self';" in response.headers["Content-Security-Policy"]


def test_add_security_headers__should_add_script_src_content_security_policy_header():
    response = Response()
    add_security_headers(response)

    assert "script-src 'self';" in response.headers["Content-Security-Policy"]


def test_add_security_headers__should_add_style_src_content_security_policy_header():
    response = Response()
    add_security_headers(response)

    assert "style-src 'self';" in response.headers["Content-Security-Policy"]


def test_add_security_headers__should_add_img_src_content_security_policy_header():
    response = Response()
    add_security_headers(response)

    assert "img-src 'self' data:;" in response.headers["Content-Security-Policy"]


def test_add_security_headers__should_add_connect_src_content_security_policy_header():
    response = Response()
    add_security_headers(response)

    assert "connect-src 'self';" in response.headers["Content-Security-Policy"]


def test_add_security_headers__should_add_object_src_content_security_policy_header():
    response = Response()
    add_security_headers(response)

    assert "object-src 'none';" in response.headers["Content-Security-Policy"]


def test_add_security_headers__should_add_base_uri_content_security_policy_header():
    response = Response()
    add_security_headers(response)

    assert "base-uri 'self';" in response.headers["Content-Security-Policy"]


def test_add_security_headers__should_add_frame_ancestors_content_security_policy_header():
    response = Response()
    add_security_headers(response)

    assert "frame-ancestors 'none';" in response.headers["Content-Security-Policy"]


def test_add_security_headers__should_add_x_content_type_options_header():
    response = Response()
    add_security_headers(response)

    assert response.headers["X-Content-Type-Options"] == 'nosniff'


def test_add_security_headers__should_add_x_frame_options_header():
    response = Response()
    add_security_headers(response)

    assert response.headers["X-Frame-Options"] == 'DENY'


def test_add_security_headers__should_add_referrer_policy_header():
    response = Response()
    add_security_headers(response)

    assert response.headers["Referrer-Policy"] == 'no-referrer'