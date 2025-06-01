"""
统一异常定义模块

定义 ANSI 转换器中使用的所有异常类型，提供清晰的错误层次结构。
"""


class AnsiConverterError(Exception):
    """ANSI 转换器基础异常类"""
    pass


class ConfigurationError(AnsiConverterError):
    """配置相关错误"""
    pass


class ToolError(AnsiConverterError):
    """工具相关错误"""
    pass


class FileProcessingError(AnsiConverterError):
    """文件处理相关错误"""
    pass


class ConversionError(AnsiConverterError):
    """转换过程相关错误"""
    pass


class MdxFormatterError(ConversionError):
    """MDX 格式化错误 - 兼容 main.py"""
    pass


class TerminalToHtmlError(ConversionError):
    """Terminal-to-HTML 转换错误 - 兼容 main.py"""
    pass


class EnvironmentError(AnsiConverterError):
    """环境验证错误 - 兼容 main.py"""
    pass
