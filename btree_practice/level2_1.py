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


def print_tree(node: BPlusNode, level: int = 0):
    """트리 시각화"""
    indent = "  " * level
    node_type = "🍃" if node.is_leaf else "🌳"
    print(f"{indent}{node_type} {node.keys}")

    if not node.is_leaf and node.children:
        for child in node.children:
            print_tree(child, level + 1)


# ======================================================================
# Task 2.1.1: Order=3 B+Tree 수동 구축
# ======================================================================


def build_static_tree_order3():
    """
    Order=3 B+Tree 구축 (최대 3개 자식, 최대 2개 키)

    [설정]
    - Order: 3
    - 최대 키 개수: 2 (Order - 1)
    - 키 목록: [1, 3, 5, 7, 9, 11] (6개)

    [목표 구조]
            [5, 9]           ← Root (2개 키, 3개 자식)
           /   |   \
        [1,3] [5,7] [9,11]  ← 3 Leaves (각 2개 키)

    [작업 순서]
    1. Leaf 3개 만들기
    2. Sibling 연결
    3. Root (Internal) 만들기
    """
    print("=" * 60)
    print("Task 2.1.1: Order=3 B+Tree 구축")
    print("=" * 60)

    ORDER = 3
    MAX_KEYS = ORDER - 1  # 2개

    print(f"\n[설정] Order={ORDER}, 최대 {MAX_KEYS}개 키/노드")
    print("[키 리스트] 1, 3, 5, 7, 9, 11 (총 6개)\n")

    # ----------------------------------------------------------------
    # Step 1: Leaf 노드들 생성
    # ----------------------------------------------------------------
    print("Step 1: Leaf 노드 생성")

    # TODO: 아래 코드를 완성하세요
    leaf1 = BPlusNode(is_leaf=True, keys=[1, 3], values=["1", "3"])  # keys=[1, 3]
    leaf2 = BPlusNode(is_leaf=True, keys=[5, 7], values=["1", "3"])  # keys=[5, 7]
    leaf3 = BPlusNode(is_leaf=True, keys=[9, 11], values=["1", "3"])  # keys=[9, 11]

    # ----------------------------------------------------------------
    # Step 2: Sibling 포인터 연결
    # ----------------------------------------------------------------
    print("Step 2: Sibling 포인터 연결")

    leaf1.next = leaf2
    leaf2.next = leaf3

    # ----------------------------------------------------------------
    # Step 3: Root (Internal) 생성
    # ----------------------------------------------------------------
    print("Step 3: Root 노드 생성")

    # TODO: Root의 keys는? children은?
    # 힌트: keys=[5, 9]면 구간이 어떻게 나뉘는지 생각해보세요
    #   child[0]: key < 5
    #   child[1]: 5 ≤ key < 9
    #   child[2]: key ≥ 9
    root = BPlusNode(
        is_leaf=False, keys=[5, 9], children=[leaf1, leaf2, leaf3], values=["1", "3"]
    )

    # ----------------------------------------------------------------
    # 결과 출력
    # ----------------------------------------------------------------
    if root:
        print("\n[완성된 트리]")
        print_tree(root)
    else:
        print("\n❌ 아직 구현되지 않았습니다!")

    return root


# ======================================================================
# Task 2.1.2: Order=4 B+Tree 수동 구축 (도전 과제)
# ======================================================================


def build_static_tree_order4():
    """
    Order=4 B+Tree 구축 (최대 4개 자식, 최대 3개 키)

    [설정]
    - Order: 4
    - 최대 키 개수: 3 (Order - 1)
    - 키 목록: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] (12개)

    [목표 구조]
            [4, 7, 10]              ← Root (3개 키, 4개 자식)
           /   |   |   \
        [1,2,3] [4,5,6] [7,8,9] [10,11,12] ← 4 Leaves (각 3개 키)

    [검증]
    - 각 Leaf: 3개 키 ≤ MAX_KEYS(3) ✅
    - Root: 3개 키, 4개 자식 ≤ Order(4) ✅
    """
    print("\n" + "=" * 60)
    print("Task 2.1.2: Order=4 B+Tree 구축 (도전 과제)")
    print("=" * 60)

    ORDER = 4
    MAX_KEYS = ORDER - 1  # 3개

    print(f"\n[설정] Order={ORDER}, 최대 {MAX_KEYS}개 키/노드")
    print("[키 리스트] 1~12 (총 12개)\n")

    # TODO: 4개 Leaf 만들기
    leaf1 = BPlusNode(is_leaf=True, keys=[1, 2, 3], values=[1, 2, 3])  # [1, 2, 3]
    leaf2 = BPlusNode(is_leaf=True, keys=[4, 5, 6], values=[1, 2, 3])  # [4, 5, 6]
    leaf3 = BPlusNode(is_leaf=True, keys=[7, 8, 9], values=[1, 2, 3])  # [7, 8, 9]
    leaf4 = BPlusNode(is_leaf=True, keys=[10, 11, 12], values=[1, 2, 3])  # [10, 11, 12]

    # TODO: Sibling 연결
    leaf1.next = leaf2
    leaf2.next = leaf3
    leaf3.next = leaf4

    # TODO: Root 만들기
    root = BPlusNode(
        is_leaf=False, children=[leaf1, leaf2, leaf3, leaf4], keys=[4, 7, 10]
    )

    if root:
        print("[완성된 트리]")
        print_tree(root)
    else:
        print("❌ 아직 구현되지 않았습니다!")

    return root


# ======================================================================
# 검증 함수
# ======================================================================


def validate_tree(node: BPlusNode, order: int) -> bool:
    """B+Tree가 올바르게 구축되었는지 검증"""
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
        if node.values is None:
            print(f"❌ Leaf에 values 없음")
            return False
        if len(node.keys) != len(node.values):
            print(f"❌ keys와 values 개수 불일치")
            return False
    else:
        if node.children is None:
            print(f"❌ Internal에 children 없음")
            return False
        if len(node.children) != len(node.keys) + 1:
            print(
                f"❌ children 개수 오류: {len(node.children)} != {len(node.keys) + 1}"
            )
            return False
        for child in node.children:
            if not validate_tree(child, order):
                return False

    return True


# ======================================================================
# 참고 정답 (학습용)
# ======================================================================


def solution_order3():
    """Order=3 정답 예시"""
    leaf1 = BPlusNode(is_leaf=True, keys=[1, 3], values=["v1", "v3"])
    leaf2 = BPlusNode(is_leaf=True, keys=[5, 7], values=["v5", "v7"])
    leaf3 = BPlusNode(is_leaf=True, keys=[9, 11], values=["v9", "v11"])

    leaf1.next = leaf2
    leaf2.next = leaf3

    root = BPlusNode(is_leaf=False, keys=[5, 9], children=[leaf1, leaf2, leaf3])
    return root


def solution_order4():
    """Order=4 정답 예시"""
    leaf1 = BPlusNode(is_leaf=True, keys=[1, 2, 3], values=["v1", "v2", "v3"])
    leaf2 = BPlusNode(is_leaf=True, keys=[4, 5, 6], values=["v4", "v5", "v6"])
    leaf3 = BPlusNode(is_leaf=True, keys=[7, 8, 9], values=["v7", "v8", "v9"])
    leaf4 = BPlusNode(is_leaf=True, keys=[10, 11, 12], values=["v10", "v11", "v12"])

    leaf1.next = leaf2
    leaf2.next = leaf3
    leaf3.next = leaf4

    root = BPlusNode(
        is_leaf=False, keys=[4, 7, 10], children=[leaf1, leaf2, leaf3, leaf4]
    )
    return root


# ======================================================================
# 메인 실행
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

    # 정답 확인용
    print("\n" + "=" * 60)
    print("📝 참고: 정답을 보려면 solution_order3(), solution_order4() 호출")
    print("=" * 60)
