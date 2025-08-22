import streamlit as st
import pandas as pd
import os
import json
import math

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="법령 및 행정규칙 조회 시스템",
    layout="wide"
)

st.title("법령 및 행정규칙 데이터 조회")

# --- 데이터 로딩 함수들 ---

@st.cache_data
def load_and_process_json(file_path):
    """일반 JSON 파일을 불러옵니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'articles' in data and isinstance(data['articles'], list):
            return data['articles']
        elif isinstance(data, list):
            return data
        else:
            st.info("선택한 파일은 테이블 형태로 표시할 수 있는 데이터가 아니므로 원본 JSON을 표시합니다.")
            st.json(data)
            return None # 테이블 표시 안함
            
    except Exception as e:
        st.error(f"'{os.path.basename(file_path)}' 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

@st.cache_data
def load_and_process_jsonl(file_path):
    """JSONL 파일을 불러와서 리스트로 변환합니다."""
    data_list = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip(): # 비어있는 줄은 무시
                    data_list.append(json.loads(line))
        return data_list
    except Exception as e:
        st.error(f"'{os.path.basename(file_path)}' 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

# --- 사이드바 UI 구성 ---
st.sidebar.header("조회 옵션")

data_type = st.sidebar.selectbox(
    "1. 데이터 종류를 선택하세요.",
    ("마켓컬리 이용약관 & FAQ", "상담사 파인튜닝 데이터"),
    key="data_type_selector"
)

# 마켓컬리 데이터, 상담사 파인튜닝 데이터 -> 폴더 이름, 이 폴더 안에 있는 json. jsonl 파일 불러와서 선택하도록 함
folder_map = { 
    "마켓컬리 이용약관 & FAQ": "data/마켓컬리 데이터",
    "상담사 파인튜닝 데이터": "data/상담사 파인튜닝 데이터"
}
selected_folder_path = folder_map[data_type]

file_list = []
if os.path.isdir(selected_folder_path):
    file_list = sorted([
        f for f in os.listdir(selected_folder_path) 
        if f.endswith(('.json', '.jsonl'))
    ])
else:
    st.sidebar.error(f"경로를 찾을 수 없습니다: '{selected_folder_path}'\n'data' 폴더 구조를 확인해주세요.")

selected_file = st.sidebar.selectbox(
    "2. 조회할 파일을 선택하세요.",
    file_list,
    index=None,
    placeholder="파일을 선택해주세요..."
)

# --- 메인 화면 UI 구성 ---
if selected_file:
    file_path = os.path.join(selected_folder_path, selected_file)
    table_data = None
    
    if selected_file.endswith('.jsonl'):
        table_data = load_and_process_jsonl(file_path)
    elif selected_file.endswith('.json'):
        table_data = load_and_process_json(file_path)

    if table_data is not None:
        df = pd.DataFrame(table_data)
        st.header(f"'{selected_file}' 파일 내용")

        items_per_page = 20
        total_items = len(df)
        total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1

        st.sidebar.subheader("페이지 이동")
        page_number = st.sidebar.number_input(
            f"페이지 (1 ~ {total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
            key=f"page_picker_{selected_file}"
        )

        start_index = (page_number - 1) * items_per_page
        end_index = start_index + items_per_page
        df_to_show = df.iloc[start_index:end_index]
        
        st.write(f"총 **{total_items}**개 항목 중 **{start_index + 1}** - **{min(end_index, total_items)}**번째 항목을 표시합니다.")
        st.dataframe(df_to_show, height=600, use_container_width=True)

else:
    st.info("왼쪽 사이드바에서 조회할 데이터 종류와 파일을 선택해주세요.")