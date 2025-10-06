from flask import Flask, jsonify, send_file, request
import os
import zipfile
import re
import json

app = Flask(__name__)

UPDATE_FILES_DIR = "updates"
VERSION_FILE = "version.json"

os.makedirs(UPDATE_FILES_DIR, exist_ok=True)

def load_version():
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"version": 3, "changelog": "Melhorias de performance e correções de bugs"}

def save_version(version_data):
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(version_data, f, indent=2, ensure_ascii=False)

version_data = load_version()
CURRENT_VERSION = version_data["version"]

@app.route("/", methods=["GET"])
def home():
    files_in_updates = [f for f in os.listdir(UPDATE_FILES_DIR) if f.endswith('.zip')] if os.path.exists(UPDATE_FILES_DIR) else []
    
    return jsonify({
        "message": "API de Atualizações PERPLAN Media Player",
        "version": CURRENT_VERSION,
        "endpoints": {
            "check_update": "/api/update",
            "get_version": "/api/version", 
            "download": "/api/download"
        },
        "files_available": files_in_updates
    })

@app.route("/api/update", methods=["GET"])
def check_update():
    version_data = load_version()
    return jsonify({
        "version": version_data["version"],
        "download_url": "http://localhost:1234/api/download",
        "changelog": version_data.get("changelog", "Atualização disponível")
    })

@app.route("/api/version", methods=["GET"])
def get_version():
    version_data = load_version()
    return jsonify({"version": version_data["version"]})

@app.route("/api/download", methods=["GET"])
def download_update():
    try:
        version_data = load_version()
        filename = f"update_v{version_data['version']}.zip"
        file_path = os.path.join(UPDATE_FILES_DIR, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename, mimetype='application/zip')
        else:
            create_sample_update_file(file_path)
            
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True, download_name=filename, mimetype='application/zip')
            else:
                return jsonify({"error": "Arquivo de atualização não encontrado"}), 404
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_sample_update_file(file_path):
    try:
        version_data = load_version()
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("README.txt", f"PERPLAN Media Player - Atualização v{version_data['version']}")
            zipf.writestr("changelog.txt", version_data.get("changelog", "Atualização disponível"))
            zipf.writestr("version.txt", str(version_data['version']))
    except Exception as e:
        print(f"Erro ao criar arquivo: {e}")

@app.route("/api/upload", methods=["POST"])
def upload_update():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
        file = request.files['file']
        changelog = request.form.get('changelog', 'Nova atualização disponível')
        
        if file.filename == '':
            return jsonify({"error": "Nome do arquivo vazio"}), 400
        
        if not file.filename.endswith('.zip'):
            return jsonify({"error": "Arquivo deve ser .zip"}), 400
        
        match = re.search(r'v?(\d+(?:\.\d+)?)', file.filename)
        if not match:
            return jsonify({"error": "Nome do arquivo deve conter versão (ex: update_v4.0.zip)"}), 400
        
        new_version = match.group(1)
        
        for old_file in os.listdir(UPDATE_FILES_DIR):
            if old_file.endswith('.zip'):
                old_path = os.path.join(UPDATE_FILES_DIR, old_file)
                os.remove(old_path)
                print(f"Removido: {old_file}")
        
        new_filename = f"update_v{new_version}.zip"
        file_path = os.path.join(UPDATE_FILES_DIR, new_filename)
        file.save(file_path)
        
        try:
            version_number = float(new_version)
        except:
            version_number = int(float(new_version))
        
        new_version_data = {
            "version": version_number,
            "changelog": changelog
        }
        save_version(new_version_data)
        
        global CURRENT_VERSION
        CURRENT_VERSION = version_number
        
        print(f"Nova versão: {version_number}")
        print(f"Arquivo salvo: {new_filename}")
        print(f"Changelog: {changelog}")
        
        return jsonify({
            "success": True,
            "message": "Atualização enviada com sucesso",
            "version": version_number,
            "changelog": changelog,
            "filename": new_filename
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    version_data = load_version()
    print(f"API de Atualizações PERPLAN Media Player v{version_data['version']}")
    print(f"Changelog: {version_data.get('changelog', 'N/A')}")
    print(f"Rodando em: http://localhost:1234")
    app.run(port=1234, host="0.0.0.0")