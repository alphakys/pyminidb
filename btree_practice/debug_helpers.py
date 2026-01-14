"""
디버깅 헬퍼 함수
"""

from typing import List


def validate_tree(node, max_keys: int, level: int = 0) -> List[str]:
    """
    트리 구조 검증

    Returns:
        에러 메시지 리스트 (비어있으면 정상)
    """
    errors = []
    indent = "  " * level

    # 1. 키 개수 체크
    if len(node.keys) > max_keys:
        errors.append(
            f"{indent}❌ 키 개수 초과: {len(node.keys)} > {max_keys} at {node.keys}"
        )

    # 2. 키 정렬 체크
    if node.keys != sorted(node.keys):
        errors.append(f"{indent}❌ 키 미정렬: {node.keys}")

    # 3. 중복 키 체크
    if len(node.keys) != len(set(node.keys)):
        errors.append(f"{indent}❌ 중복 키 발견: {node.keys}")

    if node.is_leaf:
        # Leaf 검증
        if node.values is None or len(node.keys) != len(node.values):
            errors.append(f"{indent}❌ Leaf: keys와 values 불일치")
    else:
        # Internal 검증
        if node.children is None:
            errors.append(f"{indent}❌ Internal: children이 None")
        elif len(node.children) != len(node.keys) + 1:
            errors.append(
                f"{indent}❌ Internal: children({len(node.children)}) != keys({len(node.keys)}) + 1"
            )

        # 재귀적으로 children 검증
        if node.children:
            for i, child in enumerate(node.children):
                child_errors = validate_tree(child, max_keys, level + 1)
                errors.extend(child_errors)

    return errors


def print_tree_detailed(node, level: int = 0):
    """상세 트리 출력 (children 개수 포함)"""
    indent = "  " * level
    node_type = "🍃" if node.is_leaf else "🌳"

    if node.is_leaf:
        print(
            f"{indent}{node_type} keys={node.keys} (values={len(node.values) if node.values else 0})"
        )
    else:
        child_count = len(node.children) if node.children else 0
        print(f"{indent}{node_type} keys={node.keys} (children={child_count})")

        if node.children:
            for child in node.children:
                print_tree_detailed(child, level + 1)
