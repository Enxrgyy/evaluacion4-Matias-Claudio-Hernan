#!/usr/bin/env python3
"""
Fase 3 - Backup de configuracion del router usando Netmiko
Evaluacion 4 - Ansible, Python y router Cisco CSR1000v
"""

from netmiko import ConnectHandler
from datetime import datetime
import json
import os

# ===== Configuracion de conexion =====
router = {
    "device_type": "cisco_ios",
    "host": "192.168.56.101",
    "username": os.environ.get("ROUTER_USER", "admin"),
    "password": os.environ.get("ROUTER_PASSWORD", ""),
    "secret": os.environ.get("ROUTER_PASSWORD", ""),
}

CARPETA_BACKUPS = os.path.expanduser("~/evaluacion4/backups")


def conectar():
    print(f"[INFO] Conectando a {router['host']} ...")
    conn = ConnectHandler(**router)
    conn.enable()
    print("[OK] Conexion establecida.")
    return conn


def obtener_configuracion(conn):
    print("[INFO] Obteniendo running-config ...")
    config = conn.send_command("show running-config", delay_factor=4)
    return config


def guardar_backup(config_texto):
    ahora = datetime.now()
    timestamp_archivo = ahora.strftime("%Y%m%d_%H%M%S")
    timestamp_legible = ahora.strftime("%Y-%m-%d %H:%M:%S")

    nombre_archivo = f"backup_{router['host']}_{timestamp_archivo}.json"
    ruta_completa = os.path.join(CARPETA_BACKUPS, nombre_archivo)

    backup_data = {
        "host": router["host"],
        "hostname_dispositivo": "SUC1-RTR",
        "fecha": ahora.strftime("%Y-%m-%d"),
        "hora": ahora.strftime("%H:%M:%S"),
        "fecha_hora_completa": timestamp_legible,
        "configuracion": config_texto,
    }

    os.makedirs(CARPETA_BACKUPS, exist_ok=True)
    with open(ruta_completa, "w") as f:
        json.dump(backup_data, f, indent=4, ensure_ascii=False)

    return ruta_completa


def main():
    conn = conectar()
    try:
        config_texto = obtener_configuracion(conn)
    finally:
        conn.disconnect()
        print("[INFO] Conexion cerrada.")

    ruta_guardada = guardar_backup(config_texto)
    print(f"[OK] Backup guardado en: {ruta_guardada}")


if __name__ == "__main__":
    main()
