; -------------------------------
; Pump steady infuse test via ESP bridge
; -------------------------------

; M98 P"0:/macros/io/uart_enable.g" U2 B115200

M122

; --- PING handshake ---
M98 P"0:/macros/io/uart_send.g" U2 S"PING"
; M98 P"0:/macros/io/uart_read.g" U2 N2
M261.2 P2 B2 V"io_rx"

if !exists(var.io_rx)
  abort "PING failed: var.io_rx not"

if #var.io_rx < 2
  abort "PING failed: short reply"

if var.io_rx[0] != 79 || var.io_rx[1] != 75
  abort {"PING failed: expected OK (79,75), got (" ^ var.io_rx[0] ^ "," ^ var.io_rx[1] ^ ")"}


; --- Pump sequence (do NOT tie this to PING on ESP side) ---
; M98 P"0:/macros/io/uart_send.g" U2 S"PUMP 0 STOP"
; M98 P"0:/macros/io/uart_read.g" U2 N2

; G4 S1

M98 P"0:/macros/io/uart_send.g" U2 S"PUMP 0 RESET"
; M98 P"0:/macros/io/uart_read.g" U2 N2

G4 S1

M98 P"0:/macros/io/uart_send.g" U2 S"PUMP 0 PROG test_1.txt"
; M98 P"0:/macros/io/uart_read.g" U2 N2

; Give ESP time to stream the file to the pump (tune as needed)
G4 S5

M122