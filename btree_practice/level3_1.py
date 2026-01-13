"""
Level 3.1: Insert (Split 없음)

목표:
1. Leaf에 여유 공간이 있을 때만 삽입
2. 정렬된 위치에 삽입하기
3. Split은 나중에 (일단 에러 던지기)

핵심 개념:
- "간단한 것부터" - Split 없이 Insert만 먼저
- "정렬 유지" - bisect로 올바른 위치 찾기
- "제약 확인" - Order 위반 감지
"""

from dataclasses import dataclass, field
from typing import List, Optional
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
# 이전 레벨에서 가져온 함수들
# ======================================================================


def find_leaf(root: BPlusNode, key: int) -> BPlusNode:
    """주어진 키가 속한 Leaf 찾기"""
    node = root
    while not node.is_leaf:
        index = bisect.bisect_right(node.keys, key)
        node = node.children[index]
    return node


def search(root: BPlusNode, key: int) -> Optional[str]:
    """키로 값 검색"""
    leaf = find_leaf(root, key)
    if key in leaf.keys:
        index = leaf.keys.index(key)
        return leaf.values[index]
    else:
        return None


# ======================================================================
# Task 3.1.1: insert_into_leaf() - Leaf에 삽입 (Split 없음)
# ======================================================================


def insert_into_leaf(leaf: BPlusNode, key: int, value: str, max_keys: int) -> None:
    """
    Leaf 노드에 (key, value) 삽입

    Args:
        leaf: 삽입할 Leaf 노드
        key: 삽입할 키
        value: 삽입할 값
        max_keys: 노드당 최대 키 개수 (Order - 1)

    동작:
        1. Leaf가 꽉 찼는지 확인 (len(leaf.keys) >= max_keys)
        2. 꽉 찼으면 에러 (Split은 나중에!)
        3. 여유 있으면 정렬된 위치에 삽입

    예시:
        leaf.keys = [1, 5, 9]
        insert_into_leaf(leaf, 7, "Seven", max_keys=4)
        → leaf.keys = [1, 5, 7, 9]
        → leaf.values = [..., "Seven", ...]

    TODO: 아래 코드를 완성하세요!
    """
    # Step 1: 꽉 찼는지 확인
    if len(leaf.keys) == max_keys:
        raise RuntimeError("Leaf node is full")

    insert_index = bisect.bisect_right(leaf.keys, key)

    leaf.keys.insert(insert_index, key)
    leaf.values.insert(insert_index, value)

    return None


# ======================================================================
# Task 3.1.2: insert() - 전체 Insert 로직 (Split 없음)
# ======================================================================


def insert(root: BPlusNode, key: int, value: str, max_keys: int) -> None:
    """
    B+Tree에 (key, value) 삽입

    Args:
        root: 트리의 Root
        key: 삽입할 키
        value: 삽입할 값
        max_keys: 노드당 최대 키 개수

    동작:
        1. find_leaf()로 삽입할 Leaf 찾기
        2. insert_into_leaf()로 삽입

    주의:
        - Split은 아직 구현 안 함
        - Leaf가 꽉 차면 에러 발생

    TODO: 아래 코드를 완성하세요!
    """
    leaf = find_leaf(root, key)

    insert_into_leaf(leaf, key=key, value=value, max_keys=max_keys)

    return None


# ======================================================================
# 테스트
# ======================================================================


def build_sample_tree():
    """Order=4 샘플 트리 (여유 공간 있음)"""
    leaf1 = BPlusNode(is_leaf=True, keys=[1, 3], values=["Alice", "Charlie"])
    leaf2 = BPlusNode(is_leaf=True, keys=[5, 7], values=["Eve", "Grace"])
    leaf3 = BPlusNode(is_leaf=True, keys=[10, 12], values=["Jack", "Leo"])

    leaf1.next = leaf2
    leaf2.next = leaf3

    root = BPlusNode(is_leaf=False, keys=[5, 10], children=[leaf1, leaf2, leaf3])
    return root


if __name__ == "__main__":
    print("\n📝 B+Tree Insert 실습 (Split 없음)\n")

    MAX_KEYS = 3  # Order=4

    # 샘플 트리 생성
    root = build_sample_tree()
    print("[초기 트리]")
    print_tree(root)

    # Task 3.1.1 & 3.1.2 테스트
    print("\n" + "=" * 60)
    print("Task 3.1.1 & 3.1.2: Insert 테스트")
    print("=" * 60)

    test_inserts = [
        (2, "Bob"),  # leaf1에 삽입 [1,2,3]
        (6, "Frank"),  # leaf2에 삽입 [5,6,7]
        (11, "Kate"),  # leaf3에 삽입 [10,11,12]
    ]

    print("\n[삽입 테스트]")
    for key, value in test_inserts:
        try:
            print(f"\nInsert ({key}, {value})...")
            insert(root, key, value, MAX_KEYS)
            print_tree(root)

            # 검증: 삽입된 값 찾기
            result = search(root, key)
            if result == value:
                print(f"✅ search({key}) = {result}")
            else:
                print(f"❌ search({key}) = {result} (예상: {value})")
        except Exception as e:
            print(f"⚠️  Insert 실패 또는 미구현: {e}")
            break

    # Overflow 테스트
    print("\n" + "=" * 60)
    print("Overflow 테스트 (에러 예상)")
    print("=" * 60)

    try:
        print("\nInsert (4, 'David')...")
        insert(root, 4, "David", MAX_KEYS)
        print("❌ 에러가 발생해야 하는데 성공함!")
    except Exception as e:
        print(f"✅ 예상대로 에러 발생: {e}")

    print("\n" + "=" * 60)
    print("완료 후 다음 단계: Level 3.2 - Leaf Split")
    print("=" * 60)
