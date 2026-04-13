; ============================================================
; 6-well plate demo: different faces per well with
;   - Outside-well travel: Z=zTravel, fast
;   - Inside-well travel:  Z=zLift,  slower (over a well)
;   - Drawing:             Z=zDraw
;
; Wells:
;   A1 Smile, A2 Frown, A3 Surprised,
;   B1 Wink,  B2 Flat,  B3 Big grin
; ============================================================

G28
T1

G90
G17

; ----------------------------
; Z heights (EDIT)
; ----------------------------
var zTravel = 30.0     ; safe clearance moving between wells
var zLift   = 4.0     ; pen-up travel within a well
var zDraw   = 2.5      ; pen-down drawing height

; ----------------------------
; Feeds
; ----------------------------
var fOutside = 4000    ; between wells
var fInside  = 1000    ; within well (pen up)
var fDraw    = 250    ; drawing
var fZ       = 1200

; ----------------------------
; 6-well plate geometry (EDIT)
; A1 centre and spacing
; ----------------------------
var A1x = 24.76
var A1y = 62.28
var dx  = 39.12
var dy  = 39.12

; Derived centres
var A2x = var.A1x + var.dx
var A2y = var.A1y
var A3x = var.A1x + 2*var.dx
var A3y = var.A1y

var B1x = var.A1x
var B1y = var.A1y - var.dy
var B2x = var.A1x + var.dx
var B2y = var.A1y - var.dy
var B3x = var.A1x + 2*var.dx
var B3y = var.A1y - var.dy

; ----------------------------
; Face geometry (LOCAL to well centre)
; Keep faceR conservative (e.g. <= 12–14mm) for 6-well plates.
; ----------------------------
var faceR = 12.0

; Eyes
var eyeR  = 1.5
var eyeOffX = 4.0
var eyeOffY = 4.0

; Mouth geometry
var mouthHalfW = 6.0
var mouthYoff  = -3.0

; Smile/frown arc radius (minor arc using R)
var mouthR = 8.0       ; must be >= mouthHalfW

; ============================================================
; Helpers (inline convention)
; - Outside-well travel:  Z=zTravel, F=fOutside
; - Inside-well travel:   Z=zLift,   F=fInside
; - Draw:                 Z=zDraw,   F=fDraw
; ============================================================

; Start safe
G1 Z{var.zTravel} F{var.fZ}

; ============================================================
; WELL A1 - SMILE 🙂
; ============================================================
var cx = var.A1x
var cy = var.A1y

; Outside-well travel to well centre
G1 X{var.cx} Y{var.cy} F{var.fOutside}
; Inside-well pen-up height
G1 Z{var.zLift} F{var.fZ}

; Face circle
G1 X{var.cx + var.faceR} Y{var.cy} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.faceR} Y{var.cy} I{-var.faceR} J0 F{var.fDraw}
G2 X{var.cx + var.faceR} Y{var.cy} I{ var.faceR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Left eye (circle)
G1 X{var.cx - var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.eyeOffX - var.eyeR} Y{var.cy + var.eyeOffY} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.cx - var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} I{ var.eyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Right eye (circle)
G1 X{var.cx + var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx + var.eyeOffX - var.eyeR} Y{var.cy + var.eyeOffY} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.cx + var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} I{ var.eyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Smile (minor arc). If it draws as a frown on your rig, swap G3->G2.
G1 X{var.cx - var.mouthHalfW} Y{var.cy + var.mouthYoff} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G3 X{var.cx + var.mouthHalfW} Y{var.cy + var.mouthYoff} R{var.mouthR} F{var.fDraw}
G1 Z{var.zTravel} F{var.fZ}

; ============================================================
; WELL A2 - FROWN 🙁
; ============================================================
set var.cx = var.A2x
set var.cy = var.A2y

G1 X{var.cx} Y{var.cy} F{var.fOutside}
G1 Z{var.zLift} F{var.fZ}

; Face
G1 X{var.cx + var.faceR} Y{var.cy} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.faceR} Y{var.cy} I{-var.faceR} J0 F{var.fDraw}
G2 X{var.cx + var.faceR} Y{var.cy} I{ var.faceR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Eyes
G1 X{var.cx - var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.eyeOffX - var.eyeR} Y{var.cy + var.eyeOffY} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.cx - var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} I{ var.eyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

G1 X{var.cx + var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx + var.eyeOffX - var.eyeR} Y{var.cy + var.eyeOffY} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.cx + var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} I{ var.eyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Frown (opposite direction). If A1 smile needed G2, then use G3 here.
G1 X{var.cx - var.mouthHalfW} Y{var.cy + var.mouthYoff} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx + var.mouthHalfW} Y{var.cy + var.mouthYoff} R{var.mouthR} F{var.fDraw}
G1 Z{var.zTravel} F{var.fZ}

; ============================================================
; WELL A3 - SURPRISED 😮
; (open mouth: small circle)
; ============================================================
set var.cx = var.A3x
set var.cy = var.A3y

G1 X{var.cx} Y{var.cy} F{var.fOutside}
G1 Z{var.zLift} F{var.fZ}

; Face
G1 X{var.cx + var.faceR} Y{var.cy} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.faceR} Y{var.cy} I{-var.faceR} J0 F{var.fDraw}
G2 X{var.cx + var.faceR} Y{var.cy} I{ var.faceR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Eyes (bigger)
var bigEyeR = 2.0
G1 X{var.cx - var.eyeOffX + var.bigEyeR} Y{var.cy + var.eyeOffY} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.eyeOffX - var.bigEyeR} Y{var.cy + var.eyeOffY} I{-var.bigEyeR} J0 F{var.fDraw}
G2 X{var.cx - var.eyeOffX + var.bigEyeR} Y{var.cy + var.eyeOffY} I{ var.bigEyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

G1 X{var.cx + var.eyeOffX + var.bigEyeR} Y{var.cy + var.eyeOffY} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx + var.eyeOffX - var.bigEyeR} Y{var.cy + var.eyeOffY} I{-var.bigEyeR} J0 F{var.fDraw}
G2 X{var.cx + var.eyeOffX + var.bigEyeR} Y{var.cy + var.eyeOffY} I{ var.bigEyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Open mouth (circle)
var mouthR2 = 3.5
G1 X{var.cx + var.mouthR2} Y{var.cy - 4.0} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.mouthR2} Y{var.cy - 4.0} I{-var.mouthR2} J0 F{var.fDraw}
G2 X{var.cx + var.mouthR2} Y{var.cy - 4.0} I{ var.mouthR2} J0 F{var.fDraw}
G1 Z{var.zTravel} F{var.fZ}

; ============================================================
; WELL B1 - WINK 😉
; (one eye circle, one eye as a line)
; ============================================================
set var.cx = var.B1x
set var.cy = var.B1y

G1 X{var.cx} Y{var.cy} F{var.fOutside}
G1 Z{var.zLift} F{var.fZ}

; Face
G1 X{var.cx + var.faceR} Y{var.cy} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.faceR} Y{var.cy} I{-var.faceR} J0 F{var.fDraw}
G2 X{var.cx + var.faceR} Y{var.cy} I{ var.faceR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Left eye circle
G1 X{var.cx - var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.eyeOffX - var.eyeR} Y{var.cy + var.eyeOffY} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.cx - var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} I{ var.eyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Right eye wink line
var winkHalf = 2.5
G1 X{var.cx + var.eyeOffX - var.winkHalf} Y{var.cy + var.eyeOffY} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G1 X{var.cx + var.eyeOffX + var.winkHalf} Y{var.cy + var.eyeOffY} F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Smile
G1 X{var.cx - var.mouthHalfW} Y{var.cy + var.mouthYoff} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G3 X{var.cx + var.mouthHalfW} Y{var.cy + var.mouthYoff} R{var.mouthR} F{var.fDraw}
G1 Z{var.zTravel} F{var.fZ}

; ============================================================
; WELL B2 - FLAT 😐
; (straight mouth line)
; ============================================================
set var.cx = var.B2x
set var.cy = var.B2y

G1 X{var.cx} Y{var.cy} F{var.fOutside}
G1 Z{var.zLift} F{var.fZ}

; Face
G1 X{var.cx + var.faceR} Y{var.cy} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.faceR} Y{var.cy} I{-var.faceR} J0 F{var.fDraw}
G2 X{var.cx + var.faceR} Y{var.cy} I{ var.faceR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Eyes
G1 X{var.cx - var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.eyeOffX - var.eyeR} Y{var.cy + var.eyeOffY} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.cx - var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} I{ var.eyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

G1 X{var.cx + var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx + var.eyeOffX - var.eyeR} Y{var.cy + var.eyeOffY} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.cx + var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY} I{ var.eyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Flat mouth
G1 X{var.cx - var.mouthHalfW} Y{var.cy + var.mouthYoff} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G1 X{var.cx + var.mouthHalfW} Y{var.cy + var.mouthYoff} F{var.fDraw}
G1 Z{var.zTravel} F{var.fZ}

; ============================================================
; WELL B3 - BIG GRIN 😄
; (two arcs: wide smile + small cheek lines)
; ============================================================
set var.cx = var.B3x
set var.cy = var.B3y

G1 X{var.cx} Y{var.cy} F{var.fOutside}
G1 Z{var.zLift} F{var.fZ}

; Face
G1 X{var.cx + var.faceR} Y{var.cy} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.faceR} Y{var.cy} I{-var.faceR} J0 F{var.fDraw}
G2 X{var.cx + var.faceR} Y{var.cy} I{ var.faceR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Eyes (slightly higher)
G1 X{var.cx - var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY + 1.0} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx - var.eyeOffX - var.eyeR} Y{var.cy + var.eyeOffY + 1.0} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.cx - var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY + 1.0} I{ var.eyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

G1 X{var.cx + var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY + 1.0} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G2 X{var.cx + var.eyeOffX - var.eyeR} Y{var.cy + var.eyeOffY + 1.0} I{-var.eyeR} J0 F{var.fDraw}
G2 X{var.cx + var.eyeOffX + var.eyeR} Y{var.cy + var.eyeOffY + 1.0} I{ var.eyeR} J0 F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

; Big smile (wider + slightly lower)
var grinHalfW = 7.5
var grinYoff  = -4.0
var grinR     = 9.5

G1 X{var.cx - var.grinHalfW} Y{var.cy + var.grinYoff} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G3 X{var.cx + var.grinHalfW} Y{var.cy + var.grinYoff} R{var.grinR} F{var.fDraw}

; Cheek lines
G1 Z{var.zLift} F{var.fZ}
G1 X{var.cx - 9.0} Y{var.cy - 2.0} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G1 X{var.cx - 6.5} Y{var.cy - 1.5} F{var.fDraw}
G1 Z{var.zLift} F{var.fZ}

G1 X{var.cx + 6.5} Y{var.cy - 1.5} F{var.fInside}
G1 Z{var.zDraw} F{var.fZ}
G1 X{var.cx + 9.0} Y{var.cy - 2.0} F{var.fDraw}

; Finish
G1 Z{var.zTravel} F{var.fZ}

; Park (optional)
G1 X{var.A1x} Y{var.A1y} F{var.fOutside}
G1 Z{var.zTravel} F{var.fZ}

; NOTE:
; If smiles appear inverted on your rig, swap G3 <-> G2 for the mouth arcs
; (A1 smile, B1 wink mouth, B3 grin) and also swap for the frown in A2.
