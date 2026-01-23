"""
Level 5.1: B+Tree Range Scan (Memory Model)

목표: Disk I/O 없이 메모리 객체로 Range Scan 로직을 먼저 마스터하기.
이 로직 그대로 Pager와 Page로 옮기면 됩니다.
"""

from dataclasses import dataclass
from typing import List, Optional, Iterator
import bisect


@dataclass
class Node:
    is_leaf: bool
    keys: List[int]
    children: Optional[List["Node"]] = None  # Internal: PIDs 대신 Node 참조
    values: Optional[List[str]] = None  # Leaf: 실제 데이터
    next: Optional["Node"] = None  # Leaf: Sibling Pointer

    def __repr__(self):
        return f"Leaf({self.keys})" if self.is_leaf else f"Internal({self.keys})"


def find_leaf(node: Node, key: int) -> Node:
    """
    Start Key가 위치할 Leaf 노드를 탐색
    (이미 구현하셨던 로직의 메모리 버전입니다)
    """
    if node.is_leaf:
        return node

    # Internal Node: 적절한 child 찾아 내려가기
    idx = bisect.bisect_right(node.keys, key)
    return find_leaf(node.children[idx], key)


def range_scan(root: Node, start: int, end: int) -> Iterator[str]:
    current_node = find_leaf(root, start)
    start_idx = bisect.bisect_left(current_node.keys, start)

    while current_node:
        # start_idx부터 끝까지 슬라이싱 (첫 노드는 중간부터, 나머지는 0부터)
        for k, v in zip(current_node.keys[start_idx:], current_node.values[start_idx:]):
            if k > end:
                return
            yield v

        start_idx = 0  # 다음 노드부터는 처음부터!
        current_node = current_node.next


# --- 테스트 셋업 (수정 불필요) ---
def setup_tree():
    """
           [ 30, 50 ]
          /    |     \
    [10, 20] [30, 40] [50, 60]
    """
    leaf1 = Node(True, [10, 20], values=["v10", "v20"])
    leaf2 = Node(True, [30, 40], values=["v30", "v40"])
    leaf3 = Node(True, [50, 60], values=["v50", "v60"])

    # Sibling 연결
    leaf1.next = leaf2
    leaf2.next = leaf3

    # Root
    root = Node(False, [30, 50], children=[leaf1, leaf2, leaf3])
    return root


if __name__ == "__main__":
    root = setup_tree()

    print("Test 1: Scan 15 ~ 55 (Expected: v20, v30, v40, v50)")
    results = list(range_scan(root, 15, 55))
    print(f"Result: {results}")

    print("\nTest 2: Scan 5 ~ 9 (Expected: [])")
    results = list(range_scan(root, 5, 9))
    print(f"Result: {results}")

    print("\nTest 3: Scan 55 ~ 90 (Expected: v60)")
    results = list(range_scan(root, 55, 90))
    print(f"Result: {results}")

    print("leaf1 : ", root.children[0].keys)
    print("leaf1 : ", root.children[1].keys)
    print("leaf1 : ", root.children[2].keys)
