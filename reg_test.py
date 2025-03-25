import re

def check_word_in_string(text, word):
    """
    문자열에서 특정 단어가 띄어쓰기와 무관하게 포함되어 있는지 확인합니다.

    Args:
        text (str): 확인할 문자열입니다.
        word (str): 찾을 단어입니다.

    Returns:
        bool: 단어가 문자열에 포함되어 있으면 True, 그렇지 않으면 False를 반환합니다.
    """

    # 띄어쓰기를 무시하고 단어를 찾기 위한 정규 표현식 패턴 생성
    pattern = r"\s*".join(list(word))

    # 정규 표현식으로 문자열에서 단어 찾기 (대소문자 구분 없이)
    match = re.search(pattern, text, re.IGNORECASE)

    return bool(match)

# 예시 사용
text1 = "송파구청 창업 지 원 사 업 관련 안내"
text2 = """" 
안성에서 지
원 사업을 하고자 하는 
경우에 참고하세요. 접수 창구는
시청 1층에 위치해 있습니다.
"""
text3 = "지원사업은 다양한 형태로 제공됩니다."
text4 = "안녕하세요 반갑습니다."

word = "지원사업"

print(f"'{text1}'에서 '{word}' 찾기: {check_word_in_string(text1, word)}")  # True
print(f"'{text2}'에서 '{word}' 찾기: {check_word_in_string(text2, word)}")  # True
print(f"'{text3}'에서 '{word}' 찾기: {check_word_in_string(text3, word)}")  # True
print(f"'{text4}'에서 '{word}' 찾기: {check_word_in_string(text4, word)}")  # False