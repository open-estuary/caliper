;  nasm -f elf cpuida.asm   for cpuida.o
;  gcc cpuidc.c -c          for cpuidc.o
;  gcc test.c cpuidc.o cpuida.o -lc -lm -o test
;  ./test


section .text

    global _cpuida   

 _cpuida:

    push eax
    push ebx
    push ecx
    push edx
    push edi

    mov  eax, 1
    CPUID
    mov [eaxCode1], eax  ; Features Code
    mov [edxCode1], edx  ; family/model/stepping
    mov [ebxCode1], ebx
    mov [ecxCode1], ecx

    mov  edi, idString1
    mov  eax, 0
    CPUID
    mov[edi],   ebx
    mov[edi+4], edx
    mov[edi+8], ecx
    mov ecx, 0
    mov[edi+12], ecx
    mov [intel1amd2], ebx


    ; get specials
    mov eax,80000000h
    CPUID
    cmp eax,80000000h
    jc nomore

    mov eax, [intel1amd2]
    cmp eax, 756E6547h    ; uneG
    jz intel
    cmp eax, 68747541h    ; htuA
    jnz nomore
    mov eax,80000001h
    CPUID

    mov [ext81edx], edx

    mov eax,80000000h
    CPUID
    cmp eax,80000004h
    jc nomore                
    mov  edi, idString2
    mov eax,80000002h
    CPUID
    mov[edi],    eax
    mov[edi+4],  ebx
    mov[edi+8],  ecx
    mov[edi+12], edx
    mov eax,80000003h
    CPUID
    mov[edi+16], eax
    mov[edi+20], ebx
    mov[edi+24], ecx
    mov[edi+28], edx
    mov eax,80000004h
    CPUID
    mov[edi+32], eax
    mov[edi+36], ebx
    mov[edi+40], ecx
    mov[edi+44], edx
    mov ecx, 0
    mov[edi+48], ecx
    jmp nomore
   intel:
    mov eax,80000000h
    CPUID
    cmp eax,80000004h
    jc nomore                
    mov  edi, idString2
    mov eax,80000002h
    CPUID
    mov[edi],    eax
    mov[edi+4],  ebx
    mov[edi+8],  ecx
    mov[edi+12], edx
    mov eax,80000003h
    CPUID
    mov[edi+16], eax
    mov[edi+20], ebx
    mov[edi+24], ecx
    mov[edi+28], edx
    mov eax,80000004h
    CPUID
    mov[edi+32], eax
    mov[edi+36], ebx
    mov[edi+40], ecx
    mov[edi+44], edx
    mov ecx, 0
    mov[edi+48], ecx
   nomore:

    pop edi
    pop edx
    pop ecx
    pop ebx
    pop eax


section .data

 extern  idString1
 extern  idString2
 extern  eaxCode1
 extern  ebxCode1
 extern  ecxCode1
 extern  edxCode1
 extern  intel1amd2
 extern  ext81edx


section .text

    global _calculateMHz   

 _calculateMHz:

        push eax
        push edx
        push ebx 
        RDTSC 
        mov [startCount], eax 
        mov ebx, 25000
  outerloop:
        mov edx, 25000
  innerloop:    
        dec     edx
        jne     innerloop
        dec     ebx
        jne     outerloop
        RDTSC
        mov     [endCount], eax
        sub     eax, [startCount]
        mov     [cycleCount], eax        
        pop ebx
        pop edx
        pop eax

section .data

 extern  startCount
 extern  endCount
 extern  cycleCount


