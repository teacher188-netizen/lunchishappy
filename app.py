# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Firebase 관련 라이브러리
# 이 코드는 Streamlit 환경에서 secrets.toml 파일에 저장된 Firebase 설정을 읽어옵니다.
# secrets.toml 파일에 Firebase 설정 정보를 추가해야 합니다.
# [firebase]
# api_key = "..."
# auth_domain = "..."
# project_id = "..."
# storage_bucket = "..."
# messaging_sender_id = "..."
# app_id = "..."
# measurement_id = "..."

st.set_page_config(layout="wide")

# 1. 페이지 제목
st.markdown("<h1 style='text-align: center;'>🍽️ 맛있는 급식 투표소 🗳️</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>오늘의 급식 메뉴에 투표하고, 다음 급식 메뉴를 정하는 데 참여해 보세요!</h3>", unsafe_allow_html=True)
st.markdown("---")

# 데이터 로드
@st.cache_data
def load_data():
    if os.path.exists("meals_data.csv"):
        try:
            # UTF-8로 먼저 시도
            df = pd.read_csv("meals_data.csv")
        except UnicodeDecodeError:
            # 실패하면 cp949(euc-kr)로 재시도
            df = pd.read_csv("meals_data.csv", encoding='cp949')

        # '급식일자'를 datetime 형식으로 변환하여 인덱스로 설정
        df['급식일자'] = pd.to_datetime(df['급식일자'])
        df.set_index('급식일자', inplace=True)
        return df
    else:
        # 파일이 없을 경우 GitHub에서 직접 로드 (예시)
        # 이 경로는 Streamlit Spaces의 GitHub 연동 시 자동으로 처리됩니다.
        # 실제 사용 시에는 secrets.toml에 있는 파일 경로를 사용하거나, git 연동을 확인해주세요.
        st.error("`meals_data.csv` 파일을 찾을 수 없습니다. GitHub 저장소에 파일이 있는지 확인하거나, 로컬에서 실행하고 있는지 확인해주세요.")
        return pd.DataFrame()

df = load_data()

# 데이터가 성공적으로 로드되었는지 확인
if not df.empty:
    
    # 2. 칼로리 시각화
    st.header("📈 급식 칼로리 추이")
    
    # '급식일자' 인덱스를 리셋하여 Plotly에서 사용 가능하도록 함
    df_plot = df.reset_index()
    fig = px.line(
        df_plot,
        x='급식일자',
        y='칼로리정보(Kcal)',
        title='일별 급식 칼로리 변화',
        labels={'급식일자': '날짜', '칼로리정보(Kcal)': '칼로리 (Kcal)'}
    )
    fig.update_traces(line_color="#4CAF50", line_width=2)
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="칼로리 (Kcal)",
        title_font_size=20,
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

    # 3. 투표 폼
    st.header("🗳️ 메뉴 투표하기")
    
    # 투표할 메뉴 목록
    menu_list = df['요리명'].unique()
    
    # `st.session_state`를 사용하여 투표 데이터를 저장
    if 'vote_data' not in st.session_state:
        st.session_state.vote_data = {menu: 0 for menu in menu_list}

    # 투표 폼
    with st.form("vote_form"):
        st.write("마음에 드는 급식 메뉴에 투표해 주세요.")
        
        # 라디오 버튼으로 메뉴 선택
        selected_menu = st.radio(
            "메뉴를 선택하세요:",
            menu_list,
            index=0,
            key='menu_select'
        )
        
        # 제출 버튼
        submit_button = st.form_submit_button("투표하기")
        
        if submit_button:
            # 선택된 메뉴의 투표 수 증가
            st.session_state.vote_data[selected_menu] += 1
            st.success("투표가 완료되었습니다! 소중한 한 표 감사합니다.")

    st.markdown("---")

    # 4. 실시간 투표 현황 그래프
    st.header("📊 실시간 투표 현황")
    
    # 투표 데이터프레임 생성
    vote_df = pd.DataFrame(st.session_state.vote_data.items(), columns=['메뉴', '투표수'])
    vote_df = vote_df.sort_values(by='투표수', ascending=False)
    
    # 막대 그래프로 투표 현황 시각화
    fig_votes = px.bar(
        vote_df,
        x='메뉴',
        y='투표수',
        title='실시간 메뉴 투표 현황',
        labels={'메뉴': '급식 메뉴', '투표수': '투표 수'},
        color='투표수',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_votes.update_layout(
        xaxis_title="급식 메뉴",
        yaxis_title="투표 수",
        title_font_size=20
    )
    st.plotly_chart(fig_votes, use_container_width=True)

else:
    st.warning("데이터를 로드하는 데 실패했습니다. 파일 경로를 확인해주세요.")
