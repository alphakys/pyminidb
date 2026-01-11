"""
Level 2.2: B+Tree Search 알고리즘

목표:
1. Binary Search를 사용해 Root → Leaf 탐색
2. 특정 키의 값 찾기
3. Top-Down 방식 이해 (위 → 아래)

핵심 개념:
- Internal 노드: "이정표" (어느 자식으로 갈지 결정)
- Leaf 노드: "실제 데이터" (값 반환)
- bisect 모듈: Python의 Binary Search 도구
"""

from dataclasses import dataclass, field
from typing import List, Optional
import bisect  # Python의 Binary Search 모듈


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
# 테스트용 트리 생성
# ======================================================================


def build_sample_tree():
    """
    Order=4 샘플 트리

    구조:
            [4, 7, 10]
           /   |   |   \
        [1,2,3] [4,5,6] [7,8,9] [10,11,12]
    """
    leaf1 = BPlusNode(is_leaf=True, keys=[1, 2, 3], values=["Alice", "Bob", "Charlie"])
    leaf2 = BPlusNode(is_leaf=True, keys=[4, 5, 6], values=["David", "Eve", "Frank"])
    leaf3 = BPlusNode(is_leaf=True, keys=[7, 8, 9], values=["Grace", "Henry", "Iris"])
    leaf4 = BPlusNode(is_leaf=True, keys=[10, 11, 12], values=["Jack", "Kate", "Leo"])

    leaf1.next = leaf2
    leaf2.next = leaf3
    leaf3.next = leaf4

    root = BPlusNode(
        is_leaf=False, keys=[4, 7, 10], children=[leaf1, leaf2, leaf3, leaf4]
    )
    return root


# ======================================================================
# Task 2.2.1: find_leaf() - Leaf 노드 찾기
# ======================================================================


def find_leaf(root: BPlusNode, key: int) -> BPlusNode:
    """
    주어진 키가 속한 Leaf 노드를 찾기

    Args:
        root: 트리의 Root 노드
        key: 찾을 키

    Returns:
        key가 속한 (또는 속해야 할) Leaf 노드

    알고리즘:
        1. node = root에서 시작
        2. while node가 Leaf가 아닐 때:
            a. node.keys에서 적절한 child index 찾기 (Binary Search)
            b. node = node.children[index]
        3. Leaf에 도달하면 반환

    구조:
        [4, 7, 10]
        /   |   |   \
    [1,2,3] [4,5,6] [7,8,9] [10,11,12]


    예시:
        root.keys = [4, 7, 10]

        find_leaf(root, 5):
            - 5는 4 ≤ 5 < 7 구간
            - child[1]로 이동
            - Leaf [4,5,6] 반환

    TODO: 아래 코드를 완성하세요!
    """
    node = root

    # While loop로 Leaf까지 내려가기
    while not node.is_leaf:
        # 힌트: bisect.bisect_right(node.keys, key)를 사용
        # bisect_right는 "key를 삽입할 위치"를 반환
        # 예: keys=[4, 7, 10], key=5 → index=1

        # bisect_right 함수는 keys list에서 order를 구해주는 역할을 한다.
        # index에 해당하는 children으로 pointer 이동 후 동일한 로직의 연산을 반복한다.
        index = bisect.bisect_right(node.keys, key)
        # TODO: 다음 노드로 이동
        node = node.children[index]

    return node


# ======================================================================
# Task 2.2.2: search() - 값 찾기
# ======================================================================


def search(root: BPlusNode, key: int) -> Optional[str]:
    """
    B+Tree에서 키로 값 검색

    Args:
        root: 트리의 Root
        key: 찾을 키

    Returns:
        키에 해당하는 값 (없으면 None)

    알고리즘:
        1. find_leaf()로 Leaf 찾기
        2. Leaf.keys에서 key가 있는지 확인
        3. 있으면 해당 values 반환, 없으면 None

    TODO: 아래 코드를 완성하세요!
    """
    # Step 1: Leaf 찾기
    leaf = find_leaf(root, key)

    # Step 2: Leaf에서 키 찾기
    if key in leaf.keys:
        index = leaf.keys.index(key)
        return leaf.values[index]
    else:
        return None


# ======================================================================
# Task 2.2.3: bisect 모듈 이해하기
# ======================================================================


def understand_bisect():
    """
    bisect 모듈의 동작 이해

    bisect_left vs bisect_right:
    - bisect_left: 같은 값이 있으면 왼쪽 위치
    - bisect_right: 같은 값이 있으면 오른쪽 위치

    B+Tree에서는 주로 bisect_right 사용!
    """
    print("=" * 60)
    print("Task 2.2.3: bisect 모듈 이해")
    print("=" * 60)

    keys = [4, 7, 10]

    print(f"\nkeys = {keys}")
    print("\n[bisect_right - B+Tree에서 사용]")

    test_keys = [1, 4, 5, 7, 9, 10, 15]
    for k in test_keys:
        idx = bisect.bisect_right(keys, k)
        print(f"  key={k:2d} → index={idx} (child[{idx}]로 이동)")

    print("\n[해석]")
    print("  keys=[4, 7, 10]이면 4개 구간:")
    print("    child[0]: key < 4")
    print("    child[1]: 4 ≤ key < 7")
    print("    child[2]: 7 ≤ key < 10")
    print("    child[3]: key ≥ 10")


# ======================================================================
# 테스트 실행
# ======================================================================

if __name__ == "__main__":
    print("\n🔍 B+Tree Search 알고리즘 실습\n")

    # 샘플 트리 생성
    root = build_sample_tree()
    print("[샘플 트리 구조]")
    print_tree(root)

    # Task 2.2.3: bisect 이해
    understand_bisect()

    # Task 2.2.1 & 2.2.2 테스트
    print("\n" + "=" * 60)
    print("Task 2.2.1 & 2.2.2: Search 테스트")
    print("=" * 60)

    test_cases = [
        (1, "Alice"),  # 첫 번째
        (5, "Eve"),  # 중간
        (12, "Leo"),  # 마지막
        (7, "Grace"),  # 경계값
        (13, None),  # 없는 키
        (0, None),  # 범위 밖
    ]

    print("\n[검색 테스트]")
    for key, expected in test_cases:
        try:
            result = search(root, key)
            status = "✅" if result == expected else "❌"
            # None을 문자열로 변환하여 포맷 에러 방지
            result_str = str(result) if result is not None else "None"
            expected_str = str(expected) if expected is not None else "None"
            print(
                f"{status} search({key:2d}) = {result_str:10s} (예상: {expected_str:10s})"
            )
        except (AttributeError, TypeError) as e:
            print(f"⚠️  search({key:2d}) - 아직 구현되지 않았습니다")
            break

    print("\n" + "=" * 60)
    print("완료 후 다음 단계: Level 3.1 - Insert (Split 없음)")
    print("=" * 60)
