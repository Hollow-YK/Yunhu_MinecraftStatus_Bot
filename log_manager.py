import logging
import os
from datetime import datetime

class LevelFilter(logging.Filter):
    """A filter to allow logging only specific levels."""
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level

class LogManager:
    def __init__(self, args):
        self.args = args
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
        self.log_filepath = self._setup_logging()
    
    def _setup_logging(self):
        """Initialize the logger with multiple handlers for different log levels."""
        # 创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 生成日志文件名
        log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        log_filepath = os.path.join(self.log_dir, log_filename)
        
        # 创建根日志记录器
        logger = logging.getLogger("MinecraftMonitor")
        logger.setLevel(logging.DEBUG)  # 设置为DEBUG级别以捕获所有日志
        
        # 控制台处理器
        self._setup_console_handlers(logger)
        
        # 文件处理器
        self._setup_file_handlers(logger, log_filepath)
        
        return log_filepath
    
    def _setup_console_handlers(self, logger):
        """设置控制台日志处理器"""
        # DEBUG 处理器（用于HTML内容）
        if self.args.log_with_board:
            debug_handler = self._create_console_handler(
                logging.DEBUG, 
                '\033[0;36m[MinecraftMonitor] %(asctime)s %(levelname)s : %(message)s\033[0m'
            )
            logger.addHandler(debug_handler)
        
        # INFO 处理器
        info_handler = self._create_console_handler(
            logging.INFO, 
            '[MinecraftMonitor] %(asctime)s %(levelname)s : %(message)s',
            not self.args.log_no_info
        )
        logger.addHandler(info_handler)
        
        # WARNING 处理器
        warning_handler = self._create_console_handler(
            logging.WARNING, 
            '\033[0;33m[MinecraftMonitor] %(asctime)s %(levelname)s : %(message)s\033[0m'
        )
        logger.addHandler(warning_handler)
        
        # ERROR 处理器
        error_handler = self._create_console_handler(
            logging.ERROR, 
            '\033[0;31m[MinecraftMonitor] %(asctime)s %(levelname)s : %(message)s\033[0m'
        )
        logger.addHandler(error_handler)
    
    def _setup_file_handlers(self, logger, log_filepath):
        """设置文件日志处理器"""
        if self.args.no_file_log:
            # 只写入"no-file-log"到文件，使用UTF-8编码
            with open(log_filepath, 'w', encoding='utf-8') as f:
                f.write("no-file-log\n")
            return
        
        # 创建文件格式
        file_formatter = logging.Formatter(
            '[MinecraftMonitor] %(asctime)s %(levelname)s : %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # 文件处理器，使用UTF-8编码
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        
        # 设置文件日志级别
        if self.args.log_file_no_info:
            file_handler.setLevel(logging.WARNING)
        elif self.args.log_with_board:
            file_handler.setLevel(logging.DEBUG)  # 如果启用HTML日志，则记录DEBUG级别
        else:
            file_handler.setLevel(logging.INFO)
            
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    def _create_console_handler(self, level, formatter, enabled=True):
        """创建控制台日志处理器"""
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(formatter, datefmt='%H:%M:%S'))
        handler.addFilter(LevelFilter(level))
        
        if not enabled:
            handler.setLevel(logging.CRITICAL + 1)  # 禁用处理器
        
        return handler
    
    def get_logger(self):
        """获取配置好的日志记录器"""
        return logging.getLogger("MinecraftMonitor")
    
    def get_log_filepath(self):
        """获取日志文件路径"""
        return self.log_filepath