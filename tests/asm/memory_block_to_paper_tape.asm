;   Memory Block to Paper Tape Raw

;   Punches the contents of memory to paper tape.
;
;   The start address of the data punched is taken from AC0.
;   The number of addresses to punch is taken from AC1.
;

        START=770200

        STARTADD=0
        NBYTES=1
        POINT=2
        CURADD=3
        BLEFT=4
        OUT=5

        LOC 770200
        CONO PTP,50
        MOVE CURADD,NBYTES
        HRLI POINT,440600
        HRR POINT,0
WORDL:  MOVEI BLEFT,6
BYTEL:  ILDB OUT,POINT
        DATAO PTP,OUT
        CONSO PTP,10
        JRST .-1
        SOJE BLEFT,NEWW
        JRST BYTEL
NEWW:   SOJL 3,FIN
        JRST WORDL
FIN:    HALT START

        END
