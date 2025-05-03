// Prism 语言定义：RISC-V 64bit 汇编 (GNU 风格，含伪指令)

/**
 * 将字符串数组转为不区分大小写的正则表达式
 * @param {string[]} arr
 * @returns {RegExp}
 */
function arrayToCaseInsensitivePattern(arr) {
  return new RegExp('(^|\\s)(' + arr.join('|') + ')\\b', 'i');
}

let RV_32_I_BASE_INSTRUCTION_SET = [
  'LUI',
  'AUIPC',
  'JAL',
  'JALR',
  'BEQ',
  'BNE',
  'BLT',
  'BGE',
  'BLTU',
  'BGEU',
  'LB',
  'LH',
  'LW',
  'LBU',
  'LHU',
  'SB',
  'SH',
  'SW',
  'ADDI',
  'SLTI',
  'SLTIU',
  'XORI',
  'ORI',
  'ANDI',
  'SLLI',
  'SRLI',
  'SRAI',
  'ADD',
  'SUB',
  'SLL',
  'SLT',
  'SLTU',
  'XOR',
  'SRL',
  'SRA',
  'OR',
  'AND',
  'FENCE',
  'FENCE.TSO',
  'PAUSE',
  'ECALL',
  'EBREAK',
];

const RV_64_I_BASE_INSTRUCTION_SET = [
  "LWU",
  "LD",
  "SD",
  "SLLI",
  "SRLI",
  "SRAI",
  "ADDIW",
  "SLLIW",
  "SRLIW",
  "SRAIW",
  "ADDW",
  "SUBW",
  "SLLW",
  "SRLW",
  "SRAW",
]

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
  instruction: [
    // 35. RV32/64G Instruction Set Listings
    // RV32I Base Instruction Set
    {
      pattern: arrayToCaseInsensitivePattern(RV_32_I_BASE_INSTRUCTION_SET),
      lookbehind: true,
      alias: 'keyword',
    },
    // RV64I Base Instruction Set
    {
      pattern: arrayToCaseInsensitivePattern(RV_64_I_BASE_INSTRUCTION_SET),
      lookbehind: true,
      alias: 'keyword',
    },

    // 3. RV32/RV64 _Zifencei_ Standard Extension
    // 4. RV32/RV64 _Zicsr_ Standard Extension
    // 5. RV32M Standard Extension
    // 6. RV64M Standard Extension (in addition to RV32M)
    // 7. RV32A Standard Extension
    // 8. RV64A Standard Extension (in addition to RV32A)
    // 9. RV32F Standard Extension
    // 10. RV64F Standard Extension (in addition to RV32F)
    // 11. RV32D Standard Extension
    // 12. RV64D Standard Extension (in addition to RV32D)
    // 13. RV32Q Standard Extension
    // 14. RV64Q Standard Extension (in addition to RV32Q)
    // 15. RV32Zfh Standard Extension
    // 16. RV64Zfh Standard Extension (in addition to RV32Zfh)
    // 17. Zawrs Standard Extension
  ],
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
