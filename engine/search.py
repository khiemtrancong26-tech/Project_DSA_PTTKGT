# engine/search.py
"""
Linear Search và Binary Search — thuần thuật toán.

Nguyên tắc thiết kế:
- Mỗi hàm CHỈ làm 1 việc: tìm kiếm / sắp xếp.
- Không đo thời gian ở đây — đó là việc của benchmark.py.
- Trả về kết quả thuần, không trả tuple (result, elapsed).
"""


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 1 — Tra cứu 1 sinh viên theo MSSV
# ══════════════════════════════════════════════════════════════════

def linear_search(records: list, target_id: str):
    """
    Duyệt tuần tự, so sánh từng student_id.

    Complexity : O(n)
    Không cần chuẩn bị trước (unsorted list OK).

    Returns:
        dict sinh viên nếu tìm thấy, None nếu không có.
    """
    for record in records:
        if record["student_id"] == target_id:
            return record
    return None


def binary_search(sorted_records: list, target_id: str):
    """
    Tìm kiếm nhị phân trên danh sách ĐÃ SORT theo student_id.

    Complexity : O(log n) — chỉ tính bước tìm kiếm, KHÔNG bao gồm sort.
    Caller phải đảm bảo sorted_records đã được sort theo student_id.

    Returns:
        dict sinh viên nếu tìm thấy, None nếu không có.
    """
    lo, hi = 0, len(sorted_records) - 1

    while lo <= hi:
        mid = (lo + hi) // 2
        mid_id = sorted_records[mid]["student_id"]

        if mid_id == target_id:
            return sorted_records[mid]
        elif mid_id < target_id:
            lo = mid + 1
        else:
            hi = mid - 1

    return None


# ══════════════════════════════════════════════════════════════════
#  Sort helpers — dùng cho Binary Search / Binary Filter
# ══════════════════════════════════════════════════════════════════

def sort_by_id(records: list) -> list:
    """
    Sắp xếp theo student_id — bước bắt buộc trước Binary Search (Scenario 1).

    Complexity : O(n log n) — Python dùng Timsort.
    Trả list MỚI, không sort in-place — giữ nguyên records gốc.
    """
    return sorted(records, key=lambda r: r["student_id"])


def sort_by_gpa(records: list) -> list:
    """
    Sắp xếp theo GPA tăng dần — bước chuẩn bị cho Binary Filter (Scenario 2).

    Complexity : O(n log n).
    Trả list MỚI, không sort in-place.
    """
    return sorted(records, key=lambda r: r["gpa"])