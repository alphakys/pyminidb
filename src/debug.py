"""
디버깅 헬퍼 유틸리티

사용법:
    from src.debug import debug, section, trace

    debug("변수 이름", value)  # 예쁜 출력

    with section("Split 수행"):  # 섹션 구분
        # 여러 코드...
        debug("keys", keys)
        debug("pids", pids)

    @trace  # 함수 호출 추적
    def my_function():
        ...
"""

import functools
import inspect
from typing import Any


# ANSI 색상 코드
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"


def debug(label: str, value: Any, color: str = Colors.CYAN):
    """
    예쁜 디버그 출력

    사용:
        debug("user_id", 123)
        debug("keys", [10, 20, 30])
    """
    caller = inspect.stack()[1]
    filename = caller.filename.split("/")[-1]
    lineno = caller.lineno

    print(
        f"{color}🔍 [{filename}:{lineno}] {Colors.BOLD}{label}{Colors.RESET}{color} = {value}{Colors.RESET}"
    )


class section:
    """
    코드 섹션 구분

    사용:
        with section("Split Leaf"):
            # 코드...
    """

    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}")
        print(f"{self.name}".center(60))
        print(f"{'=' * 60}{Colors.RESET}")
        return self

    def __exit__(self, *args):
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def trace(func):
    """
    함수 호출 추적 데코레이터

    사용:
        @trace
        def split_leaf(self, leaf_pid):
            ...
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        print(f"{Colors.GREEN}▶ {func_name}() 호출{Colors.RESET}")
        print(f"  args: {args[1:]}")  # self 제외
        print(f"  kwargs: {kwargs}")

        result = func(*args, **kwargs)

        print(f"{Colors.GREEN}◀ {func_name}() 반환: {result}{Colors.RESET}")
        return result

    return wrapper


# 간단한 사용을 위한 단축 함수들
def p(value):
    """한 줄 빠른 출력"""
    caller = inspect.stack()[1]
    lineno = caller.lineno
    print(f"{Colors.YELLOW}L{lineno}: {value}{Colors.RESET}")


def pp(label, value):
    """라벨 + 값"""
    debug(label, value, Colors.MAGENTA)


# 테스트
if __name__ == "__main__":
    # 테스트
    debug("테스트 값", 123)

    with section("섹션 테스트"):
        debug("keys", [10, 20, 30])
        debug("pids", [1, 2, 3, 4])

    @trace
    def test_func(x, y):
        return x + y

    result = test_func(5, 10)
