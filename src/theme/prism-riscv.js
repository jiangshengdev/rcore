function preprocessInstructionPattern(str) {
  str = str.replace(/\{([^}]+)}/g, (_, body) => {
    if (body.includes('|')) {
      return '(' + body + ')';
    }
    return '(' + body + ')?';
  });
  str = str.replace(/\[([^\]]+)]/g, '($1)?');
  return str.replace(/\./g, '\\.');
}

function toCaseInsensitiveBoundaryPattern(arr) {
  const uniqueArr = Array.from(new Set(arr));
  const processed = uniqueArr.map(preprocessInstructionPattern);
  return new RegExp(
    '(^|[\\s,;])(' + processed.join('|') + ')(?=[\\s,;]|$)',
    'i',
  );
}

function toCaseInsensitiveBoundaryPatternWithParen(arr) {
  const uniqueArr = Array.from(new Set(arr));
  const processed = uniqueArr.map(preprocessInstructionPattern);
  return new RegExp(
    '(^|[\\s,;(])(' + processed.join('|') + ')(?=[\\s,;\\)]|$)',
    'i',
  );
}

function toInstructionPattern(set) {
  return {
    pattern: toCaseInsensitiveBoundaryPattern(set),
    lookbehind: true,
    alias: 'keyword',
  };
}

function toPseudoinstructionPattern(set) {
  return {
    pattern: toCaseInsensitiveBoundaryPattern(set),
    lookbehind: true,
    alias: 'keyword',
  };
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

// RV32Zfh Standard Extension
const RV_32_ZFH_STANDARD_EXTENSION = [
  'FLH',
  'FSH',
  'FMADD.H',
  'FMSUB.H',
  'FNMSUB.H',
  'FNMADD.H',
  'FADD.H',
  'FSUB.H',
  'FMUL.H',
  'FDIV.H',
  'FSQRT.H',
  'FSGNJ.H',
  'FSGNJN.H',
  'FSGNJX.H',
  'FMIN.H',
  'FMAX.H',
  'FCVT.S.H',
  'FCVT.H.S',
  'FCVT.D.H',
  'FCVT.H.D',
  'FCVT.Q.H',
  'FCVT.H.Q',
  'FEQ.H',
  'FLT.H',
  'FLE.H',
  'FCLASS.H',
  'FCVT.W.H',
  'FCVT.WU.H',
  'FMV.X.H',
  'FCVT.H.W',
  'FCVT.H.WU',
  'FMV.H.X',
];

// RV64Zfh Standard Extension (in addition to RV32Zfh)
const RV_64_ZFH_STANDARD_EXTENSION = [
  'FCVT.L.H',
  'FCVT.LU.H',
  'FCVT.H.L',
  'FCVT.H.LU',
];

// Zawrs Standard Extension
const ZAWRS_STANDARD_EXTENSION = ['WRS.NTO', 'WRS.STO'];

// Registers of the RV32I
const REGISTERS_OF_THE_RV_32_I = [
  'x0',
  'x1',
  'x2',
  'x3',
  'x4',
  'x5',
  'x6',
  'x7',
  'x8',
  'x9',
  'x10',
  'x11',
  'x12',
  'x13',
  'x14',
  'x15',
  'x16',
  'x17',
  'x18',
  'x19',
  'x20',
  'x21',
  'x22',
  'x23',
  'x24',
  'x25',
  'x26',
  'x27',
  'x28',
  'x29',
  'x30',
  'x31',
  'pc',

  'zero',
  'ra',
  'sp',
  'gp',
  'tp',
  't0',
  't1',
  't2',
  's0',
  's1',
  'a0',
  'a1',
  'a2',
  'a3',
  'a4',
  'a5',
  'a6',
  'a7',
  's2',
  's3',
  's4',
  's5',
  's6',
  's7',
  's8',
  's9',
  's10',
  's11',
  't3',
  't4',
  't5',
  't6',

  'fp',
];

// Assembler Directives
const ASSEMBLER_DIRECTIVES = [
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

// Pseudo Instructions
const PSEUDO_INSTRUCTIONS = [
  'la',
  'la',
  'lla',
  'lga',
  'l{b|h|w|d}',
  'l{bu|hu|wu}',
  's{b|h|w|d}',
  'fl{w|d}',
  'fs{w|d}',
  'nop',
  'li',
  'mv',
  'not',
  'neg',
  'negw',
  'sext.b',
  'sext.h',
  'sext.w',
  'zext.b',
  'zext.h',
  'zext.w',
  'seqz',
  'snez',
  'sltz',
  'sgtz',
  'fmv.h',
  'fabs.h',
  'fneg.h',
  'fgt.h',
  'fge.h',
  'fmv.s',
  'fabs.s',
  'fneg.s',
  'fgt.s',
  'fge.s',
  'fmv.d',
  'fabs.d',
  'fneg.d',
  'fgt.d',
  'fge.d',
  'beqz',
  'bnez',
  'blez',
  'bgez',
  'bltz',
  'bgtz',
  'bgt',
  'ble',
  'bgtu',
  'bleu',
  'j',
  'jal',
  'jr',
  'jalr',
  'ret',
  'vfneg.v',
  'vfabs.v',
  'vmclr.m',
  'vmfge.vv',
  'vmfgt.vv',
  'vmmv.m',
  'vmnot.m',
  'vmset.m',
  'vmsge.vi',
  'vmsgeu.vi',
  'vmsge.vv',
  'vmsgeu.vv',
  'vmsgt.vv',
  'vmsgtu.vv',
  'vmslt.vi',
  'vmsltu.vi',
  'vneg.v',
  'vnot.v',
  'vncvt.x.x.w',
  'vwcvt.x.x.v',
  'vwcvtu.x.x.v',
  'vl1r.v',
  'vl2r.v',
  'vl4r.v',
  'vl8r.v',
  'vmsge{u}.vx',
  'vmsge{u}.vx',
  'vmsge{u}.vx',
  'vmsge{u}.vx',
  'call',
  'tail',
  'fence',
  'pause',
];

// Pseudoinstructions for accessing control and status registers
const PSEUDOINSTRUCTIONS_FOR_ACCESSING_CONTROL_AND_STATUS_REGISTERS = [
  'rdinstret[h]',
  'rdcycle[h]',
  'rdtime[h]',
  'csrr',
  'csrw',
  'csrs',
  'csrc',
  'csrwi',
  'csrsi',
  'csrci',
  'frcsr',
  'fscsr',
  'fscsr',
  'frrm',
  'fsrm',
  'fsrm',
  'fsrmi',
  'fsrmi',
  'frflags',
  'fsflags',
  'fsflags',
  'fsflagsi',
  'fsflagsi',
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
    pattern: /"(?:[^"\r\n]|"")*"/,
    greedy: true,
    inside: {
      variable: {
        pattern: /((?:^|[^$])(?:\${2})*)\$\w+/,
        lookbehind: true,
      },
    },
  },
  char: {
    pattern: /'(?:[^'\r\n]{0,4}|'')'/,
    greedy: true,
  },
  'version-symbol': {
    pattern: /\|[\w@]+\|/,
    greedy: true,
    alias: 'property',
  },

  boolean: /\b(?:FALSE|TRUE)\b/,
  directive: {
    pattern: toCaseInsensitiveBoundaryPattern(ASSEMBLER_DIRECTIVES),
    alias: 'property',
  },
  label: {
    pattern: /(^\s*)[A-Za-z._?$][\w.?$@~#]*:/m,
    lookbehind: true,
    alias: 'function',
  },
  instruction: [
    // RV32/64G Instruction Set Listings
    toInstructionPattern(RV_32_I_BASE_INSTRUCTION_SET),
    toInstructionPattern(RV_64_I_BASE_INSTRUCTION_SET),
    toInstructionPattern(RV_32_RV_64_ZIFENCEI_STANDARD_EXTENSION),
    toInstructionPattern(RV_32_RV_64_ZICSR_STANDARD_EXTENSION),
    toInstructionPattern(RV_32_M_STANDARD_EXTENSION),
    toInstructionPattern(RV_64_M_STANDARD_EXTENSION),
    toInstructionPattern(RV_32_A_STANDARD_EXTENSION),
    toInstructionPattern(RV_64_A_STANDARD_EXTENSION),
    toInstructionPattern(RV_32_F_STANDARD_EXTENSION),
    toInstructionPattern(RV_64_F_STANDARD_EXTENSION),
    toInstructionPattern(RV_32_D_STANDARD_EXTENSION),
    toInstructionPattern(RV_64_D_STANDARD_EXTENSION),
    toInstructionPattern(RV_32_Q_STANDARD_EXTENSION),
    toInstructionPattern(RV_64_Q_STANDARD_EXTENSION),
    toInstructionPattern(RV_32_ZFH_STANDARD_EXTENSION),
    toInstructionPattern(RV_64_ZFH_STANDARD_EXTENSION),
    toInstructionPattern(ZAWRS_STANDARD_EXTENSION),

    // A listing of standard RISC-V pseudoinstructions
    toPseudoinstructionPattern(PSEUDO_INSTRUCTIONS),
    toPseudoinstructionPattern(
      PSEUDOINSTRUCTIONS_FOR_ACCESSING_CONTROL_AND_STATUS_REGISTERS,
    ),
  ],
  variable: /\$\w+/,

  number:
    /(?:\b[2-9]_\d+|(?:\b\d+(?:\.\d+)?|\B\.\d+)(?:e-?\d+)?|\b0(?:[fd]_|x)[0-9a-f]+|&[0-9a-f]+)\b/i,

  register: {
    pattern: toCaseInsensitiveBoundaryPatternWithParen(
      REGISTERS_OF_THE_RV_32_I,
    ),
    lookbehind: true,
    alias: 'symbol',
  },

  operator: /<>|<<|>>|&&|\|\||[=!<>/]=?|[+\-*%#?&|^]|:[A-Z]+:/,
  punctuation: /[()[\],]/,
};

Prism.languages['riscv-asm'] = Prism.languages.riscv;
