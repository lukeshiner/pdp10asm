;   HELLO WORLD
;
;   Prints the string "Hello, World!" to the console.
;

        LOC 100
        MOVE 1,POINT    ; Store byte pointer
LOOP:   ILDB 2,1        ; Load byte
        JUMPE 2,FIN     ; If byte is zero jump to end
        DATAO TTY,2     ; Send byte to TTY
PLOOP:  CONSZ TTY,20    ; Skip if TTY buffer clear
        JUMPA PLOOP     ; Check buffer again
        JUMPA LOOP      ; Next character
FIN:    HALT 100

        LOC 200
POINT:  441100000201
        110145154154    ; String "Hell"
        157054040127    ; String "o, "
        157162154144    ; String "orld"
        041015012000    ; Strin "![cr][lf][NULL]"

        END