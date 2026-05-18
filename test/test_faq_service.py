from service.faq_service   import FAQService
from models.models  import FaqSearchDTO

f = FAQService()
res_list, count = f.search_faq_by_param(FaqSearchDTO(company_id=1, page=True))
print(res_list[0], count)