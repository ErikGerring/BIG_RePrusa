; 0:/macros/io/uart_send.g
; Params: U(required), S(required)

if !exists(param.U)
  abort "uart_send.g requires U (uart channel)"
if !exists(param.S)
  abort "uart_send.g requires S (string)"

; Transmit Message
; Clear RX
; M261.2 P{param.U} B0 
; Send message, wait breifly, then send LF
M260.2 P{param.U} S{param.S}
G4 P5
M260.2 P{param.U} B10

G4 P50
