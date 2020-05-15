/* Basic LinkerScript configuration for this project */
/* Taken straight from the `Bare Bones` tutorial on the OSDev wiki */
ENTRY(_tos_start)

SECTIONS
{
    . = 1M;
    
    .text BLOCK(4K) : ALIGN(4K)
    {
        *(.multiboot)
        *(.text)
    }
    
    .rodata BLOCK(4K) : ALIGN(4K)
    {
        *(.rodata)
    }
    
    .data BLOCK(4K) : ALIGN(4K)
    {
        *(.data)
    }

    .bss BLOCK(4K) : ALIGN(4K)
    {
        *(COMMON)
        *(.bss)
    }
}