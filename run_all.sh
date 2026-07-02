#!/bin/bash
###############################################################################
# Fase 4 - Script orquestador
# Evaluacion 4 - Ansible, Python y router Cisco CSR1000v
# Ejecuta en orden: Fase 1 (Ansible) -> Fase 2 (Validacion) -> Fase 3 (Backup)
###############################################################################

set -e  # Detiene el script si algun comando falla
source "$HOME/evaluacion4/.env"

# ===== Colores para el output =====
VERDE='\033[0;32m'
ROJO='\033[0;31m'
AMARILLO='\033[1;33m'
NC='\033[0m' # No Color

# ===== Rutas del proyecto =====
BASE_DIR="$HOME/evaluacion4"
ANSIBLE_DIR="$BASE_DIR/ansible"
SCRIPTS_DIR="$BASE_DIR/scripts"

echo -e "${AMARILLO}=================================================${NC}"
echo -e "${AMARILLO}  EVALUACION 4 - Orquestador de automatizacion   ${NC}"
echo -e "${AMARILLO}  Inicio: $(date '+%Y-%m-%d %H:%M:%S')            ${NC}"
echo -e "${AMARILLO}=================================================${NC}"

# ===== FASE 1: Configuracion base con Ansible =====
echo ""
echo -e "${AMARILLO}>>> FASE 1: Ejecutando playbook de Ansible...${NC}"
cd "$ANSIBLE_DIR"
if ansible-playbook playbook_fase1.yml; then
    echo -e "${VERDE}[OK] Fase 1 completada correctamente.${NC}"
else
    echo -e "${ROJO}[ERROR] Fallo en la Fase 1 (Ansible). Abortando.${NC}"
    exit 1
fi

# ===== FASE 2: Validacion de red con Python/Netmiko =====
echo ""
echo -e "${AMARILLO}>>> FASE 2: Ejecutando validacion de red...${NC}"
cd "$SCRIPTS_DIR"
if python3 validar_red.py; then
    echo -e "${VERDE}[OK] Fase 2 completada correctamente.${NC}"
else
    echo -e "${ROJO}[ERROR] Fallo en la Fase 2 (Validacion). Abortando.${NC}"
    exit 1
fi

# ===== FASE 3: Backup de configuracion =====
echo ""
echo -e "${AMARILLO}>>> FASE 3: Ejecutando backup de configuracion...${NC}"
cd "$SCRIPTS_DIR"
if python3 backup_config.py; then
    echo -e "${VERDE}[OK] Fase 3 completada correctamente.${NC}"
else
    echo -e "${ROJO}[ERROR] Fallo en la Fase 3 (Backup). Abortando.${NC}"
    exit 1
fi

echo ""
echo -e "${VERDE}=================================================${NC}"
echo -e "${VERDE}  TODAS LAS FASES SE EJECUTARON CORRECTAMENTE    ${NC}"
echo -e "${VERDE}  Fin: $(date '+%Y-%m-%d %H:%M:%S')               ${NC}"
echo -e "${VERDE}=================================================${NC}"
