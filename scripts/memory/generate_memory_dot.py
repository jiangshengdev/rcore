import sys
import argparse
from scripts.memory.parser import parse_gdb_groups
from scripts.memory.memory_dot_generator import (
  MemoryDotGenerator, NULL_VAL,
  RANKDIR, SPLINES, FONT, FONT_SIZE, NODE_MARGIN
)


def parse_args():
  parser = argparse.ArgumentParser(description="解析 GDB 内存输出并生成 Graphviz DOT 格式文件。")
  parser.add_argument('file', nargs='?', help="包含 GDB 内存输出的输入文件。如果未提供，则从标准输入读取。")
  return parser.parse_args()


def main():
  # 解析命令行参数并读取输入
  args = parse_args()
  if args.file:
    with open(args.file, 'r') as f:
      lines = f.read().splitlines()
  else:
    lines = sys.stdin.read().splitlines()
  groups = parse_gdb_groups(lines)
  # 预处理分组信息，构建全局地址映射
  group_infos = []
  global_addr_map = {}
  for idx, group in enumerate(groups, 1):
    gen = MemoryDotGenerator(group['lines'])
    prefix = f"g{idx}_"
    # 构建 all_addrs 同 to_dot
    all_addrs = gen.addresses.copy()
    # 记录组信息
    group_infos.append({'prefix': prefix, 'all_addrs': all_addrs, 'memory': gen.memory})
    # 填充全局地址映射
    for i, addr in enumerate(all_addrs):
      global_addr_map[addr] = (prefix, i)
  # 开始写入 DOT
  dot_lines = [
    "digraph MemoryLayout {",
    f"    rankdir={RANKDIR};",
    f"    splines={SPLINES};",
    f"    nodesep=0.4;",
    f"    ranksep=0.05;",
    f"    node [shape=record, fontname=\"{FONT}\", fontsize={FONT_SIZE}, margin={NODE_MARGIN}];",
    f"    edge [fontname=\"{FONT}\", fontsize={FONT_SIZE}];",
    ""
  ]
  # 各组子图
  for info in group_infos:
    dot_lines.append(
      MemoryDotGenerator.to_dot(
        info['memory'], info['all_addrs'], prefix=info['prefix']
      )
    )
  # 跨组真实连接: 指针值匹配任意已知地址
  dot_lines.append("")
  for info in group_infos:
    prefix = info['prefix']
    for i, addr in enumerate(info['all_addrs']):
      val = info['memory'].get(addr)
      if val and val != NULL_VAL and val in global_addr_map:
        tgt_prefix, tgt_i = global_addr_map[val]
        src_port = 'next' if i == 0 else 'val'
        dot_lines.append(f'    {prefix}node{i}:{src_port} -> {tgt_prefix}node{tgt_i}:addr;')
  dot_lines.append("}")
  print("\n".join(dot_lines))


if __name__ == "__main__":
  main()
