"""
Utility functions for PPL Player.
Contains helper functions used across the application.
"""

import os
from typing import Tuple


def format_time(milliseconds: int) -> str:
    """
    Convert milliseconds to MM:SS format.
    
    Args:
        milliseconds (int): Time in milliseconds
        
    Returns:
        str: Formatted time string (MM:SS)
    """
    if milliseconds < 0:
        return "00:00"
        
    seconds = int(milliseconds / 1000)
    minutes, secs = divmod(seconds, 60)
    return f"{minutes:02}:{secs:02}"


def format_time_range(current_ms: int, total_ms: int) -> str:
    """
    Format current and total time for display.
    
    Args:
        current_ms (int): Current time in milliseconds
        total_ms (int): Total duration in milliseconds
        
    Returns:
        str: Formatted time range string (current / total)
    """
    current_str = format_time(current_ms)
    total_str = format_time(total_ms)
    return f"{current_str} / {total_str}"


def is_video_file(file_path: str) -> bool:
    """
    Check if a file is a supported video format.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file is a supported video format
    """
    from config import SUPPORTED_VIDEO_EXTENSIONS
    
    if not os.path.exists(file_path):
        return False
        
    return file_path.lower().endswith(SUPPORTED_VIDEO_EXTENSIONS)


def get_video_files_from_directory(directory_path: str) -> list:
    """
    Get all video files from a directory.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        list: List of video file paths
    """
    if not os.path.isdir(directory_path):
        return []
        
    video_files = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if is_video_file(file_path):
            video_files.append(file_path)
            
    return sorted(video_files)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero.
    
    Args:
        numerator (float): The numerator
        denominator (float): The denominator
        default (float): Default value to return if division by zero
        
    Returns:
        float: Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between min and max values.
    
    Args:
        value (float): Value to clamp
        min_value (float): Minimum allowed value
        max_value (float): Maximum allowed value
        
    Returns:
        float: Clamped value
    """
    return max(min_value, min(max_value, value))


def validate_file_path(file_path: str) -> Tuple[bool, str]:
    """
    Validate if a file path exists and is accessible.
    
    Args:
        file_path (str): Path to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not file_path:
        return False, "Caminho do arquivo está vazio"
        
    if not os.path.exists(file_path):
        return False, f"Arquivo não encontrado: {file_path}"
        
    if not os.path.isfile(file_path):
        return False, f"Caminho não é um arquivo: {file_path}"
        
    if not os.access(file_path, os.R_OK):
        return False, f"Arquivo não pode ser lido: {file_path}"
        
    return True, ""


def get_file_size_string(file_path: str) -> str:
    """
    Get human-readable file size string.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Human-readable file size (e.g., "1.5 MB")
    """
    try:
        size_bytes = os.path.getsize(file_path)
        
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.1f} MB"
        else:
            return f"{size_bytes / (1024 ** 3):.1f} GB"
            
    except OSError:
        return "Tamanho desconhecido"
