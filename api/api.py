from flask import Flask, jsonify, send_file
import os
import zipfile

app = Flask(__name__)

# Versão atual disponível
CURRENT_VERSION = 3

# Pasta onde ficam os arquivos de atualização
UPDATE_FILES_DIR = "updates"

# Cria pasta se não existir
os.makedirs(UPDATE_FILES_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    """Página inicial da API"""
    files_in_updates = []
    if os.path.exists(UPDATE_FILES_DIR):
        files_in_updates = [f for f in os.listdir(UPDATE_FILES_DIR) if f.endswith('.zip')]
    
    return jsonify({
        "message": "API de Atualizações PERPLAN Media Player",
        "version": CURRENT_VERSION,
        "endpoints": {
            "check_update": "/api/update",
            "get_version": "/api/version", 
            "download": "/api/download"
        },
        "update_files_dir": os.path.abspath(UPDATE_FILES_DIR),
        "files_available": files_in_updates
    })

@app.route("/api/update", methods=["GET"])
def check_update():
    """Endpoint para verificar atualizações"""
    return jsonify({
        "version": CURRENT_VERSION,
        "download_url": "http://localhost:1234/api/download",
        "changelog": "Melhorias de performance e correções de bugs"
    })

@app.route("/api/version", methods=["GET"])
def get_version():
    """Endpoint para obter informações da versão"""
    return jsonify({
        "version": CURRENT_VERSION
    })

@app.route("/api/download", methods=["GET"])
def download_update():
    """Endpoint para baixar arquivo de atualização da máquina"""
    try:
        # Nome do arquivo de atualização
        filename = f"update_v{CURRENT_VERSION}.zip"
        file_path = os.path.join(UPDATE_FILES_DIR, filename)
        
        # Verifica se arquivo existe
        if os.path.exists(file_path):
            print(f"[API] Enviando arquivo: {file_path}")
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/zip'
            )
        else:
            # Se não existe, cria arquivo de exemplo para teste
            print(f"[API] ⚠️ Arquivo não encontrado, criando exemplo: {file_path}")
            create_sample_update_file(file_path)
            
            if os.path.exists(file_path):
                print(f"[API] Enviando arquivo criado: {file_path}")
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/zip'
                )
            else:
                return jsonify({
                    "error": "Arquivo de atualização não encontrado",
                    "message": f"Coloque o arquivo {filename} na pasta {UPDATE_FILES_DIR}"
                }), 404
                
    except Exception as e:
        print(f"[API] ❌ Erro ao enviar arquivo: {e}")
        return jsonify({
            "error": f"Erro interno: {str(e)}"
        }), 500

def create_sample_update_file(file_path):
    """Cria arquivo de atualização de exemplo"""
    try:
        print(f"[API] Criando arquivo de exemplo: {file_path}")
        
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Adiciona arquivos de exemplo
            zipf.writestr("README.txt", f"""
PERPLAN Media Player - Atualização v{CURRENT_VERSION}
===============================================

Esta é uma atualização de exemplo.

Para criar um pacote de atualização real:
1. Compile seus arquivos .exe
2. Coloque os executáveis neste ZIP
3. Salve como: {os.path.basename(file_path)}
4. Coloque na pasta: {UPDATE_FILES_DIR}

Arquivos que devem estar no ZIP:
- PPL Player.exe (executável principal)
- updater.exe (atualizador)
- Outros arquivos necessários (.dll, recursos, etc)
""")
            
            zipf.writestr("changelog.txt", f"""
Versão {CURRENT_VERSION}
- Melhorias de performance
- Correções de bugs
- Sistema de atualização automática
- Otimizações para PCs fracos
""")
            
            zipf.writestr("version.txt", str(CURRENT_VERSION))
        
        print(f"[API] ✅ Arquivo de exemplo criado: {file_path}")
        
    except Exception as e:
        print(f"[API] ❌ Erro ao criar arquivo: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 API de Atualizações PERPLAN Media Player")
    print("=" * 60)
    print(f"📡 Versão atual: {CURRENT_VERSION}")
    print(f"📁 Pasta de atualizações: {os.path.abspath(UPDATE_FILES_DIR)}")
    print(f"🌐 Rodando em: http://localhost:1234")
    print("\n📋 Endpoints disponíveis:")
    print("   GET  /                - Informações da API")
    print("   GET  /api/update      - Verificar atualizações")
    print("   GET  /api/version     - Obter versão atual")
    print("   GET  /api/download    - Baixar arquivo de atualização")
    print("\n⚠️ IMPORTANTE: Coloque seu arquivo ZIP em:")
    print(f"   {os.path.abspath(UPDATE_FILES_DIR)}/update_v{CURRENT_VERSION}.zip")
    print("=" * 60)
    print()
    
    app.run(debug=True, port=1234, host="0.0.0.0")