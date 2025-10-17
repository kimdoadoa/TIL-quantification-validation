import streamlit as st
import pandas as pd
import os
from glob import glob
from natsort import natsorted

# --- 1. 설정 (Configuration) ---
IMAGE_DIR = './images'
OUTPUT_CSV_PATH = './tils_validation_results.csv'

# --- 2. 데이터 로딩 및 준비 ---
def load_image_pairs(directory):
    """지정된 디렉토리에서 HE와 IHC 이미지 쌍의 경로 리스트를 반환합니다."""
    he_paths = natsorted(glob(os.path.join(directory, 'HE_*.png')))
    ihc_paths = natsorted(glob(os.path.join(directory, 'IHC_*.png')))
    if not he_paths or len(he_paths) != len(ihc_paths):
        st.error(f"이미지 폴더('{directory}')에 HE-IHC 쌍이 올바르게 구성되지 않았습니다. 확인해주세요.")
        return []
    return list(zip(he_paths, ihc_paths))

# --- 3. 세션 상태 초기화 ---
if 'image_pairs' not in st.session_state:
    st.session_state.image_pairs = load_image_pairs(IMAGE_DIR)

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

if 'results' not in st.session_state:
    st.session_state.results = []

# --- 4. 메인 UI 구성 ---
# 페이지 레이아웃을 'wide'로 설정하여 넓게 표시합니다.
st.set_page_config(layout="wide")
st.title("🔬 TILs Quantification Validation Study")

# 모든 평가가 끝났는지 확인
if not st.session_state.image_pairs:
    st.warning("이미지를 찾을 수 없습니다. IMAGE_DIR 경로를 확인해주세요.")
elif st.session_state.current_index >= len(st.session_state.image_pairs):
    st.success("🎉 모든 평가가 완료되었습니다. 수고하셨습니다!")
    st.info("아래 버튼을 눌러 결과 파일을 다운로드하세요.")
    
    final_df = pd.DataFrame(st.session_state.results)
    st.dataframe(final_df)
    
    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="tils_validation_results.csv",
        mime="text/csv",
    )
else:
    # 진행 상황 표시 (사이드바로 이동하여 UI를 깔끔하게 정리)
    total_images = len(st.session_state.image_pairs)
    current_image_num = st.session_state.current_index + 1
    
    st.sidebar.title("Validation Progress")
    st.sidebar.write(f"**Image Pair: {current_image_num} / {total_images}**")
    st.sidebar.progress(current_image_num / total_images)
    st.sidebar.markdown("---")


    he_path, ihc_path = st.session_state.image_pairs[st.session_state.current_index]

    # 화면을 두 개의 컬럼으로 분할
    col1, col2 = st.columns(2)

    with col1:
        st.header("H&E Image")
        # use_container_width=True를 사용하여 이미지가 컬럼 너비에 맞게 채워집니다.
        st.image(he_path, use_container_width=True)

    with col2:
        st.header("IHC Image")
        # use_container_width=True를 사용하여 이미지가 컬럼 너비에 맞게 채워집니다.
        st.image(ihc_path, use_container_width=True)

    # TIL 개수 입력 받기
    st.markdown("<br>", unsafe_allow_html=True)
    til_count = st.number_input(
        "Visually counted TILs:",
        min_value=0,
        step=1,
        key=f"til_input_{st.session_state.current_index}"
    )

    # 저장 및 다음 버튼 (너비를 채우도록 설정)
    if st.button("Save and Next Image", key="next_button", use_container_width=True):
        st.session_state.results.append({
            'he_image': os.path.basename(he_path),
            'ihc_image': os.path.basename(ihc_path),
            'til_count': til_count
        })
        
        # 매번 저장하는 대신 마지막에 한 번만 다운로드하도록 할 수 있습니다.
        # 만약 중간 과정 저장이 꼭 필요하다면 이 코드를 유지하세요.
        # pd.DataFrame(st.session_state.results).to_csv(OUTPUT_CSV_PATH, index=False)

        st.session_state.current_index += 1
        
        st.rerun()
