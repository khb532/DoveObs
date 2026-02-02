# GFAlarm 소스코드 분석 레포트 - Part 1: 개요 및 아키텍처

> 분석일: 2026-01-19
> 소스 위치: `E:\Workspace\GFAlarm`
> 프로그램명: 소녀전선 알리미 (GFAlarm)

---

## 1. 프로젝트 개요

**GFAlarm**은 모바일 게임 "Girls' Frontline (소녀전선)"의 유저용 외부 유틸리티 프로그램입니다. 게임 클라이언트와 서버 간의 HTTP/HTTPS 트래픽을 중간에서 가로채어(Man-in-the-Middle Proxy) 게임 데이터를 추출하고, 각종 알림(군수지원 완료, 제조 완료 등)을 제공합니다.

### 1.1 기술 스택

| 항목 | 내용 |
|------|------|
| **플랫폼** | Windows Desktop |
| **프레임워크** | .NET Framework 4.7.2 |
| **UI 프레임워크** | WPF (Windows Presentation Foundation) |
| **언어** | C# |
| **빌드 도구** | MSBuild / Visual Studio 2017+ |

---

## 2. 솔루션 구조

```
E:\Workspace\GFAlarm\
├── GF.sln                          # Visual Studio 솔루션 파일
├── GFAlarm/                        # 메인 프로젝트
│   ├── GFAlarm.csproj             # 프로젝트 파일
│   ├── App.xaml / App.xaml.cs     # 애플리케이션 진입점
│   ├── Window/                     # 윈도우 클래스
│   ├── View/                       # 뷰 컴포넌트
│   ├── Transaction/                # 패킷 처리 핵심 로직
│   ├── Data/                       # 데이터 모델
│   ├── Notifier/                   # 알림 시스템
│   ├── Util/                       # 유틸리티
│   ├── Constants/                  # 상수 정의
│   └── ShellHelpers/              # Windows Shell 헬퍼
├── GFDataParser/                   # 게임 데이터 파서 (별도 도구)
└── LocalizationResources/          # 다국어 리소스 라이브러리
```

---

## 3. 사용된 NuGet 패키지 및 라이브러리

### 3.1 핵심 라이브러리

| 패키지명 | 버전 | 용도 |
|---------|------|------|
| **Titanium.Web.Proxy** | 3.0.907 | HTTPS MITM 프록시 서버 구현 |
| **Newtonsoft.Json** | 12.0.3 | JSON 파싱/직렬화 |
| **NLog** | 4.6.7 | 로깅 프레임워크 |
| **Portable.BouncyCastle** | 1.8.5.2 | 암호화 라이브러리 (SSL 인증서 생성) |

### 3.2 UI 라이브러리

| 패키지명 | 버전 | 용도 |
|---------|------|------|
| **MahApps.Metro.IconPacks.Material** | 3.0.1 | Material Design 아이콘 |
| **HtmlTextBlock** | 1.0.1 | HTML 렌더링 텍스트 블록 |
| **WindowsAPICodePack-Core** | 1.1.2 | Windows API 래퍼 |
| **WindowsAPICodePack-Shell** | 1.1.1 | Windows Shell 기능 |

### 3.3 압축/스트림 라이브러리

| 패키지명 | 버전 | 용도 |
|---------|------|------|
| **SharpZipLib** | 1.2.0 | GZip 압축 해제 (패킷 디코딩) |
| **BrotliSharpLib** | 0.3.3 | Brotli 압축 지원 |
| **StreamExtended** | 1.0.201 | 스트림 확장 기능 |

### 3.4 빌드/배포

| 패키지명 | 버전 | 용도 |
|---------|------|------|
| **Costura.Fody** | 4.1.0 | DLL 임베딩 (단일 EXE 배포) |

### 3.5 시스템 라이브러리

| 참조 | 용도 |
|------|------|
| `Windows.winmd` | Windows 10 Toast 알림 API |
| `Windows.UI.Notifications` | UWP 토스트 알림 |
| `System.Windows.Forms` | NotifyIcon (트레이 아이콘) |
| `System.Net.Http` | HTTP 통신 |

---

## 4. 아키텍처 다이어그램

```d2
direction: down

GFAlarm: GFAlarm Application {
  Windows: {
    MainWindow: MainWindow (메인 UI)
    SubWindow: SubWindow (서브 UI)
    MapWindow: MapWindow (맵 뷰어)
  }

  ViewLayer: View Layer {
    DashboardView
    EchelonView
    QuestView
    SettingView
  }

  TransactionLayer: Transaction Layer {
    ProxyController: ProxyController\n(HTTPS 프록시)
    HttpController: HttpController\n(PAC 서버)
    ReceivePacket: ReceivePacket\n(패킷 처리기)
    AuthCode: AuthCode\n(RC4 복호화)

    ProxyController -> AuthCode
    ReceivePacket -> AuthCode
  }

  DataLayer: Data Layer {
    UserData
    GameData
    Config
    MissionData
  }

  NotifierLayer: Notifier Layer {
    Toast
    Mail
    Voice
    Manager
  }

  Windows -> ViewLayer
  ViewLayer -> TransactionLayer
  TransactionLayer -> DataLayer
  DataLayer -> NotifierLayer
}

External: External Components {
  MobileDevice: Mobile Device\n(게임 클라이언트)
  GameServer: Game Server\n(sunborngame.com)

  MobileDevice <-> GameServer: HTTPS Traffic
}

GFAlarm -> External: via Proxy
```

---

## 5. 핵심 동작 원리

### 5.1 프록시 기반 패킷 캡처

```
[모바일 기기] ──HTTPS──► [GFAlarm Proxy:9000] ──HTTPS──► [게임 서버]
                              │
                              ▼
                        패킷 복호화
                        데이터 추출
                        알림 생성
```

1. **PAC (Proxy Auto-Config) 서버** 실행 (HttpController)
   - 포트: 설정 가능 (기본 PAC 포트)
   - 게임 서버 도메인만 선택적으로 프록시 경유

2. **HTTPS MITM 프록시** 실행 (ProxyController via Titanium.Web.Proxy)
   - 포트: 9000 (기본값)
   - 자체 서명 인증서로 HTTPS 트래픽 복호화
   - `cert.cer`, `rootCert.pfx` 인증서 사용

3. **패킷 복호화** (AuthCode)
   - RC4 스트림 암호 + MD5 키 파생
   - GZip 압축 해제
   - JSON 파싱

4. **데이터 추출 및 알림** (ReceivePacket → Notifier)

### 5.2 지원 서버 (PAC 파일 기준)

```javascript
// GFPAC.js에서 프록시 경유 대상 도메인
*.girlfrontline.co.kr    // 한국 서버
*.ppgame.com             // 빌리빌리 서버
*.sunborngame.com        // 중국/글로벌/일본 서버
*.txwy.tw                // 대만 서버
```

---

## 6. 디자인 패턴 및 기법

### 6.1 싱글톤 패턴 (Singleton)

여러 핵심 컴포넌트에서 사용:

```csharp
// HttpController.cs:97-106
public static HttpController instance
{
    get
    {
        if (_instance == null)
            _instance = new HttpController();
        return _instance;
    }
}
private static volatile HttpController _instance;
```

### 6.2 정적 뷰 인스턴스

MainWindow에서 뷰를 정적으로 관리하여 전역 접근 허용:

```csharp
// MainWindow.xaml.cs:62-69
public static DashboardView dashboardView = new DashboardView();
public static EchelonView echelonView = new EchelonView();
public static QuestView questView = new QuestView();
public static ProxyView proxyView = new ProxyView();
public static SettingView settingView = new SettingView();
public static SettingAlarmView settingAlarmView = new SettingAlarmView();
public static ProxyGuideView proxyGuideView = new ProxyGuideView();
```

### 6.3 타이머 기반 Tick 시스템

1초마다 실행되는 타이머로 모든 시간 기반 알림 처리:

```csharp
// MainWindow.xaml.cs
private Timer timer = new Timer(Tick, null, 0, 1000);

private void Tick(object state)
{
    // 군수지원, 제조, 스킬훈련 등 시간 체크
    // 완료 시 알림 큐에 메시지 추가
}
```

### 6.4 메시지 큐 패턴

알림을 순차적으로 처리하기 위한 큐 사용:

```csharp
// Notifier/Manager.cs:28
public static Queue<Message> notifyQueue = new Queue<Message>();

// 1초마다 큐에서 메시지를 꺼내 알림 발송
private static void Tick(object state)
{
    if (notifyQueue.Count() > 0)
    {
        Message msg = notifyQueue.Dequeue();
        Notify(msg);
    }
}
```

### 6.5 URI 기반 패킷 라우팅

패킷 URI에 따라 적절한 처리기로 분기:

```csharp
// ReceivePacket.cs
public static void Process(GFPacket packet)
{
    string uri = packet.uri;

    if (uri.EndsWith("Index/index"))
        PacketProcess.Index.GetIndex(packet);
    else if (uri.EndsWith("Operation/startOperation"))
        PacketProcess.Operation.StartOperation(request_string, response_string);
    else if (uri.EndsWith("Gun/developGun"))
        PacketProcess.Gun.StartProduce(request_string, response_string);
    // ... 수십 개의 엔드포인트 처리
}
```

---

## 7. 보안 관련 구현

### 7.1 패킷 암호화/복호화 (AuthCode)

게임 서버와의 통신은 RC4 스트림 암호로 암호화됨:

```csharp
// AuthCode.cs - 복호화 로직
public static string Decode(string source, string key)
{
    // 1. MD5 키 파생
    key = MD5(key);
    string str = MD5(CutString(key, 16, 16));
    string text = MD5(CutString(key, 0, 16));
    string pass = str + MD5(str);

    // 2. Base64 디코딩
    byte[] input = Convert.FromBase64String(source);

    // 3. RC4 복호화
    byte[] array = RC4(input, pass);

    // 4. GZip 압축 해제 (# 접두사가 있는 경우)
    if (source.StartsWith("#"))
    {
        using (Stream stream2 = new GZipInputStream(stream))
        {
            return reader.ReadToEnd();
        }
    }
}
```

### 7.2 RC4 구현

```csharp
// AuthCode.cs:213-245
public static byte[] RC4(byte[] input, string pass)
{
    byte[] array = new byte[input.Length];
    byte[] key = GetKey(encoding.GetBytes(pass), 256);
    long num = 0L;
    long num2 = 0L;

    for (int i = 0; i < input.Length; i++)
    {
        num = (num + 1L) % key.Length;
        num2 = (num2 + key[num]) % key.Length;

        // Swap
        byte b = key[num];
        key[num] = key[num2];
        key[num2] = b;

        // XOR
        byte b2 = input[i];
        byte b3 = key[(key[num] + key[num2]) % key.Length];
        array[i] = (byte)(b2 ^ b3);
    }
    return array;
}
```

---

## 8. 주요 설정 항목

`Config.json`에서 관리되는 주요 설정:

| 카테고리 | 설정 항목 | 설명 |
|---------|----------|------|
| **Proxy** | port, pacPort, pacDomain | 프록시 서버 설정 |
| **Alarm** | notifyOperation, notifyProduceDoll, notifySkillTrain | 알림 활성화 |
| **Setting** | winToast, mailNotification, voiceNotification | 알림 방식 |
| **Extra** | earlyNotifySeconds | 사전 알림 시간 |
| **Window** | stickyWindow | 창 자석 기능 |

---

## 다음 파트 예고

- **Part 2**: Transaction 레이어 상세 분석 (ProxyController, ReceivePacket, PacketProcess)
- **Part 3**: UI 시스템 및 알림 시스템 상세 분석

---

*분석 작성: Claude Code*
