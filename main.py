import sys
import os
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from video_player import ModernVideoPlayer
import asyncio
from threading import Thread
from config import (
    ICON_PATH,
    HOST,
    MEDIA_PORT,
    CONTADOR_PORT,
    SUPPORTED_VIDEO_EXTENSIONS
)


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

    parser.add_argument("--croqui", type=str, help="Diretório do croqui")
    parser.add_argument("--video", type=str, help="Diretório do vídeo")
    # parser.add_argument('--opencoqui', action='store_true', help='Abrir automaticamente o croqui')

    args = parser.parse_args()

    # Normaliza e verifica os caminhos
    if args.croqui:
        croqui_path = os.path.normpath(args.croqui)
        if not os.path.exists(croqui_path):
            print(f"[ERRO] Diretório do croqui não existe: {croqui_path}")
        else:
            print(f"[OK] Croqui recebido: {croqui_path}")

    if args.video:
        video_path = os.path.normpath(args.video)
        if not os.path.exists(video_path):
            print(f"[ERRO] Diretório do vídeo não existe: {video_path}")
        else:
            print(f"[OK] Vídeo recebido: {video_path}")

    # if args.opencoqui:
    #     print("[INFO] Flag --opencoqui ativada")

    return args


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Cria o QApplication antes de qualquer QWidget
    app.setWindowIcon(QIcon(os.path.join(ICON_PATH, "road.png")))

    # armazenamento de ARGS *FUTURO DINAMICO*

    # argv_1 = sys.argv[1]
    # argv_2 = sys.argv[2]
    # argv_3 = sys.argv[3]

    #################################
    #
    # EXEMPLO:
    # args = parse_arguments()
    #
    # if args.opencoqui:
    #   print("Abrindo croqui automaticamente...")
    #
    ################################

    # Inicia o player normalmente

    player = ModernVideoPlayer()
    player.show()

    # Cria o asyncio loop
    loop = asyncio.new_event_loop()

    # Inicia o asyncio em thread separada (não trava o Qt)
    t = Thread(target=run_asyncio_loop, args=(loop,), daemon=True)
    t.start()

    # Inicia o servidor automaticamente
    start_server(loop)

    # Check if app was opened with a video file
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        if os.path.exists(video_path) and video_path.lower().endswith(SUPPORTED_VIDEO_EXTENSIONS):
            player.playlist.append(video_path)
            player.current_video_index = 0
            player.open_file(video_path)

    sys.exit(app.exec())
