import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(layout="wide")
st.title('📊 따릉이')

# CSV 파일이 저장된 디렉토리
output_dir = 'analysis_results_csv'

# 📁 저장된 데이터 불러오기 함수
@st.cache_data
def load_saved_data():
    # 저장된 CSV 파일들을 불러옵니다.
    data_frames = {}
    csv_files = {
        'gender_avg': 'gender_avg_usage_time.csv',
        'usertype_avg': 'usertype_avg_usage_time.csv',
        'combined_avg': 'combined_gender_usertype_avg_usage_time.csv',
        'avg_by_day': 'avg_by_day_usage.csv',
        'rain_grouped': 'rain_vs_clear_avg_usage.csv',
        'hourly': 'hourly_rentals.csv'
    }

    for key, filename in csv_files.items():
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            try:
                # 'Unnamed: 0' 컬럼이 생성될 수 있으므로, index_col=0 지정 또는 제거
                df = pd.read_csv(file_path, encoding='utf-8-sig', index_col=0 if key in ['gender_avg', 'usertype_avg'] else None)
                data_frames[key] = df
            except Exception as e:
                st.error(f"'{filename}' 파일을 불러오는 데 실패했습니다: {e}")
                return None
        else:
            st.error(f"필수 분석 결과 파일이 없습니다: '{filename}'")
            st.warning("먼저 이전 코드를 실행하여 CSV 파일들을 생성해야 합니다.")
            return None
            
    return data_frames

# 데이터 로딩
saved_data = load_saved_data()

if saved_data is None:
    st.stop()

# ---
# ## 📊 분석 및 시각화

# ---
# ===== [성별 + 이용자 종류 조합 분석] =====
st.subheader('👫 성별 및 이용자종류 조합에 따른 평균 이용시간')

if 'combined_avg' in saved_data:
    fig_combined = px.bar(saved_data['combined_avg'],
                          x='성별_이용자종류',
                          y='이용시간(분)',
                          title="성별 및 이용자 종류 조합별 평균 이용시간",
                          labels={"이용시간(분)": "평균 이용시간 (분)", "성별_이용자종류": "유형"},
                          text_auto='.2s'
                         )
    st.plotly_chart(fig_combined, use_container_width=True)
else:
    st.info("성별 및 이용자 종류 조합 데이터를 불러올 수 없습니다.")


# ---
# ===== [요일별 이용 패턴 분석] =====
st.subheader("📅 요일별 평균 이용시간/이용거리")

if 'avg_by_day' in saved_data:
    fig = px.bar(saved_data['avg_by_day'], x='요일', y=['이용시간(분)', '이용거리(M)'],
                 barmode='group', text_auto='.2s',
                 labels={"value": "평균", "variable": "항목"},
                 title="요일별 평균 이용시간 & 거리")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("요일별 이용 패턴 데이터를 불러올 수 없습니다.")

# ---
# ===== [비 여부에 따른 이용량 분석] =====
st.subheader("☔ 비 오는 날 vs 안 오는 날 평균 이용량")

if 'rain_grouped' in saved_data:
    rain_grouped_df = saved_data['rain_grouped']
    
    col_pie1, col_pie2 = st.columns(2)

    with col_pie1:
        st.markdown("#### 평균 이용시간 (분)")
        fig_time_pie = px.pie(rain_grouped_df,
                              names='비 여부',
                              values='이용시간(분)',
                              title='비 여부에 따른 평균 이용시간',
                              hole=.3,
                              # textinfo='value', # <-- 이 줄을 제거했습니다.
                              hover_data=['이용시간(분)'],
                             )
        # update_traces에서 textinfo와 texttemplate를 설정합니다.
        fig_time_pie.update_traces(textinfo='value', # <-- 여기에 textinfo를 설정
                                  texttemplate='%{value:.0f}분',
                                  hovertemplate='<b>%{label}</b><br>평균 이용시간: %{value:.0f}분<br>비율: %{percent}<extra></extra>')
        st.plotly_chart(fig_time_pie, use_container_width=True)

    with col_pie2:
        st.markdown("#### 평균 이용거리 (M)")
        fig_distance_pie = px.pie(rain_grouped_df,
                                  names='비 여부',
                                  values='이용거리(M)',
                                  title='비 여부에 따른 평균 이용거리',
                                  hole=.3,
                                  # textinfo='value', # <-- 이 줄을 제거했습니다.
                                  hover_data=['이용거리(M)'],
                                 )
        # update_traces에서 textinfo와 texttemplate를 설정합니다.
        fig_distance_pie.update_traces(textinfo='value', # <-- 여기에 textinfo를 설정
                                      texttemplate='%{value:.0f}M',
                                      hovertemplate='<b>%{label}</b><br>평균 이용거리: %{value:.0f}M<br>비율: %{percent}<extra></extra>')
        st.plotly_chart(fig_distance_pie, use_container_width=True)
else:
    st.info("비 여부에 따른 이용량 데이터를 불러올 수 없습니다.")

# ---
# ===== [시간대별 이용량 분석] =====
st.subheader("⏳ 시간대별 대여 수 (혼잡 시간대)")

if 'hourly' in saved_data:
    fig3 = px.line(saved_data['hourly'], x='시간대', y='대여수', markers=True,
                   title="시간대별 대여량", labels={"대여수": "대여 횟수"})
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("시간대별 대여 수 데이터를 불러올 수 없습니다.")