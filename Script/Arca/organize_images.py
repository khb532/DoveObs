import os
import re
import shutil
import sys
from urllib.parse import unquote

# 윈도우 한글 출력 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def organize_images(md_file_path):
    print(f"--- Organizing: {md_file_path} ---")
    
    # 1. 경로 파악
    md_file_abspath = os.path.abspath(md_file_path)
    md_dir = os.path.dirname(md_file_abspath)
    md_filename = os.path.basename(md_file_abspath)
    doc_name = os.path.splitext(md_filename)[0]
    
    # 2. 폴더 구조
    base_done_dir = os.path.abspath(os.path.join("Web", "Done"))
    doc_done_dir = os.path.join(base_done_dir, doc_name)
    dest_resources_dir = os.path.join(doc_done_dir, "Resources")
    
    if not os.path.exists(dest_resources_dir):
        os.makedirs(dest_resources_dir)

    dest_md_path = os.path.join(doc_done_dir, md_filename)

    # 3. 마크다운 읽기
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 4. 이미지 정리 로직 (백슬래시 최소화 시도)
    # 정규식 패턴을 조립해서 시스템의 자동 변조를 피함
    pattern_str = r"!\[(.*?)\]\((.*?)\)"
    img_pattern = re.compile(pattern_str)
    
    new_images_count = 0
    
    def replace_callback(match):
        nonlocal new_images_count
        alt_text = match.group(1)
        original_link_path = match.group(2).strip()
        
        # 로컬 경로(Resources/로 시작)만 처리
        decoded_path = unquote(original_link_path)
        clean_path = decoded_path.replace('\\', '/')
        
        if "resources/" not in clean_path.lower():
            return match.group(0)
            
        abs_src_path = os.path.normpath(os.path.join(md_dir, clean_path))
        
        if os.path.exists(abs_src_path):
            _, ext = os.path.splitext(abs_src_path)
            new_filename = f"{doc_name}_{new_images_count + 1:02d}{ext if ext else '.png'}"
            abs_dest_path = os.path.join(dest_resources_dir, new_filename)
            
            try:
                shutil.copy2(abs_src_path, abs_dest_path)
                new_images_count += 1
                return f'![{alt_text}](Resources/{new_filename})'
            except Exception:
                return match.group(0)
        return match.group(0)

    # 변환 및 저장
    new_content = img_pattern.sub(replace_callback, content)
    with open(dest_md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Organized: {dest_md_path} ({new_images_count} images)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        organize_images(sys.argv[1])