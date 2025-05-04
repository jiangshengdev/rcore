// Prism 语言定义：RISC-V 64bit 汇编 (GNU 风格，含伪指令)

/**
 * 将字符串数组转为不区分大小写的正则表达式
 * @param {string[]} arr
 * @returns {RegExp}
 */
function arrayToCaseInsensitivePattern(arr) {
  return new RegExp('(^|\\s)(' + arr.join('|') + ')\\b', 'i');
}

// RV32I Base Instruction Set
const RV_32_I_BASE_INSTRUCTION_SET = [
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

// RV64I Base Instruction Set (in addition to RV32I)
const RV_64_I_BASE_INSTRUCTION_SET = [
  'LWU',
  'LD',
  'SD',
  'SLLI',
  'SRLI',
  'SRAI',
  'ADDIW',
  'SLLIW',
  'SRLIW',
  'SRAIW',
  'ADDW',
  'SUBW',
  'SLLW',
  'SRLW',
  'SRAW',
];

// RV32/RV64 Zifencei Standard Extension
const RV_32_RV_64_ZIFENCEI_STANDARD_EXTENSION = ['FENCE.I'];

// RV32/RV64 Zicsr Standard Extension
const RV_32_RV_64_ZICSR_STANDARD_EXTENSION = [
  'CSRRW',
  'CSRRS',
  'CSRRC',
  'CSRRWI',
  'CSRRSI',
  'CSRRCI',
];

// RV32M Standard Extension
const RV_32_M_STANDARD_EXTENSION = [
  'MUL',
  'MULH',
  'MULHSU',
  'MULHU',
  'DIV',
  'DIVU',
  'REM',
  'REMU',
];

// RV64M Standard Extension (in addition to RV32M)
const RV_64_M_STANDARD_EXTENSION = ['MULW', 'DIVW', 'DIVUW', 'REMW', 'REMUW'];

// RV32A Standard Extension
const RV_32_A_STANDARD_EXTENSION = [
  'LR.W',
  'SC.W',
  'AMOSWAP.W',
  'AMOADD.W',
  'AMOXOR.W',
  'AMOAND.W',
  'AMOOR.W',
  'AMOMIN.W',
  'AMOMAX.W',
  'AMOMINU.W',
  'AMOMAXU.W',
];

// RV64A Standard Extension (in addition to RV32A)
const RV_64_A_STANDARD_EXTENSION = [
  'LR.D',
  'SC.D',
  'AMOSWAP.D',
  'AMOADD.D',
  'AMOXOR.D',
  'AMOAND.D',
  'AMOOR.D',
  'AMOMIN.D',
  'AMOMAX.D',
  'AMOMINU.D',
  'AMOMAXU.D',
];

// RV32F Standard Extension
const RV_32_F_STANDARD_EXTENSION = [
  'FLW',
  'FSW',
  'FMADD.S',
  'FMSUB.S',
  'FNMSUB.S',
  'FNMADD.S',
  'FADD.S',
  'FSUB.S',
  'FMUL.S',
  'FDIV.S',
  'FSQRT.S',
  'FSGNJ.S',
  'FSGNJN.S',
  'FSGNJX.S',
  'FMIN.S',
  'FMAX.S',
  'FCVT.W.S',
  'FCVT.WU.S',
  'FMV.X.W',
  'FEQ.S',
  'FLT.S',
  'FLE.S',
  'FCLASS.S',
  'FCVT.S.W',
  'FCVT.S.WU',
  'FMV.W.X',
];

// RV64F Standard Extension (in addition to RV32F)
const RV_64_F_STANDARD_EXTENSION = [
  'FCVT.L.S',
  'FCVT.LU.S',
  'FCVT.S.L',
  'FCVT.S.LU',
];

// RV32D Standard Extension
const RV_32_D_STANDARD_EXTENSION = [
  'FLD',
  'FSD',
  'FMADD.D',
  'FMSUB.D',
  'FNMSUB.D',
  'FNMADD.D',
  'FADD.D',
  'FSUB.D',
  'FMUL.D',
  'FDIV.D',
  'FSQRT.D',
  'FSGNJ.D',
  'FSGNJN.D',
  'FSGNJX.D',
  'FMIN.D',
  'FMAX.D',
  'FCVT.S.D',
  'FCVT.D.S',
  'FEQ.D',
  'FLT.D',
  'FLE.D',
  'FCLASS.D',
  'FCVT.W.D',
  'FCVT.WU.D',
  'FCVT.D.W',
  'FCVT.D.WU',
];

// RV64D Standard Extension (in addition to RV32D)
const RV_64_D_STANDARD_EXTENSION = [
  'FCVT.L.D',
  'FCVT.LU.D',
  'FMV.X.D',
  'FCVT.D.L',
  'FCVT.D.LU',
  'FMV.D.X',
];

// RV32Q Standard Extension
const RV_32_Q_STANDARD_EXTENSION = [
  'FLQ',
  'FSQ',
  'FMADD.Q',
  'FMSUB.Q',
  'FNMSUB.Q',
  'FNMADD.Q',
  'FADD.Q',
  'FSUB.Q',
  'FMUL.Q',
  'FDIV.Q',
  'FSQRT.Q',
  'FSGNJ.Q',
  'FSGNJN.Q',
  'FSGNJX.Q',
  'FMIN.Q',
  'FMAX.Q',
  'FCVT.S.Q',
  'FCVT.Q.S',
  'FCVT.D.Q',
  'FCVT.Q.D',
  'FEQ.Q',
  'FLT.Q',
  'FLE.Q',
  'FCLASS.Q',
  'FCVT.W.Q',
  'FCVT.WU.Q',
  'FCVT.Q.W',
  'FCVT.Q.WU',
];

// RV64Q Standard Extension (in addition to RV32Q)
const RV_64_Q_STANDARD_EXTENSION = [
  'FCVT.L.Q',
  'FCVT.LU.Q',
  'FCVT.Q.L',
  'FCVT.Q.LU',
];

function set2Instruction(set) {
  return {
    pattern: arrayToCaseInsensitivePattern(set),
    lookbehind: true,
    alias: 'keyword',
  };
}

const PSEUDO_OPS = [
  '.align',
  '.p2align',
  '.balign',
  '.file',
  '.globl',
  '.local',
  '.comm',
  '.common',
  '.ident',
  '.section',
  '.size',
  '.text',
  '.data',
  '.rodata',
  '.bss',
  '.string',
  '.asciz',
  '.equ',
  '.macro',
  '.endm',
  '.type',
  '.option',
  '.byte',
  '.2byte',
  '.half',
  '.short',
  '.4byte',
  '.word',
  '.long',
  '.8byte',
  '.dword',
  '.quad',
  '.float',
  '.double',
  '.quad',
  '.dtprelword',
  '.dtpreldword',
  '.sleb128',
  '.uleb128',
  '.zero',
  '.variant_cc',
  '.attribute',
  '.insn',
];

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
    pattern: arrayToCaseInsensitivePattern(PSEUDO_OPS),
    alias: 'property',
  },
  label: {
    pattern: /(^|\s)[A-Za-z_.$][\w.$]*:/m,
    lookbehind: true,
    alias: 'function',
  },
  instruction: [
    // 35. RV32/64G Instruction Set Listings
    set2Instruction(RV_32_I_BASE_INSTRUCTION_SET),
    set2Instruction(RV_64_I_BASE_INSTRUCTION_SET),
    set2Instruction(RV_32_RV_64_ZIFENCEI_STANDARD_EXTENSION),
    set2Instruction(RV_32_RV_64_ZICSR_STANDARD_EXTENSION),
    set2Instruction(RV_32_M_STANDARD_EXTENSION),
    set2Instruction(RV_64_M_STANDARD_EXTENSION),
    set2Instruction(RV_32_A_STANDARD_EXTENSION),
    set2Instruction(RV_64_A_STANDARD_EXTENSION),
    set2Instruction(RV_32_F_STANDARD_EXTENSION),
    set2Instruction(RV_64_F_STANDARD_EXTENSION),
    set2Instruction(RV_32_D_STANDARD_EXTENSION),
    set2Instruction(RV_64_D_STANDARD_EXTENSION),
    set2Instruction(RV_32_Q_STANDARD_EXTENSION),
    set2Instruction(RV_64_Q_STANDARD_EXTENSION),

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
