; demo.g
; Homes → traces XY limits → diagonals → centre helix
; Uses configured axis min/max from object model

G28
G90

; ===== READ AXIS LIMITS =====
var xmin = move.axes[0].min
var xmax = move.axes[0].max
var ymin = move.axes[1].min
var ymax = move.axes[1].max

var zsafe = move.axes[2].max - 100
var zlow  = move.axes[2].min + 5

var feedFast = 6000
var feedDraw = 1500

; ===== BORDER =====
G1 Z{var.zsafe} F600
G1 X{var.xmin} Y{var.ymin} F{var.feedFast}
G1 Z{var.zlow} F600

G1 X{var.xmax} Y{var.ymin} F{var.feedFast}
G1 X{var.xmax} Y{var.ymax} F{var.feedFast}
G1 X{var.xmin} Y{var.ymax} F{var.feedFast}
G1 X{var.xmin} Y{var.ymin} F{var.feedFast}

; ===== DIAGONALS =====
G1 X{var.xmax} Y{var.ymax}
G1 X{var.xmin} Y{var.ymax}
G1 X{var.xmax} Y{var.ymin}
G1 X{var.xmin} Y{var.ymin}

; ===== CENTRE =====
var cx = (var.xmin + var.xmax)/2
var cy = (var.ymin + var.ymax)/2

G1 Z{var.zsafe} F600
G1 X{var.cx} Y{var.cy} F{var.feedFast}
G1 Z{var.zlow} F600

; ===== QUICK 3D HELIX =====
var radius = (var.xmax - var.xmin)/6
var turns  = 3
var steps  = 50
var height = 20

var i = 0
while var.i <= var.steps * var.turns
  var theta = 2*pi*var.i/var.steps
  var x = var.cx + var.radius * cos(var.theta)
  var y = var.cy + var.radius * sin(var.theta)
  var z = var.zlow + var.height * var.i/(var.steps*var.turns)

  G1 X{var.x} Y{var.y} Z{var.z} F{var.feedDraw}
  set var.i = var.i + 1

; ===== FINISH =====
G1 Z{var.zsafe} F600