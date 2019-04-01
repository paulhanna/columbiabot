from .base import Module

CREWNECK_PRICE = 44.98
CREWNECK_URL = "https://columbia.bncollege.com/webapp/wcs/stores/servlet/Champion_Powerblend_Crew/ProductDisplay?catalogId=10001&storeId=10053&langId=-1&topCatId=40000&parentCatId=40360&categoryId=40424&productId=400000349149&level=&imageId=1362786&graphicId=AEC02222294002"


class Price(Module):
    DESCRIPTION = "Convert USD to YSK"
    ARGC = 1

    def response(self, query, message):
        query = query.strip().strip('$')
        price = float(query)
        return "For $%.2f, you could purchase %.2f crewnecks from the Columbia Bookstore. Make the right choice here: %s" % (price, price / SOCK_PRICE, SOCK_URL)
