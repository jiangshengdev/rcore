# scripts/lib 中的代码重复分析报告

## 🔍 分析概述

通过对 `scripts/lib` 目录的深度分析，发现 `common/utils.py` 中的功能确实存在重复实现的问题，主要体现在以下几个方面：

## 📊 重复代码发现

### 1. 项目根目录查找功能 - **严重重复**

**Python 实现** (`common/utils.py`):

```python
def find_project_root(marker_files: Tuple[str, ...] = ("docusaurus.config.ts", "package.json")) -> Optional[str]:
  """自动寻找项目根目录"""
  current_dir = os.getcwd()
  while current_dir != "/":
    for marker in marker_files:
      if os.path.isfile(os.path.join(current_dir, marker)):
        return current_dir
    current_dir = os.path.dirname(current_dir)
  return None
```

**Shell 重复实现**:

- `memory_viz/bin/common.sh` 中的 `find_rcore_root()` 函数
- `image/convert-png-to-webp.sh` 中的 `find_root()` 函数
- `image/convert-svg-to-svgo.sh` 中的 `find_root()` 函数

**重复代码统计**: 1个Python函数 + 3个Shell函数 = **4处重复实现**

### 2. 目录创建功能 - **中等重复**

**Python 实现** (`common/utils.py`):

```python
def ensure_dir(path: str) -> None:
  """确保目录存在，如果不存在则创建"""
  os.makedirs(path, exist_ok=True)
```

**重复实现**:

- `visualizers/binary_tree.py`: `os.makedirs(output_dir, exist_ok=True)`
- `visualizers/buddy_system.py`: `os.makedirs(output_dir, exist_ok=True)`
- Shell脚本中的 `mkdir -p` 命令（6处）

**重复代码统计**: 1个Python函数 + 2个直接调用 + 6个Shell命令 = **9处重复实现**

### 3. 脚本目录获取功能 - **轻微重复**

**Python 实现** (`common/utils.py`):

```python
def get_script_dir() -> str:
  """获取当前脚本所在目录"""
  return os.path.dirname(os.path.abspath(__file__))
```

**重复实现**:

- `visualizers/binary_tree.py`: `os.path.dirname(os.path.abspath(__file__))`
- `visualizers/buddy_system.py`: `os.path.dirname(os.path.abspath(__file__))`
- Shell脚本中的 `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`

**重复代码统计**: 1个Python函数 + 2个直接调用 + 多个Shell变体 = **5+处重复实现**

## 📈 使用情况分析

### ❌ utils.py 实际使用情况

- **Python导入**: 0次（未被任何Python文件导入）
- **直接调用**: 0次（无任何引用）
- **状态**: **完全未使用**

### ✅ 重复实现的使用情况

- **Shell脚本**: 高频使用，是主要的执行路径
- **Python直接实现**: 在visualizers中被直接使用
- **状态**: **正在积极使用**

## 🚨 问题严重性评估

1. **功能重复**: 同一功能被实现4-9次
2. **维护负担**: 修改逻辑需要同步更新多个位置
3. **不一致风险**: 不同实现可能出现行为差异
4. **资源浪费**: utils.py 模块完全未被使用但占用空间

## 💡 建议解决方案

### 方案一：统一到Shell实现（推荐）

```bash
# 理由：Shell脚本是主要执行路径，且已经有完善的 common.sh
# 行动：删除 utils.py，统一使用 shell 工具函数
# 影响：最小，因为Python函数未被使用
```

### 方案二：统一到Python实现

```python
# 理由：如果未来要增强Python模块功能
# 行动：修改所有Python文件导入utils.py，重构Shell脚本
# 影响：较大，需要修改多个文件
```

### 方案三：混合方案

```bash
# 保持Shell和Python分离，但消除同类型重复
# Python: 使用 utils.py
# Shell: 使用 common.sh  
# 影响：中等，需要重构Python文件
```

## 🎯 优先级建议

1. **高优先级**: 统一项目根目录查找逻辑（4处重复）
2. **中优先级**: 清理目录创建重复代码（9处重复）
3. **低优先级**: 评估是否保留 utils.py 模块

## 📝 结论

`common/utils.py` 暴露了一个典型的代码重复问题：

- **功能有价值**：所提供的工具函数确实有用
- **实现被忽略**：但是实际项目中选择了直接实现而不是复用
- **重复成本高**：导致了大量重复代码和维护负担

建议优先解决项目根目录查找的重复问题，这是影响最严重的重复实现。
