"""
Level 1.1: B+Tree 기초 - 트리 시각화 연습

목표:
1. BPlusNode 클래스 이해
2. print_tree() 함수 구현
3. 간단한 트리 출력 테스트
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BPlusNode:
    """
    B+Tree의 노드 (Leaf 또는 Internal)

    Attributes:
        is_leaf: True면 Leaf 노드 (데이터 저장), False면 Internal 노드 (인덱스)
        keys: 정렬된 키 리스트 (검색 기준)
        children: Internal 노드의 자식 노드들 (Leaf는 None)
        values: Leaf 노드의 실제 데이터 (Internal은 None)
        next: Leaf 노드의 다음 Sibling (Range Scan용)
    """

    is_leaf: bool
    keys: List[int] = field(default_factory=list)
    children: Optional[List["BPlusNode"]] = None
    values: Optional[List] = None
    next: Optional["BPlusNode"] = None


# ======================================================================
# Task 1.1.1: 트리 시각화 함수 구현
# ======================================================================


def print_tree(node: BPlusNode, level: int = 0):
    """
    트리를 텍스트로 시각화 (디버깅용)

    Args:
        node: 출력할 노드
        level: 현재 깊이 (들여쓰기용)

    출력 형식:
        [1, 3, 5]           ← Leaf
          [10]              ← Internal (들여쓰기)
            [7, 8]          ← 더 깊은 Leaf

    TODO: 이 함수를 구현하세요!

    힌트:
    1. "  " * level로 들여쓰기 생성
    2. node.keys를 출력 (예: [1, 3, 5])
    3. node.is_leaf가 False면 children도 재귀적으로 출력
    """

    # 예상 출력:
    # [5]
    #   [1, 3]
    #   [5, 7]

    indent = "  " * level
    print(f"{indent} {node.keys}")
    if not node.is_leaf:
        for n in node.children:
            print_tree(n, level + 1)


# ======================================================================
# 테스트 코드
# ======================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Level 1.1 Test: 트리 시각화")
    print("=" * 50)

    # Test 1: 단순 Leaf 노드
    print("\n[Test 1] 단순 Leaf 노드:")
    leaf = BPlusNode(is_leaf=True, keys=[1, 3, 5], values=["a", "b", "c"])
    print_tree(leaf)
    # 예상 출력: [1, 3, 5]

    # Test 2: 2-레벨 트리 (Root + 2 Leaves)
    print("\n[Test 2] 2-레벨 트리 (Root → 2 Leaves):")
    leaf1 = BPlusNode(is_leaf=True, keys=[1, 3], values=["a", "b"])
    leaf2 = BPlusNode(is_leaf=True, keys=[5, 7], values=["c", "d"])
    root = BPlusNode(is_leaf=False, keys=[5], children=[leaf1, leaf2])
    print_tree(root)
    # 예상 출력:
    # [5]
    #   [1, 3]
    #   [5, 7]

    # Test 3: 3-레벨 트리
    print("\n[Test 3] 3-레벨 트리 (더 깊은 구조):")
    leaf_a = BPlusNode(is_leaf=True, keys=[1, 2], values=["a", "b"])
    leaf_b = BPlusNode(is_leaf=True, keys=[3, 4], values=["c", "d"])
    leaf_c = BPlusNode(is_leaf=True, keys=[5, 6], values=["e", "f"])
    leaf_d = BPlusNode(is_leaf=True, keys=[7, 8], values=["g", "h"])

    internal_left = BPlusNode(is_leaf=False, keys=[3], children=[leaf_a, leaf_b])
    internal_right = BPlusNode(is_leaf=False, keys=[7], children=[leaf_c, leaf_d])
    root2 = BPlusNode(is_leaf=False, keys=[5], children=[internal_left, internal_right])
    print_tree(root2)
    # 예상 출력:
    # [5]
    #   [3]
    #     [1, 2]
    #     [3, 4]
    #   [7]
    #     [5, 6]
    #     [7, 8]

    print("\n" + "=" * 50)
    print("구현이 완료되면 위의 예상 출력과 비교해보세요!")
    print("=" * 50)
