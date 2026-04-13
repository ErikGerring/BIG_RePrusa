; Smiley face with pen up/down variables (within 0..150)
; RRF / Duet compatible

G28
T1

G90
G17                 ; XY plane arcs

; ---- Pen heights (edit these) ----
var zUp   = 5
var zDown = 0

; ---- Speeds ----
var fTravel = 6000
var fDraw   = 1000

; ---- Geometry (all within 0..150) ----
var cx = 75.0
var cy = 75.0
var faceR = 60.0

var eyeR = 5.0
var eyeLX = 55.0
var eyeLY = 95.0
var eyeRX = 95.0
var eyeRY = 95.0

; Smile endpoints and curvature (centre offset)
var smileX1 = 45.0
var smileY  = 60.0
var smileX2 = 105.0
var smileI  = 30.0
var smileJ  = -20.0        ; centre is below chord

; -------------------------
; PEN UP (travel)
G1 Z{var.zUp} F1200

; ========= FACE OUTLINE (circle) =========
; Start at rightmost point of face circle
G1 X{var.cx + var.faceR} Y{var.cy} F{var.fTravel}
G1 Z{var.zDown} F1200

; Two semicircles to make one full circle
G2 X{var.cx - var.faceR} Y{var.cy} I{-var.faceR} J0 F{var.fDraw}
G2 X{var.cx + var.faceR} Y{var.cy} I{ var.faceR} J0 F{var.fDraw}

G1 Z{var.zUp} F1200

; ========= LEFT EYE (single circle) =========
; Start at rightmost point of left eye
G1 X{var.eyeLX + var.eyeR} Y{var.eyeLY} F{var.fTravel}
G1 Z{var.zDown} F1200

; Two semicircles (this draws ONE circle total)
G2 X{var.eyeLX - var.eyeR} Y{var.eyeLY} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.eyeLX + var.eyeR} Y{var.eyeLY} I{ var.eyeR} J0 F{var.fDraw}

G1 Z{var.zUp} F1200

; ========= RIGHT EYE (single circle) =========
G1 X{var.eyeRX + var.eyeR} Y{var.eyeRY} F{var.fTravel}
G1 Z{var.zDown} F1200

G2 X{var.eyeRX - var.eyeR} Y{var.eyeRY} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.eyeRX + var.eyeR} Y{var.eyeRY} I{ var.eyeR} J0 F{var.fDraw}

G1 Z{var.zUp} F1200

; ========= SMILE (forced minor arc using R) =========
G17                         ; arcs in XY plane
G1 X45 Y60 F{var.fTravel}
G1 Z{var.zDown} F1200

; If it still draws a frown on YOUR machine, swap G2 -> G3:
G3 X105 Y60 R40 F{var.fDraw}

G1 Z{var.zUp} F1200

; PEN UP and finish
G1 X{var.cx} Y{var.cy} F{var.fTravel}
