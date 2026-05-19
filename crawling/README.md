# crawling

- 자동차 브랜드별 FAQ 데이터를 크롤링하는 프로젝트
- 크롤링 대상 브랜드
  - 현대자동차
  - 기아자동차
  - BMW

## 수행 과정

- 브랜드별 FAQ 데이터를 순차적으로 크롤링
- 크롤링 완료 후 `.env` 에 정의된 `JSON_DIR` 경로에 JSON 파일 저장
  - 저장 파일명 형식
    - `{BRAND_NAME}_{COMPANY_PK}_faq.json`
- 저장된 JSON 파일을 읽어 DB에 적재

## 프로젝트 구조

```text
project_root/
│
└── crawling/
    ├── crawling_faq.py
    ├── main_crawling_start.py
    └── README.md
````

## 사용 방법

* `project_root` 경로에서 아래 명령어 실행

```bash
python -m crawling.main_crawling_start
```
