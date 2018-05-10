from app.params import REQUEST_SETTINGS


def validate_settings():
    if REQUEST_SETTINGS.get('error'):
        return
    if not REQUEST_SETTINGS.get('expression'):
        REQUEST_SETTINGS['warning'] = 'Задайте вычисляемую функцию'
        return
    if not REQUEST_SETTINGS.get('formula'):
        REQUEST_SETTINGS['warning'] = 'Выберите необходимую формулу'
        return
    else:
        REQUEST_SETTINGS['warning'] = None

    if not REQUEST_SETTINGS.get('success'):
        REQUEST_SETTINGS['error'] = 'Что-то пошло не так. Очистите данные и попробуйте снова'
        return
    else:
        REQUEST_SETTINGS['error'] = None

    return True


def clear_validators():
    REQUEST_SETTINGS['error'] = None
    REQUEST_SETTINGS['warning'] = None
    REQUEST_SETTINGS['success'] = None


def validate_algo_response(result):
    if isinstance(result, AttributeError):
        REQUEST_SETTINGS['error'] = ('Введенная вами формула обработана с ошибкой. '
                                     'Сведения об используемом синтаксисе можно найти на странице '
                                     '"Дополнительно" (SymPy Modules)')
        return

    if isinstance(result, SyntaxError):
        REQUEST_SETTINGS['error'] = 'Данное выражение содержит ошибку. Проверьте и попробуйте еще раз'
        return
    return True
