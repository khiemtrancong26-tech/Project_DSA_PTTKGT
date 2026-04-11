# engine/collision/chaining.py

from engine.hash_table import HashTable


class ChainingHashTable(HashTable):
    """
    Hash Table giải quyết collision bằng Separate Chaining.

    Mỗi bucket là 1 list các (key, value) pair.
    Khi collision xảy ra → append vào list, không đụng bucket khác.

    Complexity:
        insert : O(1) avg — append vào đầu list
        search : O(1) avg / O(n) worst — duyệt list trong bucket
    """

    def __init__(self, size: int = 1009):
        super().__init__(size)
        # Mỗi slot là 1 list — khởi tạo list rỗng cho toàn bộ bảng
        self.table = [[] for _ in range(self.size)]

    # ---- insert ----

    def insert(self, key: str, value: dict):
        """
        Thêm (key, value) vào bảng.
        Nếu key đã tồn tại → cập nhật value (upsert), không tạo duplicate.
        """
        idx = self._hash(key)
        chain = self.table[idx]

        # Kiểm tra key đã có trong chain chưa → update nếu có
        for i, (k, v) in enumerate(chain):
            if k == key:
                chain[i] = (key, value)   # update in-place
                return

        # Key chưa có → append vào cuối chain
        chain.append((key, value))
        self.count += 1

    # ---- search ----

    def search(self, key: str):
        """
        Tìm kiếm theo key.
        Trả về value nếu tìm thấy, None nếu không có.
        """
        idx = self._hash(key)
        chain = self.table[idx]

        for k, v in chain:
            if k == key:
                return v

        return None   # không tìm thấy


