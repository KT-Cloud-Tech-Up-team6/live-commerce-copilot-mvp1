import time

from interest_tracker import InterestTracker
from rag_answer import answer_question
from unanswered_analyzer import analyze_unanswered


def to_dict(result):
    if hasattr(result, "model_dump"):
        return result.model_dump()

    if isinstance(result, dict):
        return result

    raise TypeError(
        f"지원하지 않는 RAG 결과 타입입니다: {type(result)}"
    )


def main():
    tracker = InterestTracker()

    print("=" * 64)
    print("로보락 F25 Seller Copilot - P파트 MVP")
    print("=" * 64)
    print("/dashboard : 현재 관심사 화면")
    print("/reset     : 집계 초기화")
    print("q          : 종료")
    print("=" * 64)

    while True:
        print()
        question = input("고객 댓글 > ").strip()

        if not question:
            continue

        if question.lower() in {"q", "quit", "exit"}:
            print("테스트를 종료합니다.")
            break

        if question == "/dashboard":
            tracker.print_dashboard()
            continue

        if question == "/reset":
            tracker.reset()
            print("집계를 초기화했습니다.")
            continue

        start = time.time()

        try:
            rag_result = to_dict(answer_question(question))

            status = rag_result.get("grounding_status", "")
            answer = rag_result.get("answer", "")

            if status == "GROUNDED":
                print("→ 상품 KB에서 처리 가능한 질문")

            elif status in {
                "PARTIAL_GROUNDED",
                "NO_GROUNDED_INFO",
            }:
                analysis = analyze_unanswered(
                    question=question,
                    grounding_status=status,
                    rag_answer=answer,
                )

                if analysis.topics:
                    tracker.add_topics(analysis.topics)
                    print(
                        f"→ 미답변 세부질문 "
                        f"{len(analysis.topics)}건 집계"
                    )
                else:
                    print("→ 집계할 미답변 상품 질문 없음")

            else:
                print(
                    f"→ 알 수 없는 Grounding 상태: "
                    f"{status}"
                )

            elapsed = time.time() - start
            print(f"처리 시간: {elapsed:.2f}초")

        except Exception as exc:
            print(f"오류 발생: {exc}")


if __name__ == "__main__":
    main()
