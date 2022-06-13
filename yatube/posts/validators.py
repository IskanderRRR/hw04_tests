from django.core.exceptions import ValidationError


def validate_not_empty(value):
    """Проверка о заполнении поля."""
    if value == '':
        raise ValidationError(
            'Заполните, пожалуйста, это поле',
            params={'value': value},
        )
