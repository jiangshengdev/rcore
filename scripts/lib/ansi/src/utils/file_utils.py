"""
文件处理工具模块

提供文件读写、路径处理、编码检测等通用文件操作功能。
支持 ANSI 文件读取和 MDX 文件写入操作。
"""

import logging
import pathlib
import shutil
from typing import Optional, Union, List, Dict, Any

logger = logging.getLogger(__name__)


class FileUtils:
    """文件处理工具类"""

    @staticmethod
    def ensure_directory_exists(directory_path: Union[str, pathlib.Path]) -> pathlib.Path:
        """
        确保目录存在，不存在则创建
        
        Args:
            directory_path: 目录路径
            
        Returns:
            创建或已存在的目录路径对象
        """
        path = pathlib.Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"目录已确保存在: {path}")
        return path

    @staticmethod
    def detect_file_encoding(file_path: Union[str, pathlib.Path]) -> str:
        """
        检测文件编码格式，固定返回 UTF-8
        
        Args:
            file_path: 文件路径
            
        Returns:
            固定返回 'utf-8'
        """
        path = pathlib.Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        # 用户指定全部使用 UTF-8 编码
        logger.debug(f"使用固定编码: utf-8")
        return 'utf-8'

    @staticmethod
    def read_ansi_file(file_path: Union[str, pathlib.Path],
                       encoding: Optional[str] = None) -> str:
        """
        读取 ANSI 文件内容
        
        Args:
            file_path: ANSI 文件路径
            encoding: 指定编码，为None时自动检测
            
        Returns:
            文件内容字符串
            
        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 编码解析失败
        """
        path = pathlib.Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"ANSI 文件不存在: {path}")

        # 自动检测编码
        if encoding is None:
            encoding = FileUtils.detect_file_encoding(path)

        try:
            with open(path, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()

            logger.info(f"成功读取 ANSI 文件: {path} (编码: {encoding}, 大小: {len(content)} 字符)")
            return content

        except UnicodeDecodeError as e:
            logger.error(f"ANSI 文件编码解析失败: {e}")
            # 尝试使用 utf-8 重新读取
            if encoding != 'utf-8':
                logger.info("尝试使用 utf-8 编码重新读取")
                return FileUtils.read_ansi_file(path, 'utf-8')
            raise

    @staticmethod
    def write_mdx_file(file_path: Union[str, pathlib.Path],
                       content: str,
                       encoding: str = 'utf-8',
                       create_backup: bool = True) -> bool:
        """
        写入 MDX 文件内容
        
        Args:
            file_path: MDX 文件路径
            content: 要写入的内容
            encoding: 文件编码，默认 utf-8
            create_backup: 是否创建备份文件
            
        Returns:
            写入是否成功
        """
        path = pathlib.Path(file_path)

        # 确保输出目录存在
        FileUtils.ensure_directory_exists(path.parent)

        # 创建备份文件
        if create_backup and path.exists():
            backup_path = path.with_suffix(path.suffix + '.bak')
            try:
                shutil.copy2(path, backup_path)
                logger.debug(f"已创建备份文件: {backup_path}")
            except Exception as e:
                logger.warning(f"创建备份文件失败: {e}")

        try:
            with open(path, 'w', encoding=encoding, newline='\n') as f:
                f.write(content)

            logger.info(f"成功写入 MDX 文件: {path} (编码: {encoding}, 大小: {len(content)} 字符)")
            return True

        except Exception as e:
            logger.error(f"写入 MDX 文件失败: {e}")
            return False

    @staticmethod
    def validate_file_extension(file_path: Union[str, pathlib.Path],
                                expected_extensions: List[str]) -> bool:
        """
        验证文件扩展名
        
        Args:
            file_path: 文件路径
            expected_extensions: 期望的扩展名列表（包含点号，如 ['.ansi', '.txt']）
            
        Returns:
            扩展名是否匹配
        """
        path = pathlib.Path(file_path)
        file_extension = path.suffix.lower()

        is_valid = file_extension in [ext.lower() for ext in expected_extensions]

        if not is_valid:
            logger.warning(f"文件扩展名不匹配: {file_extension}, 期望: {expected_extensions}")

        return is_valid

    @staticmethod
    def get_file_info(file_path: Union[str, pathlib.Path]) -> Dict[str, Any]:
        """
        获取文件基本信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件信息的字典
        """
        path = pathlib.Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        stat = path.stat()

        info: Dict[str, Any] = {
            'path': str(path.absolute()),
            'name': path.name,
            'stem': path.stem,
            'suffix': path.suffix,
            'size_bytes': stat.st_size,
            'size_kb': round(stat.st_size / 1024, 2),
            'modified_time': stat.st_mtime,
            'is_file': path.is_file(),
            'is_directory': path.is_dir(),
            'encoding': FileUtils.detect_file_encoding(path) if path.is_file() else None
        }

        logger.debug(f"文件信息: {info}")
        return info

    @staticmethod
    def clean_output_directory(output_dir: Union[str, pathlib.Path],
                               pattern: str = "*.mdx") -> int:
        """
        清理输出目录中的文件
        
        Args:
            output_dir: 输出目录路径
            pattern: 要清理的文件模式，默认清理所有 .mdx 文件
            
        Returns:
            清理的文件数量
        """
        output_path = pathlib.Path(output_dir)

        if not output_path.exists():
            logger.info(f"输出目录不存在，无需清理: {output_path}")
            return 0

        files_to_remove = list(output_path.glob(pattern))
        removed_count = 0

        for file_path in files_to_remove:
            try:
                file_path.unlink()
                logger.debug(f"已删除文件: {file_path}")
                removed_count += 1
            except Exception as e:
                logger.error(f"删除文件失败 {file_path}: {e}")

        logger.info(f"输出目录清理完成: 删除 {removed_count} 个文件")
        return removed_count


# 便捷函数
def read_ansi(file_path: Union[str, pathlib.Path]) -> str:
    """读取 ANSI 文件的便捷函数"""
    return FileUtils.read_ansi_file(file_path)


def write_mdx(file_path: Union[str, pathlib.Path], content: str) -> bool:
    """写入 MDX 文件的便捷函数"""
    return FileUtils.write_mdx_file(file_path, content)


def ensure_dir(directory_path: Union[str, pathlib.Path]) -> pathlib.Path:
    """确保目录存在的便捷函数"""
    return FileUtils.ensure_directory_exists(directory_path)
