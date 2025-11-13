import sys
import os
import argparse
from PySide6.QtWidgets import QApplication , QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, Signal, Qt
from video_player import ModernVideoPlayer
from config import (
    ICON_PATH,
    HOST,
    MEDIA_PORT,
    CONTADOR_PORT,
    SUPPORTED_VIDEO_EXTENSIONS,
    SUPPORTED_IMAGE_EXTENSIONS,
    API_URL
)

# Variável global para UpdateChecker (será inicializada no main)
update_checker = None

def get_version_api() -> str:
    """Obtém versão da API (lazy import para não atrasar inicialização)"""
    import requests
    
    URL = f"{API_URL}/mediaplayer/api/version"
    try:
        response = requests.get(URL, timeout=30)  # Timeout reduzido para 5s
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
        print(f"[APP] Erro ao conectar API: {e}")
    return None

class UpdateChecker(QObject):
    """Classe para verificar atualizações de forma thread-safe"""
    update_progress = Signal(str, int)  # mensagem, porcentagem (0-100, -1 = indeterminado)
    update_finished = Signal(bool, str)  # sucesso, mensagem
    show_confirmation_dialog = Signal(str, str)  # titulo, mensagem - NOVO SINAL
    request_app_exit = Signal()  # Novo sinal para fechar o app de forma thread-safe
    
    def __init__(self):
        super().__init__()
        self.progress_dialog = None
        self.user_response = None  # Armazena a resposta do usuário
        self.response_event = None  # Event para sincronização
        self.is_updating = False  # Flag para indicar se está atualizando
    
    def log_progress(self, message, percentage=-1):
        """Envia mensagem de progresso para a UI"""
        self.update_progress.emit(message, percentage)
    
    def ask_user_update(self, title, message):
        """
        Pergunta ao usuário se deseja atualizar (thread-safe).
        Emite sinal para mostrar dialog na thread principal e aguarda resposta.
        
        Returns:
            bool: True se usuário clicou Sim, False se clicou Não
        """
        import threading
        
        # Cria um Event para sincronização
        self.response_event = threading.Event()
        self.user_response = None
        
        # Emite sinal para a thread principal mostrar o dialog
        self.show_confirmation_dialog.emit(title, message)
        
        # Aguarda resposta do usuário (bloqueia a thread de atualização)
        self.response_event.wait(timeout=60)  # 60 segundos de timeout
        
        # Retorna a resposta (ou False se timeout)
        return self.user_response if self.user_response is not None else False
    
    def set_user_response(self, response):
        """
        Define a resposta do usuário e libera a thread de atualização.
        Deve ser chamado pelo slot na thread principal.
        """
        self.user_response = response
        if self.response_event:
            self.response_event.set()
    
    def close_update_progress(self):
        """Fecha o diálogo de progresso"""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
    
    def cleanup(self):
        """Limpa todos os recursos do UpdateChecker"""
        try:
            # Fecha dialog se aberto
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
            
            # Libera Event se existir
            if self.response_event:
                self.response_event.set()
                self.response_event = None
            
            # Reset de flags
            self.user_response = None
            self.is_updating = False
            
            print("[APP] UpdateChecker cleanup concluído")
            
        except Exception as e:
            print(f"[APP] Erro no UpdateChecker cleanup: {e}")

def show_confirmation_dialog_slot(title, message):
    """
    Slot que mostra o QMessageBox na thread principal.
    Executa na thread da GUI e retorna a resposta via update_checker.
    """
    global update_checker
    
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.No)
    
    # Define textos em português
    yes_button = msg_box.button(QMessageBox.Yes)
    yes_button.setText("Sim")
    no_button = msg_box.button(QMessageBox.No)
    no_button.setText("Não")
    
    # Mostra o dialog e captura a resposta
    response = msg_box.exec()
    
    # Envia a resposta de volta para a thread de atualização
    user_clicked_yes = (response == QMessageBox.Yes)
    update_checker.set_user_response(user_clicked_yes)

def exit_app_slot():
    """
    Slot que fecha o aplicativo de forma segura na thread principal.
    É chamado quando a atualização termina e o app precisa fechar.
    """
    print("[APP] 🔄 Recebido sinal para fechar aplicativo...")
    
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    
    global update_checker
    
    # Fecha o progress dialog primeiro
    try:
        if update_checker and update_checker.progress_dialog:
            update_checker.progress_dialog.close()
            update_checker.progress_dialog = None
            print("[APP] Progress dialog fechado")
    except Exception as e:
        print(f"[APP] Erro ao fechar progress dialog: {e}")
    
    # Limpa o threading.Event se existir
    try:
        if update_checker and update_checker.response_event:
            update_checker.response_event.set()  # Libera qualquer wait() pendente
            update_checker.response_event = None
            print("[APP] Threading Event limpo")
    except Exception as e:
        print(f"[APP] Erro ao limpar Event: {e}")
    
    print("[APP] 🚀 Iniciando fechamento controlado...")
    
    # Agenda o fechamento para o próximo ciclo de eventos
    QTimer.singleShot(200, lambda: QApplication.instance().quit())
    
    # Força exit após 2 segundos caso o quit não funcione
    QTimer.singleShot(2000, lambda: os._exit(0))

def show_update_progress(message, percentage):
    """Atualiza o diálogo de progresso (chamado na thread principal)"""
    from PySide6.QtWidgets import QProgressDialog
    from PySide6.QtCore import Qt
    
    global update_checker
    
    # Cria o diálogo de progresso se não existir
    if update_checker.progress_dialog is None:
        update_checker.progress_dialog = QProgressDialog()
        update_checker.progress_dialog.setWindowTitle("Atualizando...")
        update_checker.progress_dialog.setWindowModality(Qt.ApplicationModal)
        update_checker.progress_dialog.setMinimumDuration(0)
        update_checker.progress_dialog.setCancelButton(None)  # Não permite cancelar
        update_checker.progress_dialog.setMinimum(0)
        update_checker.progress_dialog.setMaximum(100)
        update_checker.progress_dialog.show()
    
    # Atualiza a mensagem e progresso
    update_checker.progress_dialog.setLabelText(message)
    
    if percentage >= 0:
        update_checker.progress_dialog.setValue(percentage)
    else:
        # Progresso indeterminado
        update_checker.progress_dialog.setMaximum(0)
        update_checker.progress_dialog.setMinimum(0)

def close_update_progress(success, message):
    """Fecha o diálogo de progresso e mostra resultado"""
    from PySide6.QtWidgets import QMessageBox
    
    global update_checker
    
    # Fecha o diálogo de progresso
    if update_checker.progress_dialog:
        update_checker.progress_dialog.close()
        update_checker.progress_dialog = None
    
    # Mostra mensagem final apenas se houver erro
    if not success:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Erro na Atualização")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("Falha ao atualizar o aplicativo")
        msg_box.setInformativeText(message)
        msg_box.exec()

def updater_app():
    """Sistema de atualização integrado com API"""
    import requests
    import subprocess
    import time
    from utils import create_version_info, get_app_data_folder, get_version_info
    
    
    try:
        print("[APP] Verificando atualizações...")
        
        # Obtém versões
        local_version_info = get_version_info()
        remote_version = get_version_api()
        
        # Extrai versão do dicionário ou usa None
        local_version = local_version_info.get("version") if local_version_info else None
        
        # Primeira execução - salva versão remota
        if not local_version:
            print("[APP] Primeira execução - Configurando...")
            
            if remote_version:
                success = create_version_info(remote_version)
                if success:
                    print(f"[APP] Primeira execução - versão {remote_version} registrada")
                else:
                    print(f"[APP] Erro ao registrar versão, mas continuando...")
            else:
                print("[APP] Primeira execução sem conexão com API")
            return
        
        # Se não conseguiu conectar na API, continua com versão local
        if not remote_version:
            print("[APP] ⚠️ Não foi possível verificar atualizações (API offline)")
            return
        
        print(f"[APP] Versão local: {local_version}")
        print(f"[APP] Versão remota: {remote_version}")
        
        # Compara versões

        if float(remote_version) > float(local_version):
            print("[APP] 🎉 Nova atualização disponível!")
            
            # Pergunta ao usuário de forma thread-safe
            user_wants_update = update_checker.ask_user_update(
                "Atualização Disponível",
                f"Nova versão {remote_version} disponível!\n\nDeseja atualizar o app agora?"
            )

            if not user_wants_update:
                print("[APP] ❌ Atualização cancelada pelo usuário.")
                return
                
            print("[APP] 🚀 Iniciando atualização...")
            
            # Marca que está atualizando
            update_checker.is_updating = True
            
            # Etapa 1: Mostra progress dialog
            update_checker.log_progress("📥 Preparando download...", 10)
            
            # Etapa 2: Download
            print("[APP] 📥 Baixando atualização...")
            update_checker.log_progress("📥 Baixando atualização...", 20)
            
            # URL de download da API
            download_url = f"{API_URL}/mediaplayer/api/download"
            
            # Pasta temporária para download
            temp_folder = get_app_data_folder()
            os.makedirs(temp_folder, exist_ok=True)
            zip_path = os.path.join(temp_folder, "update_temp.zip")
            
            # Baixa o arquivo ZIP
            response = requests.get(download_url, timeout=120)
            if response.status_code == 200:
                # Etapa 3: Salvamento
                print(f"[APP] 💾 Salvando arquivo...")
                update_checker.log_progress("💾 Salvando arquivo...", 40)
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"[APP] ✅ Arquivo salvo: {zip_path}")
                
                # Etapa 4: Extração
                print(f"[APP] 📦 Extraindo arquivos...")
                update_checker.log_progress("📦 Extraindo arquivos...", 60)
                
                import zipfile
                extract_folder = os.path.join(temp_folder, "update_extracted")
                os.makedirs(extract_folder, exist_ok=True)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_folder)
                
                print(f"[APP] ✅ Arquivos extraídos: {extract_folder}")
                update_checker.log_progress("✅ Arquivos extraídos", 80)
                
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
                    
                    # Etapa 4: Preparação
                    print("[APP] 🔄 Preparando instalação...")
                    update_checker.log_progress("🔄 Preparando instalação...", 90)
                    
                    # Comando para executar updater.exe
                    cmd = [
                        updater_exe,
                        "--zip", extract_folder,  # Passa a pasta com os arquivos extraídos
                        "--target", app_dir,
                        "--process", process_name,
                        "--version", str(remote_version),
                        "--app-name", app_name
                    ]
                    
                    # Etapa 5: Instalação
                    print(f"[APP] 🚀 Iniciando instalação...")
                    update_checker.log_progress("🚀 Instalando atualização...", 95)
                    time.sleep(0.5)
                    
                    # Inicia updater e fecha o app
                    try:
                        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW if is_frozen else 0)
                        print("[APP] ✅ Atualizador iniciado - fechando aplicativo...")
                        
                        # Mensagem final com pequeno delay para usuário ver
                        update_checker.log_progress("✅ Reiniciando aplicativo...", 100)
                        time.sleep(1.5)  # Delay maior para garantir que o usuário veja
                        
                        # Emite sinal para fechar o app de forma thread-safe (GUI thread)
                        update_checker.request_app_exit.emit()
                        
                        # Aguarda o signal processar e então encerra a thread
                        time.sleep(1)
                        
                        print("[APP] 🔄 Thread de atualização finalizando...")
                        
                    except Exception as e:
                        error_msg = f"Erro ao iniciar updater: {str(e)}"
                        print(f"[APP] ❌ {error_msg}")
                        update_checker.update_finished.emit(False, error_msg)
                else:
                    error_msg = f"Updater não encontrado no pacote"
                    print(f"[APP] ❌ {error_msg}: {updater_exe}")
                    print(f"[APP] ⚠️ O ZIP de atualização deve conter updater.exe")
                    update_checker.update_finished.emit(False, error_msg)

            else:
                error_msg = f"Erro ao baixar: HTTP {response.status_code}"
                print(f"[APP] ❌ {error_msg}")
                update_checker.update_finished.emit(False, error_msg)
                    
        else:
            print("[APP] ✅ Você está usando a versão mais recente!")
                
            
    except Exception as e:
        error_msg = f"Erro no sistema de atualização: {str(e)}"
        print(f"[APP] ❌ {error_msg}")
        import traceback
        traceback.print_exc()
        print("[APP] ⚠️ Continuando execução normal...")
        if update_checker:
            update_checker.update_finished.emit(False, error_msg)




async def handle_client(reader, writer):
    import asyncio
    addr = writer.get_extra_info("peername")
    print(f"[SERVER] Conectado por {addr}")
    while True:
        data = await reader.read(1024)
        if not data:
            break
        print(f"[SERVER] Recebido: {data.decode()}")
    writer.close()

async def server():
    import asyncio
    server = await asyncio.start_server(handle_client, HOST, MEDIA_PORT)
    print(f"[SERVER] Escutando em {HOST}:{MEDIA_PORT}")
    async with server:
        await server.serve_forever()

async def client():
    import asyncio
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
    import asyncio
    asyncio.run_coroutine_threadsafe(client(), loop)
    print("[APP] Cliente iniciado manualmente no asyncio loop.")

def run_asyncio_loop(loop):
    import asyncio
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
    # Configura handler para saída limpa
    import signal
    
    def signal_handler(sig, frame):
        print(f"[APP] Sinal recebido: {sig}")
        QApplication.quit()
        os._exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Cria o QApplication ANTES de qualquer interface
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(ICON_PATH, "road.png")))

    # Parse dos argumentos da linha de comando (rápido)
    args = parse_arguments()
    
    # Se houve erro no parsing dos argumentos, encerra o programa
    if args is None:
        sys.exit(1)

    # Inicia o player PRIMEIRO (mostra UI rapidamente)
    player = ModernVideoPlayer()
    player.show()
    
    # Processa eventos para garantir que a janela apareça
    app.processEvents()
    
    # Cria instância global do UpdateChecker
    update_checker = UpdateChecker()
    
    # Conecta o sinal para mostrar diálogo de confirmação na thread principal
    update_checker.show_confirmation_dialog.connect(show_confirmation_dialog_slot)
    
    # Conecta o sinal para fechar o app de forma thread-safe
    update_checker.request_app_exit.connect(exit_app_slot)
    
    # Conecta sinais de progresso
    update_checker.update_progress.connect(show_update_progress)
    update_checker.update_finished.connect(close_update_progress)
    
    # Sistema de auto-update - verifica atualizações EM BACKGROUND (não bloqueia UI)
    from threading import Thread
    update_thread = Thread(target=updater_app, daemon=True)
    update_thread.start()

    # Cria o asyncio loop (lazy import)
    import asyncio
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

    # Executa o app e captura o código de saída
    try:
        print("[APP] Iniciando loop de eventos Qt...")
        exit_code = app.exec()
        print(f"[APP] Loop Qt encerrado com código: {exit_code}")
    except Exception as e:
        print(f"[APP] Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    
    # Cleanup antes de sair
    print("[APP] Iniciando processo de limpeza...")
    
    try:
        # Limpa o UpdateChecker primeiro
        if 'update_checker' in locals() and update_checker:
            try:
                update_checker.cleanup()
            except Exception as e:
                print(f"[APP] Erro no cleanup do UpdateChecker: {e}")
    except Exception as e:
        print(f"[APP] Erro geral no UpdateChecker: {e}")
    
    try:
        # Fecha o player se ainda estiver aberto
        if 'player' in locals() and player:
            try:
                player.close()
                print("[APP] Player fechado")
            except Exception as e:
                print(f"[APP] Erro ao fechar player: {e}")
    except Exception as e:
        print(f"[APP] Erro no cleanup do player: {e}")
    
    try:
        # Para o loop asyncio se existir
        if 'loop' in locals() and loop and loop.is_running():
            loop.call_soon_threadsafe(loop.stop)
            print("[APP] Loop asyncio parado")
    except Exception as e:
        print(f"[APP] Erro no cleanup asyncio: {e}")
    
    try:
        # Processa eventos pendentes antes de sair
        app.processEvents()
        print("[APP] Eventos pendentes processados")
    except Exception as e:
        print(f"[APP] Erro ao processar eventos: {e}")
    
    print(f"[APP] Encerrando aplicativo com código {exit_code}...")
    
    # Pequeno delay final para garantir cleanup
    try:
        import time
        time.sleep(0.1)
    except:
        pass
    
    # Sai de forma limpa (threads daemon morrem automaticamente)
    sys.exit(exit_code)
