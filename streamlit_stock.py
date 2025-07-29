import streamlit as st
import mysql.connector
import FinanceDataReader as fdr
from datetime import datetime as dt

#헤더  
st.header("전문 스톡 프로그램")
st.subheader("v2.0")

# DB 연결 함수
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",    
        database="stock_db"  
    )

# 전역 상태 변수 초기화 (새로 고침 해도 값 유지)
if "isLogin" not in st.session_state:
    st.session_state.isLogin = False
if "username" not in st.session_state:
    st.session_state.username = ""

# 탭 구성
tab_login, tab_gugu, tab_memo , tab_stock = st.tabs(["로그인", "구구단", "메모장","주식 조회"])

# 로그인 탭
with tab_login:
    st.header("로그인")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        conn.close()
        if result:
            st.session_state.isLogin = True
            st.session_state.username = username
            st.success(f"{username}님, 로그인 OK")
        else:
            st.error("아이디 or 비밀번호가 틀렸습니다.")

# 구구단 탭
with tab_gugu:
    if not st.session_state.isLogin:
        st.warning("로그인 후 사용 할 수 있습니다.")
    else:
        st.header("구구단 출력기")
        dan = st.radio("단을 선택하세요", list(range(1, 10)), horizontal=True)
        st.markdown(f"## {dan}단")
        for i in range(1, 10):
            st.write(f"{dan} x {i} = {dan * i}")

# 메모장 탭
with tab_memo:
    if not st.session_state.isLogin:
        st.warning("로그인 후 사용 할 수 있습니다.")
    else:
        st.header("메모장")
        memo = st.text_input("메모 입력", placeholder="예) 오늘 주식시장 체크")
        if st.button("저장"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO memos (content) VALUES (%s)", (memo,))
            conn.commit()
            conn.close()
            st.success("메모 저장 완료!")

        # 메모 목록 출력
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content, created_at FROM memos ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        for content, ts in rows:
            st.markdown(f"""
            
            <b>{ts.strftime('%Y-%m-%d %H:%M:%S')}</b><br>
            {content}
            </div>
            """, unsafe_allow_html=True)
    
    #  주식 조회 탭
with tab_stock:
    if not st.session_state.isLogin:
        st.warning("로그인 후 사용 할 수 있습니다.")
    else:
        st.header("주식 조회")

        # 날짜 & 종목 코드 입력
        dateInput = st.date_input("조회 날짜를 입력해주세요", dt(2025, 7, 1))
        stockCode = st.text_input("종목 코드를 입력해주세요 (예: 005930 - 삼성전자)")

        # 주식 데이터 조회
        if st.button("조회"):
            #종목 코드가 비어있는 경우 경고 메시지 출력 (유효성 검사)
            if not stockCode.strip():
                st.warning("종목 코드를 입력해주세요.")
            else:
                try:
                    stockDf = fdr.DataReader(stockCode.strip(), dateInput)
                    if stockDf.empty:
                        # 조회 결과가 없을 때
                        st.warning("해당 날짜 이후의 주식 데이터가 없습니다.")
                    else:
                        st.subheader(f"{stockCode}의 주가 (종가 기준)")
                        data = stockDf.sort_index(ascending=True).loc[:, 'Close']
                        st.line_chart(data)
                except Exception as e:
                    #예외 발생 시 에러 메시지 출력
                    st.error(f"데이터 조회 중 오류 발생: {e}")

        # 주식 관련 메모 입력 및 저장
        memoInput = st.text_input("메모 내용", placeholder="예시) 오늘 종가 기준 확인")
        if st.button("메모 저장"):
            if memoInput.strip():
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO memos (content) VALUES (%s)", (memoInput,))
                conn.commit()
                conn.close()
                st.success("주식 메모 저장 완료!")
            else:
                st.warning("메모 내용을 입력해주세요.")
   
#    필기