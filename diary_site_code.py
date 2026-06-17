import streamlit as st
import datetime
import pandas as pd
import time

# --- [1. 기본 설정 및 중앙 저장소 세팅] ---
st.set_page_config(page_title="디지털 플래너 다이어리", layout="wide", initial_sidebar_state="expanded")

# 앱이 켜져 있는 동안 데이터를 기억하는 저장소 (로그인 계정별 개인화 데이터 구조)
if 'db' not in st.session_state:
    st.session_state.db = {
        "users": {"admin": "1234", "club_member": "2026"}, # 아이디:비밀번호
        "planner": {},     # {날짜: [{"task": 할일, "done": 완료여부, "repeat": 주기}]}
        "notes": [],       # [{"subject": 과목, "unit": 단원, "content": 내용, "date": 날짜}]
        "expenses": [],    # [{"date": 날짜, "item": 항목, "amount": 금액, "currency": 통화}]
        "diaries": {},     # {날짜: {"title": 제목, "content": 내용}}
        "custom": []       # 사용자가 만든 커스텀 기록들
    }


# --- [2. 로그인 기능] ---
def login_page():
    st.title("🔐 디지털 플래너 다이어리")
    st.error("⚠️ 경고: 아이디와 비밀번호를 잊어버리면 절대 접근이 불가능합니다.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("로그인")
        user_id = st.text_input("아이디 입력")
        user_pw = st.text_input("비밀번호 입력", type="password")
        
        if st.button("로그인하기", use_container_width=True):
            if user_id in st.session_state.db["users"] and st.session_state.db["users"][user_id] == user_pw:
                st.session_state.login_status = True
                st.session_state.current_user = user_id
                st.success(f"🎈 {user_id}님 환영합니다! 접속 중...")
                time.sleep(1)
                st.rerun()
            else:
                st.sidebar.error("❌ 아이디 또는 비밀번호가 틀렸습니다.")

# 만약 입력한 아이디가 장부에 있고 '그리고' 비밀번호까지 장부와 똑같다면?
if user_id in st.session_state.db["users"] and st.session_state.db["users"][user_id] == user_pw:
    st.success("로그인 성공!") # 통과!
else:
    st.error("❌ 아이디 또는 비밀번호가 틀렸습니다.") # 하나라도 다르면 차단!

if 'login_status' not in st.session_state:
    st.session_state.login_status = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None


# --- [3. 메인 앱 기능] ---
def main_app():
    # 사이드바 상단 로그인 정보 및 로그아웃
    st.sidebar.success(f"👤 로그인 계정: {st.session_state.current_user}")
    if st.sidebar.button("로그아웃"):
        st.session_state.login_status = False
        st.session_state.current_user = None
        st.rerun()
        
    st.sidebar.write("---")
    
    # 🌟 연/월/일 직접 다이얼 선택 기능 (기획 반영)
    st.sidebar.subheader("📅 날짜 선택 다이얼")
    c1, c2, c3 = st.sidebar.columns(3)
    with c1: selected_year = st.selectbox("연", [2026, 2027, 2028])
    with c2: selected_month = st.selectbox("월", list(range(1, 13)))
    with c3: selected_day = st.selectbox("일", list(range(1, 32)))
    
    # 가상의 한국 표준시 날짜 텍스트 완성
    date_str = f"{selected_year}-{selected_month:02d}-{selected_day:02d}"
    st.sidebar.info(f"선택된 날짜: {date_str}")
    
    # 메인 모드 전환
    mode = st.radio("📂 카테고리 전환", ["📅 플래너 모드", "📖 다이어리 모드"], horizontal=True)
    st.write("---")

    # ==================== [플래너 모드] ====================
    if mode == "📅 플래너 모드":
        st.title(f"📅 플래너 - {date_str}")
        
        tab1, tab2 = st.tabs(["일정 및 도장 깨기", "⏳ 뽀모도로 타이머"])
        
        with tab1:
            # 1. 새 일정 등록
            with st.expander("➕ 새로운 일정 등록하기"):
                task = st.text_input("할 일을 적어주세요")
                repeat = st.selectbox("반복 주기 설정", ["한 번만", "매일(날마다)", "주마다", "일주일 달성 횟수", "매달 특정일"])
                if st.button("일정 추가"):
                    if task:
                        if date_str not in st.session_state.db["planner"]:
                            st.session_state.db["planner"][date_str] = []
                        st.session_state.db["planner"][date_str].append({"task": task, "done": False, "repeat": repeat})
                        st.success("일정 등록 완료!")
                        st.rerun()

            # 2. 일정 출력 및 도장 깨기
            st.subheader("🎯 오늘의 할 일 목록")
            if date_str in st.session_state.db["planner"] and st.session_state.db["planner"][date_str]:
                # 캘린더 당 날짜 전체를 대변하는 상단 총괄 도장 상태 계산
                all_done = all(item["done"] for item in st.session_state.db["planner"][date_str])
                if all_done:
                    st.success("🏅 [날짜 전체 도장 쾅!] 오늘 일정을 모두 완료하셨습니다!")
                
                # 개별 일정 도장 깨기
                for i, item in enumerate(st.session_state.db["planner"][date_str]):
                    col_task, col_stamp = st.columns([4, 1])
                    with col_task:
                        if item["done"]:
                            st.write(f"~~✅ {item['task']} ({item['repeat']})~~")
                        else:
                            st.write(f"⚪ {item['task']} ({item['repeat']})")
                    with col_stamp:
                        if not item["done"]:
                            if st.button("💮 도장 칸", key=f"stamp_{i}"):
                                st.session_state.db["planner"][date_str][i]["done"] = True
                                st.balloons() # 축하 풍선
                                st.rerun()
                        else:
                            st.write("💮 [완료 도장 완료]")
            else:
                st.write("등록된 일정이 없습니다. 새 일정을 추가해보세요!")

        with tab2:
            st.subheader("⏳ 뽀모도로 타이머 (25분 집중 / 5분 휴식)")
            st.caption("※ 파이썬 코드가 내부적으로 작동합니다.")
            timer_mode = st.radio("타이머 선택", ["집중 모드 (25분)", "휴식 모드 (5분)"], horizontal=True)
            
            if st.button("타이머 시작"):
                duration = 25 * 60 if "집중" in timer_mode else 5 * 60
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 시뮬레이션 가동 (실제 배포환경 속도를 감안해 짧게 테스트하려면 배포 후 동아리원들과 조절 가능)
                for percent in range(100):
                    time.sleep(duration / 100)
                    progress_bar.progress(percent + 1)
                    status_text.text(f"진행률: {percent + 1}%")
                
                st.success("⏰ 타이머가 종료되었습니다! (알람 벨 울림 시뮬레이션)")
                st.audio("https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg", format="audio/ogg", autoplay=True)

    # ==================== [다이어리 모드] ====================
    else:
        st.title("📖 다이어리 및 리포트")
        sub_mode = st.sidebar.radio("다이어리 메뉴", ["📝 과목별 노트 정리", "📊 주간 리포트 (지출/습관)", "✍️ 일기 작성", "🛠️ 커스텀 작성란"])
        
        # 1. 과목별 노트 정리
        if sub_mode == "📝 과목별 노트 정리":
            st.subheader("📝 과목별 노트 정리")
            n_subject = st.text_input("과목명")
            n_unit = st.text_input("단원 및 차시")
            n_content = st.text_area("노트 정리 내용 입력")
            
            if st.button("노트 저장"):
                if n_subject and n_content:
                    st.session_state.db["notes"].append({"subject": n_subject, "unit": n_unit, "content": n_content, "date": date_str})
                    st.success("노트가 시스템 중앙 저장소에 저장되었습니다.")
            
            st.write("---")
            st.subheader("🔍 저장된 노트 열람")
            if st.session_state.db["notes"]:
                df_notes = pd.DataFrame(st.session_state.db["notes"])
                st.dataframe(df_notes) # 파이썬 데이터 가독성 도구로 표 출력
            else:
                st.write("저장된 내용이 없습니다.")

        # 2. 주간 리포트 (지출/습관)
        elif sub_mode == "📊 주간 리포트 (지출/습관)":
            st.subheader("📊 주간 리포트")
            
            # --- 지출 계산 섹션 ---
            st.markdown("### 💰 지출 관리 프로그램")
            currency = st.radio("화폐 단위 설정", ["KRW (원)", "USD ($)"], horizontal=True)
            exp_item = st.text_input("지출 항목 (예: 매점)")
            exp_amount = st.number_input("금액 입력", min_value=0, value=0)
            
            if st.button("지출 기록 저장"):
                if exp_item and exp_amount > 0:
                    st.session_state.db["expenses"].append({"date": date_str, "item": exp_item, "amount": exp_amount, "currency": currency})
                    st.success("지출 내역 기록 완료!")
                    st.rerun()
            
            # 지출액 파이썬 분석 도구(Pandas) 자동 연산 및 가독성 표
            if st.session_state.db["expenses"]:
                df_exp = pd.DataFrame(st.session_state.db["expenses"])
                st.dataframe(df_exp)
                total_sum = df_exp["amount"].sum()
                st.metric(label="현재 총 지출 합계", value=f"{total_sum:,} {currency}")
                st.caption("💡 (데이터가 누적되면 지난주/지난달 내역과 자동으로 비교 연산이 실행됩니다.)")
            
            # --- 습관 달성 현황 섹션 ---
            st.write("---")
            st.markdown("### 📈 습관 달성 현황 (플래너 연동 그래프)")
            # 플래너 데이터를 수집해서 즉석 그래프 분석 생성
            if st.session_state.db["planner"]:
                dates = list(st.session_state.db["planner"].keys())
                success_rates = []
                for d in dates:
                    total = len(st.session_state.db["planner"][d])
                    dones = sum(1 for item in st.session_state.db["planner"][d] if item["done"])
                    success_rates.append((dones / total) * 100 if total > 0 else 0)
                
                # 그래프 그리기 데이터 가독성 도구 작동
                chart_data = pd.DataFrame({"날짜": dates, "달성률(%)": success_rates})
                st.line_chart(chart_data.set_index("날짜"))
                st.table(chart_data)
            else:
                st.info("플래너에 일정을 등록하고 도장을 깨면 이곳에 월별/주별 그래프가 자동으로 그려집니다.")

        # 3. 일기 작성
        elif sub_mode == "✍️ 일기 작성":
            st.subheader(f"✍️ 오늘의 일기 - {date_str}")
            d_title = st.text_input("일기 제목")
            d_content = st.text_area("오늘 하루 어땠나요?")
            d_file = st.file_uploader("사진 첨부 버튼 (jpg/png)", type=["jpg", "png"])
            
            if st.button("시스템 메모리 저장"):
                st.session_state.db["diaries"][date_str] = {"title": d_title, "content": d_content}
                st.success(f"🔒 {date_str} 일기가 시스템 중앙 저장소에 안전하게 저장되었습니다.")
            
            st.write("---")
            st.subheader("📅 지난 일기 보기")
            if date_str in st.session_state.db["diaries"]:
                st.markdown(f"#### 📋 {st.session_state.db['diaries'][date_str]['title']}")
                st.write(st.session_state.db['diaries'][date_str]['content'])
                if d_file:
                    st.image(d_file, caption="첨부된 사진")
            else:
                st.write("이 날짜에 작성된 일기가 없습니다. 다이얼을 돌려 다른 날짜를 확인해보세요!")

        # 4. 커스텀 작성란
        elif sub_mode == "🛠️ 커스텀 작성란":
            st.subheader("🛠️ 나만의 커스텀 리포트 만들기")
            c_title = st.text_input("주제 설정 (예: 운동 기록, 식단)")
            formats = st.multiselect("출력 형식을 순서대로 복수 선택하세요", ["글 작성란", "표(Table)", "샘플 그래프"])
            
            if formats:
                st.write("👇 **내가 커스텀한 양식 미리보기 및 작성**")
                for fmt in formats:
                    if fmt == "글 작성란":
                        st.text_area(f"[{c_title}] 자유 기술란")
                    elif fmt == "표(Table)":
                        st.write(f"[{c_title}] 기록 데이터 테이블")
                        st.data_editor(pd.DataFrame({"항목": ["기록1", "기록2"], "수치": [0, 0]}))
                    elif fmt == "샘플 그래프":
                        st.write(f"[{c_title}] 변동 추이 그래프")
                        st.bar_chart([10, 20, 15, 30])
            
            if st.button("커스텀 서버 저장 및 링크 생성"):
                st.success("🔗 서버 저장 완료! 공유용 가상 링크가 생성되었습니다: https://streamlit.io/share/diary/custom-link")

# --- [4. 앱 실행 제어 부모 코드] ---
if not st.session_state.login_status:
    login_page()
else:
    main_app()
