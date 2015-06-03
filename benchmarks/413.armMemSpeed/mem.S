        .fpu neon
        .text

.macro  function name, export=1
    .macro endfunc
        .size   \name, . - \name
        .endfunc
        .purgem endfunc
    .endm
        .text
    .if \export
        .global \name
    .endif
        .type   \name, STT_FUNC
        .func   \name
        .align  6
\name:
.endm

function memcpy_arm
        push            {r4-r11}
1:      subs            r2, r2, #64
        pld             [r1, #192]
        pld             [r1, #128]
        ldm             r1!, {r4-r11}
        stm             r0!, {r4-r11}
        ldm             r1!, {r4-r11}
        stm             r0!, {r4-r11}
        bgt             1b
        pop             {r4-r11}
        bx              lr
endfunc

function memcpy_vldm_64
        mov             r3, r0
1:      pld             [r1, #192]
        pld             [r1, #128]
        vldm            r1!, {d0-d7}
        subs            r2, r2, #64
        vstm            r3!, {d0-d7}
        bgt             1b
        bx              lr
endfunc

function memcpy_vldm_128
        mov             r3, r0
1:      pld             [r1, #256]
        pld             [r1, #192]
        subs            r2, r2, #128
        vldm            r1!, {d0-d7}
        vldm            r1!, {d16-d23}
        vstm            r3!, {d0-d7}
        vstm            r3!, {d16-d23}
        bgt             1b
        bx              lr
endfunc

function memcpy_vld1
        mov             r3, r0
1:      pld             [r1, #256]
        pld             [r1, #192]
        vld1.8          {d0-d3},   [r1,:128]!
        vld1.8          {d4-d7},   [r1,:128]!
        vld1.8          {d16-d19}, [r1,:128]!
        vld1.8          {d20-d23}, [r1,:128]!
        subs            r2, r2, #128
        vst1.8          {d0-d3},   [r3,:128]!
        vst1.8          {d4-d7},   [r3,:128]!
        vst1.8          {d16-d19}, [r3,:128]!
        vst1.8          {d20-d23}, [r3,:128]!
        bgt             1b
        bx              lr
endfunc

function memcpy_armneon
        push            {r4-r11}
        mov             r3, r0
1:      subs            r2, r2, #128
        pld             [r1, #64]
        pld             [r1, #128]
        pld             [r1, #320]
        ldm             r1!, {r4-r11}
        vld1.8          {d0-d3},   [r1,:128]!
        vld1.8          {d4-d7},   [r1,:128]!
        vld1.8          {d16-d19}, [r1,:128]!
        stm             r3!, {r4-r11}
        vst1.8          {d0-d3},   [r3,:128]!
        vst1.8          {d4-d7},   [r3,:128]!
        vst1.8          {d16-d19}, [r3,:128]!
        bgt             1b
        pop             {r4-r11}
        bx              lr
endfunc

function memset_arm
        push            {r4-r11}
        mov             r3,  r0
        orr             r4,  r1, r1, lsl #8
        orr             r4,  r4, r4, lsl #16
        mov             r5,  r4
        mov             r6,  r4
        mov             r7,  r4
        mov             r8,  r4
        mov             r9,  r4
        mov             r10, r4
        mov             r11, r4
1:      subs            r2, r2, #128
        stm             r3!, {r4-r11}
        stm             r3!, {r4-r11}
        stm             r3!, {r4-r11}
        stm             r3!, {r4-r11}
        bgt             1b
        pop             {r4-r11}
        bx              lr
endfunc

function memset_vstm
1:      subs            r2,  r2,  #128
        vstm            r0!, {d0-d15}
        bgt             1b
        bx              lr
endfunc

function memset_vst1
        mov             r3, r0
        vdup.8          q0, r1
        vmov            q1, q0
1:      subs            r2, r2, #128
        vst1.8          {d0-d3},   [r3,:128]!
        vst1.8          {d0-d3},   [r3,:128]!
        vst1.8          {d0-d3},   [r3,:128]!
        vst1.8          {d0-d3},   [r3,:128]!
        bgt             1b
        bx              lr
endfunc

function memset_armneon
        push            {r4-r11}
        mov             r3,  r0
        vdup.8          q0,  r1
        vmov            q1,  q0
        orr             r4,  r1, r1, lsl #8
        orr             r4,  r4, r4, lsl #16
        mov             r5,  r4
        mov             r6,  r4
        mov             r7,  r4
        mov             r8,  r4
        mov             r9,  r4
        mov             r10, r4
        mov             r11, r4
        add             r12, r3,  r2, lsr #2
1:      subs            r2,  r2, #128
        vst1.8          {d0-d3},   [r3,:128]!
        vst1.8          {d0-d3},   [r3,:128]!
        vst1.8          {d0-d3},   [r3,:128]!
        stm             r3!, {r4-r11}
        bgt             1b
        pop             {r4-r11}
        bx              lr
endfunc

function memread_arm
        push            {r4-r11}
1:      subs            r1, r1, #128
        pld             [r0, #192]
        pld             [r0, #128]
        ldm             r0!, {r4-r11}
        ldm             r0!, {r4-r11}
        ldm             r0!, {r4-r11}
        ldm             r0!, {r4-r11}
        bgt             1b
        pop             {r4-r11}
        bx              lr
endfunc

function memread_vldm
        vpush           {d8-d15}
1:      subs            r1,  r1,  #128
        pld             [r0, #320]
        pld             [r0, #256]
        vldm            r0!, {d0-d15}
        bgt             1b
        vpop            {d8-d15}
        bx              lr
endfunc

function memread_vld1
1:      subs            r1, r1, #128
        pld             [r0, #320]
        pld             [r0, #256]
        vld1.8          {d0-d3},   [r0,:128]!
        vld1.8          {d4-d7},   [r0,:128]!
        vld1.8          {d16-d19}, [r0,:128]!
        vld1.8          {d20-d23}, [r0,:128]!
        bgt             1b
        bx              lr
endfunc

function memread_armneon
        push            {r4-r11}
        add             r12, r0,  r1, lsr #2
1:      subs            r1,  r1, #128
        pld             [r0,  #64]
        pld             [r12, #320]
        pld             [r12, #256]
        vld1.8          {d0-d3},   [r12,:128]!
        vld1.8          {d4-d7},   [r12,:128]!
        vld1.8          {d16-d19}, [r12,:128]!
        ldm             r0!, {r4-r11}
        bgt             1b
        pop             {r4-r11}
        bx              lr
endfunc

#ifdef PLE_A8
#include "ple_a8.S"
#endif
