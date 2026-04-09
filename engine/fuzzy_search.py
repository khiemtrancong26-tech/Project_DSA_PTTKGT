# engine/fuzzy_search.py
"""
Tìm kiếm theo tên mơ hồ — Scenario 3.

Hash Table chỉ match chính xác theo key (student_id).
Tên thì không unique, không chính xác.
→ Giải pháp duy nhất khả thi: fuzzy linear search O(n).

Điểm kỹ thuật cốt lõi:
    normalize() — bỏ dấu tiếng Việt trước khi so sánh.
    "Văn An" và "van an" phải match nhau — không thì miss toàn bộ.
"""

import unicodedata


# ══════════════════════════════════════════════════════════════════
#  Normalize — xử lý dấu tiếng Việt
# ══════════════════════════════════════════════════════════════════

def normalize(text: str) -> str:
    """
    Lowercase + bỏ dấu tiếng Việt để so sánh không phân biệt dấu.

    Cơ chế:
        NFKD decomposition tách ký tự có dấu thành 2 phần:
            ký tự gốc  +  combining diacritic (dấu)
        Sau đó lọc bỏ toàn bộ combining character → chỉ giữ ký tự gốc.
    """
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ══════════════════════════════════════════════════════════════════
#  Fuzzy linear search
# ══════════════════════════════════════════════════════════════════

def fuzzy_linear_search(records: list, query: str) -> list:
    """
    Tìm tất cả sinh viên có query xuất hiện trong name (substring match).
    Không phân biệt dấu, không phân biệt hoa thường.

    Complexity : O(n × m) — n records, m độ dài query.
    Trong thực tế m rất nhỏ (≤ 20 ký tự) → coi gần như O(n).

    Returns:
        list[dict] các record có name chứa query (sau normalize).
        list rỗng nếu không tìm thấy.
    """
    q = normalize(query)
    return [r for r in records if q in normalize(r["name"])]