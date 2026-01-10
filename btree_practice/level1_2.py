"""
Level 1.2: B+Tree 용어 정리 및 구조 이해

목표:
1. Leaf vs Internal Node의 차이 명확히 이해
2. Order, Fanout 개념 이해
3. BPlusNode의 각 필드가 왜 필요한지 체감
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BPlusNode:
    """
    B+Tree의 노드

    핵심 구분:
    - Leaf (is_leaf=True): 실제 데이터를 저장
    - Internal (is_leaf=False): 검색 경로만 안내 (이정표)
    """

    is_leaf: bool
    keys: List[int] = field(default_factory=list)
    children: Optional[List["BPlusNode"]] = None
    values: Optional[List] = None
    next: Optional["BPlusNode"] = None


def print_tree(node: BPlusNode, level: int = 0):
    """트리 시각화 (Level 1.1에서 구현한 함수)"""
    indent = "  " * level
    node_type = "🍃LEAF" if node.is_leaf else "🌳INTERNAL"
    print(f"{indent}{node_type}: {node.keys}")

    if not node.is_leaf and node.children:
        for child in node.children:
            print_tree(child, level + 1)


# ======================================================================
# Task 1.2.1: Leaf vs Internal 비교 실습
# ======================================================================


def demonstrate_node_types():
    """
    Leaf와 Internal 노드의 차이를 명확히 보여주는 예제

    핵심 차이:
    1. Leaf: values 사용 (실제 데이터)
    2. Internal: children 사용 (포인터)
    3. Leaf: next 사용 (Sibling 링크)
    """
    print("=" * 60)
    print("Task 1.2.1: Leaf vs Internal Node")
    print("=" * 60)

    # Leaf 노드 생성
    print("\n[1] Leaf 노드 특징:")
    leaf = BPlusNode(
        is_leaf=True,
        keys=[10, 20, 30],
        values=["Alice", "Bob", "Charlie"],  # ← 실제 데이터!
        next=None,  # ← Sibling 포인터 (나중에 연결)
    )

    print(f"   - keys: {leaf.keys}")
    print(f"   - values: {leaf.values}")
    print(f"   - children: {leaf.children}")  # None
    print(f"   - next: {leaf.next}")

    # Internal 노드 생성
    print("\n[2] Internal 노드 특징:")
    dummy_child = BPlusNode(is_leaf=True, keys=[1], values=["dummy"])
    internal = BPlusNode(
        is_leaf=False,
        keys=[50],  # ← "50 이하는 왼쪽, 50 초과는 오른쪽"
        children=[dummy_child, dummy_child],  # ← 자식 포인터!
        values=None,  # ← 데이터 없음!
    )

    print(f"   - keys: {internal.keys}")
    print(f"   - values: {internal.values}")  # None
    print(f"   - children: {len(internal.children)} 개")
    print(f"   - next: {internal.next}")  # None (Internal은 Sibling 안 씀)

    print("\n✅ 핵심: Leaf는 '데이터', Internal은 '포인터'")


# ======================================================================
# Task 1.2.2: Order와 Fanout 이해
# ======================================================================


def demonstrate_order_concept():
    """
    Order(M)의 의미와 실제 사용 예시

    Order = 노드당 최대 자식 수
    - Order=3 → 최대 3개 자식, 최대 2개 키
    - Order=4 → 최대 4개 자식, 최대 3개 키

    공식: MAX_KEYS = Order - 1
    """
    print("\n" + "=" * 60)
    print("Task 1.2.2: Order와 Fanout")
    print("=" * 60)

    ORDER = 4  # 최대 4개 자식
    MAX_KEYS = ORDER - 1  # 최대 3개 키

    print(f"\n[설정] Order = {ORDER}")
    print(f"   → 한 노드당 최대 {ORDER}개 자식")
    print(f"   → 한 노드당 최대 {MAX_KEYS}개 키")

    # 예시: Order=4인 Internal 노드
    print("\n[예시] Order=4 Internal 노드:")
    leaf1 = BPlusNode(is_leaf=True, keys=[1, 2], values=["a", "b"])
    leaf2 = BPlusNode(is_leaf=True, keys=[5, 6], values=["c", "d"])
    leaf3 = BPlusNode(is_leaf=True, keys=[10, 11], values=["e", "f"])
    leaf4 = BPlusNode(is_leaf=True, keys=[20, 21], values=["g", "h"])

    # Internal 노드: 4개 자식, 3개 키
    internal = BPlusNode(
        is_leaf=False,
        keys=[5, 10, 20],  # 3개 키 (Order - 1)
        children=[leaf1, leaf2, leaf3, leaf4],  # 4개 자식 (Order)
    )
    print(f"   - keys 개수: {len(internal.keys)} (최대 {MAX_KEYS})")
    print(f"   - children 개수: {len(internal.children)} (최대 {ORDER})")

    print("\n[키와 자식의 관계]")
    print("   keys=[5, 10, 20]이면:")
    print("   child[0]: key < 5")
    print("   child[1]: 5 ≤ key < 10")
    print("   child[2]: 10 ≤ key < 20")
    print("   child[3]: key ≥ 20")

    print("\n✅ 핵심: 키가 N개면 자식은 N+1개!")


# ======================================================================
# Task 1.2.3: Sibling Pointer (next) 이해
# ======================================================================


def demonstrate_sibling_pointer():
    """
    Leaf의 next 포인터가 왜 필요한지

    목적: Range Scan 효율화
    - "10 ≤ id ≤ 30" 같은 범위 쿼리를 빠르게!
    - Tree를 다시 타지 않고 옆으로 쭉 순회
    """
    print("\n" + "=" * 60)
    print("Task 1.2.3: Sibling Pointer (Range Scan)")
    print("=" * 60)

    # 3개 Leaf 생성
    leaf1 = BPlusNode(is_leaf=True, keys=[1, 3, 5], values=["a", "b", "c"])
    leaf2 = BPlusNode(is_leaf=True, keys=[7, 9, 11], values=["d", "e", "f"])
    leaf3 = BPlusNode(is_leaf=True, keys=[13, 15, 17], values=["g", "h", "i"])

    # Sibling 연결 (Linked List처럼)
    leaf1.next = leaf2
    leaf2.next = leaf3
    leaf3.next = None  # 마지막

    print("\n[Leaf Linked List 구조]")
    print("   leaf1 → leaf2 → leaf3 → None")
    print(f"     {leaf1.keys} → {leaf2.keys} → {leaf3.keys}")

    # Range Scan 시뮬레이션: 5 ≤ key ≤ 13
    print("\n[Range Scan 시뮬레이션] 5 ≤ key ≤ 13:")
    current = leaf1  # 시작 Leaf
    result = []

    while current:
        for i, key in enumerate(current.keys):
            if 5 <= key <= 13:
                result.append((key, current.values[i]))
        current = current.next  # 다음 Leaf로!

    print(f"   결과: {result}")
    print("\n✅ 핵심: Sibling 포인터로 Tree 재탐색 없이 범위 조회!")


# ======================================================================
# Task 1.2.4: 용어 퀴즈
# ======================================================================


def terminology_quiz():
    """
    용어 이해도 체크
    """
    print("\n" + "=" * 60)
    print("Task 1.2.4: 용어 퀴즈")
    print("=" * 60)

    questions = [
        {
            "q": "1. Leaf Node가 저장하는 것은?",
            "options": ["A) 자식 포인터", "B) 실제 데이터 (values)", "C) 둘 다"],
            "answer": "B",
        },
        {
            "q": "2. Internal Node가 저장하는 것은?",
            "options": ["A) 자식 포인터", "B) 실제 데이터", "C) 아무것도 없음"],
            "answer": "A",
        },
        {
            "q": "3. Order=5인 노드의 최대 키 개수는?",
            "options": ["A) 4개", "B) 5개", "C) 6개"],
            "answer": "A",
        },
        {
            "q": "4. keys=[10, 20]인 노드의 자식 개수는?",
            "options": ["A) 2개", "B) 3개", "C) 4개"],
            "answer": "B",
        },
        {
            "q": "5. Sibling Pointer(next)를 사용하는 이유는?",
            "options": ["A) 메모리 절약", "B) Range Scan 효율화", "C) 트리 균형"],
            "answer": "B",
        },
    ]

    for i, item in enumerate(questions, 1):
        print(f"\n{item['q']}")
        for opt in item["options"]:
            print(f"   {opt}")

    print("\n" + "=" * 60)
    print("정답: B, A, A, B, B")
    print("=" * 60)


# ======================================================================
# 메인 실행
# ======================================================================

if __name__ == "__main__":
    demonstrate_node_types()
    demonstrate_order_concept()
    demonstrate_sibling_pointer()
    terminology_quiz()

    print("\n" + "=" * 60)
    print("🎉 Level 1.2 완료!")
    print("=" * 60)
    print("\n다음 단계: Level 2.1 - 정적 트리 수동 구축")
    print("이제 실제로 완성된 B+Tree를 손으로 만들어봅니다!")
