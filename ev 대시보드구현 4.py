import streamlit as st
import pandas as pd

#col2, col3 = st.columns([7, 3])
# 엑셀파일
d=pd.read_excel('C:/Users/JoEunSeo/OneDrive - inha.edu/바탕 화면/QAQC데이터분석/스트림릿 폴더/page/Overview.xlsx')

# xlsx 파일 결측값 제거
d=pd.read_excel("C:/Users/JoEunSeo/OneDrive - inha.edu/바탕 화면/QAQC데이터분석/스트림릿 폴더/page/Overview.xlsx")
d=d.drop(columns=["Unnamed: 13"], errors="ignore")
d=d.drop(index=[32, 33], errors="ignore")

#파일 불러오기
dfAA = pd.read_csv('C:/Users/JoEunSeo/OneDrive - inha.edu/바탕 화면/QAQC데이터분석/스트림릿 폴더/page/dfAA.csv')
dfBB = pd.read_csv('C:/Users/JoEunSeo/OneDrive - inha.edu/바탕 화면/QAQC데이터분석/스트림릿 폴더/page/dfBB.csv')


# 전력 소모 컬럼 추가
dfAA['HVAC Power Consumption'] = dfAA['Heating Power CAN [kW]']+dfAA['AirCon Power [kW]']
dfBB['HVAC Power Consumption'] = dfBB['Heating Power CAN [kW]']+dfBB['AirCon Power [kW]']
import plotly.graph_objects as go
import plotly.express as px




# **사이드바에서 Trip 선택**
with st.sidebar:
    st.header("📌 Trip 선택")

    # ✅ 두 데이터프레임의 file_name을 합쳐서 유니크한 값 가져오기
    unique_trips = pd.concat([dfAA["file_name"], dfBB["file_name"]]).unique()

    # ✅ 사용자가 선택한 Trip 저장
    selected_trip = st.selectbox("Trip을 선택하세요:", unique_trips)

# ✅ 사용자가 선택한 Trip 데이터만 필터링
df_selected_A = dfAA[dfAA["file_name"] == selected_trip]
df_selected_B = dfBB[dfBB["file_name"] == selected_trip]
df_selected = pd.concat([df_selected_A, df_selected_B])

# **슬라이더 추가: 사용자가 원하는 Time [s] 구간 선택**
min_time, max_time = df_selected["Time [s]"].min(), df_selected["Time [s]"].max()

selected_time = st.slider(
    " 주행 시점을 선택하세요 (Time [s])",
    min_value=min_time, 
    max_value=max_time,
    value=min_time,
    step=0.1
)

# ✅ 사용자가 선택한 Time [s] 구간에 맞게 필터링
df_selected_time = df_selected[df_selected["Time [s]"] == selected_time]

# 🔹 상단 부분: 배터리 정보, 주행 가능 거리, 에너지 소비율 (가로 레이아웃)
with st.container():
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  # 각 열 크기 동일하게 설정

    with col1:
        with st.expander("🚗 주행 가능 거리", expanded=True):
            if "주행가능거리" in df_selected_time.columns:
                estimated_range = df_selected_time["주행가능거리"].iloc[0] if not df_selected_time.empty else 0
            else:
                estimated_range = 0  # 컬럼이 없는 경우 처리
            
            # 주행 가능 거리 계산
            range_color = (
                "#4CAF50" if estimated_range > 600 else  # 녹색 (600km 이상)
                "#FFC107" if estimated_range > 400 else  # 노란색 (400km)
                "#F44336"  # 빨간색 (400km 이하)
            )

            # 주행 가능 거리에는 기존 테두리 색상
            st.markdown(
                f"""
                <div style="height: 100px; display: flex; justify-content: center; align-items: center; 
                            font-size: 18px; background-color: {range_color}; color: white; border-radius: 10px; 
                            border: 2px solid #ddd; text-align: center;">
                    <strong>{estimated_range:.0f} km<strong>
                </div>
                """, 
                unsafe_allow_html=True
            )

    with col2:
        with st.expander("🔋 현재 배터리 용량", expanded=True):
            battery_percent = df_selected_time.iloc[0]["SoC [%]"] if not df_selected_time.empty else 0
            st.markdown(
                f"""
                <div style="height: 78px; display: flex; justify-content: center; align-items: center; 
                            font-size: 18px; border-radius: 10px; border: 2px solid white; text-align: center;">
                   <strong>{battery_percent} %<strong>
                </div>
                """, 
                unsafe_allow_html=True
            )

    with col3:
        with st.expander("⚡ 에너지 소비율", expanded=True):
            energy_consumption = df_selected_time["Energy Consumption (Wh/km)"].iloc[0] if not df_selected_time.empty else 0
            st.markdown(
                f"""
                <div style="height: 100px; display: flex; justify-content: center; align-items: center; 
                            font-size: 18px; border-radius: 10px; border: 2px solid white; text-align: center;">
                    <strong>{energy_consumption:.0f} Wh/km<strong>
                </div>
                """, 
                unsafe_allow_html=True
            )

    with col4:
        with st.expander("🌡️ HVAC로 소모되는 전력량", expanded=True):
            HVAC_Power_Consumption = df_selected_time["HVAC Power Consumption"].iloc[0] if not df_selected_time.empty else 0
            st.markdown(
                f"""
                <div style="height: 78px; display: flex; justify-content: center; align-items: center; 
                            font-size: 18px; border-radius: 10px; border: 2px solid white; text-align: center;">
                    <strong>{HVAC_Power_Consumption} W<strong>
                </div>
                """, 
                unsafe_allow_html=True
            )



# 🔹 중단 부분: 속도 상태와 배터리 전류 프로파일 (가로 2열 레이아웃)
with st.container():
        col1, col2 = st.columns(2)  # 가로 2열 레이아웃

        with col1:
            # ✅ 전체 데이터에서 회생제동 에너지 누적합 계산
            df_selected["회생제동으로 얻은 총 에너지"] = (
                    df_selected.apply(
                        lambda row: row["Battery Voltage [V]"] * row["Battery Current [A]"] * 0.1
                        if row["Battery Current [A]"] > 0 else 0, axis=1
                    ).cumsum()
                )
            # ✅ 선택한 시간까지의 누적된 회생 에너지 계산
            regen_energy = df_selected[df_selected["Time [s]"] <= selected_time]["회생제동으로 얻은 총 에너지"].max()

            # 왼쪽(col1)에 순서대로 위젯을 배치하면 세로로 쌓임
            with st.expander("♻️ 회생제동으로 얻은 총 에너지", expanded=True):
                st.markdown(
                f"<div style='text-align: center;'><strong>{regen_energy:.0f} Wh</strong></div>", 
                unsafe_allow_html=True
            )


            with st.expander("📉 실시간 속도 상태", expanded=True):
                velocity = df_selected_time.iloc[0]["Velocity [km/h]"] if not df_selected_time.empty else 0

            fig_velocity_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=velocity,
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "blue", "thickness": 0.2}
                },
                title={'text': "Speed (km/h)", 'font': {'size': 24,'weight': 'bold'}}                
            ))
            fig_velocity_gauge.update_layout(
                margin=dict(l=30, r=30, t=50, b=0),
                width=200,
                height=300
            )
            st.plotly_chart(fig_velocity_gauge, use_container_width=True)

        with col2:
            # 오른쪽(col2)에는 배터리 전류 프로파일 그래프 배치
            with st.expander("⚡ 배터리 전류 프로파일", expanded=True):
                fig_current = px.line(
                    df_selected, x="Time [s]", y="Battery Current [A]", 
                    labels={"Time [s]": "시간 (s)", "Battery Current [A]": "배터리 전류 (A)"},
                    title="배터리 전류 변화 그래프",
                    height=300
                )
                st.plotly_chart(fig_current, use_container_width=True)
                # ✅ 전체 데이터에서 회생제동 에너지 누적합 계산
                df_selected["회생제동으로 얻은 총 에너지"] = (
                    df_selected.apply(
                        lambda row: row["Battery Voltage [V]"] * row["Battery Current [A]"] * 0.1
                        if row["Battery Current [A]"] > 0 else 0, axis=1
                    ).cumsum()
                )
                # ✅ 선택한 시간까지의 누적된 회생 에너지 계산
                regen_energy = df_selected[df_selected["Time [s]"] <= selected_time]["회생제동으로 얻은 총 에너지"].max()





# selected_trip이 "A1" ~ "A9"라면 "A01" ~ "A09"로 변경
if selected_trip[1].isdigit() and int(selected_trip[1:]) < 10:
    selected_trip = f"A0{selected_trip[1:]}"  # "A1" -> "A01", "A9" -> "A09"

# d["Trip"]에서 "Trip" 뒤의 숫자 부분만 추출
d["Trip_Number"] = d["Trip"].str.extract(r"TripA(\d+)")
d["Trip_Number"] = "A" + d["Trip_Number"].astype(str).str.zfill(2)  # "1" -> "A01"

# 선택한 Trip에 해당하는 데이터 필터링
selected_data = d[d["Trip_Number"] == selected_trip]

# **주행 환경 정보 박스 크기 및 글씨 크기 줄이기**
st.markdown(
    """
    <div style="padding: 10px; border-radius: 10px; border: 3px solid #2196F3; 
        text-align: center; font-size: 14px; font-weight: bold; 
        background-color: #f1f8ff; color: #333; padding: 8px;">
        🌦 **주행 환경 정보**
    </div>
    """,
    unsafe_allow_html=True
)

# ✅ 네모 박스 내부에 3열 레이아웃 추가
col_date, col_weather, col_temp = st.columns(3)


import pandas as pd

# 📅 첫 번째 열 (선택한 Trip의 날짜 + 시간)
with col_date:
    with st.expander("📅 현재 시각", expanded=True):
        # 언더스코어를 공백으로 변경 후, datetime 형식으로 변환
        selected_data["Date"] = pd.to_datetime(selected_data["Date"].str.replace("_", " "), format="%Y-%m-%d %H-%M-%S")

        if not df_selected_time.empty:
            selected_seconds = df_selected_time["Time [s]"].iloc[0]  # 선택한 시점 (초)
        else:
            selected_seconds = 0  

        # 날짜에 초 단위 시간 추가
        selected_datetime = selected_data["Date"].iloc[0] + pd.to_timedelta(selected_seconds, unit="s")

        # 포맷 변경하여 출력
        formatted_datetime = selected_datetime.strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"**📌 {formatted_datetime}**")




# ⛅ 두 번째 열 (선택한 Trip의 날씨)
with col_weather:
    with st.expander("⛅ 날씨", expanded=True):
        selected_weather = selected_data["Weather"].values[0]
        st.markdown(f"**🌤 {selected_weather}**")

# 🌡 세 번째 열 (선택한 Trip과 선택한 시점의 외기 온도)
with col_temp:
    with st.expander("🌡 외기 온도", expanded=True):
        if not df_selected_time.empty:
            ambient_temp = df_selected_time["Ambient Temperature [°C]"].iloc[0]
        else:
            ambient_temp = "데이터 없음"

        st.markdown(f"**🌡 {ambient_temp}°C**")