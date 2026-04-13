; ============================================================
; Spiral demo (button-gated)
; - Starts at spiral centre ("eye") and expands outward
; - Spiral "band" (outer radius) roughly 20 mm (2 cm) from centre
; - Draws in ~10 mm (1 cm) stroke segments
; - After EACH segment:
;     - M400 (finish motion)
;     - retract up 2 mm
;     - wait for button: 0:/macros/io/wait_button.g
;     - return to draw height and continue
;
; Assumptions:
;   - Z0 reference established for your drawing plane
;   - Your wait button macro exists at 0:/macros/io/wait_button.g
; ============================================================

G90
G17

; ----------------------------
; Parameters (edit)
; ----------------------------
var zDraw   = 0.0     ; pen-down height
var zLift   = 2.0     ; retract amount between segments
var zTravel = 15.0    ; safe travel height

var fTravel = 6000
var fDraw   = 100
var fZ      = 1200

var waitMacro = "0:/macros/io/wait_button.g"

; Spiral geometry
var cx = 50.0         ; centre X (edit)
var cy = 50.0         ; centre Y (edit)
var rMax = 20.0       ; ~2 cm wide spiral (outer radius)
var turns = 5.0       ; number of turns to reach rMax (edit)
var segLen = 5.0     ; ~1 cm strokes

; Archimedean spiral: r = k * theta, with theta from 0..thetaMax
var thetaMax = 2*3.1415926535*var.turns
var k = var.rMax / var.thetaMax

; ----------------------------
; Helper: finish segment + wait
; ----------------------------
; after a segment:
;   M400
;   G91
;   G1 Z{zLift}
;   G90
;   M98 wait_button
;   G91
;   G1 Z{-zLift}
;   G90

; ----------------------------
; Move to start (centre)
; ----------------------------
G1 Z{var.zTravel} F{var.fZ}
G1 X{var.cx} Y{var.cy} F{var.fTravel}
G1 Z{var.zDraw} F{var.fZ}

; ----------------------------
; Draw spiral by stepping theta so each chord ~ segLen
; For small steps, ds ≈ r * dθ (dominant term), so choose:
;   dθ ≈ segLen / max(r, rMin)
; We'll clamp with rMin to avoid huge dθ near the centre.
; ----------------------------
var rMin = 2.0         ; prevents giant first step
var theta = 0.0

; Initial point
var r = var.k * var.theta
var x = var.cx + var.r * cos(var.theta)
var y = var.cy + var.r * sin(var.theta)

; ensure we start exactly at centre
G1 X{var.x} Y{var.y} F{var.fDraw}

while var.theta < var.thetaMax
  ; compute dTheta for ~10mm step
  set var.r = var.k * var.theta
  var rEff = max(var.r, var.rMin)
  var dTheta = var.segLen / var.rEff

  ; limit dTheta so we don't jump too far at centre
  if var.dTheta > 0.8
    set var.dTheta = 0.8

  ; advance
  set var.theta = var.theta + var.dTheta
  if var.theta > var.thetaMax
    set var.theta = var.thetaMax

  set var.r = var.k * var.theta
  set var.x = var.cx + var.r * cos(var.theta)
  set var.y = var.cy + var.r * sin(var.theta)

  ; draw segment to next point
  G1 X{var.x} Y{var.y} F{var.fDraw}

  ; gate after each ~1 cm stroke
  M400
  G91
  G1 Z{var.zLift} F{var.fZ}
  G90
  M98 P{var.waitMacro}
  G91
  G1 Z{-var.zLift} F{var.fZ}
  G90

; Finish
G1 Z{var.zTravel} F{var.fZ}
M118 P0 S"Spiral complete."
