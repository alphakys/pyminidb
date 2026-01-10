"""
Level 2.1: 정적 B+Tree 수동 구축

목표:
1. 주어진 키들로 완성된 B+Tree 만들기 (Insert 알고리즘 없이!)
2. Leaf → Internal → Root 순서로 Bottom-Up 구축
3. Sibling 포인터 연결 연습
4. 트리 검증 함수로 정확성 확인

핵심 개념:
- "Insert는 나중에 배우고, 일단 완성된 트리부터 만들자"
- "아래(Leaf)부터 위(Root)로 쌓아올리기"
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BPlusNode:
    is_leaf: bool
    keys: List[int] = field(default_factory=list)
    children: Optional[List["BPlusNode"]] = None
    values: Optional[List] = None
    next: Optional["BPlusNode"] = None

    is_leaf: bool
    keys: List[int] = field(default_factory=list)
    children: Optional[List["BPlusNode"]]
    values: Optional[List]
    next: Optional["BPlusNode"]


def print_tree(node: BPlusNode, level: int = 0):
    """트리 시각화"""
    indent = "  " * level
    node_type = "🍃" if node.is_leaf else "🌳"
    print(f"{indent}{node_type} {node.keys}")

    if not node.is_leaf and node.children:
        for child in node.children:
            print_tree(child, level + 1)


# ======================================================================
# Task 2.1.1: Order=3 B+Tree 수동 구축 (키: 1, 3, 5, 7, 9, 11, 13, 15)
# ======================================================================


def build_static_tree_order3():
    """
    Order=3 B+Tree 구축 (최대 3개 자식, 최대 2개 키)

    목표 구조:
            [7]              ← Root (Internal)
           /   \
        [1,3,5] [7,9,11,13,15] ← 아니다! Order=3이면 Leaf도 최대 2개 키!

    올바른 구조:
            [5, 11]           ← Root (Internal)
           /   |   \
        [1,3] [5,7,9] [11,13,15] ← Leaves

    작업 순서:
    1. Leaf 3개 만들기
    2. Sibling 연결
    3. Root (Internal) 만들기
    """
    print("=" * 60)
    print("Task 2.1.1: Order=3 B+Tree 구축")
    print("=" * 60)

    ORDER = 3
    MAX_KEYS_PER_NODE = ORDER - 1  # 2개

    print(f"\n[설정] Order={ORDER}, 최대 {MAX_KEYS_PER_NODE}개 키/노드")
    print("[키 리스트] 1, 3, 5, 7, 9, 11, 13, 15 (총 8개)\n")

    # Step 1: Leaf 노드들 생성
    print("Step 1: Leaf 노드 생성 (Bottom Layer)")

    # TODO: 여기에 코드를 작성하세요!
    # 힌트:
    # - Leaf는 최대 2개 키를 가질 수 있음
    # - 8개 키를 3개 Leaf에 나눠 담기
    # - 각 Leaf는 is_leaf=True, values도 설정

    leaf1 = None  # [1, 3]
    leaf2 = None  # [5, 7, 9] ← 3개? Order 위반!
    leaf3 = None  # [11, 13, 15]

    # Step 2: Sibling 포인터 연결
    print("Step 2: Sibling 포인터 연결 (Linked List)")

    # TODO: leaf1.next = ? 형식으로 연결

    # Step 3: Root (Internal) 생성
    print("Step 3: Root 노드 생성 (Index Layer)")

    # TODO: Internal 노드 생성
    # 힌트:
    # - keys는 각 구간의 "시작점"
    # - children은 [leaf1, leaf2, leaf3]

    root = None

    # 검증
    if root:
        print("\n[완성된 트리]")
        print_tree(root)
    else:
        print("\n❌ 아직 구현되지 않았습니다!")

    return root


# ======================================================================
# Task 2.1.2: Order=4 B+Tree 수동 구축 (더 복잡한 예제)
# ======================================================================


def build_static_tree_order4():
    """
    Order=4 B+Tree 구축 (최대 4개 자식, 최대 3개 키)

    키: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 (총 12개)

    목표 구조:
              [4, 8]                    ← Root
             /   |   \
        [1,2,3] [4,5,6,7] [8,9,10,11,12] ← Leaves (5개는 Order 위반!)

    올바른 구조:
              [4, 7, 10]                ← Root
             /   |   |   \
        [1,2,3] [4,5,6] [7,8,9] [10,11,12] ← 4개 Leaves

    도전 과제! 스스로 구축해보세요.
    """
    print("\n" + "=" * 60)
    print("Task 2.1.2: Order=4 B+Tree 구축 (도전 과제)")
    print("=" * 60)

    ORDER = 4
    MAX_KEYS_PER_NODE = ORDER - 1  # 3개

    print(f"\n[설정] Order={ORDER}, 최대 {MAX_KEYS_PER_NODE}개 키/노드")
    print("[키 리스트] 1~12 (총 12개)\n")

    # TODO: 여기에 코드를 작성하세요!
    # 4개 Leaf를 만들고, Sibling 연결하고, Root 만들기

    leaf1 = BPlusNode(is_leaf=True, keys=[1, 2, 3], values=["a", "b", "c"])
    leaf2 = None  # [4, 5, 6]
    leaf3 = None  # [7, 8, 9]
    leaf4 = None  # [10, 11, 12]

    # Sibling 연결
    # TODO

    # Root
    root = None  # keys=[4, 7, 10], children=[leaf1, leaf2, leaf3, leaf4]

    if root:
        print("[완성된 트리]")
        print_tree(root)
    else:
        print("❌ 아직 구현되지 않았습니다!")

    return root


# ======================================================================
# Task 2.1.3: 트리 검증 함수
# ======================================================================


def validate_tree(node: BPlusNode, order: int) -> bool:
    """
    B+Tree가 올바르게 구축되었는지 검증

    검증 항목:
    1. 키가 정렬되어 있는가?
    2. Order 제약을 지키는가? (최대 order-1개 키)
    3. Leaf의 Sibling이 연결되어 있는가?
    4. Internal의 children 개수가 keys+1인가?
    """
    MAX_KEYS = order - 1

    # 1. 키 정렬 확인
    if node.keys != sorted(node.keys):
        print(f"❌ 키가 정렬되지 않음: {node.keys}")
        return False

    # 2. Order 제약 확인
    if len(node.keys) > MAX_KEYS:
        print(f"❌ 키 개수 초과: {len(node.keys)} > {MAX_KEYS}")
        return False

    # 3. Leaf vs Internal 검증
    if node.is_leaf:
        # Leaf: values 있어야 함
        if node.values is None:
            print(f"❌ Leaf에 values 없음")
            return False
        if len(node.keys) != len(node.values):
            print(f"❌ keys와 values 개수 불일치")
            return False
    else:
        # Internal: children 있어야 함
        if node.children is None:
            print(f"❌ Internal에 children 없음")
            return False
        if len(node.children) != len(node.keys) + 1:
            print(
                f"❌ children 개수 오류: {len(node.children)} != {len(node.keys) + 1}"
            )
            return False

        # 재귀적으로 children 검증
        for child in node.children:
            if not validate_tree(child, order):
                return False

    return True


# ======================================================================
# 테스트 실행
# ======================================================================

if __name__ == "__main__":
    print("\n🏗️  B+Tree 수동 구축 실습\n")

    # Task 2.1.1
    tree1 = build_static_tree_order3()
    if tree1:
        print("\n[검증]")
        if validate_tree(tree1, order=3):
            print("✅ Order=3 트리가 올바르게 구축되었습니다!")
        else:
            print("❌ 트리 구조에 오류가 있습니다.")

    # Task 2.1.2
    tree2 = build_static_tree_order4()
    if tree2:
        print("\n[검증]")
        if validate_tree(tree2, order=4):
            print("✅ Order=4 트리가 올바르게 구축되었습니다!")
        else:
            print("❌ 트리 구조에 오류가 있습니다.")

    print("\n" + "=" * 60)
    print("완료 후 다음 단계: Level 2.2 - Search 알고리즘")
    print("=" * 60)
