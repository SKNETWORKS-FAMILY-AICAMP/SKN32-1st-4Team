from database.db_service import DBService
from models.dtos    import *

if __name__=='__main__':
    d = DBService()

    faqs = d.select_faq()
    print(len(faqs), type(faqs[0]))

    faqs = d.select_faq(FaqSearchDTO(page=1, size=10, get_pages=True))
    print(len(faqs), type(faqs[0]), faqs[:2])

    faqs = d.select_faq(FaqSearchDTO(page=2, size=10, get_pages=True))
    print(len(faqs), type(faqs[0]), faqs[:2])

    faqSearchDTO = FaqSearchDTO(page=1, size=10, get_pages=True)
    faqSearchDTO.order_clauses = [("created_at", "DESC"), ("id", None)]
    faqs = d.select_faq(faqSearchDTO)
    print(len(faqs), type(faqs[0]), faqs[:2])

    faqSearchDTO = FaqSearchDTO(page=1, size=10, get_pages=True, company_id=2)
    faqSearchDTO.order_clauses = [("created_at", "DESC"), ("id", None)]
    faqs = d.select_faq(faqSearchDTO)
    print(len(faqs), type(faqs[0]), faqs[:2])

    cate = d.select_category()
    print(len(cate), type(cate[0]))

    cateSearchDTO = CategorySearchDTO(page=2, size=10, get_pages=True)
    cateSearchDTO.order_clauses = [("display_order", "DESC"), ("id", None)]
    cate = d.select_category(cateSearchDTO)
    print(len(cate), type(cate[0]), cate[:2])

    cateSearchDTO = CategorySearchDTO(page=1, size=10, get_pages=True, company_id=2)
    cateSearchDTO.order_clauses = [("display_order", "DESC"), ("id", None)]
    cate = d.select_category(cateSearchDTO)
    print(len(cate), type(cate[0]), cate[:2])

    company = d.select_company()
    print(len(company), type(company[0]))

    cateSearchDTO = CompanySearchDTO(page=2, size=10, get_pages=True)
    cateSearchDTO.order_clauses = [("id", "desc")]
    company = d.select_company(cateSearchDTO)
    print(len(company))

    cateSearchDTO = CompanySearchDTO(page=1, size=10, get_pages=True, company_id=2)
    cateSearchDTO.order_clauses = [("id", "desc")]
    company = d.select_company(cateSearchDTO)
    print(len(company), type(company[0]), company[:2])