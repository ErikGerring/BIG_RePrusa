; continuous_spiral.g
; High-precision spiral approximated with G1 segments only
; Keeps your scaffold: program -> home/tool -> move in -> run pump -> wait button -> spiral -> stop/retract.

; ===== EDIT =====
var cx       = 50.0      ; centre X (mm)
var cy       = 50.0      ; centre Y (mm)
var zAbove   = 30.0
var zInside  = 0.2

var diameter = 15.0      ; outer diameter (mm)
var pitch    = 0.8       ; radial growth per full turn (mm/rev)
var chord    = 0.05      ; max chord length per segment (mm). Smaller = more precise.
var feed     = 150       ; XY feed (mm/min)
var zFeed    = 600

var progMacro  = "0:/macros/tools/pump/pump_prog_droplet.g"
var runMacro   = "0:/macros/tools/pump/pump_run.g"
var stopMacro  = "0:/macros/tools/pump/pump_stop.g"
var buttonMacro= "0:/macros/io/wait_button.g"

; ===== CHECKS =====
if var.diameter <= 0 || var.pitch <= 0
  abort "diameter and pitch must be > 0"
if var.chord <= 0
  abort "chord must be > 0"

; ===== PUMP PROGRAM =====
G4 S2
M98 P{var.progMacro}

; ===== HOME + TOOL =====
G28

M400
T2

; ===== MOVE IN =====
G90
G1 Z{var.zAbove} F{var.zFeed}
G1 X{var.cx} Y{var.cy} F6000
G1 Z{var.zInside} F{var.zFeed}

M400
M98 P{var.runMacro}
M98 P{var.buttonMacro} S"Press button when droplets begin"

; ===== SPIRAL (ARCHIMEDEAN) =====
; r(theta) = r0 + k*theta, where k = pitch/(2*pi)
; Parametrise and emit small G1 segments with max chord length ~= chord.
; Segment angle dθ chosen from chord ≈ r*dθ  => dθ = chord/max(r, r_min)

var r0   = 0.5
var rMax = var.diameter/2.0
var k    = var.pitch/(2.0*pi)

var theta = 0.0
var r     = var.r0

; Start at theta=0 on +X
G1 X{var.cx + var.r} Y{var.cy} F{var.feed}

; Safety floor so dθ doesn't explode near r=0
var rMinForStep = 0.5

while var.r < var.rMax

  ; choose angular increment for this segment
  var rStep = var.r
  if var.rStep < var.rMinForStep
    set var.rStep = var.rMinForStep

  var dTheta = var.chord / var.rStep   ; radians
  ; clamp so it doesn't get too big if chord is large
  if var.dTheta > 0.2                  ; ~11.5°
    set var.dTheta = 0.2
  if var.dTheta < 0.001                ; ~0.057°
    set var.dTheta = 0.001

  ; advance
  set var.theta = var.theta + var.dTheta
  set var.r     = var.r0 + var.k * var.theta
  if var.r > var.rMax
    set var.r = var.rMax

  ; next point
  var x = var.cx + var.r * cos(var.theta)
  var y = var.cy + var.r * sin(var.theta)

  G1 X{var.x} Y{var.y} F{var.feed}

; ===== STOP + RETRACT =====
M400
M98 P{var.stopMacro}
G1 Z{var.zAbove} F{var.zFeed}
