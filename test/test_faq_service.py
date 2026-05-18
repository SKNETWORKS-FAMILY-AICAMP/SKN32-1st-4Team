from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from service.faq_service import FAQService
from models.models import FaqSearchDTO

f = FAQService()

res_list, count = f.search_faq_by_param(
    FaqSearchDTO(company_id=5, keyword="BMW", page=1, size=20, get_pages=True)
)
print(len(res_list), count)

for faq in res_list:
    print(faq.company_id, faq.question)
