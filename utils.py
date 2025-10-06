"""
Utility functions for PPL Player.
Contains helper functions used across the application.
"""

import os
from typing import Tuple
from datetime import datetime
import json
import requests
import zipfile
import tempfile


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

def get_app_data_folder():
    """Retorna o caminho da pasta de dados do app"""
    if os.name == 'nt':  # Windows
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:  # Linux/Mac
        app_data = os.path.expanduser('~/.local/share')
    
    return os.path.join(app_data, 'perplan-media')

def create_version_info(version):
    """Cria arquivo de informações detalhadas da versão"""
    try:
        app_folder = get_app_data_folder()
        info_file = os.path.join(app_folder, 'version_info.json')
        
        version_info = {
            "version": str(version),
        }
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)
        
        print(f"[VERSION] Informações salvas: {info_file}")
        return True
        
    except Exception as e:
        print(f"[VERSION] Erro ao salvar informações: {e}")
        return False

def get_version_info():
    """Lê informações detalhadas da versão"""
    try:
        app_folder = get_app_data_folder()
        info_file = os.path.join(app_folder, 'version_info.json')
        
        if os.path.exists(info_file):
            with open(info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
        
    except Exception as e:
        print(f"[VERSION] Erro ao ler informações: {e}")
        return None

def get_updater() -> str:
    try:
        app_folder = get_app_data_folder()
        info_file = os.path.join(app_folder, 'updater.exe')
        
        if os.path.exists(info_file):
            return info_file
        return None
        
    except Exception as e:
        print(f"[VERSION] Erro ao ler informações: {e}")
        return None
    
def download_and_extract(url, extract_to=None):
    """Download simples e extração em local específico"""
    try:
        print(f"[DOWNLOAD] Baixando: {url}")
        
        # Define pasta de extração
        if extract_to is None:
            extract_to = os.getcwd()  # Pasta atual do app
        
        # Cria pasta se não existir
        os.makedirs(extract_to, exist_ok=True)
        
        # Baixa o arquivo
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # Salva temporariamente
            temp_file = os.path.join(tempfile.gettempdir(), "update_temp.zip")
            
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            print(f"[DOWNLOAD] ✅ Arquivo baixado")
            
            # Extrai para local específico
            print(f"[EXTRACT] Extraindo para: {extract_to}")
            
            with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            # Remove arquivo temporário
            os.remove(temp_file)
            
            print(f"[EXTRACT] ✅ Extração concluída em: {extract_to}")
            return True
            
        else:
            print(f"[DOWNLOAD] ❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[DOWNLOAD] ❌ Erro: {e}")
        return False