# Convenience wrappers. Usage:
#   make erase PORT=/dev/cu.SLAB_USBtoUART
#   make flash PORT=/dev/cu.SLAB_USBtoUART
#   make deploy PORT=/dev/cu.SLAB_USBtoUART
#   make repl  PORT=/dev/cu.SLAB_USBtoUART

PORT ?=

.PHONY: erase flash deploy repl reset

erase:
	PORT=$(PORT) ./tools/erase_flash.sh

flash:
	PORT=$(PORT) ./tools/flash_micropython.sh

deploy:
	PORT=$(PORT) ./tools/deploy.sh

repl:
	PORT=$(PORT) ./tools/repl.sh

reset:
	PORT=$(PORT) ./tools/reset.sh
