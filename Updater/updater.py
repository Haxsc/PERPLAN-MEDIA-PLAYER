import argparse
import os
import shutil
import subprocess
import time
import sys


def wait_for_process_to_close(process_name):
    while True:
        try:
            tasks = os.popen("tasklist").read().lower()
            if process_name.lower() not in tasks:
                break
            time.sleep(1)
        except Exception:
            break


def replace_file(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    shutil.move(src, dst)


def restart_app(exe_path):
    subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))


def schedule_self_delete():
    if getattr(sys, "frozen", False):  # só tenta apagar se for .exe (via PyInstaller)
        exe_path = sys.executable
        bat_path = exe_path + ".bat"
        with open(bat_path, "w") as f:
            f.write(
                f"""@echo off
ping 127.0.0.1 -n 3 > nul
del "{exe_path}" /f /q
del "{bat_path}" /f /q
"""
            )
        subprocess.Popen([bat_path], creationflags=subprocess.CREATE_NO_WINDOW)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--main", required=True)
    args = parser.parse_args()

    print("Aguardando encerramento do aplicativo...")
    wait_for_process_to_close(args.main)

    print("Substituindo arquivo antigo...")
    target_exe_path = os.path.join(args.target, args.main)
    replace_file(args.exe, target_exe_path)

    print("Reiniciando o app...")
    restart_app(target_exe_path)

    print("Finalizando atualizador...")
    schedule_self_delete()
