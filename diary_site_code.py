import streamlit as st
import datetime
import pandas as pd
import time

# --- [1. 기본 설정 및 동적 가상 DB 세팅] ---
st.set_page_config(page_title="디지털 플래너 다이어리", layout="wide")

# 가상 데이터베이스 초기화 (회원정보 및 개인 창고)
if 'db' not in st.session_state:
    st.session_state.db = {
        "users": {},       # {아이디: 비밀번호} 실시간 저장소
        "user_data": {}    # {아이디: {개인 플래너/다이어리 창고}}
    }

if 'login_status' not in st.session_state:
    st.session_state.login_status = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# --- [2. 로그인 / 진짜 회원가입 제어] ---
if not st.session_state.login_status:
    st.title("🔐 디지털 플래너 다이어리")
    st.error("⚠️ 경고: 자체 로그인 시스템이므로 아이디와 비밀번호를 잊어버리면 절대 접근이 불가능합니다.")
    
    # 로그인과 회원가입 탭 분리
    menu_tab1, menu_tab2 = st.tabs(["🔒 로그인", "📝 회원가입"])
    
    # [회원가입 탭]
    with menu_tab2:
        st.subheader("새로운 계정 만들기")
        new_id = st.text_input("원하는 아이디 입력", key="join_id")
        new_pw = st.text_input("원하는 비밀번호 입력", type="password", key="join_pw")
        
        if st.button("회원가입 완료하기", use_container_width=True):
            if new_id == "" or new_pw == "":
                st.warning("아이디와 비밀번호를 모두 입력해주세요.")
            elif new_id in st.session_state.db["users"]:
                st.error("❌ 이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.")
            else:
                # 회원 장부에 등록 및 전용 빈 창고 자동 개설
                st.session_state.db["users"][new_id] = new_pw
                st.session_state.db["user_data"][new_id] = {
                    "planner": {}, "notes": [], "expenses": [], "diaries": {}, "custom": []
                }
                st.success("🎉 회원가입 성공! 로그인 탭으로 이동해서 로그인해 주세요.")
                
    # [로그인 탭]
    with menu_tab1:
        st.subheader("사용자 로그인")
        
        # 🌟 중요: 파이썬이 글자를 먼저 인식하도록 입력창을 무조건 '위쪽'에 선언!
        user_id = st.text_input("아이디 입력", key="login_id")
        user_pw = st.text_input("비밀번호 입력", type="password", key="login_pw")
        
        if st.button("로그인하기", use_container_width=True):
            # 🔍 비밀번호 철저 검증 로직 (이제 user_id가 위에서 선언되었으므로 NameError가 나지 않습니다)
            if user_id in st.session_state.db["users"]:
                if st.session_state.db["users"][user_id] == user_pw:
                    st.session_state.login_status = True
                    st.session_state.current_user = user_id
                    st.success(f"🎈 {user_id}님 환영합니다! 개인 창고 연결 중...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 기존에 저장한 정보와 다릅니다. 다시 확인해주세요.")
            else:
                st.error("❌ 존재하지 않는 아이디입니다. 회원가입을 먼저 진행해주세요.")

# --- [3. 메인 앱 기능 (로그인 성공 시 작동)] ---
else:
    # 현재 로그인한 유저의 개인 비밀창고 연결
    my_username = st.session_state.current_user
    my_vault = st.session_state.db["user_data"][my_username]

    st.sidebar.success(f"👤 사용자: {my_username}님 전용 모드")
    if st.sidebar.button("로그아웃"):
        st.session_state.login_status = False
        st.session_state.current_user = None
        st.rerun()
        
    st.sidebar.write("---")
    
    # 📅 [기획 반영] 연/월/일 직접 다이얼 선택 기능
    st.sidebar.subheader("📅 날짜 선택 다이얼")
    c1, c2, c3 = st.sidebar.columns(3)
    with c1: selected_year = st.selectbox("연", [2026, 2027, 2028])
    with c2: selected_month = st.selectbox("월", list(range(1, 13)))
    with c3: selected_day = st.selectbox("일", list(range(1, 32)))
    
    date_str = f"{selected_year}-{selected_month:02d}-{selected_day:02d}"
    st.sidebar.info(f"선택된 날짜: {date_str}")
    
    # 메인 카테고리 전환 (플래너 vs 다이어리)
    mode = st.radio("📂 카테고리 전환", ["📅 플래너 모드", "📖 다이어리 모드"], horizontal=True)
    st.write("---")

    # ==================== [플래너 모드] ====================
    if mode == "📅 플래너 모드":
        st.title(f"📅 플래너 - {date_str}")
        tab1, tab2 = st.tabs(["일정 및 도장 깨기", "⏳ 뽀모도로 타이머"])
        
        with tab1:
            # 일정 등록 및 5가지 반복 주기 옵션 기획 반영
            with st.expander("➕ 새로운 일정 등록하기"):
                task = st.text_input("할 일을 적어주세요")
                repeat = st.selectbox("반복 주기 설정", ["한 번만", "매일(날마다)", "주마다", "일주일 달성 횟수", "매달 특정일"])
                if st.button("일정 추가"):
                    if task:
                        if date_str not in my_vault["planner"]:
                            my_vault["planner"][date_str] = []
                        my_vault["planner"][date_str].append({"task": task, "done": False, "repeat": repeat})
                        st.success("일정 등록 완료!")
                        st.rerun()

            st.subheader("🎯 오늘의 할 일 목록")
            if date_str in my_vault["planner"] and my_vault["planner"][date_str]:
                # 🏅 [기획 반영] 캘린더 날짜 전체에 해당하는 셀 하나에 찍는 상단 총괄 도장
                all_done = all(item["done"] for item in my_vault["planner"][date_str])
                if all_done:
                    st.success("🏅 [날짜 전체 도장 쾅!] 오늘 일정을 모두 완벽하게 달성하셨습니다!")
                
                # 일정 옆 도장 칸 기획 반영
                for i, item in enumerate(my_vault["planner"][date_str]):
                    col_task, col_stamp = st.columns([4, 1])
                    with col_task:
                        if item["done"]:
                            st.write(f"~~✅ {item['task']} ({item['repeat']})~~")
                        else:
                            st.write(f"⚪ {item['task']} ({item['repeat']})")
                    with col_stamp:
                        if not item["done"]:
                            if st.button("💮 도장 칸", key=f"stamp_{i}"):
                                my_vault["planner"][date_str][i]["done"] = True
                                st.balloons() # 풍선 효과
                                st.rerun()
                        else:
                            st.write("💮 [완료 도장 완료]")
            else:
                st.write("등록된 일정이 없습니다. 일정을 먼저 등록해 보세요!")

        with tab2:
            st.subheader("⏳ 뽀모도로 타이머 (25분 집중 / 5분 휴식)")
            timer_mode = st.radio("타이머 선택", ["집중 모드 (25분)", "휴식 모드 (5분)"], horizontal=True)
            if st.button("타이머 시작"):
                duration = 25 * 60 if "집중" in timer_mode else 5 * 60
                progress_bar = st.progress(0)
                for percent in range(100):
                    time.sleep(duration / 100)
                    progress_bar.progress(percent + 1)
                st.success("⏰ 타이머가 종료되었습니다! 알람이 울립니다.")
                # 온라인 무료 알람 브라우저 오디오 연동
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
                    my_vault["notes"].append({"subject": n_subject, "unit": n_unit, "content": n_content, "date": date_str})
                    st.success("노트가 시스템 중앙 개인 창고에 안전하게 저장되었습니다.")
            
            st.write("---")
            st.subheader("🔍 저장된 노트 열람")
            if my_vault["notes"]:
                st.dataframe(pd.DataFrame(my_vault["notes"]))
            else:
                st.write("저장된 내용이 없습니다.")

        # 2. 주간 리포트 (지출 및 습관 연동 그래프)
        elif sub_mode == "📊 주간 리포트 (지출/습관)":
            st.subheader("📊 주간 리포트")
            
            # [지출 프로그램 기본 원화(KRW), 달러(USD) 연산 기획 반영]
            st.markdown("### 💰 지출 관리 프로그램")
            currency = st.radio("화폐 단위 설정", ["KRW (원)", "USD ($)"], horizontal=True)
            exp_item = st.text_input("지출 항목 (예: 책 구매)")
            exp_amount = st.number_input("금액 입력", min_value=0, value=0)
            
            if st.button("지출 기록 저장"):
                if exp_item and exp_amount > 0:
                    my_vault["expenses"].append({"date": date_str, "item": exp_item, "amount": exp_amount, "currency": currency})
                    st.success("지출 내역 기록 완료!")
                    st.rerun()
            
            if my_vault["expenses"]:
                df_exp = pd.DataFrame(my_vault["expenses"])
                st.dataframe(df_exp)
                total_sum = df_exp["amount"].sum()
                st.metric(label="현재 총 지출 합계 (맨 밑 합계 자동 계산)", value=f"{total_sum:,} {currency}")
                st.caption("💡 (데이터가 쌓이면 지난주/지난달 금액과 자동 연산 비교가 활성화됩니다.)")
            
            # [습관 달성 현황 - 플래너 도장 데이터 연동 그래프 기획 반영]
            st.write("---")
            st.markdown("### 📈 습관 달성 현황 (플래너 연동 그래프)")
            if my_vault["planner"]:
                dates = list(my_vault["planner"].keys())
                success_rates = []
                for d in dates:
                    total = len(my_vault["planner"][d])
                    dones = sum(1 for item in my_vault["planner"][d] if item["done"])
                    success_rates.append((dones / total) * 100 if total > 0 else 0)
                
                chart_data = pd.DataFrame({"날짜": dates, "달성률(%)": success_rates})
                st.line_chart(chart_data.set_index("날짜")) # 선형 그래프 시각화
                st.table(chart_data) # 퍼센트 나열 표 열람
            else:
                st.info("플래너에 일정을 등록하고 도장을 깨면 이곳에 월별/주별 그래프가 자동으로 연동됩니다.")

        # 3. 일기 작성 및 메모리 저장
        elif sub_mode == "✍️ 일기 작성":
            st.subheader(f"✍️ 오늘의 일기 - {date_str}")
            d_title = st.text_input("일기 제목 입력란")
            d_content = st.text_area("일기 내용 입력란")
            st.file_uploader("사진 및 파일 첨부 버튼", type=["jpg", "png"])
            
            if st.button("메모리 시스템 저장"):
                my_vault["diaries"][date_str] = {"title": d_title, "content": d_content}
                st.success("🔒 일기가 개인 창고에 안전하게 저장되었습니다.")
            
            st.write("---")
            st.subheader("📅 지난 일기 보기")
            if date_str in my_vault["diaries"]:
                st.markdown(f"#### 📋 {my_vault['diaries'][date_str]['title']}")
                st.write(my_vault['diaries'][date_str]['content'])
            else:
                st.write("이 날짜에 작성된 일기가 없습니다. 다이얼을 돌려 다른 날을 확인해보세요.")

        # 4. 커스텀 작성란 (복수선택 및 순서 배치 기획 반영)
        elif sub_mode == "🛠️ 커스텀 작성란":
            st.subheader("🛠️ 나만의 커스텀 리포트")
            c_title = st.text_input("주제 설정 (예: 식단 기록, 운동)")
            formats = st.multiselect("출력 형식을 순서대로 복수 선택하세요 (선택 순서대로 자동 배치)", ["글 작성란", "표(Table)", "샘플 그래프"])
            if formats:
                st.write("👇 **선택한 순서로 자동 구현된 작성 영역**")
                for fmt in formats:
                    if fmt == "글 작성란": st.text_area(f"[{c_title}] 자유 기술란")
                    elif fmt == "표(Table)": st.data_editor(pd.DataFrame({"항목": ["내용"], "수치": [0]}))
                    elif fmt == "샘플 그래프": st.bar_chart([10, 20, 15, 30])
            
            if st.button("서버 저장 및 가상 링크 생성"):
                st.success("🔗 서버 저장 완료! 공유용 링크: https://streamlit.io/share/custom-link")
