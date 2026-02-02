# 파일 포맷과 바이너리 기초

## 컴퓨터에서 파일이란

컴퓨터의 모든 파일은 바이트의 연속이다. 텍스트 파일, 이미지, 실행 파일, 동영상 등 어떤 종류든 궁극적으로는 0과 1로 이루어진 비트 시퀀스가 저장 매체에 기록된 것이다. 파일 자체에는 "이것은 이미지다", "이것은 문서다"라는 정보가 별도로 존재하지 않는다.

그렇다면 운영체제와 프로그램은 어떻게 파일의 종류를 구분할까? 두 가지 방식이 있다.

**확장자 기반 판별**: Windows는 파일 이름 끝의 확장자(`.txt`, `.jpg`, `.exe`)를 보고 어떤 프로그램으로 열지 결정한다. 하지만 확장자는 파일 이름의 일부일 뿐이므로 사용자가 자유롭게 변경할 수 있다. `photo.jpg`를 `photo.txt`로 바꿔도 파일 내용은 그대로다.

**파일 내용 기반 판별**: Unix/Linux의 `file` 명령어는 확장자를 무시하고 파일 내용의 처음 몇 바이트(매직 넘버)를 읽어 실제 포맷을 판별한다. 보안 소프트웨어도 이 방식을 사용하여 확장자 위조를 탐지한다.

파일 포맷이란 결국 "이 바이트 시퀀스를 어떤 규칙으로 해석할 것인가"에 대한 약속이다. 동일한 바이트열이라도 해석 규칙에 따라 텍스트가 될 수도, 이미지가 될 수도 있다. 포맷을 정의하는 쪽(파일 생성자)과 해석하는 쪽(파일 리더)이 같은 규칙을 공유해야만 데이터가 의미를 가진다.

---

## 파일 포맷 설계의 핵심 요소

나만의 파일 포맷을 설계하려면 몇 가지 요소를 결정해야 한다. 이 요소들은 서로 연결되어 있으며, 하나를 이해하면 다음 개념이 자연스럽게 따라온다.

### 매직 넘버 (Magic Number)

매직 넘버는 파일의 첫 몇 바이트에 위치하는 고정된 바이트 패턴으로, 파일 포맷을 식별하는 서명 역할을 한다.

파일 확장자는 사용자나 프로그램이 언제든 변경할 수 있다. `malware.exe`를 `image.jpg`로 이름만 바꾸는 것은 아무런 제약 없이 가능하다. 하지만 매직 넘버는 파일 내용 자체에 포함되어 있으므로, 프로그램이 파일을 열기 전에 실제 포맷을 검증할 수 있다.

| 파일 종류       | 매직 넘버 (16진수)  | ASCII 표현   |
| --------------- | ------------------- | ------------ |
| PDF             | `25 50 44 46`       | `%PDF`       |
| PNG             | `89 50 4E 47`       | `.PNG`       |
| ZIP/PPTX/DOCX   | `50 4B 03 04`       | `PK..`       |
| JPEG            | `FF D8 FF`          | (비표시 문자) |
| GIF             | `47 49 46 38`       | `GIF8`       |
| EXE/DLL (PE)    | `4D 5A`             | `MZ`         |

ZIP 계열 파일의 매직 넘버 `PK`는 ZIP 포맷을 만든 Phil Katz의 이니셜이다.

### 왜 16진수로 표기하는가?

위 표에서 매직 넘버를 `25 50 44 46`처럼 16진수로 표기했다. 컴퓨터는 모든 데이터를 0과 1의 비트로 저장하는데, 왜 2진수가 아닌 16진수로 표현하는 걸까?

2진수로 표기하면 1바이트가 8자리(`01010000`)가 되어 가독성이 떨어진다. 반면 16진수는 4비트를 한 자리로 표현하므로, 1바이트가 정확히 두 자리(`50`)로 대응된다. 이 일대일 대응 관계 덕분에 바이트 단위 데이터를 시각적으로 파악하기 쉽고, 비트 패턴과의 변환도 직관적이다.

| 진법   | 1바이트 표현 길이 | 예시 (문자 'P', ASCII 80) |
| ------ | ----------------- | ------------------------- |
| 2진수  | 8자리             | `01010000`                |
| 10진수 | 1~3자리           | `80`                      |
| 16진수 | 정확히 2자리      | `50`                      |

```
2진수:    0101  0000
           ↓     ↓
16진수:    5     0     →  0x50
```

HEX 에디터, 디버거, 네트워크 패킷 분석 도구 등 바이너리 데이터를 다루는 거의 모든 도구가 16진수 표기를 사용한다.

### 엔디안 (Byte Order)

매직 넘버처럼 1바이트 단위로 읽는 데이터는 문제가 없다. 하지만 파일 포맷에는 "데이터 길이: 4바이트 정수"처럼 멀티바이트 값도 포함된다. 이때 문제가 되는 것이 엔디안이다.

1바이트를 초과하는 정수를 메모리에 저장할 때, CPU마다 바이트를 배치하는 순서가 다르다. 2바이트 정수 `0x1234`를 예로 들면:

| 방식          | 메모리 배치    | 특징                           | 사용 환경                    |
| ------------- | -------------- | ------------------------------ | ---------------------------- |
| Big Endian    | `12 34`        | 최상위 바이트(MSB)가 낮은 주소 | 네트워크 프로토콜, Java, 일부 RISC CPU |
| Little Endian | `34 12`        | 최하위 바이트(LSB)가 낮은 주소 | x86/x64 CPU, Windows, Linux  |

동일한 파일을 Big Endian 시스템에서 작성하고 Little Endian 시스템에서 읽으면, `0x1234`가 `0x3412`로 잘못 해석될 수 있다. 따라서 파일 포맷을 설계할 때는 엔디안을 명시적으로 정의해야 한다.

대표적인 방법으로 BOM(Byte Order Mark)이 있다:

```
FF FE       → UTF-16 Little Endian
FE FF       → UTF-16 Big Endian
EF BB BF    → UTF-8 (엔디안 무관, 식별용)
```

또는 포맷 명세에서 "이 포맷은 Little Endian만 사용한다"고 고정하는 방법도 있다.

### 비표준 비트 단위

일반적으로 파일 I/O는 바이트(8비트) 단위로 이루어지지만, 논리적인 데이터 단위를 비표준 비트 수로 정의하는 것도 가능하다.

**가변 길이 코딩**: Huffman 코딩은 빈도가 높은 심볼에 짧은 비트열을, 빈도가 낮은 심볼에 긴 비트열을 할당한다. JPEG, MP3, ZIP 등의 압축 포맷이 이 방식을 사용한다.

**비트 필드 최적화**: 0~7 범위의 값은 3비트면 충분하고, boolean 플래그 8개는 1바이트에 담을 수 있다.

**난독화**: 의도적으로 비표준 비트 정렬을 사용하면 일반 HEX 에디터로 데이터를 해석하기 어려워진다. 바이트 경계와 데이터 경계가 일치하지 않기 때문이다.

```
[커스텀 비트 스트림 포맷 예시]
├─ 비트 0-4 (5비트): 버전 번호 (0~31)
├─ 비트 5-7 (3비트): 플래그
├─ 비트 8-20 (13비트): 페이로드 길이 (0~8191)
├─ 비트 21~: 7비트씩 문자 데이터
└─ 마지막 4비트: CRC 체크섬
```

이런 포맷은 바이트 경계에 맞지 않으므로, 읽고 쓸 때 비트 시프트와 마스킹 연산이 필수적이다.

---

## 기존 포맷 활용: ZIP 컨테이너

직접 바이너리 포맷을 설계하는 대신, 검증된 기존 포맷을 활용하는 방법도 있다. `.docx`, `.xlsx`, `.pptx`, `.apk`, `.epub` 등 많은 현대 파일 포맷들은 내부적으로 ZIP 컨테이너를 사용한다. 확장자를 `.zip`으로 변경하면 일반 압축 프로그램으로 내부 구조를 열어볼 수 있다.

### 왜 ZIP을 기반으로 하는가?

복합 문서 포맷을 설계할 때 가장 큰 문제는 텍스트, 이미지, 스타일 정보, 메타데이터 등 이질적인 데이터를 하나의 파일로 묶어야 한다는 점이다. ZIP을 채택하면 여러 이점을 얻을 수 있다.

**압축 효율**: ZIP은 DEFLATE 알고리즘을 사용하여 데이터를 압축한다. XML 기반 문서의 경우 텍스트 중복이 많아 압축률이 높으며, 이는 저장 공간 절약과 네트워크 전송 속도 향상으로 이어진다.

**랜덤 액세스**: ZIP 파일은 Central Directory라는 목차 구조를 파일 끝에 배치한다. 이 덕분에 압축 파일 전체를 순차적으로 읽지 않고도 특정 파일의 위치를 바로 찾아 추출할 수 있다.

**검증된 구현체**: ZIP은 1989년에 공개된 이후 수십 년간 사용되어 온 포맷이다. 대부분의 프로그래밍 언어에 ZIP 처리 라이브러리가 기본 제공되며, 압축/해제 알고리즘의 안정성도 충분히 검증되었다.

**디버깅 용이성**: 개발 과정에서 파일 내부 구조를 확인해야 할 때, 별도의 전용 도구 없이 일반 압축 프로그램으로 열어볼 수 있다.

### 실제 구조 예시 (.docx 내부)

```
document.docx (= ZIP 파일)
├─ [Content_Types].xml    # MIME 타입 매핑 정보
├─ _rels/                 # 파일 간 관계 정의
├─ docProps/              # 문서 메타데이터 (작성자, 생성일 등)
└─ word/
   ├─ document.xml        # 본문 텍스트와 구조
   ├─ styles.xml          # 스타일 정의
   └─ media/              # 임베드된 이미지, 동영상 등
```

---

## C++에서 파일 다루기

지금까지 파일 포맷의 개념을 살펴봤다. 이제 C++에서 실제로 파일을 읽고 쓰는 방법을 알아보자. C++은 두 가지 라이브러리를 제공한다: 파일 내용을 다루는 `<fstream>`과 파일 시스템을 다루는 `<filesystem>`이다.

### 파일 스트림 (`<fstream>`)

`<fstream>`은 파일 내용을 읽고 쓰는 스트림 기반 API를 제공한다. 텍스트 모드와 바이너리 모드를 구분하는 것이 중요하다.

**텍스트 모드**: 운영체제의 줄바꿈 문자를 자동 변환한다. Windows에서는 `\r\n`을 `\n`으로, 또는 그 반대로 변환한다.

**바이너리 모드**: `std::ios::binary` 플래그를 지정하면 어떤 변환도 하지 않고 바이트를 그대로 읽고 쓴다.

```cpp
#include <fstream>

// 텍스트 모드 (기본값)
std::ofstream TextFile("log.txt");
TextFile << "Hello\n";  // Windows에서 "Hello\r\n"으로 저장됨

// 바이너리 모드
std::ofstream BinaryFile("data.bin", std::ios::binary);
uint32_t Value = 0x12345678;
BinaryFile.write(reinterpret_cast<char*>(&Value), sizeof(Value));
```

바이너리 파일을 텍스트 모드로 열면 `0x0A`(LF) 바이트가 `0x0D 0x0A`(CRLF)로 변환되어 데이터가 손상된다. 커스텀 파일 포맷을 다룰 때는 항상 `std::ios::binary`를 명시해야 한다.

### 파일 시스템 (`<filesystem>`)

`<filesystem>`은 파일 내용이 아닌 파일 시스템 자체를 조작하는 API다. 경로 처리, 디렉토리 탐색, 파일 속성 조회 등을 담당한다.

```cpp
#include <filesystem>
namespace fs = std::filesystem;

// 경로 조작
fs::path FilePath = "C:/Users/Documents/report.docx";
fs::path Dir = FilePath.parent_path();       // "C:/Users/Documents"
fs::path Name = FilePath.filename();         // "report.docx"
fs::path Stem = FilePath.stem();             // "report"
fs::path Ext = FilePath.extension();         // ".docx"

// 파일 존재 여부 및 속성
if (fs::exists(FilePath))
{
    auto Size = fs::file_size(FilePath);     // 파일 크기 (바이트)
}

// 디렉토리 탐색
for (const auto& Entry : fs::directory_iterator("C:/Users/Documents"))
{
    if (Entry.is_regular_file())
    {
        // Entry.path()로 파일 경로 접근
    }
}

// 파일/디렉토리 조작
fs::create_directories("Output/SubDir");     // 중첩 디렉토리 생성
fs::copy("source.txt", "backup.txt");        // 파일 복사
fs::remove("temp.txt");                      // 파일 삭제
```

### 두 라이브러리의 역할 분담

| 작업 | 사용할 라이브러리 |
| ---- | ----------------- |
| 파일 내용 읽기/쓰기 | `<fstream>` |
| 파일 존재 여부 확인 | `<filesystem>` |
| 경로 문자열 파싱 | `<filesystem>` |
| 디렉토리 생성/삭제 | `<filesystem>` |
| 파일 크기 조회 | `<filesystem>` |

---

## 실습: 커스텀 파일 포맷 구현

지금까지 배운 내용을 종합하여 나만의 파일 포맷 `.cciq`를 구현해보자. 이 포맷은 다음 요소를 포함한다:

- **매직 넘버**: 파일 시작 부분에 "CCIQ" 문자열로 포맷 식별
- **버전 정보**: 향후 포맷 변경에 대비
- **데이터 길이**: 멀티바이트 정수 (Little Endian 고정)
- **인코딩된 데이터**: XOR 연산으로 간단히 난독화

### 포맷 구조

```
오프셋 0-3:   매직 넘버 "CCIQ" (4바이트)
오프셋 4:     버전 (1바이트)
오프셋 5-8:   데이터 길이 (4바이트, Little Endian)
오프셋 9~:    XOR 0x42로 인코딩된 데이터
```

### 인코더 (파일 생성)

`<filesystem>`으로 출력 디렉토리를 준비하고, `<fstream>`의 바이너리 모드로 데이터를 쓴다.

```cpp
#include <fstream>
#include <filesystem>
#include <string>
#include <cstdint>

namespace fs = std::filesystem;

void EncodeCCIQ(const std::string& Text, const fs::path& FilePath)
{
    // 출력 디렉토리가 없으면 생성
    if (FilePath.has_parent_path())
    {
        fs::create_directories(FilePath.parent_path());
    }

    // 바이너리 모드로 파일 열기
    std::ofstream File(FilePath, std::ios::binary);

    // 매직 넘버 (1바이트씩 쓰므로 엔디안 무관)
    File.write("CCIQ", 4);

    // 버전 (1바이트)
    uint8_t Version = 1;
    File.write(reinterpret_cast<char*>(&Version), 1);

    // 텍스트 길이 (4바이트, Little Endian)
    // x86/x64에서는 자연스럽게 Little Endian으로 저장됨
    uint32_t Length = static_cast<uint32_t>(Text.size());
    File.write(reinterpret_cast<char*>(&Length), 4);

    // XOR 인코딩
    for (char c : Text)
    {
        char Encrypted = c ^ 0x42;
        File.write(&Encrypted, 1);
    }
}
```

### 디코더 (파일 읽기)

파일을 열기 전에 `<filesystem>`으로 존재 여부를 확인하고, 매직 넘버를 검증하여 올바른 포맷인지 판별한다.

```cpp
#include <fstream>
#include <filesystem>
#include <string>
#include <cstdint>
#include <stdexcept>

namespace fs = std::filesystem;

std::string OpenCCIQ(const fs::path& FilePath)
{
    // 파일 존재 여부 확인
    if (!fs::exists(FilePath))
    {
        throw std::runtime_error("파일이 존재하지 않습니다: " + FilePath.string());
    }

    // 바이너리 모드로 파일 열기
    std::ifstream File(FilePath, std::ios::binary);

    // 매직 넘버 검증
    char Magic[5] = {0};
    File.read(Magic, 4);
    if (std::string(Magic) != "CCIQ")
    {
        throw std::runtime_error("올바른 CCIQ 파일이 아닙니다!");
    }

    // 버전 읽기
    uint8_t Version;
    File.read(reinterpret_cast<char*>(&Version), 1);

    // 데이터 길이 읽기
    uint32_t Length;
    File.read(reinterpret_cast<char*>(&Length), 4);

    // XOR 디코딩
    std::string Result;
    Result.reserve(Length);
    for (uint32_t i = 0; i < Length; ++i)
    {
        char Encrypted;
        File.read(&Encrypted, 1);
        Result += Encrypted ^ 0x42;
    }

    return Result;
}
```

### 사용 예시

```cpp
int main()
{
    // 인코딩
    EncodeCCIQ("Hello, World!", "Output/My.cciq");

    // 디코딩
    std::string Result = OpenCCIQ("Output/My.cciq");
    // Result == "Hello, World!"

    return 0;
}
```

### 실제 파일 내용 (HEX 덤프)

"abc"를 인코딩한 결과:

```
43 43 49 51  01  03 00 00 00  23 20 21
│           │   │            │
"CCIQ"      v1  길이=3       'a'^0x42, 'b'^0x42, 'c'^0x42
```

`'a'`(0x61) XOR 0x42 = 0x23, `'b'`(0x62) XOR 0x42 = 0x20, `'c'`(0x63) XOR 0x42 = 0x21

이 예시에서 앞서 다룬 개념들이 모두 적용되었다:
- **매직 넘버**: "CCIQ"로 파일 포맷 식별
- **16진수 표기**: HEX 덤프로 바이너리 데이터 확인
- **엔디안**: 길이 필드를 Little Endian으로 고정
- **바이너리 모드**: `std::ios::binary`로 데이터 손상 방지
- **`<filesystem>`**: 디렉토리 생성, 파일 존재 확인
