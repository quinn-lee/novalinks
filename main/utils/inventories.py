# coding:utf-8

from sp_api.api import Reports, Catalog
from sp_api.base import SellingApiException, Marketplaces
from main.models import Inventory
import time


def obtain_inventories(user):
    time.sleep(3)
    try:
        create_report_res = Reports(marketplace=Marketplaces.DE, credentials=user.credentials()).create_report(
            reportType="GET_FLAT_FILE_OPEN_LISTINGS_DATA")
        print(create_report_res)
        time.sleep(10)
        get_report_res = Reports(marketplace=Marketplaces.DE, credentials=user.credentials()).get_report(
            report_id=create_report_res.payload.get("reportId"))
        print(get_report_res)
        print(get_report_res.payload.get("processingStatus"))
        while get_report_res.payload.get("processingStatus") != "DONE":
            time.sleep(3)
            get_report_res = Reports(marketplace=Marketplaces.DE, credentials=user.credentials()).get_report(
                report_id=create_report_res.payload.get("reportId"))
            print(get_report_res.payload.get("processingStatus"))
        reportDocumentId = get_report_res.payload.get("reportDocumentId")
        time.sleep(3)
        res = Reports(marketplace=Marketplaces.DE, credentials=user.credentials()).get_report_document(
            document_id=reportDocumentId, decrypt=True,
            file="main/static/excels/{}.csv".format(create_report_res.payload.get("reportId")))
        with open("main/static/excels/{}.csv".format(create_report_res.payload.get("reportId"))) as f:
            line = f.readline()
            i = 0
            while line:
                i += 1
                if i == 1:
                    line = f.readline()
                    continue
                Inventory(user=user, sku=line.split()[0], asin=line.split()[1], price=float(line.split()[2]),
                          quantity=int(line.split()[3])).save()
                line = f.readline()
    except SellingApiException as ex:
        print(ex)


def obtain_catalogs(inventory):
    time.sleep(5)
    try:
        res = Catalog(marketplace=Marketplaces.DE, credentials=inventory.user.credentials()).\
            get_item(MarketplaceId='A1PA6795UKMFR9', asin=inventory.asin)

        if res.payload.get('Identifiers') is not None and res.payload.get('Identifiers') != {}:
            inventory.Identifiers = res.payload.get('Identifiers')
        if res.payload.get('AttributeSets') is not None and res.payload.get('AttributeSets') != []:
            inventory.AttributeSets = res.payload.get('AttributeSets')
        if res.payload.get('Relationships') is not None and res.payload.get('Relationships') != []:
            inventory.Relationships = res.payload.get('Relationships')
        if res.payload.get('SalesRankings') is not None and res.payload.get('SalesRankings') != []:
            inventory.SalesRankings = res.payload.get('SalesRankings')

        inventory.has_attrs = True
        inventory.save()

    except SellingApiException as ex:
        print(ex)
