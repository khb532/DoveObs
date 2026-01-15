# 언리얼 엔진: 블루프린트

![[image.png]]

## Section 1. 기초

### 기초 & 변수타입

**단축키**
실행 전 컴파일+세이브는 필수
변수 이름은 대문자로 시작
코멘트(주석): 드래그(선택)+C
연결 끊기: Alt+왼클릭
일렬로 정리: 드래그(선택)+Q

**함수**
Boolean: True or False 값 (참/거짓)
(Boolean 변수의 이름은 소문자b로 작성하면 구분이 편리하다. Ex. bSound)
Byte: 0~255까지 저장, 가장 크기가 작음(1 byte만 할당), Ex. 캐릭터 커마의 헤어 스타일 종류 등
Integer: -21억에서 21억까지 저장, Ex. 스택, HP등.
Integer64: 21억 초과, Ex. 보스의 체력(데미지 인플레이션이 있는 오래된 게임)
\*정수를 나타냄
Float: 소수점 표현(부동소수점), Ex. 이동 스피드, 현재 위치한 X/Y축 등
Name: 엔진 내부에서 사용하면서 절대로 바뀌지 않음+빠른 검색이 필요할 때 이용.
Ex. 아트 리소스의 Bone Name 등
String: 다국어 변환이 필요하지 않은 것들, Ex. 플레이어 이름 등.
Text: 언어의 로컬라이제이션에 사용. Ex. 다국어 변환 시 사용(한국어 > 영어 등)

## Section 2. 변수

### Get, Set

Set - 저장한 변수를 호출.
Get - 저장한 변수를 읽어온다.
* Ctrl + 변수 Drag and Drop = Get /  Alt + 변수 Drag and Drop = Set 노드 생성

![[image 1.png]]

### 사칙 연산

사칙연산(덧셈)의 예시

![[image 2.png]]

나눗셈은 Float변수로 나누어야한다.(숫자가 정수로 떨어지는 경우 Integer도 O)

![[image 3.png]]

Integer 변수는 블루프린트 상에서 임시로 Float나 다른 변수로 변환 가능.(우클릭 + 변환 타입)

### 비교 연산

비교 연산자의 종류

| == | 같다 |
| --- | --- |
| > | 크다 |
| < | 작다 |
| >= | 크거나 같다 |
| <= | 작거나 같다 |
| != | 다르다 |

비교연산의 예시

![[image 4.png]]

비교연산의 결과물을 Promote to Value를 통해 변수로 승격시킬 수 있음.
(자동으로 변수 생성가능)
B + 우클릭 = Branch(if-else) 노드 호출

### 디버그

F9으로 브레이크 포인트 생성 및 플레이.
F10을 눌러 브레이크 포인트 이후 노드로 넘어가면서 디버그 진행.

### 연습 문제

총알 발사 및 남은 탄약 표시 만들기 예시

![[image 5.png]]

재장전 예시

![[image 6.png]]

### 논리연산

- NOT
- AND
- OR

## Section 3. 흐름제어

### 흐름 제어 - Branch(분기문), Sequence, Flip Flop

Branch (B+좌클릭)- 갈림길, 조건에 대한 결과로 참 또는 거짓을 반환

Sequence (S+좌클릭) - 순차 실행

Sequence의 예시 - (1, 2, 3, 4, 5, 6이 출력)

![[image 7.png]]

Flip Flop - A와B를 반복 실행

Flip Flop의 예시 - (Q를 입력하면 A와 B가 번갈아가면서 출력)

![[image 8.png]]

Branch로 Flip Flop 만들기

![[image 9.png]]

### 연습 문제: Min, Max, Clamp

Min - 입력 값 중에서 가장 작은 수를 반환

Min의 예시

![[image 10.png]]

Max - 입력 값 중에서 가장 큰 수를 반환
Max의 예시

![[image 11.png]]

Clamp - Min과  Max를 동시에 사용하는 개념

### 흐름 제어 - For Loop, While Loop(반복문)

While Loop - 특정 조건에 만족하면 빠져나온다.

While Loop의 예시

![[image 12.png]]

For Loop -

For Loop의 예시

![[image 13.png]]

For Loop With Break의 예시

![[image 14.png]]
