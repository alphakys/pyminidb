class Cursor:
    """
    [어원과 역사: 왜 'Cursor'인가?]

    1. 어원: 라틴어 'currere' (달리다)
       - 'Cursor'는 '달리는 사람' 또는 '심부름꾼'을 의미합니다. 컴퓨팅에서는
         결과를 가져오기 위해 데이터 세트 위를 역동적으로 '달리는 존재'를 상징합니다.

    2. 역사: 계산자 (Slide Rule)
       - 현대적 컴퓨터가 등장하기 전, 계산자 위에서 숫자를 가리키기 위해 사용하는
         투명한 슬라이딩 부품을 '커서'라고 불렀습니다.

    3. Cursor vs. Pointer
       - Pointer: 정적인 메모리 주소 (단순한 위치 정보).
       - Cursor: 상태를 가진 반복자 (Iterator). 단순히 위치만 가리키는 것이 아니라
         '현재 어디인지', '더 읽을 데이터가 있는지', '어떻게 전진할지'에 대한 문맥을 가집니다.

    4. DBMS 맥락:
       - SQL은 '집합(Set)' 단위로 결과를 내놓지만, 우리가 사용하는 언어(Python 등)는
         데이터를 '한 줄씩(Row by row)' 처리해야 합니다.
       - 커서는 이 집합 위를 순회하며 애플리케이션 로직에 데이터를 한 줄씩 전달하는
         '가교(Bridge)' 역할을 수행합니다.
    """

    def __init__(self, table, row_num):
        self.table = table
        self.row_num = row_num
        self.end_of_table = False
