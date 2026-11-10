"""
字节字段参数处理模块。

此模块提供参数检测、计算和注入功能，
用于处理字节字段图表的布局参数。
"""

import re

from .constants import (
    DEFAULT_BOXES_PER_ROW,
    DIAGRAM_TOTAL_WIDTH,
    DEFAULT_LEFT_MARGIN,
    DEFAULT_RIGHT_MARGIN,
    DEFAULT_ROW_HEIGHT,
    DEFAULT_FONT_SIZE,
)


def detect_boxes_per_row(content: str) -> int:
    """
    从 EDN 内容中检测 boxes-per-row 的值。
    
    使用正则表达式匹配 (def boxes-per-row <数字>) 模式，
    提取每行盒子数量的定义。如果未找到定义，
    返回默认值 DEFAULT_BOXES_PER_ROW。
    
    参数:
        content: EDN 内容字符串
        
    返回:
        检测到的 boxes-per-row 值，未找到则返回默认值
        
    示例:
        >>> content = "(def boxes-per-row 16)"
        >>> detect_boxes_per_row(content)
        16
        >>> detect_boxes_per_row("(draw-box ...)")
        32
    """
    # 使用正则表达式匹配 (def boxes-per-row <数字>)
    pattern = r'\(def\s+boxes-per-row\s+(\d+)\s*\)'
    match = re.search(pattern, content)

    if match:
        # 提取匹配到的数字
        value = int(match.group(1))
        # 验证是否为有效正整数
        if value > 0:
            return value

    # 未找到或无效，返回默认值
    return DEFAULT_BOXES_PER_ROW


def calculate_box_width(boxes_per_row: int) -> int:
    """
    根据每行盒子数量计算单个盒子的宽度。
    
    使用图表总宽度除以每行盒子数量来计算单个盒子的宽度。
    结果会转换为整数，确保宽度值可以直接用于 SVG 渲染。
    
    参数:
        boxes_per_row: 每行盒子的数量
        
    返回:
        计算出的盒子宽度（整数）
        
    示例:
        >>> calculate_box_width(32)
        24
        >>> calculate_box_width(16)
        48
    """
    # 使用总宽度除以盒子数量计算宽度
    box_width = DIAGRAM_TOTAL_WIDTH / boxes_per_row
    # 返回整数结果
    return int(box_width)


def inject_or_replace_param(content: str, param_name: str, param_value: int) -> str:
    """
    在 EDN 内容中注入或替换参数定义。
    
    如果参数已存在，则替换其值；如果不存在，则在合适的位置注入新定义。
    注入位置策略：
    1. 优先在最后一个 (def ...) 之后插入
    2. 如果没有 (def ...)，则在第一个 (draw-...) 之前插入
    3. 如果都没有，则在内容开头插入
    
    参数:
        content: EDN 内容字符串
        param_name: 参数名称（如 "left-margin"）
        param_value: 参数值（整数）
        
    返回:
        处理后的 EDN 内容字符串
        
    示例:
        >>> content = "(def boxes-per-row 32)\\n(draw-box ...)"
        >>> result = inject_or_replace_param(content, "left-margin", 1)
        >>> "(def left-margin 1)" in result
        True
    """
    # 构建参数定义的正则表达式模式
    param_pattern = rf'\(def\s+{re.escape(param_name)}\s+\d+\s*\)'

    # 检查参数是否已存在
    if re.search(param_pattern, content):
        # 参数已存在，替换其值
        new_def = f'(def {param_name} {param_value})'
        content = re.sub(param_pattern, new_def, content)
    else:
        # 参数不存在，需要注入
        new_def = f'(def {param_name} {param_value})'

        # 查找最后一个 (def ...) 的位置
        def_pattern = r'\(def\s+[^\s]+\s+[^)]+\)'
        def_matches = list(re.finditer(def_pattern, content))

        if def_matches:
            # 在最后一个 (def ...) 之后插入
            last_def = def_matches[-1]
            insert_pos = last_def.end()
            # 找到下一个换行符的位置
            next_newline = content.find('\n', insert_pos)
            if next_newline != -1:
                insert_pos = next_newline + 1
                content = content[:insert_pos] + new_def + '\n' + content[insert_pos:]
            else:
                # 没有换行符，直接在末尾添加
                content = content[:insert_pos] + '\n' + new_def + '\n' + content[insert_pos:]
        else:
            # 没有 (def ...)，查找第一个 (draw-...) 的位置
            draw_pattern = r'\(draw-[^\s]+\s+'
            draw_match = re.search(draw_pattern, content)

            if draw_match:
                # 在第一个 (draw-...) 之前插入
                insert_pos = draw_match.start()
                content = content[:insert_pos] + new_def + '\n' + content[insert_pos:]
            else:
                # 都没有，在内容开头插入
                content = new_def + '\n' + content

    return content


def process_bytefield_params(content: str) -> tuple[str, dict]:
    """
    处理字节字段图表的所有布局参数。
    
    此函数是参数处理的主入口，执行以下操作：
    1. 检测 boxes-per-row 的值
    2. 根据 boxes-per-row 计算 box-width
    3. 注入或替换 left-margin 参数
    4. 注入或替换 right-margin 参数
    5. 注入或替换 box-width 参数
    6. 注入或替换 row-height 参数（强制覆盖）
    7. 注入或替换 font-size 参数（默认字号定义）
    8. 在 defattrs 中注入 :font-size（如果缺失）
    9. 处理内容中的字号（:font-size）：大于 12 的除以 2，小于等于 12 的保持不变
    
    参数:
        content: EDN 内容字符串
        
    返回:
        元组 (处理后的内容, 处理信息字典)
        处理信息字典包含：
        - boxes_per_row: 检测到的每行盒子数
        - box_width: 计算出的盒子宽度
        - left_margin: 设置的左边距值
        - right_margin: 设置的右边距值
        - row_height: 设置的行高值
        - font_size: 设置的默认字号值
        - left_margin_replaced: 是否替换了 left-margin（布尔值）
        - right_margin_replaced: 是否替换了 right-margin（布尔值）
        - row_height_replaced: 是否替换了 row-height（布尔值）
        - box_width_injected: 是否注入了 box-width（布尔值）
        - font_size_injected: 是否注入了 font-size（布尔值）
        - font_sizes_processed: 处理的内容字号数量
        - font_size_changes: 内容字号变化列表
        
    示例:
        >>> content = "(def boxes-per-row 16)\\n(draw-box ...)"
        >>> result_content, info = process_bytefield_params(content)
        >>> info['boxes_per_row']
        16
        >>> info['box_width']
        48
    """
    # 记录处理信息
    info = {}

    # 1. 检测 boxes-per-row
    boxes_per_row = detect_boxes_per_row(content)
    info['boxes_per_row'] = boxes_per_row

    # 2. 计算 box-width
    box_width = calculate_box_width(boxes_per_row)
    info['box_width'] = box_width

    # 3. 检测原始参数是否存在
    left_margin_pattern = r'\(def\s+left-margin\s+(\d+)\s*\)'
    right_margin_pattern = r'\(def\s+right-margin\s+(\d+)\s*\)'
    box_width_pattern = r'\(def\s+box-width\s+(\d+)\s*\)'
    row_height_pattern = r'\(def\s+row-height\s+(\d+)\s*\)'
    font_size_pattern = r'\(def\s+font-size\s+(\d+)\s*\)'

    left_margin_match = re.search(left_margin_pattern, content)
    right_margin_match = re.search(right_margin_pattern, content)
    box_width_match = re.search(box_width_pattern, content)
    row_height_match = re.search(row_height_pattern, content)
    font_size_match = re.search(font_size_pattern, content)

    # 记录原始值
    if left_margin_match:
        info['left_margin_original'] = int(left_margin_match.group(1))
        info['left_margin_replaced'] = True
    else:
        info['left_margin_replaced'] = False

    if right_margin_match:
        info['right_margin_original'] = int(right_margin_match.group(1))
        info['right_margin_replaced'] = True
    else:
        info['right_margin_replaced'] = False

    if box_width_match:
        info['box_width_original'] = int(box_width_match.group(1))
        info['box_width_injected'] = False  # 已存在，不是注入
    else:
        info['box_width_injected'] = True  # 不存在，需要注入

    if row_height_match:
        info['row_height_original'] = int(row_height_match.group(1))
        info['row_height_replaced'] = True
    else:
        info['row_height_replaced'] = False

    if font_size_match:
        info['font_size_original'] = int(font_size_match.group(1))
        info['font_size_replaced'] = True
    else:
        info['font_size_injected'] = True

    # 4. 处理 left-margin
    info['left_margin'] = DEFAULT_LEFT_MARGIN
    content = inject_or_replace_param(content, 'left-margin', DEFAULT_LEFT_MARGIN)

    # 5. 处理 right-margin
    info['right_margin'] = DEFAULT_RIGHT_MARGIN
    content = inject_or_replace_param(content, 'right-margin', DEFAULT_RIGHT_MARGIN)

    # 6. 处理 box-width
    content = inject_or_replace_param(content, 'box-width', box_width)

    # 7. 处理 row-height（强制覆盖）
    info['row_height'] = DEFAULT_ROW_HEIGHT
    content = inject_or_replace_param(content, 'row-height', DEFAULT_ROW_HEIGHT)

    # 8. 处理默认字号（font-size）定义
    info['font_size'] = DEFAULT_FONT_SIZE
    content = inject_or_replace_param(content, 'font-size', DEFAULT_FONT_SIZE)

    # 9. 在 defattrs 中注入字号（如果缺失）
    content = inject_font_size_to_defattrs(content, DEFAULT_FONT_SIZE)

    # 10. 处理内容中的字号（:font-size）
    content, font_size_info = process_font_sizes(content)
    info.update(font_size_info)

    return content, info


def process_font_sizes(content: str) -> tuple[str, dict]:
    """
    处理 EDN 内容中的字号（font-size）。
    
    对于大于 12 的字号，将其除以 2；
    对于小于等于 12 的字号，保持不变。
    
    参数:
        content: EDN 内容字符串
        
    返回:
        元组 (处理后的内容, 处理信息字典)
        处理信息字典包含：
        - font_sizes_processed: 处理的字号数量
        - font_size_changes: 字号变化列表 [(原值, 新值), ...]
        
    示例:
        >>> content = '{:font-size 18}'
        >>> result, info = process_font_sizes(content)
        >>> ':font-size 9' in result
        True
    """
    info = {
        'font_sizes_processed': 0,
        'font_size_changes': []
    }

    # 匹配 :font-size 和 font-size 后面的数字
    # 支持多种格式：:font-size 18, font-size 12, 等
    # 使用两个模式分别处理

    def replace_font_size(match):
        prefix = match.group(1)  # 可能是 ":" 或 空字符串
        original_size = int(match.group(2))

        # 对大于 12 的字号进行除以 2
        if original_size > 12:
            new_size = original_size // 2
            info['font_sizes_processed'] += 1
            info['font_size_changes'].append((original_size, new_size))
            return f'{prefix}font-size {new_size}'
        else:
            # 小于等于 12 的保持不变
            return match.group(0)

    # 匹配 :font-size 或 "font-size（在 defattrs 中）
    # 模式说明：(:)?font-size\s+(\d+)
    # (:)? - 可选的冒号
    # font-size - 字面量
    # \s+ - 一个或多个空格
    # (\d+) - 数字
    pattern = r'(:)?font-size\s+(\d+)'

    # 替换所有匹配的字号
    content = re.sub(pattern, replace_font_size, content)

    return content, info


def inject_font_size_to_defattrs(content: str, font_size: int) -> str:
    """
    在 defattrs 中注入或更新 :font-size。
    
    如果 defattrs 中已有 :font-size，则更新它；
    如果没有，则注入默认字号。
    
    参数:
        content: EDN 内容字符串
        font_size: 要设置的字号值
        
    返回:
        处理后的 EDN 内容字符串
        
    示例:
        >>> content = '(defattrs :plain [:plain {:font-family "M+ 1p"}])'
        >>> result = inject_font_size_to_defattrs(content, 12)
        >>> ':font-size 12' in result
        True
    """
    # 匹配 defattrs 定义
    # 模式：(defattrs :name [:name {属性}])
    defattrs_pattern = r'\(defattrs\s+:\w+\s+\[:\w+\s+\{([^}]+)\}\]\)'

    def process_defattrs(match):
        attrs = match.group(1)

        # 检查是否已有 :font-size
        if ':font-size' in attrs:
            # 已有，不需要处理（会被 process_font_sizes 处理）
            return match.group(0)
        else:
            # 没有，注入默认字号
            # 在属性末尾添加 :font-size
            new_attrs = attrs.rstrip() + f' :font-size {font_size}'
            return match.group(0).replace(attrs, new_attrs)

    content = re.sub(defattrs_pattern, process_defattrs, content)
    return content
