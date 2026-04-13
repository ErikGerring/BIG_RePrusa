; 0:/macros/io/uart_enable.g
; Params: U=uart channel (required), B=baud (optional, default 115200)

if !exists(param.U)
  abort "uart_enable.g requires U (uart channel)"

var io_baud = 115200
if exists(param.B)
  set var.io_baud = param.B

; Put UART into device mode
M575 P{param.U} B{var.io_baud} S7

; Clear RX buffer
M261.2 P{param.U} B0