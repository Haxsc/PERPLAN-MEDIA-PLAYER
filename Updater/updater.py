import argparse
import os
import shutil
import subprocess
import time
import sys
import zipfile
import tempfile
import json


def wait_for_process_to_close(process_name, timeout=30):
    """Aguarda processo específico fechar co                     print(f"[UPDATER] ⚠️ Reinicie o aplicativo manualmente")
                print(f"[UPDATER] Local: {args.target}")
        
        # Auto-exclusão
        time.sleep(2)     print(f"[UPDATER] ⚠️ Reinicie o aplicativo manualmente")
                print(f"[UPDATER] Local: {args.target}")
        
        # Auto-exclusão
        time.sleep(2)
        schedule_self_delete()ut"""
    print(f"[UPDATER] Aguardando processo '{process_name}' fechar...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            tasks = os.popen("tasklist").read().lower()
            # Verifica se o processo específico está na lista
            found = False
            for line in tasks.split('\n'):
                if process_name.lower() in line:
                    found = True
                    break
            
            if not found:
                print(f"[UPDATER] ✅ Processo '{process_name}' encerrado")
                time.sleep(1)  # Aguarda extra para liberar arquivos
                return True
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[UPDATER] ⚠️ Erro ao verificar processo: {e}")
            time.sleep(1)
    
    print(f"[UPDATER] ⚠️ Timeout aguardando processo fechar")
    return False





def copy_update_files(source_dir, target_dir, exclude_updater=True):
    """Copia arquivos da pasta de atualização para pasta alvo"""
    try:
        print(f"[UPDATER] 📦 Copiando arquivos...")
        print(f"[UPDATER]   De: {source_dir}")
        print(f"[UPDATER]   Para: {target_dir}")
        
        if not os.path.exists(source_dir):
            print(f"[UPDATER] ❌ Pasta de origem não encontrada: {source_dir}")
            return False
        
        # Lista todos os arquivos
        files_copied = 0
        for item in os.listdir(source_dir):
            # Não copia o próprio updater
            if exclude_updater and item.lower() == "updater.exe":
                print(f"[UPDATER]   ⊘ Pulando: {item}")
                continue
            
            source_path = os.path.join(source_dir, item)
            target_path = os.path.join(target_dir, item)
            
            try:
                if os.path.isfile(source_path):
                    # Copia arquivo
                    shutil.copy2(source_path, target_path)
                    print(f"[UPDATER]   ✓ {item}")
                    files_copied += 1
                elif os.path.isdir(source_path):
                    # Copia pasta inteira
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)
                    print(f"[UPDATER]   ✓ {item}/ (pasta)")
                    files_copied += 1
            except Exception as e:
                print(f"[UPDATER]   ✗ Erro ao copiar {item}: {e}")
        
        print(f"[UPDATER] ✅ {files_copied} itens copiados com sucesso")
        return files_copied > 0
        
    except Exception as e:
        print(f"[UPDATER] ❌ Erro ao copiar arquivos: {e}")
        return False


def update_version_file(target_dir, new_version):
    """Atualiza version_info.json na pasta perplan-media"""
    try:
        # Atualiza arquivo na pasta de dados do app
        if os.name == 'nt':
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        else:
            app_data = os.path.expanduser('~/.local/share')
        
        version_dir = os.path.join(app_data, 'perplan-media')
        os.makedirs(version_dir, exist_ok=True)
        
        version_file = os.path.join(version_dir, 'version_info.json')
        
        # Lê arquivo existente ou cria novo
        version_info = {"version": str(new_version)}
        
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_info = json.load(f)
            except:
                pass
        
        # Atualiza versão
        version_info["version"] = str(new_version)
        
        # Salva arquivo
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)
        
        print(f"[UPDATER] ✅ Versão atualizada para: {new_version} em {version_file}")
        return True
        
    except Exception as e:
        print(f"[UPDATER] ⚠️ Erro ao atualizar versão: {e}")
        return False


def restart_app(app_dir, main_script="main.py"):
    """Reinicia o aplicativo"""
    try:
        print(f"[UPDATER] 🔄 Reiniciando aplicativo...")
        
        # Se for executável compilado
        exe_path = os.path.join(app_dir, "PPL Player.exe")
        if os.path.exists(exe_path):
            subprocess.Popen([exe_path], cwd=app_dir)
            print(f"[UPDATER] ✅ Aplicativo reiniciado: {exe_path}")
            return True
        
        # Se for script Python
        main_path = os.path.join(app_dir, main_script)
        if os.path.exists(main_path):
            # Tenta encontrar Python
            python_cmd = "python"
            if shutil.which("python"):
                python_cmd = "python"
            elif shutil.which("python3"):
                python_cmd = "python3"
            
            subprocess.Popen([python_cmd, main_path], cwd=app_dir)
            print(f"[UPDATER] ✅ Aplicativo reiniciado: {main_path}")
            return True
        
        print(f"[UPDATER] ⚠️ Não foi possível encontrar executável")
        return False
        
    except Exception as e:
        print(f"[UPDATER] ❌ Erro ao reiniciar app: {e}")
        return False


def cleanup_temp_files(temp_folder):
    """Remove pasta temporária completa"""
    try:
        if os.path.exists(temp_folder):
            # Se for uma pasta, remove recursivamente
            if os.path.isdir(temp_folder):
                shutil.rmtree(temp_folder)
                print(f"[UPDATER] 🗑️ Pasta temporária removida: {temp_folder}")
            else:
                # Se for arquivo, remove normalmente
                os.remove(temp_folder)
                print(f"[UPDATER] 🗑️ Arquivo temporário removido")
    except Exception as e:
        print(f"[UPDATER] ⚠️ Erro ao limpar: {e}")


def schedule_self_delete():
    """Agenda auto-exclusão do updater"""
    if getattr(sys, "frozen", False):
        exe_path = sys.executable
        bat_path = exe_path + ".bat"
        try:
            with open(bat_path, "w") as f:
                f.write(f"""@echo off
ping 127.0.0.1 -n 5 > nul
del "{exe_path}" /f /q
del "{bat_path}" /f /q
""")
            subprocess.Popen([bat_path], creationflags=subprocess.CREATE_NO_WINDOW)
            print(f"[UPDATER] 🗑️ Auto-exclusão agendada")
        except Exception as e:
            print(f"[UPDATER] ⚠️ Erro ao agendar exclusão: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("PERPLAN Media Player - Atualizador")
    print("=" * 60)
    
    parser = argparse.ArgumentParser(description="Atualizador do PERPLAN Media Player")
    parser.add_argument("--zip", required=True, help="Pasta com arquivos extraídos da atualização")
    parser.add_argument("--target", required=True, help="Pasta de instalação do app")
    parser.add_argument("--process", required=True, help="Nome do processo principal do app")
    parser.add_argument("--version", help="Nova versão")
    parser.add_argument("--app-name", default="PPL Player.exe", help="Nome do executável principal")
    args = parser.parse_args()
    
    print(f"\n[UPDATER] Configuração:")
    print(f"[UPDATER]   Origem: {args.zip}")
    print(f"[UPDATER]   Destino: {args.target}")
    print(f"[UPDATER]   Processo: {args.process}")
    print(f"[UPDATER]   App Name: {args.app_name}")
    print(f"[UPDATER]   Versão: {args.version or 'N/A'}")
    print()
    
    # Etapa 1: Aguardar processo fechar
    print("[UPDATER] Etapa 1/5: Aguardando aplicativo fechar...")
    if not wait_for_process_to_close(args.process, timeout=60):
        print("[UPDATER] ⚠️ Timeout - forçando continuação...")
    
    # Delay extra para garantir que arquivos foram liberados
    time.sleep(2)
    
    # Etapa 2: Copiar arquivos novos
    print("[UPDATER] Etapa 2/5: Copiando arquivos novos...")
    if copy_update_files(args.zip, args.target):
        print("[UPDATER] ✅ Atualização instalada com sucesso!")
        
        # Etapa 3: Atualizar versão
        print("[UPDATER] Etapa 3/5: Atualizando versão...")
        if args.version:
            update_version_file(args.target, args.version)
        
        # Etapa 4: Limpar arquivos temporários
        print("[UPDATER] Etapa 4/5: Limpando arquivos temporários...")
        # Limpa a pasta pai (que contém tanto o ZIP quanto a pasta extraída)
        temp_parent = os.path.dirname(args.zip)
        if "perplan-media" in temp_parent.lower():
            cleanup_temp_files(temp_parent)
        
        # Etapa 5: Reiniciar aplicativo
        print("[UPDATER] Etapa 5/5: Reiniciando aplicativo...")
        time.sleep(1)
        
        # Tenta reiniciar usando o nome do app fornecido
        app_exe = os.path.join(args.target, args.app_name)
        if os.path.exists(app_exe):
            try:
                subprocess.Popen([app_exe], cwd=args.target)
                print(f"[UPDATER] ✅ Aplicativo reiniciado: {app_exe}")
            except Exception as e:
                print(f"[UPDATER] ⚠️ Erro ao reiniciar: {e}")
                print(f"[UPDATER] Reinicie manualmente: {app_exe}")
        else:
            # Fallback para restart_app
            if restart_app(args.target):
                print("[UPDATER] ✅ Aplicativo reiniciado!")
            else:
                print("[UPDATER] ⚠️ Reinicie o aplicativo manualmente")
                print(f"[UPDATER] Local: {args.target}")
        
        # Etapa 7: Auto-exclusão
        print("[UPDATER] Etapa 7/7: Finalizando updater...")
        time.sleep(2)
        schedule_self_delete()
        
        print("[UPDATER] ✅ Processo de atualização concluído!")
        
    else:
        print("[UPDATER] ❌ Falha na instalação da atualização")
        input("[UPDATER] Pressione Enter para fechar...")
    
    # Aguarda antes de fechar
    time.sleep(1)
