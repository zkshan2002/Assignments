DATA segment
        line_feed   db 13, 10, '$'
        msg         db 'NAME: xxx', 13, 10, 'ID: xxxxxxxxxx', '$'
        lookup_str  db 'Zero', 'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Alpha', 'Bravo', 'China', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet', 'Kilo', 'Lima', 'Mary', 'November', 'Oscar', 'Paper', 'Quebec', 'Research', 'Sierra', 'Tango', 'Uniform', 'Victor', 'Whisky', 'X-ray', 'Yankee', 'Zulu', '$'
        lookup_bias dw 0,4,9,15,20,26,31,36,43,49,54,59,64,69,74,78,85,89,94,99,105,109,113,117,125,130,135,141,149,155,160,167,173,179,184,190
        lookup_len  db 4,5,6,5,6,5,5,7,6,5,5,5,5,5,4,7,4,5,5,6,4,4,4,8,5,5,6,8,6,5,7,6,6,5,6,4
DATA ends
STACK segment
              dw 128 dup(0)
STACK ends
CODE segment
                     assume CS:CODE, DS:DATA
new_line proc
                     mov    DX, offset line_feed
                     mov    AH, 9
                     int    21H
                     ret
new_line endP
print_word proc                                           ;specify index in SI; set DI = 0 if not lowercase
                     mov    BX, offset lookup_len         ;store len at CL
                     mov    AX, SI
                     xlat
                     mov    CL, AL
                     mov    BX, offset lookup_bias        ;store bias at SI
                     mov    AX, SI
                     shl    AX, 1
                     xlat
                     mov    SI, AX

                     mov    BX, offset lookup_str
                     mov    AX, SI
                     xlat
                     mov    DL, AL
                     cmp    DI, 0
                     je     not_lower
                     add    DL, 20H                       ;if lowercase, transform first digit
        not_lower:   
                     mov    AH, 2
                     int    21H
                     inc    SI
                     dec    CL
        print_char:  
                     mov    AX, SI
                     xlat
                     mov    DL, AL
                     mov    AH, 2
                     int    21H
                     inc    SI
                     loop   print_char
                     call   new_line
                     mov    CX, 2
                     ret
print_word endP
handle_input proc
                     mov    AH, 7
                     int    21H
                     cmp    AL, 1BH                       ;if input ESC, terminate
                     je     terminate
                     cmp    AL, '0'                       ;'0'~'9', 'A'~'Z', 'a'~'z'
                     jl     error
                     cmp    AL, '9'
                     jle    digit
                     cmp    AL, 'A'
                     jl     error
                     cmp    AL, 'Z'
                     jle    upper
                     cmp    AL, 'a'
                     jl     error
                     cmp    AL, 'z'
                     jle    lower
        error:       
                     mov    AH, 2
                     mov    DL, '?'
                     int    21H
                     call   new_line
                     mov    CX, 2
                     ret
        digit:       
                     sub    AL, '0'
                     mov    SI, AX
                     mov    DI, 0
                     call   print_word
                     ret
        upper:       
                     sub    AL, 'A'
                     mov    SI, AX
                     add    SI, 10
                     mov    DI, 0
                     call   print_word
                     ret
        lower:       
                     sub    AL, 'a'
                     mov    SI, AX
                     add    SI, 10
                     mov    DI, 1
                     call   print_word
                     ret
        terminate:   
                     mov    CX, 1
                     ret
handle_input endP
        begin:       
                     mov    AX, DATA
                     mov    DS, AX
                     mov    AX, STACK
                     mov    SS, AX
        main_loop:   
                     call   handle_input
                     loop   main_loop

                     mov    DX, offset msg
                     mov    AH, 9
                     int    21H

                     mov    AX, 4C00H
                     INT    21H
CODE ends
End begin