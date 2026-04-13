; RRF macro - generated for Erik's multi-tool gantry platform
; Target: Duet 3 + RepRapFirmware (RRF)

; Go to XY maximum (Xmax, Ymax) at safe Z
; Uses configured axis maxima from the object model.
G90
var xmax = move.axes[0].max
var ymax = move.axes[1].max
G1 X{var.xmax} Y{var.ymax} F6000
