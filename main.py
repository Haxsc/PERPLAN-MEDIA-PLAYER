import sys
import os
import argparse
import requests
import subprocess
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from utils import create_version_info, download_and_extract, get_app_data_folder, get_updater, get_version_info
from video_player import ModernVideoPlayer
import asyncio
from threading import Thread
from config import (
    ICON_PATH,
    HOST,
    MEDIA_PORT,
    CONTADOR_PORT,
    SUPPORTED_VIDEO_EXTENSIONS,
    SUPPORTED_IMAGE_EXTENSIONS
)

def get_version_api() -> str:
    URL = "http://localhost:1234/api/version"
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            data = response.json()
            version = data.get("version")
            if version:
                return version
            else:
                print("[APP] Versão não encontrada na resposta da API.")
        else:
            print(f"[APP] Erro ao obter informações da versão: {response.status_code}")
    except Exception as e:
        print(f"[APP] Erro: {e}")
    return None

def updater_app():
    """Sistema de atualização integrado com API"""
    
    try:
        # Obtém versões
        local_version_info = get_version_info()
        remote_version = get_version_api()
        
        # Extrai versão do dicionário ou usa None
        local_version = local_version_info.get("version") if local_version_info else None
        
        # Primeira execução - salva versão remota
        if not local_version:
            if remote_version:
                create_version_info(remote_version)
                print(f"[APP] Primeira execução - versão {remote_version} registrada")
            return
        
        # Se não conseguiu conectar na API, continua com versão local
        if not remote_version:
            print("[APP] ⚠️ Não foi possível verificar atualizações (API offline)")
            return
        
        print(f"[APP] Versão local: {local_version}")
        print(f"[APP] Versão remota: {remote_version}")
        
        # Compara versões
        try:
            if float(remote_version) > float(local_version):
                print("[APP] 🎉 Nova atualização disponível!")
                print("[APP] 💾 Baixando atualização...")
                
                # URL de download da API
                download_url = "http://localhost:1234/api/download"
                
                # Pasta temporária para download
                temp_folder = get_app_data_folder()
                os.makedirs(temp_folder, exist_ok=True)
                zip_path = os.path.join(temp_folder, "update_temp.zip")
                
                # Baixa o arquivo ZIP
                response = requests.get(download_url, timeout=30)
                if response.status_code == 200:
                    # Salva arquivo
                    with open(zip_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"[APP] ✅ Atualização baixada: {zip_path}")
                    
                    # Extrai os arquivos na pasta temporária
                    import zipfile
                    extract_folder = os.path.join(temp_folder, "update_extracted")
                    os.makedirs(extract_folder, exist_ok=True)
                    
                    print(f"[APP] 📦 Extraindo atualização...")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder)
                    print(f"[APP] ✅ Arquivos extraídos em: {extract_folder}")
                    
                    # Procura updater.exe nos arquivos extraídos
                    updater_exe = os.path.join(extract_folder, "updater.exe")
                    
                    if os.path.exists(updater_exe):
                        # Detecta se está rodando como executável ou script
                        is_frozen = getattr(sys, 'frozen', False)
                        
                        if is_frozen:
                            # Rodando como executável (.exe)
                            app_exe = sys.executable  # Caminho do .exe atual
                            app_dir = os.path.dirname(app_exe)
                            app_name = os.path.basename(app_exe)
                            process_name = app_name
                        else:
                            # Rodando como script Python
                            app_dir = os.path.dirname(os.path.abspath(__file__))
                            app_name = "main.py"
                            process_name = "python.exe"
                        
                        print("[APP] 🔄 Iniciando atualizador...")
                        
                        # Comando para executar updater.exe
                        cmd = [
                            updater_exe,
                            "--zip", extract_folder,  # Passa a pasta com os arquivos extraídos
                            "--target", app_dir,
                            "--process", process_name,
                            "--version", str(remote_version),
                            "--app-name", app_name
                        ]
                        
                        print(f"[APP] Executando: {' '.join(cmd)}")
                        
                        # Inicia updater e fecha o app
                        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW if is_frozen else 0)
                        print("[APP] ✅ Atualizador iniciado - fechando aplicativo...")
                        time.sleep(1)
                        sys.exit(0)
                    else:
                        print(f"[APP] ❌ Updater não encontrado no pacote: {updater_exe}")
                        print(f"[APP] ⚠️ O ZIP de atualização deve conter updater.exe")

                else:
                    print(f"[APP] ❌ Erro ao baixar: HTTP {response.status_code}")
                    
            else:
                print("[APP] ✅ Você está usando a versão mais recente!")
                
        except ValueError:
            print("[APP] ❌ Erro ao comparar versões (formato inválido)")
        except Exception as e:
            print(f"[APP] ❌ Erro durante atualização: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"[APP] ❌ Erro no sistema de atualização: {e}")
        import traceback
        traceback.print_exc()
        print("[APP] ⚠️ Continuando execução normal...")




async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"[SERVER] Conectado por {addr}")
    while True:
        data = await reader.read(1024)
        if not data:
            break
        print(f"[SERVER] Recebido: {data.decode()}")
    writer.close()

async def server():
    server = await asyncio.start_server(handle_client, HOST, MEDIA_PORT)
    print(f"[SERVER] Escutando em {HOST}:{MEDIA_PORT}")
    async with server:
        await server.serve_forever()

async def client():
    try:
        reader, writer = await asyncio.open_connection(HOST, CONTADOR_PORT)
        print(f"[CLIENT] Conectado ao peer em {HOST}:{CONTADOR_PORT}")
    except ConnectionRefusedError:
        print("[CLIENT] Não foi possível conectar, peer não disponível.")
        return

    async def send_messages():
        while True:
            msg = await asyncio.get_event_loop().run_in_executor(None, input)
            if msg.strip().lower() == "sair":
                writer.close()
                await writer.wait_closed()
                break
            writer.write(msg.encode())
            await writer.drain()

    async def receive_messages():
        while True:
            data = await reader.read(1024)
            if not data:
                break
            print(f"[CLIENT] Recebido: {data.decode()}")

    await asyncio.gather(send_messages(), receive_messages())

def start_server(loop):
    loop.create_task(server())
    print("[APP] Servidor iniciado no asyncio loop.")

def start_client(loop):
    asyncio.run_coroutine_threadsafe(client(), loop)
    print("[APP] Cliente iniciado manualmente no asyncio loop.")

def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Aplicativo ModernVideoPlayer")

    parser.add_argument("--croqui", type=str, help="Caminho para o arquivo de imagem do croqui")
    parser.add_argument("--video", type=str, help="Caminho para o arquivo de vídeo")

    args = parser.parse_args()

    # Normaliza e verifica os caminhos
    if args.croqui:
        croqui_path = os.path.normpath(args.croqui)
        if not os.path.exists(croqui_path):
            print(f"[ERRO] Arquivo do croqui não existe: {croqui_path}")
            return None
        else:
            # Verifica se é um arquivo de imagem
            if not croqui_path.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS):
                print(f"[ERRO] Arquivo do croqui deve ser uma imagem: {croqui_path}")
                return None
            print(f"[OK] Croqui recebido: {croqui_path}")

    if args.video:
        video_path = os.path.normpath(args.video)
        if not os.path.exists(video_path):
            print(f"[ERRO] Arquivo do vídeo não existe: {video_path}")
            return None
        else:
            # Verifica se é um arquivo de vídeo suportado
            if not video_path.lower().endswith(SUPPORTED_VIDEO_EXTENSIONS):
                print(f"[ERRO] Formato de vídeo não suportado: {video_path}")
                return None
            print(f"[OK] Vídeo recebido: {video_path}")

    return args

if __name__ == "__main__":
    # Sistema de auto-update - verifica atualizações antes de iniciar
    updater_app()

    app = QApplication(sys.argv)  # Cria o QApplication antes de qualquer QWidget
    app.setWindowIcon(QIcon(os.path.join(ICON_PATH, "road.png")))

    # Parse dos argumentos da linha de comando
    args = parse_arguments()
    
    # Se houve erro no parsing dos argumentos, encerra o programa
    if args is None:
        sys.exit(1)

    # Inicia o player
    player = ModernVideoPlayer()
    player.show()

    # Cria o asyncio loop
    loop = asyncio.new_event_loop()

    # Inicia o asyncio em thread separada (não trava o Qt)
    t = Thread(target=run_asyncio_loop, args=(loop,), daemon=True)
    t.start()

    # Inicia o servidor automaticamente
    #start_server(loop)

    # Processa argumentos recebidos
    croqui_accepted = True  # Por padrão, aceita continuar
    
    # Se foi passado um croqui, abre o modal
    if args.croqui:
        croqui_accepted = player.open_croqui_modal(args.croqui)
        if not croqui_accepted:
            print("[INFO] Aplicativo encerrado - croqui cancelado pelo usuário")
            sys.exit(0)

    # Se foi passado um vídeo e o croqui foi aceito (ou não havia croqui), carrega o vídeo
    if args.video and croqui_accepted:
        if os.path.exists(args.video) and args.video.lower().endswith(SUPPORTED_VIDEO_EXTENSIONS):
            player.playlist.append(args.video)
            player.current_video_index = 0
            player.open_file(args.video)
        
    # Check if app was opened with a video file (compatibilidade com versão anterior)
    elif len(sys.argv) > 1 and not args.croqui and not args.video:
        video_path = sys.argv[1]
        if os.path.exists(video_path) and video_path.lower().endswith(SUPPORTED_VIDEO_EXTENSIONS):
            player.playlist.append(video_path)
            player.current_video_index = 0
            player.open_file(video_path)

    sys.exit(app.exec())
