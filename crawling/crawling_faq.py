import os
import json
import random
from common.logger import logger
from alive_progress import alive_bar
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from models.models import CrawlItem
from dataclasses import asdict

load_dotenv()
HYUNDAI = "HYUNDAI"
KIA = "KIA"
BMW = "BMW"
NO_ANSWER_MSG = "현재 답변을 확인할 수 없습니다. 제조사에 직접 문의해 주시면 안내받으실 수 있습니다."

class FAQCrawler:
    def __init__(self):
        # self.url = os.getenv("CRAWL_URL", "")
        self.urls = os.getenv("CRAWL_URLS", "").split(",")
        self.json_dir = os.getenv("JSON_DIR", "")
        self.brand_type = None

    def set_brand_type(self, brand_type):
        self.brand_type = brand_type
        
    # 외부에서 호출하는 메인 크롤링 + 저장 메서드
    def save_faq_crawled_data_to_json(self, company_id):
        if self.brand_type == HYUNDAI:
            faq_list = self.__crawl_hyundai_faq(company_id)
        elif self.brand_type == KIA:
            faq_list = self.__crawl_kia_faq(company_id)
        elif self.brand_type == BMW:
            faq_list = self.__crawl_bmw_faq(company_id)
        else:
            logger.warning("Brand not found...")
            return ""

        os.makedirs(self.json_dir, exist_ok=True) 
        output_path = os.path.join(self.json_dir, f"{self.brand_type}_{company_id}_faq.json")
        return self.__store_faq_list(faq_list, output_path)
    
    # ------------------------------------------------------------
    # Playwright 브라우저 실행 및 FAQ 크롤링
    # ------------------------------------------------------------
    def __crawl_hyundai_faq(self, company_id) -> list[CrawlItem]:
        faq_data = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = self.__init_page(browser)

            page.goto(self.urls[0], wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(1500)

            category_buttons = self.__get_category_buttons(page)
            for display_order, btn in enumerate(category_buttons, start=1):
                category_name = self.__get_category_name(btn)
                if not category_name:
                    continue

                logger.info(f"[+] 크롤링 시작: {category_name}")
                btn.click()
                page.wait_for_timeout(1500)

                page_num = 1
                while True:
                    logger.info(f"[*] {category_name} - {page_num} 페이지 수집 중")
                    faq_items = self.__get_faq_items(page)

                    if not faq_items:
                        logger.info("[-] FAQ 없음 → 다음 카테고리로 이동")
                        break

                    self.__extract_faq_items(faq_items, faq_data, company_id, category_name, display_order)
                    
                    if not self.__go_to_next_page(page):
                        break
                    page_num += 1

            browser.close()
        logger.info("[*] 크롤링 완료")
        return faq_data

    def __crawl_kia_faq(self, company_id) -> list[CrawlItem]:
        faq_data = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = self.__init_page(browser)

            page.goto(self.urls[1], wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(1500)

            category_buttons = self.__get_category_buttons(page)
            for display_order, btn in enumerate(category_buttons, start=1):
                category_name = self.__get_category_name(btn)
                if not category_name:
                    continue

                logger.info(f"[+] 크롤링 시작: {category_name}")
                with page.expect_response(lambda response: "faq.search?searchTag" in response.url) as response_info:
                    btn.click()

                # 응답 객체 가져오기
                response = response_info.value
                
                try:
                    # JSON 형태로 파싱
                    faq_json_data = response.json()
                except Exception as e:
                    logger.warning(f"JSON 파싱 실패: {e}")
                    continue
                
                # 제대로 가져왔는지 상위 항목 확인
                items = faq_json_data.get("data", {}).get("faqList", {}).get("items", [])
                count = len(items)
                logger.info(f"성공적으로 {len(items)}개의 FAQ JSON 데이터를 캐치했습니다!")
                items_sorted = sorted(items, key=lambda x: x.get("sortorder", 0), reverse=True)
                with alive_bar(count) as bar:
                    for item in items_sorted:
                        try:
                            faq_data.append(CrawlItem(
                                company_id=company_id,
                                category_name=category_name,
                                display_order=display_order,
                                question=item.get("question"),
                                answer=item.get("answer").get("html")
                            ))
                        except Exception as e:
                            logger.error(f"[!] FAQ 항목 처리 오류: {e}")
                            logger.error(item)
                        bar()


            browser.close()
        logger.info("[*] 크롤링 완료")
        return faq_data

    def __crawl_bmw_faq(self, company_id) -> list[CrawlItem]:
        faq_data = []
        all_articles = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = self.__init_page(browser)

            page.goto(self.urls[2], wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(1500)

            while True:
                try:
                    # "도움말 더 보기" 버튼 선택
                    button = page.query_selector("button[data-name='loadMoreButton']")
                    if not button:
                        logger.warning("더 이상 버튼이 없습니다.")
                        break

                    # 버튼 클릭 후, 두 번째 POST 요청이 올 때까지 기다림
                    with page.expect_response(lambda resp: "aura.ApexAction.execute=1" in resp.url) as response_info:
                        button.click()
                    
                    response = response_info.value
                    data = response.json()

                    # articleList 추출
                    articles = data['actions'][0]['returnValue']['returnValue'].get('articleList', [])
                    if not articles:
                        logger.warning("더 이상 기사 없음.")
                        break

                    # existing_ids = {article['id'] for article in all_articles}  # 이미 수집된 ID
                    # new_articles = [a for a in articles if a['id'] not in existing_ids]  # 중복 제거
                    # all_articles.extend(new_articles)
                    all_articles = articles
                    logger.info(f"수집된 기사 수: {len(all_articles)}")

                    # 잠시 대기 (사이트 부하 방지)
                    page.wait_for_timeout(500)

                except Exception as e:
                    logger.error("오류 발생:", e)
                    break

            browser.close()
        logger.info("[*] 크롤링 완료")
        category_order = {}
        current_order = 0
        with alive_bar(len(all_articles)) as bar:
            for item in all_articles:
                try:
                    '''
                    "categories": [
                        {
                            "label": "Customer Care",
                            "value": "Customer Care"
                        },
                        {
                            "label": "Profile & Personalization",
                            "value": "Profile & Personalization"
                        }
                    ],
                    "category": "Account",
                    "categoryLabel": "프로필", <- 이거 쓰는걸로
                    '''
                    category = item.get("categoryLabel")

                    if category not in category_order:
                        category_order[category] = current_order
                        current_order += 1

                    display_order = category_order[category]

                    faq_data.append(CrawlItem(
                        company_id=company_id,
                        category_name=item.get("categoryLabel"),
                        display_order=display_order,
                        question=item.get("title"),
                        answer=item.get("fields")[0].get("text", NO_ANSWER_MSG)
                    ))
                except Exception as e:
                    logger.error(f"[!] FAQ 항목 처리 오류: {e}")
                    logger.error(item)
                bar()

        return faq_data

    # ------------------------------------------------------------
    # Playwright 페이지 초기화
    # ------------------------------------------------------------
    def __init_page(self, browser):
        # return browser.new_page(user_agent=(
        #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        #     "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        # ), locale="ko-KR")

        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        ]
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            java_script_enabled=True,
            accept_downloads=True,
            ignore_https_errors=True
        )
        
        return context.new_page()
        

    # ------------------------------------------------------------
    # 카테고리 버튼 목록 추출
    # ------------------------------------------------------------
    def __get_category_buttons(self, page):
        if self.brand_type == HYUNDAI:
            tab_root = page.locator("div.tab").nth(0)
            all_tabs = tab_root.locator(
                ":scope > div.tab-menu > ul.tab-menu__icon-wrapper > li > button"
            )
            return [all_tabs.nth(i) for i in range(all_tabs.count())]
        elif self.brand_type == KIA:
            tab_root = page.locator("#tab-list")
            all_tabs = tab_root.locator("li > button")
            return [all_tabs.nth(i) for i in range(2, all_tabs.count())]
        else:
            return []

    # 카테고리 이름 추출
    def __get_category_name(self, btn_element):
        try:
            return btn_element.locator("span").inner_text().strip()
        except:
            return ""

    # FAQ 항목 리스트 추출
    def __get_faq_items(self, page):
        count = page.locator(".list-wrap .list-item").count()
        return [page.locator(".list-wrap .list-item").nth(i) for i in range(count)]

    # FAQ 항목 추출 및 faq_data에 저장
    def __extract_faq_items(self, faq_items, faq_data, company_id, category_name, display_order):
        with alive_bar(len(faq_items)) as bar:
            for item in faq_items:
                try:
                    question, answer = self.__get_question_answer(item)
                    if question and answer:
                        faq_data.append(CrawlItem(
                            company_id=company_id,
                            category_name=category_name,
                            display_order=display_order,
                            question=question,
                            answer=answer
                        ))
                except Exception as e:
                    logger.error(f"[!] FAQ 항목 처리 오류: {e}")
                bar()

    # 개별 FAQ 질문/답변 추출
    def __get_question_answer(self, item):
        title_btn = item.locator("button.list-title")
        question = item.locator("button.list-title .list-content").inner_text().strip()
        
        # 아코디언이 닫혀 있으면 열기
        if "active" not in (item.get_attribute("class") or ""):
            title_btn.click()
            title_btn.page.wait_for_timeout(600)

        answer = item.locator(".conts").inner_html().strip()

        # 닫기
        title_btn.click()
        title_btn.page.wait_for_timeout(300)

        return question, answer

    # 다음 페이지 이동
    def __go_to_next_page(self, page):
        next_btn = page.locator("div.pagenation button.btn-next")
        if next_btn.count() == 0:
            return False

        class_attr = next_btn.get_attribute("class") or ""
        if "ative" not in class_attr and "active" not in class_attr:
            return False

        try:
            next_btn.click()
            page.wait_for_timeout(1500)
            return True
        except:
            return False

    # ------------------------------------------------------------
    # JSON 저장
    # ------------------------------------------------------------
    def __store_faq_list(self, faq_data, output_filename="hyundai_faq.json") -> str:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump([asdict(item) for item in faq_data], f, ensure_ascii=False, indent=4)
        logger.info(f"[*] 총 {len(faq_data)}개 FAQ 저장 완료 → {output_filename}")
        return output_filename