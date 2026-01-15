import re
import os
import shutil
import sys
from html.parser import HTMLParser
from urllib.parse import unquote

class HTMLToMarkdownConverter(HTMLParser):
    def __init__(self, source_dir, dest_resources_dir):
        super().__init__()
        self.markdown = []
        self.current_tag = []
        self.list_stack = []
        self.in_pre = False
        self.in_code = False
        self.link_url = None
        self.image_urls = []
        self.skip_content = False
        self.suppress_link_closing = False
        
        self.source_dir = source_dir # HTML 파일이 있는 원본 폴더 (이미지 찾을 때 사용)
        self.dest_resources_dir = dest_resources_dir # 이미지가 복사될 타겟 폴더

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag in ['script', 'style', 'nav', 'header', 'footer']:
            self.skip_content = True
            return

        if tag == 'h1':
            self.markdown.append('\n# ')
            self.current_tag.append('h1')
        elif tag == 'h2':
            self.markdown.append('\n## ')
            self.current_tag.append('h2')
        elif tag == 'h3':
            self.markdown.append('\n### ')
            self.current_tag.append('h3')
        elif tag == 'h4':
            self.markdown.append('\n#### ')
            self.current_tag.append('h4')
        elif tag == 'h5':
            self.markdown.append('\n##### ')
            self.current_tag.append('h5')
        elif tag == 'h6':
            self.markdown.append('\n###### ')
            self.current_tag.append('h6')
        elif tag == 'p':
            self.markdown.append('\n\n')
            self.current_tag.append('p')
        elif tag == 'br':
            self.markdown.append('  \n')
        elif tag == 'strong' or tag == 'b':
            self.markdown.append('**')
            self.current_tag.append('strong')
        elif tag == 'em' or tag == 'i':
            self.markdown.append('*')
            self.current_tag.append('em')
        elif tag == 'code':
            if not self.in_pre:
                self.markdown.append('`')
                self.in_code = True
            self.current_tag.append('code')
        elif tag == 'pre':
            self.markdown.append('\n```\n')
            self.in_pre = True
            self.current_tag.append('pre')
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            self.link_url = href
            self.markdown.append('[')
            self.current_tag.append('a')
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            
            # Skip emoticons, avatars, icons
            if any(x in str(attrs) for x in ['emoticon', 'avatar', 'gravatar', 'icon', 'channel-icon']):
                return
            
            # Check if this image is inside an 'a' tag
            if self.current_tag and self.current_tag[-1] == 'a':
                if self.markdown and self.markdown[-1] == '[':
                    self.markdown.pop() # Remove the opening '['
                    self.suppress_link_closing = True

            if src:
                # 이미지 처리 로직
                # 1. 웹 이미지인지 로컬 이미지인지 확인
                if src.startswith(('http:', 'https:', 'data:', '//')):
                    # 웹 이미지는 그대로
                    self.image_urls.append(src)
                    self.markdown.append(f'\n![{alt}]({src})\n')
                else:
                    # 로컬 이미지 처리
                    # src는 보통 "./AAA_files/image.png" 형태
                    # URL 디코딩
                    src = unquote(src)
                    src_clean = src.replace('\\', '/')
                    
                    # 원본 파일 찾기
                    # HTML 파일 기준 상대 경로로 찾음
                    abs_src_path = os.path.normpath(os.path.join(self.source_dir, src_clean))
                    
                    if os.path.exists(abs_src_path):
                        filename = os.path.basename(abs_src_path)
                        dest_path = os.path.join(self.dest_resources_dir, filename)
                        
                        try:
                            shutil.copy2(abs_src_path, dest_path)
                            # 마크다운에는 Resources/filename.png 로 기록
                            self.markdown.append(f'\n![{alt}](Resources/{filename})\n')
                            self.image_urls.append(filename)
                        except Exception as e:
                            print(f"Error copying image {abs_src_path}: {e}")
                            # 실패 시 원본 경로 유지
                            self.markdown.append(f'\n![{alt}]({src})\n')
                    else:
                        print(f"Warning: Image source not found: {abs_src_path}")
                        self.markdown.append(f'\n![{alt}]({src})\n')

        elif tag == 'video':
            src = attrs_dict.get('src', '')
            if src:
                self.image_urls.append(src)
                self.markdown.append(f'\n![video]({src})\n')
            self.current_tag.append('video')
        elif tag == 'source' and self.current_tag and self.current_tag[-1] == 'video':
            src = attrs_dict.get('src', '')
            if src and not any(src in url for url in self.image_urls):
                self.image_urls.append(src)
                self.markdown.append(f'\n![video]({src})\n')
        elif tag == 'ul':
            self.list_stack.append('ul')
            self.markdown.append('\n')
        elif tag == 'ol':
            self.list_stack.append('ol')
            self.markdown.append('\n')
        elif tag == 'li':
            indent = '  ' * (len(self.list_stack) - 1)
            if self.list_stack and self.list_stack[-1] == 'ul':
                self.markdown.append(f'{indent}- ')
            elif self.list_stack and self.list_stack[-1] == 'ol':
                self.markdown.append(f'{indent}1. ')
            self.current_tag.append('li')
        elif tag == 'blockquote':
            self.markdown.append('\n> ')
            self.current_tag.append('blockquote')
        elif tag == 'hr':
            self.markdown.append('\n---\n')

    def handle_endtag(self, tag):
        if tag in ['script', 'style', 'nav', 'header', 'footer']:
            self.skip_content = False
            return

        if self.current_tag and self.current_tag[-1] == tag:
            self.current_tag.pop()

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.markdown.append('\n')
        elif tag == 'p':
            pass
        elif tag == 'strong' or tag == 'b':
            self.markdown.append('**')
        elif tag == 'em' or tag == 'i':
            self.markdown.append('*')
        elif tag == 'code':
            if not self.in_pre:
                self.markdown.append('`')
                self.in_code = False
        elif tag == 'pre':
            self.markdown.append('\n```\n')
            self.in_pre = False
        elif tag == 'a':
            if self.suppress_link_closing:
                self.suppress_link_closing = False
                self.link_url = None
            elif self.link_url:
                self.markdown.append(f']({self.link_url})')
                self.link_url = None
        elif tag == 'ul' or tag == 'ol':
            if self.list_stack:
                self.list_stack.pop()
            self.markdown.append('\n')
        elif tag == 'li':
            self.markdown.append('\n')
        elif tag == 'blockquote':
            self.markdown.append('\n')
        elif tag == 'video':
            pass  # Video content handled in starttag

    def handle_data(self, data):
        if self.skip_content:
            return
        if data.strip():
            # Clean up excessive whitespace
            cleaned = ' '.join(data.split())
            if self.in_pre or self.in_code:
                self.markdown.append(data)
            else:
                self.markdown.append(cleaned)

    def get_markdown(self):
        result = ''.join(self.markdown)
        # Clean up excessive newlines
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()

def convert_html_to_markdown(html_file):
    # 경로 설정
    html_file_abs = os.path.abspath(html_file)
    source_dir = os.path.dirname(html_file_abs)
    filename_no_ext = os.path.splitext(os.path.basename(html_file))[0]
    
    # 출력 디렉토리 설정: Web/Convert/파일명/
    output_base_dir = os.path.join("Web", "Convert", filename_no_ext)
    dest_resources_dir = os.path.join(output_base_dir, "Resources")
    
    if not os.path.exists(dest_resources_dir):
        os.makedirs(dest_resources_dir)
        
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    title = title_match.group(1) if title_match else 'Untitled'

    # Extract article body
    body_match = re.search(r'<div[^>]*class=["\']article-body["\'][^>]*>(.*?)<div\s+class=["\'](?:vote-box|vote-area|comment-wrapper|article-action)',
                          html_content, re.DOTALL | re.IGNORECASE)
    if body_match:
        html_content = body_match.group(1)
    else:
        body_match2 = re.search(r'<div[^>]*class=["\']article-body["\'][^>]*>(.*)',
                               html_content, re.DOTALL | re.IGNORECASE)
        if body_match2:
            content = body_match2.group(1)
            content = re.split(r'<div[^>]*class=["\'](?:vote-box|vote-area|comment-wrapper|article-footer|article-action)', content)[0]
            html_content = content

    # Converter 초기화 시 source_dir과 dest_resources_dir 전달
    converter = HTMLToMarkdownConverter(source_dir, dest_resources_dir)
    converter.feed(html_content)

    markdown_content = converter.get_markdown()

    # Clean up title
    title_parts = title.split(' - ')
    if len(title_parts) > 1:
        title = title_parts[0].strip()

    final_markdown = f"# {title}\n\n{markdown_content}"
    
    # 마크다운 파일 저장 경로: Web/Convert/파일명/파일명.md
    output_md_file = os.path.join(output_base_dir, f"{filename_no_ext}.md")

    return final_markdown, converter.image_urls, output_md_file

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python arca_to_md.py <input.html>")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"Converting {input_file} ...")
    markdown, images, output_file = convert_html_to_markdown(input_file)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"Markdown saved to: {output_file}")
    print(f"Processed {len(images)} images")
