; homeall.g
; Home all axes (sensorless X/Y + probed Z)
; Adds an operator confirmation button press BEFORE probing Z.

; ---------- Lift Z (clearance before travelling to probe point) ----------
G91
G1 H2 Z30 F1200
G90

; ---------- Home X then Y (use dedicated macros) ----------
M98 P"homex.g"
M98 P"homey.g"

; ---------- Move to probe position ----------
;var xCenter = move.axes[0].min + (move.axes[0].max - move.axes[0].min)* 7 / 8 - sensors.probes[0].offsets[0]
;var yCenter = move.axes[1].min + (move.axes[1].max - move.axes[1].min)* 1 / 8 - sensors.probes[0].offsets[1]

var xCenter = move.axes[0].min + (move.axes[0].max - move.axes[0].min)* 7 / 8 - sensors.probes[0].offsets[0]
var yCenter = move.axes[1].min + (move.axes[1].max - move.axes[1].min)* 7 / 8 - sensors.probes[0].offsets[1]
G1 X{var.xCenter} Y{var.yCenter} F6000

; ---------- Operator gate BEFORE probing ----------
; M118 P0 S"Clear the probe area, then press the CONTINUE button to probe Z."
; M98 P"0:/macros/io/wait_button.g" S"Clear the probe area, then press the CONTINUE button to probe Z."

G30

G1 Z30 F1200
