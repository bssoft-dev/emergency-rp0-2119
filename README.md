# 비상벨 디바이스 프로그램
> 주의: 디바이스 버전과 프로그램 release 버전의 앞자리가 동일한지 확인하고 구동해야 함  
> v3.0 이상의 경우 zero2, rp3 이상 버전에서만 동작

## 통신
1. 오디오 분석 
<디바이스> -(감지 결과 로그 전송)-> <비상벨 대시보드 서버> -(서버 데이터 수신 결과 전달)-> <디바이스>
3. 연결상태 전송(주기), 이벤트 알림(비주기)
<디바이스> -> <비상벨 대시보드 서버>

## 최신기능
- 네트워크 끊길 경우 LED 붉은색으로 변경되는 기능 추가
- 프로그램 동작 모니터링용 프로그램 삭제

## 주요기능
1. 자동실행 - 기기 부팅 후 메인 프로그램과 모니터링 프로그램 자동 실행
2. 사용자 설정 - /boot/bssoft/ 폴더의 id.txt와 smartbell_config.txt를 이용하여 기기 아이디와 각종 설정 변경 가능  
    (id.txt 파일이 있으면 해당 파일 내 텍스트를 deviceId로 인식하며, 파일이 없으면 unix time 기반으로 아이디를 만들고 id.txt를 생성함)  
3. USB 무선랜으로 iptime N150UA 이용 가능
4. 녹음 및 재생 보드로 Seeed의 ReSpeaker 2-Mics Pi HAT 이용

## 메인 프로그램
- heartbeat와 button-check, audio-record-and-send 세가지 함수를 coroutine으로 만들어 main함수에서 gather로 실행
- LED와 알람은 이벤트 발생(버튼 누름, 비명 감지) 시 동작하나, LED의 경우 최초 부팅 시 welcome lighting이 있음
- 알람 중 버튼을 누르는 경우는 알람 소리를 처음부터 다시 재생하나, 비명 감지의 경우는 비명이 감지되도 알람 중간에 다시 시작되지는 않음
- pyaudio의 non-blocking 기반 녹음을 이용하여 비동기 프로그래밍이 가능하도록 하였음

## 기타
- 프로그램 구동 시 welcome light 이후 BLUE LED가 상시 켜지게 되어 있으며, 이는 프로그램이 정지되거나 재부팅, 
심지어 전력 공급이 잠깐 중단되는 경우에도 잔여 전류 때문에 계속 BLUE LED는 켜진 상태로 유지되므로 이 불빛을 통해 전원공급 이상상태를 판단할 수는 없음 
