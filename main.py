"""퀴즈 게임 실행 파일. 터미널에서 `python main.py`로 실행한다."""

import sys

from quiz_game import QuizGame


def main():
    # 윈도우 콘솔·파이프에서도 한글과 이모지가 깨지지 않도록 입출력 인코딩을 UTF-8로 맞춘다.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    game = QuizGame()
    game.run()


if __name__ == "__main__":
    main()
