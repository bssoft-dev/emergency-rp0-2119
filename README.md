# 비상벨 디바이스 프로그램

## 통신
1. 오디오 분석 
<디바이스> - <머신러닝 서버> 
2. 연결상태 전송(주기), 이벤트 알림(비주기)
<디바이스> - <대시보드 서버>

## 주요기능
1. 자동실행 - 기기 부팅 후 메인 프로그램과 모니터링 프로그램 자동 실행
2. 사용자 설정 - /boot/bssoft/ 폴더의 deviceId.txt와 smartbell_config.txt를 이용하여 기기 아이디와 각종 설정 변경 가능
3. USB 무선랜으로 iptime N150UA와 NEXT 201Nmini 이용 가능
4. 녹음 및 재생 보드로 Seeed의 ReSpeaker 2-Mics Pi HAT 이용

## 메인 프로그램
> logs/smartbell.log에 로그 기록, 예기치 못한 오류 발생시 log.txt에 기록
- heartbeat와 button-check, audio-record-and-send 세가지 함수를 coroutine으로 만들어 gather로 실행
- LED와 알람은 이벤트 발생(버튼 누름, 비명 감지) 시 동작하나, LED의 경우 최초 부팅 시 welcome lighting이 있음
- 알람 중 버튼을 누르는 경우는 알람이 처음부터 다시 시작하나, 비명 감지의 경우는 비명이 감지되도 알람 중간에 다시 시작되지는 않도록 lock을 도입함
- pyaudio의 non-blocking 기반 녹음을 이용하여 비동기 프로그래밍이 가능하도록 하였음

## 모니터 프로그램
> monlog.txt에 로그 기록
- 예기치 못한 오류로 인해 프로그램이 중지되었을 경우를 대비해, 10초마다 실행 상태를 모니터링하여 프로그램을 다시 시작하게 함
- 네트워크 문제(ssh 서비스의 중단)가 있을 경우 기기를 재부팅 함
