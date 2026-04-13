; 0:/macros/io/uart_read.g
; Simple UART read into a global buffer (no predeclared var needed)
;
; Params:
;   U = UART channel (Duet 3 Mini IO_1 is usually 2)
;   N = number of bytes to read
;
; Output:
;   global.io_rx   = array of bytes read (length N)
;   global.io_rx_n = N

if !exists(param.U)
  abort "uart_read_simple.g requires U"
if !exists(param.N)
  abort "uart_read_simple.g requires N"

; Ensure globals exist (create once)
if !exists(global.io_rx)
  global io_rx = {0}
; if !exists(global.io_rx_n)
;   global io_rx_n = 0

; Read N bytes into a NEW local variable called 'rx'
; (Don't call M261.2 V\"rx\" twice in the same macro scope)
; M261.2 P{param.U} B{param.N} V"rx"

M261.2 P{param.U} B{param.N} V"rx"

; Copy to globals so caller can use it
set global.io_rx = var.rx
; set global.io_rx_n = param.N



; Optional debug echo
echo {"UART RX (" ^ param.N ^ "): " ^ global.io_rx}
