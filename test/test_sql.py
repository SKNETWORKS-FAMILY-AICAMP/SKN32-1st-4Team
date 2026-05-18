from database.db_service import DBService
from models.models import CategorySearchDTO, CompanySearchDTO, FaqSearchDTO


def print_rows(title, rows, limit=3):
    print(f"\n[{title}] {len(rows)}건")
    for row in rows[:limit]:
        print(row)


if __name__ == "__main__":
    db_service = DBService()

    companies = db_service.select_company()
    categories = db_service.select_category()
    faqs = db_service.select_faq()

    print_rows("회사", companies)
    print_rows("카테고리", categories)
    print_rows("FAQ", faqs)

    faq_search = FaqSearchDTO(page=1, size=10, get_pages=True)
    faq_search.order_clauses = [("created_at", "DESC"), ("id", "DESC")]
    print_rows("FAQ 최신 10건", db_service.select_faq(faq_search), limit=10)

    for company in companies:
        company_categories = db_service.select_category(
            CategorySearchDTO(company_id=company.id)
        )
        company_faqs = db_service.select_faq(FaqSearchDTO(company_id=company.id))
        print(
            f"\n{company.name}: "
            f"카테고리 {len(company_categories)}건, FAQ {len(company_faqs)}건"
        )

    bmw = db_service.select_company(CompanySearchDTO(company_name="BMW"))
    if bmw:
        faq_rows, total_count = db_service.select_faq_view(
            company_name="BMW",
            category_name="기타",
            page=1,
            size=5,
        )
        print(f"\n[BMW / 기타] {total_count}건")
        for row in faq_rows:
            print(row["question"])
