# GFAlarm Window 코드 완전 해부 가이드
## C# WPF 초보자를 위한 코드 리딩 가이드

> 이 문서는 `MainWindow.xaml.cs`를 처음부터 끝까지 한 줄 한 줄 해설합니다.
> "왜 이렇게 썼지?", "이 문법은 뭐지?"라는 질문에 답하는 것이 목표입니다.

---

# 목차
1. [Using 문 - 네임스페이스 가져오기](#1-using-문---네임스페이스-가져오기)
2. [클래스 선언과 상속](#2-클래스-선언과-상속)
3. [static과 인스턴스의 차이](#3-static과-인스턴스의-차이)
4. [프로퍼티(Property) 완전 정복](#4-프로퍼티property-완전-정복)
5. [Dispatcher.Invoke - UI 스레드 이해하기](#5-dispatcherinvoke---ui-스레드-이해하기)
6. [Timer와 비동기 프로그래밍](#6-timer와-비동기-프로그래밍)
7. [람다 표현식 (Lambda Expression)](#7-람다-표현식-lambda-expression)
8. [이벤트 핸들러](#8-이벤트-핸들러)
9. [#region 지시어](#9-region-지시어)
10. [Lazy Initialization 패턴](#10-lazy-initialization-패턴)

---

# 1. Using 문 - 네임스페이스 가져오기

```csharp
using GFAlarm.Constants;
using GFAlarm.Data;
using System;
using System.Windows;
using System.Threading;
```

## 이게 뭔가요?

`using`은 **"이 파일에서 이런 라이브러리/기능을 사용하겠다"**는 선언입니다.

## 비유로 이해하기

```
요리를 할 때:
"오늘은 파스타를 만들 거야"
→ 냉장고에서 토마토, 파스타면, 올리브오일을 꺼내온다

코드를 짤 때:
"오늘은 윈도우 앱을 만들 거야"
→ using으로 필요한 기능들을 가져온다
```

## 각 using의 의미

| using 문 | 무엇을 가져오나? |
|----------|----------------|
| `using System;` | C#의 기본 기능 (문자열, 숫자, 날짜 등) |
| `using System.Windows;` | WPF 윈도우 관련 기능 |
| `using System.Threading;` | 타이머, 스레드 관련 기능 |
| `using GFAlarm.Data;` | 이 프로젝트 내의 Data 폴더 기능 |

## 왜 필요한가요?

```csharp
// using이 없으면 매번 전체 경로를 써야 함
System.Windows.MessageBox.Show("안녕");
System.Threading.Timer timer = new System.Threading.Timer(...);

// using System.Windows; 가 있으면
MessageBox.Show("안녕");  // 짧게 쓸 수 있음
```

---

# 2. 클래스 선언과 상속

```csharp
namespace GFAlarm
{
    public partial class MainWindow : Window
    {
        // 클래스 내용...
    }
}
```

## 한 줄씩 해부하기

### `namespace GFAlarm`
```
"이 코드는 GFAlarm이라는 이름의 상자 안에 들어있어요"
```
- 네임스페이스는 **코드를 정리하는 폴더** 같은 것
- 같은 이름의 클래스가 있어도 네임스페이스가 다르면 구분 가능

### `public partial class MainWindow`

**public** - 접근 제한자
```
public  = 누구나 접근 가능 (공개)
private = 이 클래스 안에서만 (비공개)
internal = 같은 프로젝트 안에서만
```

**partial** - 부분 클래스
```
"이 클래스는 여러 파일에 나눠서 작성했어요"

MainWindow.xaml.cs  ← 코드 로직 (우리가 보는 파일)
MainWindow.xaml     ← UI 디자인 (XAML 파일)

두 파일이 합쳐져서 하나의 MainWindow 클래스가 됨
```

### `: Window` - 상속
```csharp
public partial class MainWindow : Window
//                              ↑ 콜론은 "~를 상속받는다"
```

**상속이란?**
```
Window 클래스가 가진 모든 기능을 MainWindow도 갖게 됨

Window 클래스에는:
- 창 열기/닫기
- 최소화/최대화
- 드래그해서 이동
- 등등...

이런 기능이 이미 구현되어 있음
MainWindow는 이걸 물려받아서 사용
```

---

# 3. static과 인스턴스의 차이

## 코드 살펴보기

```csharp
// static 변수
private static readonly Logger log = LogManager.GetCurrentClassLogger();
internal static MainWindow view;
public static DashboardView dashboardView = new DashboardView();

// 인스턴스 변수
private Timer timer;
public bool forceStop = true;
```

## static이 뭔가요?

```
static = "클래스 전체에서 딱 하나만 존재"
인스턴스 = "객체를 만들 때마다 새로 생성"
```

## 비유로 이해하기

```
🏫 학교(클래스)가 있다고 생각해보세요

static 변수 = 학교에 하나만 있는 것
  - 교장 선생님 (딱 한 명)
  - 교가 (학교당 하나)
  - 학교 이름 (하나)

인스턴스 변수 = 학생마다 각자 가지는 것
  - 이름
  - 나이
  - 성적
```

## 실제 코드에서의 의미

```csharp
// ✅ static - 프로그램 전체에서 하나만 존재
public static DashboardView dashboardView = new DashboardView();
```
```
왜 static으로 했을까?

다른 클래스(예: ReceivePacket.cs)에서 대시보드를 업데이트하고 싶을 때:
MainWindow.dashboardView.Update();

이렇게 바로 접근할 수 있음. 객체를 만들 필요 없이!
```

```csharp
// ✅ 인스턴스 변수 - 각 창마다 개별적으로 가짐
private Timer timer;
```
```
왜 인스턴스로 했을까?

타이머는 각 윈도우 객체가 독립적으로 관리해야 함
창을 여러 개 만들면 각자 자기만의 타이머를 가져야 함
```

## internal vs public vs private

```csharp
internal static MainWindow view;
public static DashboardView dashboardView;
private static readonly Logger log;
```

| 키워드 | 의미 | 이 프로젝트에서 |
|--------|------|----------------|
| `public` | 어디서든 접근 가능 | 다른 클래스에서 `MainWindow.dashboardView`로 접근 |
| `internal` | 같은 프로젝트 내에서만 | 프로젝트 내부에서만 `MainWindow.view` 사용 |
| `private` | 이 클래스 안에서만 | 로그는 외부에서 건드릴 필요 없음 |

## readonly란?

```csharp
private static readonly Logger log = LogManager.GetCurrentClassLogger();
//             ↑ "처음 설정하면 절대 바꿀 수 없어요"
```

```
readonly = 읽기 전용 (한 번 설정하면 변경 불가)

log = new Logger();  // ❌ 에러! readonly라서 재할당 불가

왜 이렇게 했을까?
→ 로거는 프로그램 시작할 때 한 번만 설정하면 됨
→ 실수로 바꾸는 걸 방지
```

---

# 4. 프로퍼티(Property) 완전 정복

## 코드 살펴보기

```csharp
public bool isMaxBp
{
    get { return _isMaxBp; }
    set
    {
        if (_isMaxBp == value)
            return;
        _isMaxBp = value;
        Dispatcher.Invoke(() =>
        {
            if (value)
            {
                this.BpPointTextBlock.Foreground =
                    Application.Current.Resources["OrangeBrush"] as Brush;
            }
            else
            {
                this.BpPointTextBlock.Foreground =
                    Application.Current.Resources["NormalBrush"] as Brush;
            }
        });
    }
}
private bool _isMaxBp = false;
```

## 프로퍼티가 뭔가요?

```
프로퍼티 = 변수 + 추가 로직

일반 변수:
public bool isMaxBp;  // 값을 저장만 함

프로퍼티:
public bool isMaxBp { get; set; }  // 값을 저장 + 읽고 쓸 때 추가 동작 가능
```

## get과 set 이해하기

```csharp
public bool isMaxBp
{
    get { return _isMaxBp; }    // 값을 "읽을 때" 실행됨
    set { _isMaxBp = value; }   // 값을 "쓸 때" 실행됨
}
```

```
// 사용할 때
bool result = isMaxBp;      // ← get 실행됨 (읽기)
isMaxBp = true;             // ← set 실행됨 (쓰기)
```

## value 키워드

```csharp
set
{
    _isMaxBp = value;  // value = 대입하려는 값
}
```

```
isMaxBp = true;   // 이때 value는 true
isMaxBp = false;  // 이때 value는 false
```

## 왜 이렇게 복잡하게 했을까?

```csharp
set
{
    // 1️⃣ 같은 값이면 무시 (불필요한 UI 업데이트 방지)
    if (_isMaxBp == value)
        return;

    // 2️⃣ 값 저장
    _isMaxBp = value;

    // 3️⃣ 값이 바뀌면 자동으로 UI 색상 변경!
    Dispatcher.Invoke(() =>
    {
        if (value)
            // true면 주황색
            this.BpPointTextBlock.Foreground = ... "OrangeBrush" ...
        else
            // false면 기본색
            this.BpPointTextBlock.Foreground = ... "NormalBrush" ...
    });
}
```

```
장점:
- isMaxBp = true; 한 줄만 쓰면 자동으로 UI 색상이 바뀜
- UI 업데이트 로직이 프로퍼티 안에 캡슐화됨
- 코드 중복 방지

단순히 변수를 쓰면:
_isMaxBp = true;
// 매번 수동으로 색상 변경 코드도 써야 함
this.BpPointTextBlock.Foreground = orangeBrush;
```

## Backing Field (_isMaxBp)

```csharp
public bool isMaxBp { get; set; }    // 프로퍼티 (공개)
private bool _isMaxBp = false;        // 백킹 필드 (비공개)
```

```
왜 두 개가 필요할까?

isMaxBp (프로퍼티)
  → 외부에서 접근하는 "문"
  → 읽기/쓰기할 때 추가 로직 실행

_isMaxBp (백킹 필드)
  → 실제 값이 저장되는 곳
  → 언더스코어(_)는 "이건 내부용이에요"라는 관례
```

---

# 5. Dispatcher.Invoke - UI 스레드 이해하기

## 코드 살펴보기

```csharp
Dispatcher.Invoke(() =>
{
    this.BpPointTextBlock.Foreground =
        Application.Current.Resources["OrangeBrush"] as Brush;
});
```

## 이게 왜 필요한가요?

```
🚨 WPF의 황금 규칙:
"UI는 반드시 UI 스레드에서만 건드릴 수 있다"
```

## 스레드가 뭔가요?

```
스레드 = 일을 처리하는 작업자

🏃 메인(UI) 스레드
  → 화면 그리기, 버튼 클릭 처리 등
  → 사용자가 보는 모든 것을 담당

🏃 백그라운드 스레드
  → 파일 다운로드, 타이머, 네트워크 통신 등
  → 보이지 않는 곳에서 일함
```

## 문제 상황

```csharp
private void Tick(object state)  // ← 타이머는 백그라운드 스레드에서 실행됨
{
    // ❌ 에러 발생!
    this.BpPointTextBlock.Foreground = orangeBrush;
    // "다른 스레드에서 UI를 건드렸어요!"
}
```

## 해결책: Dispatcher.Invoke

```csharp
private void Tick(object state)
{
    // ✅ 정상 작동
    Dispatcher.Invoke(() =>
    {
        this.BpPointTextBlock.Foreground = orangeBrush;
    });
    // "UI 스레드야, 이 일 좀 대신 해줘!"
}
```

## 비유로 이해하기

```
🏢 회사에 비유하면:

UI 스레드 = 고객 응대 직원 (창구)
백그라운드 스레드 = 백오피스 직원 (뒤에서 일처리)

규칙: 고객(화면)을 직접 만날 수 있는 건 창구 직원뿐!

백오피스 직원이 고객에게 전달할 게 있으면?
→ 창구 직원에게 "이거 좀 전달해줘" (Dispatcher.Invoke)
```

## Invoke vs BeginInvoke

```csharp
Dispatcher.Invoke(() => { ... });      // 동기: 끝날 때까지 기다림
Dispatcher.BeginInvoke(() => { ... }); // 비동기: 요청만 하고 바로 다음 줄로
```

---

# 6. Timer와 비동기 프로그래밍

## 코드 살펴보기

```csharp
private Timer timer;

// 생성자에서 타이머 시작
public MainWindow()
{
    timer = new Timer(Tick, null, 0, 1000);
}

// 1초마다 호출되는 메서드
private void Tick(object state)
{
    // 여기에 반복할 작업
}
```

## Timer 생성자 파라미터

```csharp
new Timer(Tick, null, 0, 1000);
//        ↑     ↑    ↑   ↑
//        |     |    |   +-- 반복 간격 (밀리초) = 1000ms = 1초
//        |     |    +------ 첫 실행까지 대기 = 0ms = 즉시
//        |     +----------- state 파라미터 = 사용 안 함
//        +----------------- 콜백 메서드 = Tick
```

## 왜 Timer를 쓰나요?

```
🕐 1초마다 해야 할 일:
- 군수지원 남은 시간 업데이트
- 제조 완료 체크
- 알림 발송 여부 확인

while(true) + Thread.Sleep(1000) 대신 Timer를 쓰는 이유:
→ 더 효율적이고 안정적
→ 시스템 리소스를 덜 먹음
```

## Tick 메서드 구조

```csharp
private void Tick(object state)
{
    int nowTime = TimeUtil.GetCurrentSec();  // 현재 시간

    // 각 항목의 완료 시간 체크
    foreach (var item in UserData.Echelon.dispatchedList)
    {
        if (nowTime > item.endTime)  // 완료됐으면
        {
            // 알림 발송
            Notifier.Manager.notifyQueue.Enqueue(new Message() { ... });
        }
    }
}
```

---

# 7. 람다 표현식 (Lambda Expression)

## 코드 살펴보기

```csharp
Dispatcher.Invoke(() =>
{
    this.BpPointTextBlock.Foreground = orangeBrush;
});
```

## 람다가 뭔가요?

```
람다 = 이름 없는 작은 함수 (익명 함수)

() => { ... }
↑      ↑
|      +-- 실행할 코드
+--------- 파라미터 (없으면 빈 괄호)
```

## 람다 없이 쓰면?

```csharp
// 람다 없이 (옛날 방식)
private void UpdateColor()
{
    this.BpPointTextBlock.Foreground = orangeBrush;
}

Dispatcher.Invoke(new Action(UpdateColor));  // 복잡함

// 람다로 (현대 방식)
Dispatcher.Invoke(() =>
{
    this.BpPointTextBlock.Foreground = orangeBrush;
});  // 간단함
```

## 람다 문법 변형

```csharp
// 파라미터 없음
() => { Console.WriteLine("Hello"); }

// 파라미터 하나
(x) => { return x * 2; }
x => x * 2  // 축약형

// 파라미터 여러 개
(x, y) => { return x + y; }
(x, y) => x + y  // 축약형
```

## 이벤트 핸들러에서의 람다

```csharp
// 버튼 클릭 이벤트
button.Click += (sender, e) =>
{
    MessageBox.Show("클릭됨!");
};

// sender = 이벤트를 발생시킨 객체 (버튼)
// e = 이벤트 정보
```

---

# 8. 이벤트 핸들러

## 코드 살펴보기

```csharp
private void BT_MenuDashboard_Click(object sender, RoutedEventArgs e)
{
    this.SideMenuClose();
    this.ChangeContent(Menus.DASHBOARD);
}
```

## 이벤트가 뭔가요?

```
이벤트 = "무언가 일어났다"는 신호

버튼 클릭 → Click 이벤트 발생
마우스 올림 → MouseEnter 이벤트 발생
창 닫기 → Closing 이벤트 발생
```

## 이벤트 핸들러 연결 (XAML)

```xml
<!-- MainWindow.xaml -->
<Button Name="BT_MenuDashboard"
        Click="BT_MenuDashboard_Click" />
<!--              ↑ 이벤트 = "핸들러 메서드 이름" -->
```

## 이벤트 핸들러 연결 (코드)

```csharp
// 코드에서 연결하기
BT_MenuDashboard.Click += BT_MenuDashboard_Click;

// 람다로 연결하기
BT_MenuDashboard.Click += (sender, e) =>
{
    this.SideMenuClose();
    this.ChangeContent(Menus.DASHBOARD);
};
```

## sender와 RoutedEventArgs

```csharp
private void BT_MenuDashboard_Click(object sender, RoutedEventArgs e)
{
    // sender = 이벤트를 발생시킨 객체
    Button clickedButton = sender as Button;

    // e = 이벤트 추가 정보
    // (마우스 좌표, 키보드 상태 등)
}
```

## 여러 버튼에 같은 핸들러 쓰기

```csharp
private void MenuButton_Click(object sender, RoutedEventArgs e)
{
    Button btn = sender as Button;

    if (btn.Name == "BT_MenuDashboard")
        ChangeContent(Menus.DASHBOARD);
    else if (btn.Name == "BT_MenuEchelon")
        ChangeContent(Menus.ECHELON);
    // ...
}
```

---

# 9. #region 지시어

## 코드 살펴보기

```csharp
#region Footer

public bool isMaxBp { get; set; }
public bool isMaxGlobalExp { get; set; }
// ... 많은 코드 ...

#endregion
```

## 이게 뭔가요?

```
#region = 코드 접기/펴기용 표시

Visual Studio에서:
[+] Footer          ← 클릭하면 접힘
[-] Footer          ← 클릭하면 펼쳐짐
    public bool isMaxBp ...
    public bool isMaxGlobalExp ...
```

## 왜 쓰나요?

```
MainWindow.xaml.cs = 2300줄이 넘는 긴 파일

#region으로 구분하면:
- 관련된 코드끼리 묶음
- 안 보고 싶은 부분은 접어둠
- 코드 탐색이 쉬워짐
```

## 주의사항

```
#region은 컴파일과 무관
→ 실행 파일에 아무 영향 없음
→ 순전히 개발자 편의를 위한 것
```

---

# 10. Lazy Initialization 패턴

## 코드 살펴보기

```csharp
internal static SubWindow subView
{
    get
    {
        if (_subView == null)
            _subView = new SubWindow();
        return _subView;
    }
}
private static SubWindow _subView = null;
```

## 이게 뭔가요?

```
Lazy Initialization = 지연 초기화 = 필요할 때 만들기

처음부터 만들지 않고,
진짜 사용하는 순간에 만든다
```

## 왜 이렇게 하나요?

```csharp
// ❌ 즉시 초기화 (Eager)
private static SubWindow _subView = new SubWindow();
// 프로그램 시작할 때 바로 생성됨
// 서브 윈도우를 안 쓰더라도 메모리 차지

// ✅ 지연 초기화 (Lazy)
internal static SubWindow subView
{
    get
    {
        if (_subView == null)        // 아직 안 만들었으면
            _subView = new SubWindow();  // 그때 만들어
        return _subView;
    }
}
// 처음 접근할 때 생성됨
// 안 쓰면 생성 안 됨 = 메모리 절약
```

## 실제 동작

```csharp
// 1. 첫 번째 호출
var window1 = MainWindow.subView;
// _subView가 null이므로 new SubWindow() 실행
// _subView에 새 객체 저장
// 그 객체 반환

// 2. 두 번째 호출
var window2 = MainWindow.subView;
// _subView가 null이 아니므로 그냥 반환
// 새로 만들지 않음 = 같은 객체 재사용
```

## 싱글톤 패턴과의 관계

```
이 코드는 사실 "싱글톤(Singleton) 패턴"의 일종

싱글톤 = 프로그램 전체에서 딱 하나만 존재하는 객체

SubWindow는 하나만 있으면 되므로:
- static으로 선언 (클래스 전체에서 공유)
- 한 번만 생성
- 이후에는 같은 객체 재사용
```

---

# 11. 종합 예제: 전체 흐름 이해하기

## 프로그램 시작부터 알림까지

```
1️⃣ 프로그램 시작
   └── MainWindow 생성자 실행
       └── Timer 시작 (1초 간격)

2️⃣ 1초마다 Tick() 실행 (백그라운드 스레드)
   └── 각 항목의 완료 시간 체크
       └── 완료된 게 있으면
           └── notifyQueue에 메시지 추가

3️⃣ 상태 변경 시 (예: isMaxBp = true)
   └── set 프로퍼티 실행
       └── Dispatcher.Invoke로 UI 스레드에 요청
           └── UI 색상 변경

4️⃣ Notifier의 Timer
   └── notifyQueue에서 메시지 꺼냄
       └── Toast/Mail/Voice 알림 발송
```

## 코드로 보는 흐름

```csharp
// 1️⃣ 생성자
public MainWindow()
{
    InitializeComponent();
    timer = new Timer(Tick, null, 0, 1000);  // 타이머 시작
}

// 2️⃣ 1초마다 실행
private void Tick(object state)
{
    int nowTime = TimeUtil.GetCurrentSec();

    // BP 포인트 체크
    int bpPoint = UserData.CombatSimulation.GetCurrentBpPoint();
    if (bpPoint >= UserData.CombatSimulation.maxBpPoint)
    {
        // 3️⃣ 프로퍼티 set 호출 → UI 자동 업데이트
        isMaxBp = true;

        // 4️⃣ 알림 큐에 추가
        Notifier.Manager.notifyQueue.Enqueue(new Message()
        {
            type = MessageType.reach_max_bp_point,
            subject = "모의작전 점수 최대",
            content = "점수가 최대입니다"
        });
    }
}

// 3️⃣ UI 자동 업데이트
public bool isMaxBp
{
    set
    {
        _isMaxBp = value;
        Dispatcher.Invoke(() =>  // UI 스레드에서 실행
        {
            if (value)
                this.BpPointTextBlock.Foreground = orangeBrush;
        });
    }
}
```

---

# 12. 자주 묻는 질문 (FAQ)

## Q: `as` 키워드는 뭔가요?

```csharp
this.BpPointTextBlock.Foreground =
    Application.Current.Resources["OrangeBrush"] as Brush;
```

```
as = 형변환 (안전한 버전)

Resources["OrangeBrush"]는 object 타입으로 반환됨
→ Brush 타입으로 바꿔야 사용 가능

(Brush)Resources["OrangeBrush"]  // 직접 캐스팅 (실패하면 에러)
Resources["OrangeBrush"] as Brush  // as 캐스팅 (실패하면 null)
```

## Q: `this`는 왜 쓰나요?

```csharp
this.BpPointTextBlock.Foreground = ...
```

```
this = "현재 이 객체"를 가리킴

쓰는 이유:
1. 명확하게 "이 클래스의 멤버"임을 표시
2. 파라미터와 멤버 변수 이름이 같을 때 구분

사실 생략해도 됨:
BpPointTextBlock.Foreground = ...  // 같은 의미
```

## Q: `Application.Current.Resources`는 뭔가요?

```csharp
Application.Current.Resources["OrangeBrush"] as Brush
```

```
App.xaml에 정의된 전역 리소스에 접근

<Application.Resources>
    <SolidColorBrush x:Key="OrangeBrush" Color="Orange"/>
    <SolidColorBrush x:Key="NormalBrush" Color="White"/>
</Application.Resources>

코드에서 접근:
Resources["키이름"] → 해당 리소스 반환
```

---

# 마무리

이 가이드를 통해 MainWindow.xaml.cs의 핵심 개념들을 이해하셨기를 바랍니다.

**핵심 요약:**
1. `using` = 라이브러리 가져오기
2. `static` = 클래스 전체에서 공유
3. `프로퍼티` = 변수 + 추가 로직 (get/set)
4. `Dispatcher.Invoke` = UI 스레드에서 실행
5. `Timer` = 주기적 작업 실행
6. `람다 () => {}` = 간단한 익명 함수
7. `이벤트 핸들러` = 사용자 동작에 반응

더 궁금한 부분이 있으면 코드의 특정 라인을 물어봐 주세요!

---

*작성: Claude Code*
