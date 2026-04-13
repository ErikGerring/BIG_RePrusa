; RRF macro - generated for Erik's multi-tool gantry platform
; Target: Duet 3 + RepRapFirmware (RRF)

; Go to XY home
; Uses configured axis maxima from the object model.
G90
var xCenter = move.axes[0].min + (move.axes[0].max - move.axes[0].min) * 7 / 8 - sensors.probes[0].offsets[0]
var yCenter = move.axes[1].min + (move.axes[1].max - move.axes[1].min) * 7 / 8 - sensors.probes[0].offsets[1]
G1 X{var.xCenter} Y{var.yCenter} F6000




