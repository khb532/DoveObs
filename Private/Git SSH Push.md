# 개인 장비에 SSH 키 생성 및 Git에 등록하는 법

## 1. 현재 HTTP 통신으로 설정되어 있는지 확인

```
$ git remote -v

```

## 2. SSH 키가 존재하는지 확인

```
$ cd ~/.ssh
$ ls
# 여기에 `{id}.pub, {id}` 있는지 확인

```

### 2-1. `.ssh/` 에 사용 가능한 `id_rsa` 키가 존재한다면

- `5번` 으로.
- Custom Key를 등록하고 싶다면 `2-2` 로

### 2-2. `.ssh/` 디렉토리가 존재하고, SSH 키가 없다면 생성

```
$ ssh-keygen (선택)-t rsa

Generating public/private rsa key pair.
Enter file in which to save the key (/{User}/{User}/.ssh/id_rsa): {(선택)id 입력}
Enter passphrase (empty for no passphrase): {(선택)password 입력}

```

### 2-3. `.ssh/` 디렉토리가 존재하지 않는다면,

```
$ ssh-keygen (선택)-t rsa

Generating public/private rsa key pair.
Enter file in which to save the key (/{User}/{User}/.ssh/id_rsa): (그대로 엔터)
Enter passphrase (empty for no passphrase): {(선택)password 입력}

```

## 3. SSH 키 복사

```
$ cat ~/.ssh/{생성된 key 파일 이름}.pub
# 여기에 ssh 키값이 출력된다.

```

## 4. Git에 등록

`프로필 이미지` 클릭
`Settings` 클릭
`SSH and GPG keys` 클릭
`New SSH key` 클릭
`Title` 입력
`Key`에 복사한 SSH 키값 모두 복붙

## 5. SSH 방식으로 Remote에 data 전송하도록 변경

형식: git remote set-url origin [git@github.com](mailto:git@github.com):Organization이름/저장소이름.git
예시: Organization 이름이 'MyStudio'이고 저장소 이름이 'GameProject'인 경우

```
$ git remote set-url origin git@github.com:MyStudio/GameProject.git
# 확인
$ ssh -T git@github.com

```

## 6. 평소 하던대로 Git 이용

## 6-1. 만약 등록했는데 key 인식을 못할 경우.

- 보통 `3번` 에서 `rsa`로 만들지 않은 경우 .
- 로컬 컴퓨터에서 해당 SSH 키를 사용토록 활성화

```
# Agent 실행
$ eval "$(ssh-agent -s)"
# 키 추가 (파일명이 다르면 수정)
$ ssh-add ~/.ssh/{id}
# 확인
$ ssh -T git@github.com

```

## 999. 만약에!! 삭제한다면

- Local SSH 키 삭제

```
$ rm -rf ~/.ssh
# 등록된 모든 키 삭제
$ ssh-add -D

# (선택 사항) SSH 에이전트 프로세스 종료
# Windows: 서비스에서 'OpenSSH Authentication Agent' 중지
# Mac/Linux:
ssh-agent -k

```

- GitHub(원격 서버)에서 공개 키 삭제
`프로필 이미지` 클릭
`Settings` 클릭
`SSH and GPG keys` 클릭
등록된 SSH 키 옆에 `Delete` 클릭

👍👍👍