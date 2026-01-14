"""
Step 4.1.2: B+Tree Node 직렬화 계층

목표:
- Internal Page: keys + child PIDs 직렬화/역직렬화
- Leaf Page: 기존 Row 방식 유지
"""

from typing import List, Tuple, Iterable
import struct


class BTreeNode:
    """
    Internal Page 직렬화 헬퍼

    Constants:
        KEY_COUNT_SIZE (int): 2 bytes (unsigned short)
        INT_SIZE (int): 4 bytes (unsigned int)

    Internal Page 구조:
    ┌────────────┬─────────┬─────────┬─────────┬──────────────┐
    │ key_count  │  key1   │  key2   │  key3   │  pids[0..3]  │
    │   (2B)     │  (4B)   │  (4B)   │  (4B)   │  (4B each)   │
    └────────────┴─────────┴─────────┴─────────┴──────────────┘

    예시:
        keys = [10, 20, 30]
        pids = [1, 2, 3, 4]  # N keys → N+1 children

        직렬화 →
        [0x03, 0x00] [0x0A, 0x00, 0x00, 0x00] [0x14, ...] [0x1E, ...]
        [0x01, 0x00, 0x00, 0x00] [0x02, ...] [0x03, ...] [0x04, ...]
        [0x01, 0x00, 0x00, 0x00] [0x02, ...] [0x03, ...] [0x04, ...]
    """

    KEY_COUNT_SIZE = 2
    INT_SIZE = 4

    @staticmethod
    def serialize_internal(keys: List[int], child_pids: List[int]) -> bytes:
        """
        Internal 노드 → 바이트

        Args:
            keys: 정렬된 키 리스트 (예: [10, 20, 30])
            child_pids: 자식 Page ID (예: [1, 2, 3, 4])

        Returns:
            직렬화된 바이트
        """
        # [작성 가이드]
        # 1. key_count 계산 (len(keys))
        # 2. key_count를 2바이트(<H)로 변환
        # 3. keys를 돌면서 각각 4바이트(<I)로 변환해서 붙이기
        # 4. child_pids를 돌면서 각각 4바이트(<I)로 변환해서 붙이기

        assert isinstance(keys, Iterable) and isinstance(child_pids, Iterable), (
            "keys object는 반드시 iterable이어야 합니다."
        )

        key_count = len(keys)
        # 한번에 메모리 확보를 위해 bytearray 사용 (선택사항이나, += 보다 extend가 효율적)
        buffer = bytearray()

        # 1. Key Count (2 bytes)
        buffer.extend(struct.pack("<H", key_count))

        # 2. Keys (Batch Packing!)
        # keys 리스트를 쫙 펼쳐서 한방에 팩킹
        buffer.extend(struct.pack(f"<{key_count}I", *keys))

        # 3. Child PIDs (Batch Packing!)
        # pids 리스트(count+1개)를 쫙 펼쳐서 한방에 팩킹
        buffer.extend(struct.pack(f"<{len(child_pids)}I", *child_pids))

        return bytes(buffer)

    @staticmethod
    def deserialize_internal(data: bytes) -> Tuple[List[int], List[int]]:
        """
        바이트 → Internal 노드

        Args:
            data: 직렬화된 바이트

        Returns:
            (keys, child_pids)
        """
        # [작성 가이드]
        # 1. 처음 2바이트를 읽어서 key_count 파악 (<H)
        # 2. key_count만큼 루프 돌면서 4바이트씩 읽어 keys 리스트 복원 (<I)
        # 3. key_count + 1만큼 루프 돌면서 4바이트씩 읽어 child_pids 리스트 복원 (<I)

        # TODO: 직접 구현해보세요!
        key_count = struct.unpack("<H", data[: BTreeNode.KEY_COUNT_SIZE])[0]
        offset = BTreeNode.KEY_COUNT_SIZE

        # Keys slicing
        keys_end = offset + (key_count * BTreeNode.INT_SIZE)
        keys = struct.unpack(f"<{key_count}I", data[offset:keys_end])

        # Child PIDs slicing
        pids_start = keys_end
        pids_end = pids_start + ((key_count + 1) * BTreeNode.INT_SIZE)
        child_pids = struct.unpack(f"<{key_count + 1}I", data[pids_start:pids_end])

        return list(keys), list(child_pids)


# ======================================================================
# 테스트 코드 (구현 후 실행하세요!)
# ======================================================================

if __name__ == "__main__":
    print("\n🧪 Step 4.1.2 테스트\n")

    # Test 1: 직렬화/역직렬화
    print("=" * 60)
    print("Test 1: serialize/deserialize 왕복")
    print("=" * 60)

    keys = [10, 20, 30]
    pids = [1, 2, 3, 4]  # N keys → N+1 children

    print(f"Original keys: {keys}")
    print(f"Original pids: {pids}")

    # 직렬화
    try:
        data = BTreeNode.serialize_internal(keys, pids)
        if data is None:
            print("\n❌ 미구현: serialize_internal이 None을 반환했습니다.")
        else:
            print(f"\n직렬화 결과: {len(data)} bytes")
            print(f"  Hex: {data.hex()}")

            # 역직렬화
            restored_keys, restored_pids = BTreeNode.deserialize_internal(data)
            print(f"\n복원된 keys: {restored_keys}")
            print(f"복원된 pids: {restored_pids}")

            # 검증
            assert keys == restored_keys, f"Keys 불일치: {keys} != {restored_keys}"
            assert pids == restored_pids, f"PIDs 불일치: {pids} != {restored_pids}"
            print("\n✅ Test 1 통과!")
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")

    # Test 2: Edge Case - 키 1개
    print("\n" + "=" * 60)
    print("Test 2: Edge Case (키 1개)")
    print("=" * 60)

    keys2 = [50]
    pids2 = [10, 20]  # 1 key → 2 children

    try:
        data2 = BTreeNode.serialize_internal(keys2, pids2)
        if data2:
            r_keys2, r_pids2 = BTreeNode.deserialize_internal(data2)
            assert keys2 == r_keys2
            assert pids2 == r_pids2
            print(f"Keys: {keys2} → {r_keys2} ✅")
            print(f"PIDs: {pids2} → {r_pids2} ✅")
    except Exception:
        pass  # Test 1에서 이미 에러 출력됨

    print("\n" + "=" * 60)
    print("🎉 테스트 종료")
    print("=" * 60)
