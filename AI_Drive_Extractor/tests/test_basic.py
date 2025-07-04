import importlib


def test_modules_import():
    assert importlib.import_module('AI_Drive_Extractor.drive_utils')
    assert importlib.import_module('AI_Drive_Extractor.pdf_utils')
    assert importlib.import_module('AI_Drive_Extractor.chat_utils')
