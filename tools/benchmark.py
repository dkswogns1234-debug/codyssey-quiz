"""퀴즈 개수가 많아질 때(1,000개 이상) 성능을 측정하는 개발용 스크립트.

실행: python tools/benchmark.py
- 실제 state.json은 건드리지 않고, 임시 폴더에 가짜 퀴즈 N개짜리 파일을 만들어 측정한다.
- 측정 항목: 파일 크기, 저장(save_state)·불러오기(load_state) 시간, 무작위 출제(random.sample) 시간,
  목록 출력(list_quizzes) 시간, 불러오기 중 최대 메모리와 불러온 뒤 남는 메모리(tracemalloc),
  들여쓰기 없이(JSON_INDENT=None) 저장했을 때의 파일 크기.
- 측정 횟수: 시간 항목은 5회 중 최솟값, 메모리·파일 크기는 1회 측정(실행마다 거의 같은 값).
- 한계: 목록 출력은 문자열을 만드는 시간만 재고 터미널에 그리는 시간은 포함하지 않는다.
  tracemalloc은 파이썬이 할당한 메모리만 재며, 프로세스 전체 메모리(인터프리터 자체 등)는 포함하지 않는다.
"""

import contextlib
import io
import json
import random
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

# tools 폴더에서 실행해도 프로젝트 루트의 모듈을 불러올 수 있게 한다.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quiz import Quiz            # noqa: E402
from quiz_game import QuizGame   # noqa: E402

SIZES = [1_000, 10_000, 100_000]
REPEAT = 5  # 각 측정을 5번 해서 가장 빠른 값을 쓴다 (다른 프로그램의 영향 줄이기)


def make_quizzes(count):
    """실제 퀴즈와 비슷한 길이의 가짜 퀴즈 count개를 만든다."""
    return [
        Quiz(f"벤치마크용 {i}번 문제: 파이썬에서 리스트의 길이를 구하는 함수는?",
             ["len()", "size()", "count()", "length()"], 1)
        for i in range(count)
    ]


def best_time(func):
    """func를 REPEAT번 실행해 가장 짧은 시간(밀리초)을 반환한다."""
    times = []
    for _ in range(REPEAT):
        start = time.perf_counter()
        func()
        times.append((time.perf_counter() - start) * 1000)
    return min(times)


def compact_size_mb(count):
    """같은 퀴즈를 들여쓰기 없이 JSON으로 바꿨을 때의 크기(MB). 저장 형식은 save_state와 같다."""
    data = {"quizzes": [q.to_dict() for q in make_quizzes(count)], "best_score": None, "best_correct": 0, "best_total": 0}
    return len(json.dumps(data, ensure_ascii=False).encode("utf-8")) / 1024 / 1024


def measure(count, folder):
    state_file = Path(folder) / f"state_{count}.json"
    game = QuizGame(state_file)
    game.save_enabled = True
    game.quizzes = make_quizzes(count)

    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet):  # 측정 중 안내 문구는 화면에 찍지 않는다.
        save_ms = best_time(game.save_state)
        load_ms = best_time(game.load_state)
        list_ms = best_time(game.list_quizzes)
    sample_ms = best_time(lambda: random.sample(game.quizzes, 10))

    tracemalloc.start()
    loaded = QuizGame(state_file)
    with contextlib.redirect_stdout(quiet):
        loaded.load_state()
    current, peak = tracemalloc.get_traced_memory()  # (지금 남은 양, 측정 중 최대치)
    memory_mb, peak_mb = current / 1024 / 1024, peak / 1024 / 1024
    tracemalloc.stop()

    size_mb = state_file.stat().st_size / 1024 / 1024
    return size_mb, save_ms, load_ms, sample_ms, list_ms, memory_mb, peak_mb


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Python {sys.version.split()[0]}, 시간은 {REPEAT}회 중 최솟값, 메모리·파일 크기는 1회 측정\n")
    print("| 퀴즈 수 | 파일 크기 | 저장 | 불러오기 | 무작위 10문제 출제 | 목록 출력(화면 표시 제외) | 불러오기 중 최대 메모리 | 불러온 뒤 메모리 |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    compact = []
    with tempfile.TemporaryDirectory() as folder:
        for count in SIZES:
            size_mb, save_ms, load_ms, sample_ms, list_ms, memory_mb, peak_mb = measure(count, folder)
            print(f"| {count:,}개 | {size_mb:.2f} MB | {save_ms:.0f} ms | {load_ms:.0f} ms "
                  f"| {sample_ms:.3f} ms | {list_ms:.0f} ms | {peak_mb:.1f} MB | {memory_mb:.1f} MB |")
            compact.append((count, size_mb, compact_size_mb(count)))
    print("\n들여쓰기 없이 저장(JSON_INDENT=None)했을 때 파일 크기")
    for count, indented, small in compact:
        print(f"- {count:,}개: {indented:.2f} MB → {small:.2f} MB ({(1 - small / indented) * 100:.0f}% 감소)")


if __name__ == "__main__":
    main()
