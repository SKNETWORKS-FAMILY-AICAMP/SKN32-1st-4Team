CREATE DATABASE if not exists K_Car_Navigator
	default character set utf8mb4
    collate utf8mb4_unicode_ci;
USE K_Car_Navigator;
DROP TABLE IF EXISTS faq;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS company;
DROP TABLE IF EXISTS vehicle_registration_status;
DROP TABLE IF EXISTS district;
DROP TABLE IF EXISTS region;
DROP TABLE IF EXISTS vehicle_type;

CREATE TABLE company (
    id INT AUTO_INCREMENT PRIMARY KEY  COMMENT '회사_id',
    name VARCHAR(255) NOT NULL COMMENT '회사명',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '등록일'
) COMMENT='자동차 회사 테이블';

CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '카테고리_id',
    company_id INT NOT NULL  COMMENT '회사_id',
    name VARCHAR(255) NOT NULL  COMMENT '카테고리명',
    display_order INT DEFAULT 0  COMMENT '카테고리 순서',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  COMMENT '등록일',
    FOREIGN KEY (company_id) REFERENCES company(id)
) COMMENT='faq 카테고리 코드 테이블';

CREATE TABLE faq (
    id INT AUTO_INCREMENT PRIMARY KEY  COMMENT 'faq_id',
    company_id INT NOT NULL  COMMENT '회사_id',
    category_id INT DEFAULT NULL  COMMENT '카테고리_id',
    question TEXT NOT NULL  COMMENT '질문',
    answer TEXT NOT NULL  COMMENT '답변',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  COMMENT '등록일',
    FOREIGN KEY (company_id) REFERENCES company(id),
    FOREIGN KEY (category_id) REFERENCES category(id)
) COMMENT='FAQ 테이블';


CREATE TABLE vehicle_type (
    code CHAR(2) PRIMARY KEY COMMENT '차량 종류 코드 (01: 승용, 02: 승합, 03: 화물, 04: 특수)',
    name VARCHAR(20) NOT NULL COMMENT '차량 종류 명칭'
) COMMENT='차량 종류 코드 테이블';

CREATE TABLE region (
    code CHAR(2) PRIMARY KEY COMMENT '시도 코드',
    name VARCHAR(20) NOT NULL COMMENT '시도 명칭'
) COMMENT='시도(광역시/도) 코드 테이블';

CREATE TABLE district (
    code CHAR(4) PRIMARY KEY COMMENT '시군구 코드',
    region_code CHAR(2) NOT NULL COMMENT '상위 시도 코드',
    name VARCHAR(50) NOT NULL COMMENT '시군구 명칭',
    FOREIGN KEY (region_code) REFERENCES region(code)
) COMMENT='시군구 코드 테이블 (상위 시도 코드 포함)';

CREATE TABLE vehicle_registration_status
(
  pk                INT AUTO_INCREMENT PRIMARY KEY COMMENT '자동 증가 기본키',
  type              CHAR(2) NOT NULL COMMENT '차량 종류 코드 (FK: vehicle_type.code)',
  registration_date DATE NOT NULL COMMENT '등록일',
  vehicles          INT NOT NULL COMMENT '등록 차량 수',
  region            CHAR(2) NOT NULL COMMENT '시도 코드 (FK: region.code)',
  district          CHAR(4) NOT NULL COMMENT '시군구 코드 (FK: district.code)',
  FOREIGN KEY (type)     REFERENCES vehicle_type(code),
  FOREIGN KEY (region)   REFERENCES region(code),
  FOREIGN KEY (district) REFERENCES district(code)
) COMMENT='자동차 등록 현황 테이블';




