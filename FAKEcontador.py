import asyncio

HOST = "localhost"
CONTADOR_PORT = 3000  # Porta deste app
MEDIA_PORT = 1337  # Porta do app principal


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
    server = await asyncio.start_server(handle_client, HOST, CONTADOR_PORT)
    print(f"[SERVER] Escutando em {HOST}:{CONTADOR_PORT}")
    async with server:
        await server.serve_forever()


async def client():
    try:
        reader, writer = await asyncio.open_connection(HOST, MEDIA_PORT)
        print(f"[CLIENT] Conectado ao peer em {HOST}:{MEDIA_PORT}")
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


async def main():
    # Inicia servidor e cliente juntos
    await asyncio.gather(server(), client())


if __name__ == "__main__":
    asyncio.run(main())
