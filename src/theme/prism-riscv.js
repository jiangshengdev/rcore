// Prism 语言定义：RISC-V 64bit 汇编 (GNU 风格，含伪指令)
Prism.languages.riscv = {
  comment: [
    {
      pattern: /#.*/,
      greedy: true,
    },
    {
      pattern: /;.*/,
      greedy: true,
    },
  ],
  string: {
    pattern: /"(?:\\.|[^"\\\r\n])*"/,
    greedy: true,
  },
  directive: {
    pattern:
      /\.(?:section|globl|global|text|data|bss|align|word|dword|byte|half|asciz|ascii|zero|type|size|option|macro|endm|set|equ|org|include|ifdef|ifndef|endif|else|rept|endr|space|fill|comm|lcomm|file|ident|weak|p2align|balign|skip|string|pushsection|popsection|previous|sleb128|uleb128|loc|cfi_\w+|insn)\b/,
    alias: 'property',
  },
  label: {
    pattern: /(^|\s)[A-Za-z_.$][\w.$]*:/m,
    lookbehind: true,
    alias: 'function',
  },
  instruction: {
    pattern:
      /(^|\s)(?:addiw?|addi?u?w?|andn?|auipc|beq|bge|bgeu|blt|bltu|bne|bnez|c\.add|c\.addi|c\.addi16sp|c\.addi4spn|c\.addiw|c\.addw|c\.and|c\.andi|c\.beqz|c\.bnez|c\.ebreak|c\.jal|c\.jalr|c\.li|c\.lui|c\.lw|c\.ld|c\.mv|c\.nop|c\.or|c\.ret|c\.slli|c\.srai|c\.srli|c\.sub|c\.subw|c\.sw|c\.sd|c\.xor|div|divu|divuw|divw|ebreak|ecall|fence|fence\.i|j|jal|jalr|lb|lbu|ld|lh|lhu|li|lui|lw|lwu|mv|mul|mulh|mulhu|mulhsu|mulw|or|ori|rem|remu|remuw|remw|sb|sd|sh|sll|slli|slliw|sllw|slt|slti|sltiu|sltu|sra|srai|sraiw|sraw|srl|srli|srliw|srlw|sub|subw|sw|xor|xori|not|neg|seqz|snez|sltz|sgtz|call|tail|ret|nop|la|lla|jr|rdcycle|rdtime|rdinstret|csrrw|csrrs|csrrc|csrrwi|csrrsi|csrrci|wfi|sfence\.vma|mret|sret|uret|fence\.tso|pause|unimp|unreachable|lr\.w|sc\.w|amoswap\.w|amoadd\.w|amoxor\.w|amoand\.w|amoor\.w|amomin\.w|amomax\.w|amominu\.w|amomaxu\.w|lr\.d|sc\.d|amoswap\.d|amoadd\.d|amoxor\.d|amoand\.d|amoor\.d|amomin\.d|amomax\.d|amominu\.d|amomaxu\.d)\b/i,
    lookbehind: true,
    alias: 'keyword',
  },
  pseudoinstruction: {
    pattern:
      /(^|\s)(?:li|la|mv|not|neg|seqz|snez|sltz|sgtz|call|tail|ret|nop)\b/i,
    lookbehind: true,
    alias: 'builtin',
  },
  register: {
    pattern:
      /\b(?:x(?:[12]?\d|3[01]|[0-9])|zero|ra|sp|gp|tp|t(?:[0-6])|s(?:[0-9]|1[01])|a[0-7]|f(?:[12]?\d|3[01]|[0-9])|ft(?:1[01]|[0-9])|fs[0-2]|fa[0-7])\b/i,
    alias: 'variable',
  },
  number: [/\b0x[\da-f]+\b/i, /\b0b[01]+\b/i, /\b\d+\b/],
  operator: /[+\-*/%&|^~!<>=]/,
  punctuation: /[()[\]{},.:]/,
};

Prism.languages['riscv-asm'] = Prism.languages.riscv;
