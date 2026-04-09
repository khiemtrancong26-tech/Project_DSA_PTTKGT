# engine/benchmark.py
"""
Đo thời gian thực thi của tất cả algorithm cho 3 Scenario.

Nguyên tắc đo:
    - Dùng time.perf_counter() — độ phân giải nano-second, đủ cho O(1) lookup.
    - Lặp REPEAT lần, lấy trung bình — loại bỏ nhiễu OS scheduler.
    - _avg_ms trả về CẢ kết quả lần chạy cuối → không phải gọi hàm thêm 1 lần
      chỉ để lấy result.

Mỗi hàm trả về dict chuẩn để frontend render —
không có bất kỳ logic in ấn nào ở đây (Separation of Concerns).

Cache department index:
    Composite Hash (S2A) cần 1 dict {dept: [records]}.
    Build lại mỗi lần gọi = lãng phí + làm sai lệch ý nghĩa benchmark
    (mục tiêu là đo QUERY time sau khi đã preprocess, không phải build time).

    Giải pháp: cache theo id(records). Cùng 1 list → dùng lại index cũ.
    Load dataset mới → list mới → id() khác → tự động build lại.
    Không cần web.py biết hay sửa gì.
"""

import time
import bisect

from engine.search import (
    linear_search,
    binary_search,
    sort_by_id,
    sort_by_gpa,
)
from engine.fuzzy_search import fuzzy_linear_search


REPEAT = 20   # số lần lặp để lấy trung bình — đủ loại nhiễu cho demo web


# ══════════════════════════════════════════════════════════════════
#  Helper chung
# ══════════════════════════════════════════════════════════════════

def _avg_ms(fn, repeat: int = REPEAT) -> tuple:
    """
    Chạy fn() `repeat` lần, trả về (avg_ms, last_result).

    Trả luôn kết quả lần chạy cuối để caller không phải gọi fn() thêm 1 lần
    chỉ để lấy kết quả.
    """
    total  = 0.0
    result = None
    for _ in range(repeat):
        start  = time.perf_counter()
        result = fn()
        total += time.perf_counter() - start
    return (total / repeat) * 1000, result


# ---- Dept index cache ----

_dept_index_cache = {"records_id": None, "index": None}


def _get_dept_index(records: list) -> dict:
    """
    Trả về dict {department_code: [records]} — build 1 lần, cache lại.

    Cache key = id(records). Nếu web.py truyền cùng 1 list object thì
    dùng lại index đã build, không duyệt lại n records.
    """
    if _dept_index_cache["records_id"] == id(records):
        return _dept_index_cache["index"]

    index = {}
    for r in records:
        index.setdefault(r["department_code"], []).append(r)

    _dept_index_cache["records_id"] = id(records)
    _dept_index_cache["index"]      = index
    return index


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 1 — Tra cứu theo MSSV
# ══════════════════════════════════════════════════════════════════

def bench_s1_chain(ht_chain, target_id: str) -> dict:
    """Hash Chaining — tìm 1 sinh viên theo MSSV."""
    ms, found = _avg_ms(lambda: ht_chain.search(target_id))
    return {
        "algo":    "Hash Chaining",
        "ms":      ms,
        "sort_ms": None,
        "found":   found,
        "failed":  False,
    }


def bench_s1_open(ht_open, target_id: str) -> dict:
    """Hash Open Addressing — tìm 1 sinh viên theo MSSV."""
    ms, found = _avg_ms(lambda: ht_open.search(target_id))
    return {
        "algo":    "Hash Open Addr.",
        "ms":      ms,
        "sort_ms": None,
        "found":   found,
        "failed":  False,
    }


def bench_s1_linear(records: list, target_id: str) -> dict:
    """Linear Search — O(n)."""
    ms, found = _avg_ms(lambda: linear_search(records, target_id))
    return {
        "algo":    "Linear Search",
        "ms":      ms,
        "sort_ms": None,
        "found":   found,
        "failed":  False,
    }


def bench_s1_binary(records: list, target_id: str) -> dict:
    """Binary Search — sort 1 lần (đo riêng), rồi đo search."""
    sort_start     = time.perf_counter()
    sorted_records = sort_by_id(records)
    sort_ms        = (time.perf_counter() - sort_start) * 1000

    ms, found = _avg_ms(lambda: binary_search(sorted_records, target_id))
    return {
        "algo":    "Binary Search",
        "ms":      ms,
        "sort_ms": sort_ms,
        "found":   found,
        "failed":  False,
    }


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2A — Lọc GPA + Department
# ══════════════════════════════════════════════════════════════════

def bench_s2a_hash(records: list, department: str, min_gpa: float, max_gpa: float) -> dict:
    """Composite Hash — bucket theo department (cached), filter khoảng GPA trong bucket."""
    dept_index = _get_dept_index(records)   # cache hit sau lần đầu

    def _filter():
        bucket = dept_index.get(department, [])
        return [r for r in bucket if min_gpa <= r["gpa"] <= max_gpa]

    ms, matches = _avg_ms(_filter)
    return {
        "algo":        "Composite Hash",
        "ms":          ms,
        "sort_ms":     None,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }


def bench_s2a_linear(records: list, department: str, min_gpa: float, max_gpa: float) -> dict:
    """Linear Scan — duyệt toàn bộ, check khoảng GPA và department."""
    def _filter():
        return [
            r for r in records
            if r["department_code"] == department and min_gpa <= r["gpa"] <= max_gpa
        ]

    ms, matches = _avg_ms(_filter)
    return {
        "algo":        "Linear Scan",
        "ms":          ms,
        "sort_ms":     None,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }


def bench_s2a_binary(records: list, department: str, min_gpa: float, max_gpa: float) -> dict:
    """Binary Filter — sort theo GPA, bisect tìm khoảng [min, max], filter department."""
    sort_start    = time.perf_counter()
    sorted_by_gpa = sort_by_gpa(records)
    sort_ms       = (time.perf_counter() - sort_start) * 1000

    gpa_keys = [r["gpa"] for r in sorted_by_gpa]

    def _filter():
        lo = bisect.bisect_left(gpa_keys, min_gpa)
        hi = bisect.bisect_right(gpa_keys, max_gpa)
        return [r for r in sorted_by_gpa[lo:hi] if r["department_code"] == department]

    ms, matches = _avg_ms(_filter)
    return {
        "algo":        "Binary Filter",
        "ms":          ms,
        "sort_ms":     sort_ms,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2B — Lọc khoảng GPA thuần
# ══════════════════════════════════════════════════════════════════

def bench_s2b_hash(min_gpa: float, max_gpa: float) -> dict:
    """Hash — FAILED: không có khái niệm khoảng (chỉ match exact key)."""
    return {
        "algo":        "Hash lookup",
        "ms":          None,
        "sort_ms":     None,
        "match_count": 0,
        "matches":     [],
        "failed":      True,
    }


def bench_s2b_linear(records: list, min_gpa: float, max_gpa: float) -> dict:
    """Linear Scan — duyệt toàn bộ, check khoảng GPA."""
    def _filter():
        return [r for r in records if min_gpa <= r["gpa"] <= max_gpa]

    ms, matches = _avg_ms(_filter)
    return {
        "algo":        "Linear Scan",
        "ms":          ms,
        "sort_ms":     None,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }


def bench_s2b_binary(records: list, min_gpa: float, max_gpa: float) -> dict:
    """Binary Filter — sort theo GPA, bisect tìm khoảng [min, max]."""
    sort_start    = time.perf_counter()
    sorted_by_gpa = sort_by_gpa(records)
    sort_ms       = (time.perf_counter() - sort_start) * 1000

    gpa_keys = [r["gpa"] for r in sorted_by_gpa]

    def _filter():
        lo = bisect.bisect_left(gpa_keys, min_gpa)
        hi = bisect.bisect_right(gpa_keys, max_gpa)
        return sorted_by_gpa[lo:hi]

    ms, matches = _avg_ms(_filter)
    return {
        "algo":        "Binary Filter",
        "ms":          ms,
        "sort_ms":     sort_ms,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 3 — Tìm tên mờ
# ══════════════════════════════════════════════════════════════════

def bench_s3_hash(ht_chain, query: str) -> dict:
    """Hash — FAILED: không tìm được theo tên (key là student_id)."""
    return {
        "algo":        "Hash lookup",
        "ms":          None,
        "match_count": 0,
        "matches":     [],
        "failed":      True,
    }


def bench_s3_fuzzy(records: list, query: str) -> dict:
    """Fuzzy Linear Search — normalize + substring match."""
    ms, matches = _avg_ms(lambda: fuzzy_linear_search(records, query))
    return {
        "algo":        "Fuzzy Linear Search",
        "ms":          ms,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }