; -------------------------------
; Pump beep test via ESP bridge
; -------------------------------

M98 P"0:/macros/io/uart_enable.g" U2 B115200

; --- PING handshake ---
M98 P"0:/macros/io/uart_send.g" U2 S"PING"
M98 P"0:/macros/io/uart_read.g" U2 N2

; Expect ASCII 'O' 'K' = {79,75}
if !exists(global.io_rx)
  abort "PING failed: global.uartRx not set by uart_read.g"

if #global.io_rx < 2
  abort "PING failed: short reply"

if global.io_rx[0] != 79 || global.io_rx[1] != 75
  abort {"PING failed: expected OK (79,75), got (" ^ global.io_rx[0] ^ "," ^ global.io_rx[1] ^ ")"}

; --- Pump sequence (do NOT tie this to PING on ESP side) ---
; M98 P"0:/macros/io/uart_send.g" U2 S"PUMP 0 STOP"
; M98 P"0:/macros/io/uart_read.g" U2 N2

; G4 S1

M98 P"0:/macros/io/uart_send.g" U2 S"PUMP 0 RESET"
M98 P"0:/macros/io/uart_read.g" U2 N2

G4 S1

M98 P"0:/macros/io/uart_send.g" U2 S"PUMP 0 PROG beep.txt"
M98 P"0:/macros/io/uart_read.g" U2 N2

; Give ESP time to stream the file to the pump (tune as needed)
G4 S3

M98 P"0:/macros/io/uart_send.g" U2 S"PUMP 0 RUN"
M98 P"0:/macros/io/uart_read.g" U2 N2
