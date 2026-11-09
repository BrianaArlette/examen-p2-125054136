#!/bin/bash
set -euo pipefail

# Inicialización de SSH y autenticación mediante llaves
mkdir -p /home/alumno/.ssh /run/sshd
chown alumno:alumno /home/alumno/.ssh
chmod 700 /home/alumno/.ssh
if [ ! -f /home/alumno/.ssh/id_ed25519 ]; then
    runuser -u alumno -- ssh-keygen -q -t ed25519 -N '' -f /home/alumno/.ssh/id_ed25519
fi
cat /home/alumno/.ssh/id_ed25519.pub > /home/alumno/.ssh/authorized_keys
printf '%s\n' \
  'Host localhost 127.0.0.1' \
  '    StrictHostKeyChecking accept-new' \
  '    BatchMode yes' \
  > /home/alumno/.ssh/config
chown alumno:alumno /home/alumno/.ssh/*
chmod 600 /home/alumno/.ssh/id_ed25519 /home/alumno/.ssh/authorized_keys /home/alumno/.ssh/config
chmod 644 /home/alumno/.ssh/id_ed25519.pub
ssh-keygen -A >/dev/null 2>&1
exec /usr/sbin/sshd -D -e
