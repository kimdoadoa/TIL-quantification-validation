import streamlit as st
import pandas as pd
import os
from glob import glob
from natsort import natsorted

# --- 1. 설정 (Configuration) ---
# HE 이미지 파일만 찾도록 설정합니다.
IMAGE_DIR = './images'
OUTPUT_CSV_PATH = './tils_validation_results_he_only.csv'

# --- 2. 데이터 로딩 및 준비 ---
def load_he_images(directory):
    """지정된 디렉토리에서 HE 이미지 경로 리스트를 반환합니다."""
    # 'HE_'로 시작하고 '.png'로 끝나는 파일만 찾습니다.
    he_paths = natsorted(glob(os.path.join(directory, 'HE_*.png')))
    
    if not he_paths:
        st.error(f"이미지 폴더('{directory}')에서 HE 이미지 파일(예: HE_001.png)을 찾을 수 없습니다. 경로와 파일 이름을 확인해주세요.")
        return []
        
    return he_paths

# --- 3. 세션 상태 초기화 ---
if 'he_paths' not in st.session_state:
    st.session_state.he_paths = load_he_images(IMAGE_DIR)

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

if 'results' not in st.session_state:
    st.session_state.results = []

# --- 4. 메인 UI 구성 ---
# 페이지 레이아웃을 'wide'로 설정하여 넓게 표시합니다.
st.set_page_config(layout="wide")
st.title("🔬 TILs Quantification Validation Study (H&E Only)")

# 모든 평가가 끝났는지 확인
if not st.session_state.he_paths:
    st.warning("이미지를 찾을 수 없습니다. IMAGE_DIR 경로를 확인해주세요.")
elif st.session_state.current_index >= len(st.session_state.he_paths):
    st.success("🎉 모든 평가가 완료되었습니다. 수고하셨습니다!")
    st.info("아래 버튼을 눌러 결과 파일을 다운로드하세요.")
    
    final_df = pd.DataFrame(st.session_state.results)
    st.dataframe(final_df)
    
    # 결과를 CSV로 인코딩하여 다운로드 버튼에 연결
    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name=OUTPUT_CSV_PATH,
        mime="text/csv",
    )
else:
    # 진행 상황 표시 (사이드바로 이동하여 UI를 깔끔하게 정리)
    total_images = len(st.session_state.he_paths)
    current_image_num = st.session_state.current_index + 1
    
    st.sidebar.title("Validation Progress")
    st.sidebar.write(f"**Image: {current_image_num} / {total_images}**")
    st.sidebar.progress(current_image_num / total_images)
    st.sidebar.markdown("---")

    # 현재 이미지 경로 가져오기
    he_path = st.session_state.he_paths[st.session_state.current_index]

    st.header("H&E Image for TILs Quantification")
    
    # 이미지를 컬럼 너비에 맞게 표시합니다.
    st.image(he_path, use_container_width=True)

    # TIL 개수 입력 받기
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 입력 필드를 중앙에 배치하기 위해 컬럼 사용
    input_col, _, _ = st.columns([1, 1, 1])

    with input_col:
        til_count = st.number_input(
            "Visually counted TILs:",
            min_value=0,
            step=1,
            key=f"til_input_{st.session_state.current_index}",
            help="H&E 이미지에서 육안으로 확인한 TILs(종양침윤림프구)의 개수를 입력해주세요."
        )

    # 저장 및 다음 버튼 (너비를 채우도록 설정)
    if st.button("Save and Next Image", key="next_button", use_container_width=True):
        st.session_state.results.append({
            'image_file': os.path.basename(he_path),
            'til_count': til_count
        })
        
        st.session_state.current_index += 1
        
        # Streamlit 앱을 다시 실행하여 다음 이미지를 표시합니다.
        st.rerun()
