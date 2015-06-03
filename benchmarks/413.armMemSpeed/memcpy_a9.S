.text
.global memcpy_a9
.type memcpy_a9, %function
.align 4

memcpy_a9:
   .fnstart
        CMP      r2,#3
        BLS      _my_memcpy_lastbytes
        ANDS     r12,r0,#3
        BEQ      l1
        LDRB     r3,[r1],#1
        CMP      r12,#2
        ADD      r2,r2,r12
        LDRLSB   r12,[r1],#1
        STRB     r3,[r0],#1
        LDRCCB   r3,[r1],#1
        STRLSB   r12,[r0],#1
        SUB      r2,r2,#4
        STRCCB   r3,[r0],#1
l1:
        ANDS     r3,r1,#3
        BEQ      __my_aeabi_memcpy4
l3:
        SUBS     r2,r2,#8
        BCC      l2
        LDR      r3,[r1],#4
        LDR      r12,[r1],#4
        STR      r3,[r0],#4
        STR      r12,[r0],#4
        B        l3
l2:
        ADDS     r2,r2,#4
        LDRPL    r3,[r1],#4
        STRPL    r3,[r0],#4
        MOV      r0,r0
_my_memcpy_lastbytes:
        LSLS     r2,r2,#31
        LDRCSB   r3,[r1],#1
        LDRCSB   r12,[r1],#1
        LDRMIB   r2,[r1],#1
        STRCSB   r3,[r0],#1
        STRCSB   r12,[r0],#1
        STRMIB   r2,[r0],#1
        BX       lr
__my_aeabi_memcpy4:
__my_aeabi_memcpy8:
__my_rt_memcpy_w:
        PUSH     {r4-r8,lr}
        SUBS     r2,r2,#0x20
        BCC      l4
        DSB          /* reset A9 BIU for early walloc supprssion */
        PLD     [r1, #0x20]  /* Start stream so LDMCS doest stall */
        PLD     [r1, #0x40]
        PLD     [r1, #0x60]
        PLD     [r1, #0x80]
        PLD     [r1, #0xa0]
        PLD     [r1, #0xc0]
        PLD     [r1, #0xe0]
l5:
        PLD      [r1,#0x100]
        LDMCS    r1!,{r3-r8,r12,lr}
        SUBCSS   r2,r2,#0x20
        STMCS    r0!,{r3-r8,r12,lr}
        BCS      l5
l4:
        LSLS     r12,r2,#28
        LDMCS    r1!,{r3,r4,r12,lr}
        STMCS    r0!,{r3,r4,r12,lr}
        LDMMI    r1!,{r3,r4}
        STMMI    r0!,{r3,r4}
        POP      {r4-r8,lr}
        LSLS     r12,r2,#30
        LDRCS    r3,[r1],#4
        STRCS    r3,[r0],#4
        BXEQ     lr
_my_memcpy_lastbytes_aligned:
        LSLS     r2,r2,#31
        LDRCSH   r3,[r1],#2
        LDRMIB   r2,[r1],#1
        STRCSH   r3,[r0],#2
        STRMIB   r2,[r0],#1
        BX       lr
   .fnend
.end
