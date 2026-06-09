class ParserError(Exception):
    """Базовое исключение парсера."""
    pass


class InvalidFileFormatError(ParserError):
    """Файл имеет неверный формат."""
    pass


class InvalidDataError(ParserError):
    """Ошибка в данных экземпляра."""
    pass