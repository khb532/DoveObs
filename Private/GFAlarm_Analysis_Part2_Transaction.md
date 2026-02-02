# GFAlarm 소스코드 분석 레포트 - Part 2: Transaction Layer 상세 분석

> 분석일: 2026-01-19
> 소스 위치: `E:\Workspace\GFAlarm\GFAlarm\Transaction`

---

## 1. Transaction Layer 개요

Transaction Layer는 GFAlarm의 핵심 로직을 담당하며, 게임 서버와의 통신을 가로채고 처리하는 역할을 합니다.

```
Transaction/
├── ProxyController.cs      # HTTPS MITM 프록시 서버
├── HttpController.cs       # PAC 파일 서버
├── GFPacket.cs            # 패킷 데이터 모델
├── ReceivePacket.cs       # 응답 패킷 처리 라우터
└── PacketProcess/         # 패킷 종류별 처리기
    ├── Index.cs           # 로그인/인덱스 관련
    ├── Operation.cs       # 군수지원
    ├── Gun.cs             # 인형 관련
    ├── Equip.cs           # 장비 관련
    ├── Fairy.cs           # 요정 관련
    ├── Mission.cs         # 전투/작전 관련
    ├── Dorm.cs            # 숙소/정보분석
    ├── Squad.cs           # 중장비
    ├── Automission.cs     # 자율작전
    ├── Explore.cs         # 탐색
    ├── Mall.cs            # 상점
    ├── Chip.cs            # 칩셋
    └── Outhouse.cs        # 외부시설 (작전보고서)
```

---

## 2. ProxyController.cs - HTTPS MITM 프록시

### 2.1 클래스 구조

```csharp
// ProxyController.cs:30-52
public class ProxyController
{
    private static readonly Logger log = LogManager.GetCurrentClassLogger();

    private ProxyServer proxyServer;                          // Titanium.Web.Proxy 서버
    private ExplicitProxyEndPoint endPointIPv4, endPointIPv6; // 엔드포인트

    private Queue<GFPacket> queue;   // 패킷 처리 큐
    private Thread thread;           // 패킷 처리 스레드

    // 싱글톤 인스턴스
    public static ProxyController instance { get; }
    private static volatile ProxyController _instance;
}
```

### 2.2 프록시 서버 시작 로직

```csharp
// ProxyController.cs:124-172
public bool Start()
{
    log.Debug("trying to start proxy server");

    // 이미 실행 중인지 체크
    if (proxyServer != null && proxyServer.ProxyRunning)
    {
        log.Warn("proxy server already started");
        return false;
    }

    try
    {
        // Titanium.Web.Proxy 서버 생성
        proxyServer = new ProxyServer(false, false, false);
        proxyServer.CertificateManager.PfxPassword = "testpassword";
        proxyServer.ForwardToUpstreamGateway = true;
        proxyServer.CertificateManager.SaveFakeCertificates = false;

        // 이벤트 핸들러 등록
        proxyServer.BeforeRequest += OnRequest;    // 요청 가로채기
        proxyServer.BeforeResponse += OnResponse;  // 응답 가로채기

        // 상위 프록시 설정 (선택적)
        if (Config.Proxy.upstreamProxy)
        {
            proxyServer.UpStreamHttpProxy = new ExternalProxy()
            {
                HostName = Config.Proxy.upstreamHost,
                Port = Config.Proxy.upstreamPort
            };
            proxyServer.UpStreamHttpsProxy = new ExternalProxy()
            {
                HostName = Config.Proxy.upstreamHost,
                Port = Config.Proxy.upstreamPort
            };
        }

        // IPv4 및 IPv6 엔드포인트 생성
        endPointIPv4 = new ExplicitProxyEndPoint(
            IPAddress.Any,
            Config.Proxy.port,
            Config.Proxy.decryptSsl  // SSL 복호화 여부
        );
        endPointIPv6 = new ExplicitProxyEndPoint(
            IPAddress.IPv6Any,
            Config.Proxy.port,
            Config.Proxy.decryptSsl
        );

        proxyServer.AddEndPoint(endPointIPv4);
        proxyServer.AddEndPoint(endPointIPv6);
        proxyServer.Start();

        return true;
    }
    catch (Exception ex)
    {
        log.Error(ex, "failed to start proxy server");
    }
    return false;
}
```

### 2.3 요청/응답 이벤트 처리

**요청 가로채기 (OnRequest)**
```csharp
// ProxyController.cs:204-212
private async Task OnRequest(object sender, SessionEventArgs e)
{
    string uri = e.HttpClient.Request.RequestUri.AbsoluteUri;

    // 허용된 호스트가 아니면 무시
    if (!IsAllowHost(uri))
        return;

    string method = e.HttpClient.Request.Method.ToUpper();
    if (method == "POST" || method == "PUT" || method == "GET")
        requestBodyString = await e.GetRequestBodyAsString();
}
```

**응답 가로채기 (OnResponse)**
```csharp
// ProxyController.cs:220-311
private async Task OnResponse(object sender, SessionEventArgs e)
{
    string uri = e.HttpClient.Request.RequestUri.AbsoluteUri;
    if (!IsAllowHost(uri))
        return;

    string method = e.HttpClient.Request.Method.ToUpper();
    if (method == "POST" || method == "PUT" || method == "GET")
    {
        try
        {
            string param = requestBodyString;
            long reqId = 0;
            string outdatacode = "";

            // URI 파라미터에서 outdatacode, req_id 추출
            if (!string.IsNullOrEmpty(param))
            {
                string uriAndParam = string.Format("{0}?{1}", uri, param);
                Dictionary<string, string> queries =
                    Util.Common.GetUriQueries(uriAndParam);

                if (queries.ContainsKey("outdatacode"))
                    outdatacode = queries["outdatacode"];
                if (queries.ContainsKey("req_id"))
                    reqId = Parser.String.ParseLong(queries["req_id"]);
            }

            bool editedBody = false;
            string body = await e.GetResponseBodyAsString();

            // 로그인 시 Sign 키 가져오기
            if (uri.EndsWith("Index/getUidTianxiaQueue") ||
                uri.EndsWith("Index/getDigitalSkyNbUid") ||
                uri.EndsWith("Index/getUidEnMicaQueue"))
            {
                Transaction.PacketProcess.Index.GetUid(new GFPacket() { ... });
            }

            // 검열해제 모드 (패킷 변조)
            if (Config.Extra.unlockCensorMode && uri.EndsWith("Index/index"))
            {
                string newBody = ForgeUncensorMode(body);
                if (!string.IsNullOrEmpty(newBody))
                {
                    body = newBody;
                    editedBody = true;
                }
            }

            // 랜덤부관 (패킷 변조)
            if (Config.Adjutant.useRandomAdjutant && uri.EndsWith("Index/index"))
            {
                string newBody = ForgeRandomAdjutant(body);
                if (!string.IsNullOrEmpty(newBody))
                {
                    body = newBody;
                    editedBody = true;
                }
            }

            // 변조된 응답 설정
            if (editedBody)
            {
                e.SetResponseBodyString(body);
            }

            // 패킷 큐에 추가 (별도 스레드에서 처리)
            queue.Enqueue(new GFPacket()
            {
                req_id = reqId,
                uri = uri,
                outdatacode = outdatacode,
                body = body,
            });
        }
        catch (Exception ex) { log.Error(ex); }
    }
}
```

### 2.4 호스트 필터링

```csharp
// ProxyController.cs:388-398
// 게임 서버 도메인 패턴
private static Regex hostFilter = new Regex(
    "(gf-|gfjp-).*(girlfrontline\\.co\\.kr|ppgame\\.com|txwy\\.tw|sunborngame\\.com).*"
);

// 제외할 파일 확장자 패턴
private static Regex pathFilter = new Regex(
    ".*(\\.html|\\.js|\\.txt|\\.jpg|\\.png|\\.css|\\.ico).*"
);

private static bool IsAllowHost(string host)
{
    if (hostFilter.IsMatch(host))
    {
        if (!pathFilter.IsMatch(host))  // 리소스 파일 제외
            return true;
    }
    return false;
}
```

**지원 서버 목록:**
| 서버 | 도메인 패턴 |
|------|------------|
| 한국 | `gf-*.girlfrontline.co.kr` |
| 빌리빌리 (중국) | `gf-*.ppgame.com` |
| 일본 | `gfjp-*.sunborngame.com` |
| 글로벌 | `gf-*.sunborngame.com` |
| 대만 | `*-*.txwy.tw` |

### 2.5 패킷 변조 기능

**검열해제 모드**
```csharp
// ProxyController.cs:355-378
private string ForgeUncensorMode(string body)
{
    if (string.IsNullOrEmpty(UserData.sign))
        return "";

    try
    {
        log.Debug("검열해제 모드 시도 중...");

        // 응답 복호화
        string decodeBody = AuthCode.Decode(body, UserData.sign);
        if (string.IsNullOrEmpty(decodeBody))
            return "";

        JObject response = Parser.Json.ParseJObject(decodeBody);
        if (response != null && response.ContainsKey("naive_build_gun_formula"))
        {
            // 검열 해제 공식으로 변경
            response["naive_build_gun_formula"] = "130:130:130:30";
            log.Debug("검열해제 모드 설정");
            return response.ToString(Formatting.None);
        }
    }
    catch (Exception ex) { log.Error(ex); }

    return "";
}
```

---

## 3. HttpController.cs - PAC 파일 서버

### 3.1 개요

PAC(Proxy Auto-Configuration) 파일을 제공하는 간단한 HTTP 서버입니다. 모바일 기기에서 이 PAC 파일을 참조하여 게임 서버 트래픽만 선택적으로 프록시를 통해 전송합니다.

### 3.2 주요 코드

```csharp
// HttpController.cs:108-161
public bool Start()
{
    // 관리자 권한 체크
    if (!App.isElevated)
    {
        log.Warn("access denied (need administrator privilege)");
        return false;
    }

    // 리소스 디렉토리 설정
    _rootDir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location)
               + "\\resource\\http";

    // PAC 파일 생성
    string pacFilename = pacDir + "\\GFPAC.js";
    if (File.Exists(pacFilename))
    {
        string pacFilestream = FileUtil.GetFile(pacFilename);

        // 프록시 주소 삽입
        string pacAddress = "";
        if (!string.IsNullOrEmpty(Config.Proxy.pacDomain))
            pacAddress = string.Format("\"PROXY {0}:{1}\"",
                Config.Proxy.pacDomain, Config.Proxy.port);
        else
            pacAddress = string.Format("\"PROXY {0}:{1}\"",
                Config.ip, Config.Proxy.port);

        pacFilestream = pacFilestream.Replace("{0}", pacAddress);
        File.WriteAllText(_rootDir + "/GFPAC.js", pacFilestream);
    }

    // HTTP 리스너 시작
    _port = Config.Proxy.pacPort;
    _listener = new HttpListener();
    _listener.Prefixes.Add(string.Format("http://*:{0}/", _port));
    _listener.Start();

    _serverThread = new Thread(this.Listen);
    _serverThread.Start();

    return true;
}
```

### 3.3 MIME 타입 매핑

```csharp
// HttpController.cs:20-87
private static IDictionary<string, string> _mimeTypeMappings =
    new Dictionary<string, string>(StringComparer.InvariantCultureIgnoreCase)
{
    {".css", "text/css"},
    {".gif", "image/gif"},
    {".htm", "text/html"},
    {".html", "text/html"},
    {".ico", "image/x-icon"},
    {".jpeg", "image/jpeg"},
    {".jpg", "image/jpeg"},
    {".js", "application/x-javascript"},
    {".png", "image/png"},
    {".txt", "text/plain"},
    // ... 기타 MIME 타입
};
```

---

## 4. GFPacket.cs - 패킷 데이터 모델

```csharp
// GFPacket.cs:1-11
namespace GFAlarm.Transaction
{
    public class GFPacket
    {
        public long req_id = 0;          // 요청 ID (시퀀스 번호)
        public string uri = "";          // API 엔드포인트 URI
        public string outdatacode = "";  // 암호화된 요청 데이터
        public string body = "";         // 암호화된 응답 데이터
    }
}
```

---

## 5. ReceivePacket.cs - 패킷 처리 라우터

### 5.1 URI 기반 라우팅

```csharp
// ReceivePacket.cs:24-1592
public static void Process(GFPacket packet)
{
    string uri = packet.uri;

    // 패킷 복호화
    string request_string = "";
    string response_string = "";
    try
    {
        request_string = AuthCode.Decode(packet.outdatacode, UserData.sign);
        response_string = AuthCode.Decode(packet.body, UserData.sign);
    }
    catch (Exception ex)
    {
        log.Error(ex, "failed to decode response body");
        return;
    }

    // URI 패턴에 따라 적절한 처리기로 분기
    if (uri.EndsWith("Index/index"))
        PacketProcess.Index.GetIndex(packet);
    else if (uri.EndsWith("Index/home"))
        /* 메인화면 처리 */
    else if (uri.EndsWith("Operation/startOperation"))
        PacketProcess.Operation.StartOperation(request_string, response_string);
    else if (uri.EndsWith("Operation/finishOperation"))
        PacketProcess.Operation.FinishOperation(request_string, response_string);
    // ... 약 80개 이상의 엔드포인트 처리
}
```

### 5.2 주요 API 엔드포인트

| 카테고리 | 엔드포인트 | 설명 |
|---------|-----------|------|
| **인덱스** | `Index/index` | 전체 게임 데이터 로드 |
| | `Index/home` | 메인화면 진입 |
| | `Index/changeAdjutant` | 부관 변경 |
| **군수지원** | `Operation/startOperation` | 군수지원 시작 |
| | `Operation/finishOperation` | 군수지원 완료 |
| | `Operation/abortOperation` | 군수지원 취소 |
| **인형** | `Gun/developGun` | 인형 제조 시작 |
| | `Gun/finishDevelop` | 인형 제조 완료 |
| | `Gun/fixGuns` | 인형 수복 시작 |
| | `Gun/fixFinish` | 인형 수복 완료 |
| | `Gun/skillUpgrade` | 스킬 훈련 시작 |
| | `Gun/finishUpgrade` | 스킬 훈련 완료 |
| | `Gun/combineGun` | 편제확대 |
| | `Gun/eatGun` | 인형 강화 |
| | `Gun/retireGun` | 인형 해체 |
| **장비** | `Equip/develop` | 장비 제조 시작 |
| | `Equip/finishDevelop` | 장비 제조 완료 |
| | `Equip/adjust` | 장비 교정 |
| **요정** | `Fairy/eatFairy` | 요정 강화 |
| | `Fairy/skillUpgrade` | 요정 스킬 훈련 |
| **전투** | `Mission/startMission` | 작전 시작 |
| | `Mission/battleFinish` | 전투 종료 |
| | `Mission/teamMove` | 제대 이동 |
| **탐색** | `Explore/start` | 탐색 시작 |
| | `Explore/balance` | 탐색 정산 |
| **숙소** | `Dorm/data_analysis` | 정보분석 시작 |
| | `Dorm/giftToGun` | 인형에게 선물 |

---

## 6. AuthCode.cs - 암호화/복호화

### 6.1 복호화 알고리즘 흐름

```
암호화된 패킷
     │
     ▼
┌─────────────┐
│ Base64 디코드│
└─────────────┘
     │
     ▼
┌─────────────┐
│  키 파생    │  sign → MD5 → 분할 → MD5 → 조합
└─────────────┘
     │
     ▼
┌─────────────┐
│ RC4 복호화  │
└─────────────┘
     │
     ▼
┌─────────────┐
│ GZip 해제   │  (# 접두사가 있는 경우만)
│ (선택적)    │
└─────────────┘
     │
     ▼
평문 JSON 데이터
```

### 6.2 키 파생 과정

```csharp
// AuthCode.cs:25-116
public static string Decode(string source, string key)
{
    if (string.IsNullOrEmpty(source) || string.IsNullOrEmpty(key))
        return "";

    // 키 파생: MD5 체인
    key = MD5(key);                              // 원본 키 MD5
    string str = MD5(CutString(key, 16, 16));    // 후반부 16자 MD5
    string text = MD5(CutString(key, 0, 16));    // 전반부 16자 MD5
    string pass = str + MD5(str);                // 최종 RC4 키

    // GZip 압축 여부 확인 (# 접두사)
    if (source.StartsWith("#"))
    {
        source = source.Substring(1);
        byte[] input = Convert.FromBase64String(source);
        byte[] array = RC4(input, pass);

        // 헤더 제거 후 GZip 해제
        byte[] array2 = new byte[array.Length - 26];
        Array.Copy(array, 26, array2, 0, array.Length - 26);

        using (MemoryStream stream = new MemoryStream(array2))
        using (Stream stream2 = new GZipInputStream(stream))
        using (StreamReader reader = new StreamReader(stream2, Encoding.UTF8))
        {
            return reader.ReadToEnd();
        }
    }
    else
    {
        // 단순 RC4 복호화
        byte[] input = Convert.FromBase64String(source);
        string @string = encoding.GetString(RC4(input, pass));
        return CutString(@string, 26);  // 헤더 26바이트 제거
    }
}
```

### 6.3 RC4 알고리즘 구현

```csharp
// AuthCode.cs:213-245
public static byte[] RC4(byte[] input, string pass)
{
    if (input == null || pass == null)
        return null;

    byte[] array = new byte[input.Length];
    byte[] key = GetKey(encoding.GetBytes(pass), 256);  // S-box 초기화

    long num = 0L;   // i
    long num2 = 0L;  // j

    for (int i = 0; i < input.Length; i++)
    {
        num = (num + 1L) % key.Length;
        num2 = (num2 + key[num]) % key.Length;

        // S-box 스왑
        byte b = key[num];
        key[num] = key[num2];
        key[num2] = b;

        // XOR 연산
        byte b2 = input[i];
        byte b3 = key[(key[num] + key[num2]) % key.Length];
        array[i] = (byte)(b2 ^ b3);
    }

    return array;
}
```

### 6.4 S-box 초기화 (Key Scheduling Algorithm)

```csharp
// AuthCode.cs:192-211
private static byte[] GetKey(byte[] pass, int kLen)
{
    byte[] array = new byte[kLen];

    // S-box 초기화 (0 ~ 255)
    for (long num = 0L; num < kLen; num++)
    {
        array[(int)num] = (byte)num;
    }

    // 키와 혼합하여 셔플
    long num2 = 0L;
    for (long num3 = 0L; num3 < kLen; num3++)
    {
        num2 = (num2 + array[(int)num3] + pass[(int)(num3 % pass.Length)]) % kLen;

        // 스왑
        byte b = array[(int)num3];
        array[(int)num3] = array[(int)num2];
        array[(int)num2] = b;
    }

    return array;
}
```

---

## 7. 패킷 예시

### 7.1 Index/home 응답 (메인화면)

```json
{
    "recover_mp": 0,
    "recover_ammo": 0,
    "recover_mre": 0,
    "recover_part": 0,
    "gem": 4706,
    "all_favorup_gun": [],
    "last_favor_recover_time": "1569276194",
    "kick": 0,
    "friend_messagelist": [],
    "friend_applylist": [],
    "index_getmaillist": [],
    "squad_data_daily": [
        {
            "user_id": 343650,
            "squad_id": "11",
            "type": "slay:mech",
            "last_finish_time": "2019-09-24",
            "count": 0,
            "receive": 0
        }
    ],
    "build_coin_flag": -4,
    "is_bind": "0"
}
```

### 7.2 Mission/battleFinish 요청 (전투 종료)

```json
{
    "spot_id": 17,
    "if_enemy_die": true,
    "current_time": 1564036501,
    "boss_hp": 0,
    "mvp": 10545856,
    "last_battle_info": "",
    "use_skill_squads": [],
    "guns": [
        {"id": 6762038, "life": 650},
        {"id": 10545856, "life": 565},
        {"id": 12131545, "life": 525}
    ],
    "user_rec": "{\"seed\":89382062,\"record\":[]}",
    "battle_damage": {}
}
```

---

## 8. 기술적 특징 요약

| 기술 | 사용 목적 |
|------|----------|
| **Titanium.Web.Proxy** | HTTPS MITM 프록시 구현 |
| **RC4 스트림 암호** | 패킷 암호화/복호화 |
| **MD5 해시** | 키 파생 함수 |
| **GZip 압축** | 대용량 패킷 압축 해제 |
| **Queue + Thread** | 비동기 패킷 처리 |
| **Regex 필터링** | 게임 서버 도메인 선별 |
| **JSON 파싱** | 패킷 데이터 구조화 |

---

*분석 작성: Claude Code*
