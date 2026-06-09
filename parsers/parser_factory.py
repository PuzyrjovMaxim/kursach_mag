from parsers.solomon_parser import SolomonParser


class ParserFactory:

    @staticmethod
    def create_parser(file_path: str):

        return SolomonParser()