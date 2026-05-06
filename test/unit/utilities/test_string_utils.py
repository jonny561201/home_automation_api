import string

from svc.utilities.string_utils import generate_password


def test_generate_password__should_return_password_of_requested_length():
    actual = generate_password(24)

    assert len(actual) == 24


def test_generate_password__should_return_empty_string_when_length_is_zero():
    actual = generate_password(0)

    assert actual == ''


def test_generate_password__should_use_only_letters_digits_and_punctuation():
    valid_chars = string.ascii_letters + string.digits + string.punctuation

    actual = generate_password(50)

    assert all(c in valid_chars for c in actual)


def test_generate_password__should_return_different_values_on_consecutive_calls():
    first = generate_password(24)
    second = generate_password(24)

    assert first != second
