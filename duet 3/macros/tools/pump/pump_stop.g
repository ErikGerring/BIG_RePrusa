; -------------------------------
; Pump stop via ESP bridge
; -------------------------------

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

; --- Pump sequence ---
M98 P"0:/macros/io/uart_send.g" U2 S"PUMP 0 STP ALL"

G4 P200

M98 P"0:/macros/io/uart_read.g" U2 N2
