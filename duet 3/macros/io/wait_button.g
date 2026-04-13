; wait_button.g
; Wait for a press+release on gpIn created via M950 J...

var gp = 1            ; gpIn index (J1 usually maps to gpIn[0])
var poll = 50         ; ms
var debounce = 200    ; ms

if exists(param.S)
  M118 P0 S{param.S}
else 
  M118 P0 S"Waiting for CONTINUE button..."

; Wait for press (NO button to GND => value goes 0 when pressed)
while sensors.gpIn[var.gp].value = 1
  G4 P{var.poll}

; Wait for release
while sensors.gpIn[var.gp].value = 0
  G4 P{var.poll}

G4 P{var.debounce}
M118 P0 S"Continuing."
