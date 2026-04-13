; ============================================================
; Smiley face (100x100 mm) drawn in 10 mm (1 cm) segments
; After EACH segment:
;   - wait for motion complete
;   - retract up 2 mm
;   - wait for button (0:/macros/io/wait_button.g)
;   - return to draw height and continue
;
; Assumptions:
;   - Z0 is your "draw plane" reference (paper/plate surface)
;   - Your pen-down height is zDraw (can be 0 if you touch-off)
;   - Button macro exists at: 0:/macros/io/wait_button.g
; ============================================================

; === HOME + PEN TOOL SELECT ===
G28
T1

G90
G17

; ----------------------------
; Parameters (edit these)
; ----------------------------
var zDraw   = 0     ; pen-down drawing height
var zLift   = 2.0     ; retract amount between segments
var zTravel = 30.0    ; safe travel height

var fTravel = 6000
var fDraw   = 2000
var fZ      = 1200

; Face bounding box: 0..100 in X and Y
var cx = 50.0
var cy = 50.0
var R  = 45.0     ; face radius fits inside 100x100 with margin
var eyeR = 5.0

; Handy pause macro path
var waitMacro = "0:/macros/io/wait_button.g"

; ----------------------------
; Helper: "finish segment then wait"
; ----------------------------
; Usage pattern:
;   (after a drawing move)
;   M400
;   G91
;   G1 Z{var.zLift} F{var.fZ}
;   G90
;   M98 P{var.waitMacro}
;   G91
;   G1 Z{-var.zLift} F{var.fZ}
;   G90

; ============================================================
; Start: go to safe height, then to first point
; ============================================================
G1 Z{var.zTravel} F{var.fZ}

; ============================================================
; FACE OUTLINE (approximated polygon, 10mm chords)
; 36 segments of ~10mm chord on radius 45 => ~7.2mm chord actually.
; To force 10mm-ish steps, we do 32 segments (11-ish mm).
; ============================================================
var n = 32
var i = 0

; Move to start point (rightmost)
G1 X{var.cx + var.R} Y{var.cy} F{var.fTravel}
G1 Z{var.zDraw} F{var.fZ}

while var.i < var.n
  ; next point on circle
  var a0 = (2*3.1415926535*var.i)/var.n
  var a1 = (2*3.1415926535*(var.i+1))/var.n
  var x1 = var.cx + var.R * cos(var.a1)
  var y1 = var.cy + var.R * sin(var.a1)

  ; draw segment
  G1 X{var.x1} Y{var.y1} F{var.fDraw}

  ; segment gate
  M400
  G91
  G1 Z{var.zLift} F{var.fZ}
  G90
  M98 P{var.waitMacro}
  G91
  G1 Z{-var.zLift} F{var.fZ}
  G90

  set var.i = var.i + 1

; Pen up
G1 Z{var.zTravel} F{var.fZ}

; ============================================================
; LEFT EYE (small circle, segmented)
; ============================================================
var exL = var.cx - 15.0
var ey  = var.cy + 12.0
set var.n = 16
set var.i = 0

; start at rightmost of left eye circle
G1 X{var.exL + var.eyeR} Y{var.ey} F{var.fTravel}
G1 Z{var.zDraw} F{var.fZ}

while var.i < var.n
  var a1 = (2*3.1415926535*(var.i+1))/var.n
  var x1 = var.exL + var.eyeR * cos(var.a1)
  var y1 = var.ey  + var.eyeR * sin(var.a1)
  G1 X{var.x1} Y{var.y1} F{var.fDraw}

  M400
  G91
  G1 Z{var.zLift} F{var.fZ}
  G90
  M98 P{var.waitMacro}
  G91
  G1 Z{-var.zLift} F{var.fZ}
  G90

  set var.i = var.i + 1

G1 Z{var.zTravel} F{var.fZ}

; ============================================================
; RIGHT EYE
; ============================================================
var exR = var.cx + 15.0
set var.n = 16
set var.i = 0

G1 X{var.exR + var.eyeR} Y{var.ey} F{var.fTravel}
G1 Z{var.zDraw} F{var.fZ}

while var.i < var.n
  var a1 = (2*3.1415926535*(var.i+1))/var.n
  var x1 = var.exR + var.eyeR * cos(var.a1)
  var y1 = var.ey  + var.eyeR * sin(var.a1)
  G1 X{var.x1} Y{var.y1} F{var.fDraw}

  M400
  G91
  G1 Z{var.zLift} F{var.fZ}
  G90
  M98 P{var.waitMacro}
  G91
  G1 Z{-var.zLift} F{var.fZ}
  G90

  set var.i = var.i + 1

G1 Z{var.zTravel} F{var.fZ}

; ============================================================
; SMILE (polyline arc, 10mm-ish segments)
; Define a smile arc from -150° to -30° on a smaller radius.
; ============================================================
var mR = 25.0
var mCx = var.cx
var mCy = var.cy - 5.0

; angles in radians
var aStart = -2.617993878   ; -150°
var aEnd   = -0.523598776   ; -30°
var arcLen = (var.aEnd - var.aStart) * var.mR
var segLen = 10.0
var mN = floor(abs(var.arcLen)/var.segLen)
if var.mN < 4
  set var.mN = 4

set var.i = 0

; move to start of smile
var sx = var.mCx + var.mR * cos(var.aStart)
var sy = var.mCy + var.mR * sin(var.aStart)
G1 X{var.sx} Y{var.sy} F{var.fTravel}
G1 Z{var.zDraw} F{var.fZ}

while var.i < var.mN
  var t = (var.i + 1) / var.mN
  var a = var.aStart + (var.aEnd - var.aStart) * var.t
  var x1 = var.mCx + var.mR * cos(var.a)
  var y1 = var.mCy + var.mR * sin(var.a)

  G1 X{var.x1} Y{var.y1} F{var.fDraw}

  M400
  G91
  G1 Z{var.zLift} F{var.fZ}
  G90
  M98 P{var.waitMacro}
  G91
  G1 Z{-var.zLift} F{var.fZ}
  G90

  set var.i = var.i + 1

; Finish
G1 Z{var.zTravel} F{var.fZ}
M118 P0 S"Smiley complete."
