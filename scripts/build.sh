#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
    echo "sudo ilə işlət"
    exit 1
fi

lb clean --purge
bash auto/config
lb build
