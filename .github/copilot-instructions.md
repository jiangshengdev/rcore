# 编码规范指引

## 操作流程规范

### 强制确认机制

- 每一步都需要等待明确确认，禁止自行行动
- 任何代码修改、文件创建、删除操作都必须先说明意图并等待用户确认
- 禁止在单次回复中执行多个未经确认的操作
- 如果用户要求批量操作，必须逐项列出并等待逐一确认

### 禁止行为

- 禁止假设用户意图
- 禁止自动修复未明确要求修复的问题
- 禁止主动重构代码结构
- 禁止未经允许安装或修改依赖

## 代码注释规范

修改文件时，不要注释你修改了什么，而是注释这段代码是做什么的

## 示例说明

### 修改前

```rust
pub unsafe fn add_to_heap(&mut self, mut start: usize, mut end: usize) {
    start = align_up(start, size_of::<usize>());
    end = align_down(end, size_of::<usize>());
    assert!(start <= end);
    // ...其余代码...
}
```

### 修改后（错误）

```rust
// 提取对齐常量，而未说明该常量用途
let ptr_align = size_of::<usize>();
// 对 start 地址进行了上对齐，但未说明目的
start = align_up(start, ptr_align);
// ...更多修改...
fn add_to_heap(start: usize, end: usize) {}
```

### 修改后（正确）

```rust
/// 将内存区间 [start, end) 按伙伴算法加入堆管理
pub unsafe fn add_to_heap(&mut self, mut start: usize, mut end: usize) {
    // usize 对齐边界，用于确保地址以指针大小对齐
    let ptr_align = size_of::<usize>();
    // 将 start 向上对齐到指针对齐边界
    start = align_up(start, ptr_align);
    // 将 end 向下对齐到指针对齐边界
    end = align_down(end, ptr_align);
    // 验证对齐后区间为有效范围
    assert!(start <= end);
    // ...其余代码...
}
```

以上示例展示了正确的注释方式：注释描述代码行为和目的，而非改动本身。
