"""
Level 3.3: Internal Split

목표:
1. Internal 노드가 꽉 찼을 때 2개로 분할
2. Leaf Split과의 차이 이해
3. 재귀적 Split 처리

핵심 차이:
- Leaf: promote_key를 **복사** (오른쪽에도 남음)
- Internal: promote_key를 **이동** (제거됨!)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import bisect


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
# Task 3.3.1: split_internal() - Internal 노드 분할
# ======================================================================


def split_internal(internal: BPlusNode) -> Tuple[int, BPlusNode]:
    """
    꽉 찬 Internal 노드를 2개로 분할

    Args:
        internal: 꽉 찬 Internal 노드

    Returns:
        (promote_key, new_internal):
            - promote_key: 부모에 올릴 키
            - new_internal: 새로 만든 오른쪽 Internal

    핵심 차이 (Leaf와 비교):
        Leaf Split:
            Before: [1, 3, 5, 7, 9]
            After:  [1, 3] | [5, 7, 9]
            Promote: 5 (오른쪽에도 남아있음!)

        Internal Split:
            Before: keys=[1, 3, 5, 7, 9]
            After:  keys=[1, 3] | [7, 9]  (5가 사라짐!)
            Promote: 5 (중간 키를 빼서 올림)

    예시:
        Before:
            internal.keys = [10, 20, 30, 40, 50]
            internal.children = [A, B, C, D, E, F]

        After:
            mid = 5 // 2 = 2
            promote_key = 30  ← 중간 키

            internal.keys = [10, 20]  ([:mid])
            internal.children = [A, B, C]  ([:mid+1])

            new_internal.keys = [40, 50]  ([mid+1:])
            new_internal.children = [D, E, F]  ([mid+1:])

    TODO: 아래 코드를 완성하세요!
    """
    mid = len(internal.keys) // 2

    # ⭐ 핵심: 중간 키를 빼서 올림
    promote_key = internal.keys[mid]

    # 오른쪽 새 Internal 생성
    # TODO: mid+1부터 끝까지 (중간 키 제외!)
    new_internal = BPlusNode(
        is_leaf=False,
        keys=internal.keys[mid + 1 :],
        children=internal.children[mid + 1 :],
    )

    # 왼쪽 축소 (대입 필수!)
    internal.keys = internal.keys[:mid]
    internal.children = internal.children[: mid + 1]

    return promote_key, new_internal


# ======================================================================
# 이전 레벨 함수들 (수정 버전)
# ======================================================================


def split_leaf(leaf: BPlusNode) -> Tuple[int, BPlusNode]:
    """Leaf 분할 (Level 3.2)"""
    mid = len(leaf.keys) // 2

    promote_key = leaf.keys[mid]  # 복사!

    new_leaf = BPlusNode(
        is_leaf=True,
        keys=leaf.keys[mid:],  # 중간 키 포함!
        values=leaf.values[mid:],
    )

    leaf.keys = leaf.keys[:mid]
    leaf.values = leaf.values[:mid]

    new_leaf.next = leaf.next
    leaf.next = new_leaf

    return promote_key, new_leaf


def insert_into_parent(
    parent: BPlusNode, promote_key: int, new_child: BPlusNode
) -> None:
    """Parent에 키 삽입 (Level 3.2)"""
    index = bisect.bisect_right(parent.keys, promote_key)
    parent.keys.insert(index, promote_key)
    parent.children.insert(index + 1, new_child)


# ======================================================================
# Task 3.3.2: insert_recursive() - 재귀적 Insert (Split 전파)
# ======================================================================


def insert_full(root: BPlusNode, key: int, value: str, max_keys: int) -> BPlusNode:
    """완전한 Insert (Root Split 포함)"""
    split_result = insert_recursive(root, key, value, max_keys)

    if split_result:
        # Root가 Split됨 → 새 Root 생성
        promote_key, new_node = split_result
        new_root = BPlusNode(
            is_leaf=False, keys=[promote_key], children=[root, new_node]
        )
        return new_root

    return root


def insert_recursive(
    node: BPlusNode, key: int, value: str, max_keys: int
) -> Optional[Tuple[int, BPlusNode]]:
    """
    재귀적 Insert (Split을 위로 전파)

    Returns:
        None: Split 불필요
        (promote_key, new_node): Split 발생 → 부모가 처리해야 함

    동작:
        1. Leaf면: 삽입 후 넘치면 split_leaf()
        2. Internal이면:
            a. 적절한 child 선택
            b. child에 재귀 호출
            c. child가 Split했으면 자신한테 promote_key 삽입
            d. 자신도 넘치면 split_internal()

    TODO: 아래 코드를 완성하세요!
    """
    if node.is_leaf:
        # Base case: Leaf에 삽입
        index = bisect.bisect_left(node.keys, key)
        node.keys.insert(index, key)
        node.values.insert(index, value)

        # 넘쳤나?
        if len(node.keys) > max_keys:
            return split_leaf(node)
        else:
            return None  # Split 불필요

    else:
        # Recursive case: 적절한 child 찾기
        # TODO: child 선택
        child_index = bisect.bisect_right(node.keys, key)  # bisect 사용
        child = node.children[child_index]

        # 재귀 호출
        split_result = insert_recursive(child, key, value, max_keys)

        if split_result:
            promote_key, new_child = split_result

            # 자신한테 promote_key 삽입
            insert_into_parent(node, promote_key, new_child)

            # 자신도 넘쳤나?
            if len(node.keys) > max_keys:
                return split_internal(node)

        return None


# ======================================================================
# 이전 Search 함수
# ======================================================================


def find_leaf(root: BPlusNode, key: int) -> BPlusNode:
    """Leaf 찾기"""
    node = root
    while not node.is_leaf:
        index = bisect.bisect_right(node.keys, key)
        node = node.children[index]
    return node


def search(root: BPlusNode, key: int) -> Optional[str]:
    """검색"""
    leaf = find_leaf(root, key)
    if key in leaf.keys:
        index = leaf.keys.index(key)
        return leaf.values[index]
    else:
        return None


# ======================================================================
# 테스트
# ======================================================================

if __name__ == "__main__":
    print("\n🚀 B+Tree Internal Split 실습\n")

    MAX_KEYS = 2  # Order=3

    # 초기 트리
    root = BPlusNode(is_leaf=True, keys=[], values=[])

    # 많은 데이터 삽입 (Internal Split 유발)
    test_data = [
        (10, "Ten"),
        (20, "Twenty"),
        (5, "Five"),
        (6, "Six"),
        (12, "Twelve"),
        (30, "Thirty"),
        (7, "Seven"),
        (17, "Seventeen"),
    ]

    print("=" * 60)
    print("Insert 테스트 (Internal Split 포함)")
    print("=" * 60)

    for key, value in test_data:
        print(f"\nInsert ({key}, {value})...")
        try:
            root = insert_full(root, key, value, MAX_KEYS)
            print_tree(root)
        except Exception as e:
            print(f"⚠️  에러 또는 미구현: {e}")
            import traceback

            traceback.print_exc()
            break

    # 검증
    print("\n" + "=" * 60)
    print("검색 검증")
    print("=" * 60)

    all_keys = sorted([k for k, _ in test_data])
    print(f"\n삽입된 키: {all_keys}")

    success = 0
    for key, expected in test_data:
        result = search(root, key)
        if result == expected:
            success += 1
            print(f"✅ search({key:2d}) = {result}")
        else:
            print(f"❌ search({key:2d}) = {result} (예상: {expected})")

    print(f"\n{success}/{len(test_data)} 성공")

    print("\n" + "=" * 60)
    print("🎉 Level 3 완료! 다음: Level 4 - 완전한 재귀 Insert")
    print("=" * 60)
