# engine/collision/open_addressing_multi.py

from engine.hash_table import HashTable


class OpenAddressingMultiHashTable(HashTable):
    """
    Open Addressing Hash Table cho bài toán 1 key → nhiều value.

    Dùng cho Scenario 2A — key là department_code,
    value là list tất cả record thuộc khoa đó.

    Complexity:
        insert : O(1) avg
        search : O(1) avg — trả về list toàn bộ record của key đó
    """

    def __init__(self, size: int = 1009):
        super().__init__(size)
        self.table = [None] * self.size

    def insert(self, key: str, value: dict):
        
        idx   = self._hash(key)

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                self.table[idx] = (key, [value])
                self.count += 1
                return

            if slot[0] == key:
                # Key đã tồn tại → append vào list, không ghi đè
                slot[1].append(value)
                return

            idx = (idx + 1) % self.size   # linear probe

        raise OverflowError("Hash table đầy — không thể insert thêm.")
    def search(self, key: str):
        idx   = self._hash(key)

        for _ in range(self.size):
            slot = self.table[idx]

            if slot is None:
                return []   # chắc chắn không có — dừng probe

            if slot[0] == key:
                return slot[1]  # trả về list các record
            
            idx = (idx + 1) % self.size

        return []  # không tìm thấy → list rỗng