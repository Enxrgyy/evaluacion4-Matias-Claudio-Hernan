# Evaluación 4 — Automatización de Red con Ansible, Python y Cisco CSR1000v

Proyecto de automatización de redes que configura, valida y respalda un router Cisco CSR1000v de forma automática, integrando Ansible, Python (Netmiko) y Bash.

## Integrantes del equipo

- Matías Peralta — Desarrollador
- Hernán Vera — Documentador
- Claudio Zambra — README / Documentación

## Descripción del proyecto

Esta actividad simula un escenario real de automatización de redes, donde se configura un router de sucursal de forma completamente automatizada, se valida su estado con scripts de Python, se genera un respaldo de su configuración, y todo el proceso se orquesta con un único script de Bash.

Nota de seguridad: los archivos ansible/inventory.ini y ansible/group_vars/all.yml con las credenciales reales no están en este repositorio por razones de seguridad, ya que es público. Se incluyen únicamente sus versiones .example como plantilla. Los backups (backups/) y reportes (reportes/) tampoco se suben, ya que contienen configuración real del dispositivo.

## Topología

Router Cisco CSR1000v en la IP 192.168.56.101, con usuario administrativo cisco por defecto. DevASC, el equipo de control con Ansible, Python y Netmiko, en la IP 192.168.56.102. Ambos equipos se comunican mediante red host-only en VirtualBox.

## Requisitos

Ansible 2.9 o superior, Python 3.8 o superior, y las librerías Python netmiko y paramiko. Se requiere acceso SSH al router Cisco CSR1000v.

Instalación de dependencias en DevASC:
pip3 install netmiko paramiko

## Fases del proyecto

### Fase 1 — Configuración base (Ansible)

El playbook ansible/playbook_fase1.yml configura automáticamente: hostname y dominio del router, servidor NTP, usuario administrativo con privilegio 15 y usuario de solo lectura con privilegio 1, llave RSA de 2048 bits para SSH con verificación de idempotencia (solo la genera si no existe), SSH versión 2 con timeouts y límite de reintentos, bloqueo de acceso tras 3 intentos fallidos de login en 60 segundos con bloqueo de 120 segundos, logging de seguridad con buffer, timestamps y archive de configuración, la interfaz física de management, y 3 subinterfaces lógicas (VLAN 10, 20 y 30) con encapsulación 802.1Q.

Ejecución:
cd ansible
ansible-playbook playbook_fase1.yml

### Fase 2 — Validación de red (Python + Netmiko)

El script scripts/validar_red.py se conecta al router vía SSH y valida el hostname configurado, el servidor NTP configurado, el estado de las interfaces física y lógicas (up o down), y la conectividad mediante ping hacia el equipo de control. Genera un reporte en reportes/reporte_validacion.json con fecha, hora y el resultado detallado de cada verificación.

Ejecución:
cd scripts
python3 validar_red.py

### Fase 3 — Backup de configuración (Python + Netmiko)

El script scripts/backup_config.py se conecta al router, obtiene el running-config completo y lo guarda en un archivo JSON con marca de fecha y hora, dentro de la carpeta backups/.

Ejecución:
cd scripts
python3 backup_config.py

Formato del backup generado (ejemplo): un objeto JSON con los campos host, hostname_dispositivo, fecha, hora, fecha_hora_completa y configuracion, donde este último contiene el running-config completo del router.

### Fase 4 — Orquestación (Bash)

El script run_all.sh ejecuta las 3 fases anteriores en orden, deteniéndose automáticamente si alguna falla, y mostrando el resultado de cada etapa por pantalla.

Ejecución:
./run_all.sh

## Seguridad implementada

Autenticación SSH con llave RSA de 2048 bits en versión SSH 2. Dos niveles de usuario: administrador con privilegio 15 y solo lectura con privilegio 1. Bloqueo automático de acceso tras intentos fallidos de login como protección contra fuerza bruta. Registro de intentos de login exitosos y fallidos. Credenciales excluidas del control de versiones mediante .gitignore.

## Cómo usar este proyecto (configuración inicial)

Primero, clonar el repositorio:
git clone https://github.com/Enxrgyy/evaluacion4-Matias-Claudio-Hernan.git
cd evaluacion4-Matias-Claudio-Hernan

Luego, crear los archivos reales de configuración a partir de las plantillas:
cp ansible/inventory.ini.example ansible/inventory.ini
cp ansible/group_vars/all.yml.example ansible/group_vars/all.yml

Editar ansible/inventory.ini y ansible/group_vars/all.yml con las credenciales reales del entorno.

Finalmente, ejecutar el pipeline completo:
./run_all.sh

## Evidencias

Las evidencias de ejecución, como capturas de pantalla de cada fase, pruebas de login SSH y contenido de los reportes JSON, se encuentran documentadas en la carpeta o enlace donde el equipo suba las capturas.

## Herramientas utilizadas

Ansible para la automatización de la configuración inicial del router. Python 3 para la lógica de validación y respaldo. Netmiko para la conexión SSH programática a dispositivos de red Cisco. Bash para la orquestación del flujo completo. Cisco CSR1000v como router virtual utilizado como dispositivo objetivo. GNS3 y VirtualBox como entorno de laboratorio virtualizado.

## Notas

El router cuenta con una única interfaz física (GigabitEthernet1), por lo que las VLANs se implementaron como subinterfaces, en modalidad router-on-a-stick, sobre dicha interfaz. El servidor NTP utilizado (pool.ntp.org) es un servidor público de ejemplo, dado que la actividad no especificó uno propio de la institución.
