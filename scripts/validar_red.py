#!/usr/bin/env python3
"""
Fase 2 - Validacion de red usando Netmiko
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
    "username": "admin",
    "password": "AdminP4ss!",
    "secret": "AdminP4ss!",
}

# ===== Datos esperados (segun lo configurado en Fase 1) =====
HOSTNAME_ESPERADO = "SUC1-RTR"
NTP_ESPERADO = "pool.ntp.org"
INTERFACES_ESPERADAS = [
    "GigabitEthernet1",
    "GigabitEthernet1.10",
    "GigabitEthernet1.20",
    "GigabitEthernet1.30",
]

RUTA_REPORTE = os.path.expanduser("~/evaluacion4/reportes/reporte_validacion.json")


def conectar():
    print(f"[INFO] Conectando a {router['host']} ...")
    conn = ConnectHandler(**router)
    conn.enable()
    print("[OK] Conexion establecida.")
    return conn


def validar_hostname(conn, resultado):
    salida = conn.send_command("show run | include hostname")
    hostname_actual = salida.split()[-1] if salida else ""
    ok = hostname_actual == HOSTNAME_ESPERADO
    resultado["hostname"] = {
        "esperado": HOSTNAME_ESPERADO,
        "actual": hostname_actual,
        "estado": "OK" if ok else "FALLO",
    }
    print(f"[{'OK' if ok else 'FALLO'}] Hostname: {hostname_actual}")


def validar_ntp(conn, resultado):
    salida = conn.send_command("show run | include ntp server")
    ok = NTP_ESPERADO in salida
    resultado["ntp"] = {
        "esperado": NTP_ESPERADO,
        "configurado": salida.strip(),
        "estado": "OK" if ok else "FALLO",
    }
    print(f"[{'OK' if ok else 'FALLO'}] NTP: {salida.strip()}")


def validar_interfaces(conn, resultado):
    salida = conn.send_command("show ip interface brief")
    interfaces_estado = []
    todas_ok = True

    for iface in INTERFACES_ESPERADAS:
        encontrada = False
        up = False
        for linea in salida.splitlines():
            if linea.startswith(iface + " ") or linea.startswith(iface + "\t"):
                encontrada = True
                up = "up" in linea.lower()
                break
        estado = "OK" if (encontrada and up) else "FALLO"
        if estado == "FALLO":
            todas_ok = False
        interfaces_estado.append({
            "interfaz": iface,
            "encontrada": encontrada,
            "up": up,
            "estado": estado,
        })
        print(f"[{estado}] Interfaz {iface} - encontrada={encontrada}, up={up}")

    resultado["interfaces"] = {
        "detalle": interfaces_estado,
        "estado": "OK" if todas_ok else "FALLO",
    }


def validar_conectividad(conn, resultado):
    # Ping desde el propio router hacia si mismo o hacia DevASC para probar
    salida = conn.send_command("ping 192.168.56.102", delay_factor=2)
    ok = "!!!!!" in salida or "success rate is 100" in salida.lower()
    resultado["conectividad"] = {
        "destino": "192.168.56.102 (DevASC)",
        "resultado_crudo": salida.strip(),
        "estado": "OK" if ok else "FALLO",
    }
    print(f"[{'OK' if ok else 'FALLO'}] Ping a DevASC (192.168.56.102)")


def main():
    resultado = {
        "fecha_validacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "host": router["host"],
    }

    conn = conectar()

    try:
        validar_hostname(conn, resultado)
        validar_ntp(conn, resultado)
        validar_interfaces(conn, resultado)
        validar_conectividad(conn, resultado)
    finally:
        conn.disconnect()
        print("[INFO] Conexion cerrada.")

    # Estado general
    estados = [
        resultado["hostname"]["estado"],
        resultado["ntp"]["estado"],
        resultado["interfaces"]["estado"],
        resultado["conectividad"]["estado"],
    ]
    resultado["estado_general"] = "OK" if all(e == "OK" for e in estados) else "FALLO"

    os.makedirs(os.path.dirname(RUTA_REPORTE), exist_ok=True)
    with open(RUTA_REPORTE, "w") as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)

    print(f"\n[INFO] Reporte guardado en: {RUTA_REPORTE}")
    print(f"[RESULTADO GENERAL]: {resultado['estado_general']}")


if __name__ == "__main__":
    main()
