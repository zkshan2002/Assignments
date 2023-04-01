DATA segment
    buffer       db 128 dup(0)
    line_feed    db 13, 10, '$'
    msg         db 'NAME: xxx', 13, 10, 'ID: xxxxxxxxxx', '$'
    msg_fail     db 'No...', '$'
    msg_success  db 'Yes! Location: ', '$'
    print_buffer db 4 dup(0)
DATA ends
STACK segment
          dw 128 dup(0)
STACK ends
CODE segment
                  assume CS:CODE, DS:DATA, ES:DATA
new_line proc
                  mov    DX, offset line_feed
                  mov    AH, 9
                  int    21H
                  ret
new_line endp
input_str proc
                  mov    BX, offset buffer            ;place buffer size at start of buffer
                  mov    byte ptr [BX], 128

                  mov    AH, 0AH
                  mov    DX, offset buffer
                  int    21H

                  mov    BX, offset buffer            ;place '$' at end of string
                  mov    AL, [BX + 1]
                  add    BL, 3
                  add    BL, AL
                  mov    byte ptr [BX], '$'

                  mov    DX, offset buffer            ;print input string
                  add    DX, 2
                  mov    AH, 9
                  int    21H
                  call   new_line
                  ret
input_str endp
char_query proc
                  mov    AH, 7
                  int    21H
                  cmp    AL, 1BH                      ;if input ESC, terminate
                  je     terminate

                  mov    DI, AX                       ;temporally safe input char at DI
                  mov    DL, AL                       ;print char
                  mov    AH, 2
                  int    21H
                  call   new_line

                  mov    AX, DI                       ;prepare: char at AL, string start address at DI, len at CL
                  xor    AH, AH
                  mov    DI, offset buffer
                  add    DI, 2
                  mov    BX, offset buffer
                  mov    CL, [BX + 1]
    query_next:   
                  cld
                  repne  scasb                        ;compare AL with [ES:DI], set flag, then inc DI
                  je     found

    not_found:    
                  mov    DX, offset msg_fail
                  mov    AH, 9
                  int    21H
                  
                  call   new_line
                  mov    CX, 2
                  ret
    found:                                            ;DI - offset = bias
                  mov    BX, offset buffer
                  add    BX, 2                        ;index starts at 1
                  sub    DI, BX                       ;DI stores index, convert to decimal string

                  mov    DX, offset msg_success
                  mov    AH, 9
                  int    21H

                  mov    AX, DI                       ;move index to AX
                  call   print_decimal

                  call   new_line
                  mov    CX, 2
                  ret
    terminate:    
                  mov    CX, 1
                  ret
char_query endp
print_decimal proc                                    ;specify int at AX
                  mov    BX, offset print_buffer
                  mov    CX, 0
                  mov    DL, 10
    loop_div:     
                  div    DL                           ;div AX with DL. safe quotient at AL, remainder at AH
                  add    AH, '0'
                  mov    [BX], AH
                  xor    AH, AH
                  inc    BX
                  inc    CX
                  cmp    AL, 0
                  jg     loop_div
                  mov    AH, 2
    loop_print:   
                  mov    DL, [BX - 1]
                  int    21H
                  dec    BX
                  loop   loop_print
                  ret
print_decimal endp
    begin:        
                  mov    AX, DATA
                  mov    DS, AX
                  mov    ES, AX
                  mov    AX, STACK
                  mov    SS, AX

                  call   input_str
    main_loop:    
                  call   char_query
                  loop   main_loop

                  mov    DX, offset msg
                  mov    AH, 9
                  int    21H
                     
                  mov    AX, 4C00H
                  int    21H
CODE ends
End begin