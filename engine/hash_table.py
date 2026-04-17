# engine/hash_table.py

class HashTable:
    """
    Base class — định nghĩa interface chung cho mọi loại hash table.
    Chaining và Open Addressing đều kế thừa từ class này.
    """

    def __init__(self, size: int = 1009):
        self.size  = size                  # kích thước bảng — dùng số nguyên tố
        self.table = [None] * self.size    # mảng các bucket
        self.count = 0                     # số phần tử hiện có

    # ---- Hash function ----

    def _hash(self, key: str) -> int:
        """
        Chuyển student_id (CCCD string) → chỉ số bucket.
        Dùng Polynomial Rolling Hash — đọc toàn bộ ký tự,
        không bỏ sót prefix → tránh clustered collision.
        """
    def _hash(self, key: str) -> int:
        h = 0
        for char in key:
            #h = (h + ord(char)) % self.size          # weak hash
            h = (h * 31 + ord(char)) % self.size     # strong hash
        return h

    # ---- Interface bắt buộc — subclass PHẢI override ----

    def insert(self, key: str, value: dict):
        raise NotImplementedError

    def search(self, key: str):
        raise NotImplementedError

