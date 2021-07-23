# coding:utf-8
import datetime
from werkzeug.security import check_password_hash
from pymodm import connect, fields, MongoModel, EmbeddedMongoModel
from pymongo.operations import IndexModel
from config import Config
import os

connect(Config.MONGODB_URI)


# 用户
class User(MongoModel):
    email = fields.EmailField(required=True)  # 邮箱
    name = fields.CharField(required=True)  # 昵称
    pwd = fields.CharField(required=True)  # 密码，加密

    refresh_token = fields.CharField()  # refresh token
    lwa_app_id = fields.CharField()  # Client-ID
    lwa_client_secret = fields.CharField()  # Client-SECRET
    aws_secret_key = fields.CharField()
    aws_access_key = fields.CharField()
    role_arn = fields.CharField()

    add_time = fields.DateTimeField(default=datetime.datetime.now)  # 添加时间

    role = fields.CharField()  # 角色 admin/seller/operator/inspector
    status = fields.IntegerField(default=0)  # 0-正常/1-停用

    class Meta:
        indexes = [
            IndexModel([('email', 1)], unique=True)
        ]

    def __repr__(self):  # 查询的时候返回
        return "<User %r>" % self.name

    def to_json(self):
        return {
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'status': {0: '正常', 1: '停用'}.get(self.status)
        }

    def check_password(self, passwd):
        """
        检验密码正确性
        :param passwd:  用户登录时填写的原始密码
        :return:  如果正确返回True 否则返回 False
        """
        return check_password_hash(self.pwd, passwd)

    def credentials(self):
        return dict(
            refresh_token=self.refresh_token,
            lwa_app_id=self.lwa_app_id,
            lwa_client_secret=self.lwa_client_secret,
            aws_secret_key=self.aws_secret_key,
            aws_access_key=self.aws_access_key,
            role_arn=self.role_arn,
        )


# 授权
class Authorization(MongoModel):
    from_user = fields.ReferenceField(User)  # 请求授权用户（角色为OPERATOR）
    to_user = fields.ReferenceField(User)  # 接受授权用户（角色为SELLER）
    status = fields.IntegerField()  # 授权状态（0-发起请求，1-接受，2-拒绝）
    request_time = fields.DateTimeField(default=datetime.datetime.now)  # operator请求时间
    processing_time = fields.DateTimeField()  # seller处理时间

    def to_operator_json(self):
        return {
            'email': self.to_user.email,
            'name': self.to_user.name,
            'status': {0: '等待卖家授权', 1: '已授权', 2: '拒绝授权'}.get(self.status),
            'request_time': self.request_time.strftime("%F %T"),
            'processing_time': self.processing_time.strftime("%F %T") if self.processing_time is not None else ""
        }

    def to_seller_json(self):
        return {
            'id': str(self._id),
            'email': self.from_user.email,
            'name': self.from_user.name,
            'status': {0: '待授权', 1: '已授权', 2: '拒绝授权'}.get(self.status),
            'request_time': self.request_time.strftime("%F %T"),
            'processing_time': self.processing_time.strftime("%F %T") if self.processing_time is not None else ""
        }


# 仓库
class Depot(MongoModel):
    code = fields.CharField()
    name = fields.CharField()
    country = fields.CharField()
    province = fields.CharField()
    city = fields.CharField()
    district = fields.CharField()
    street = fields.CharField()
    street_number = fields.CharField()
    house_number = fields.CharField()
    postcode = fields.CharField()
    telephone = fields.CharField()
    is_use = fields.BooleanField(default=True)

    def to_json(self):
        return {
            'id': str(self._id),
            'code': self.code,
            'name': self.name,
            'country': self.country,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'street': self.street,
            'street_number': self.street_number,
            'house_number': self.house_number,
            'postcode': self.postcode,
            'telephone': self.telephone,
            'is_use': self.is_use
        }


# 运单
class Waybill(MongoModel):
    w_no = fields.CharField()  # 运单号（预报号）
    seller = fields.ReferenceField(User)  # 用户（卖家名）
    wms_user = fields.CharField(blank=True)  # wms用户名
    operator = fields.ReferenceField(User)  # 服务商（操作员）
    depot = fields.ReferenceField(Depot)  # 收件人（地址代号）
    wms_info = fields.DictField(blank=True)  # wms同步过来的信息
    cont_num = fields.IntegerField(blank=True)  # 箱数，与WMS同步
    real_weight = fields.FloatField(blank=True)  # 实重，与WMS同步
    volume_weight = fields.FloatField(blank=True)  # 材重，与WMS同步
    billing_weight = fields.FloatField(blank=True)  # 收费重，操作员填写
    fare = fields.FloatField(blank=True)  # 费用，计算
    declared_value = fields.FloatField(blank=True)  # 申报价值，wms备案换算
    customs_apply = fields.IntegerField(blank=True)  # 报关情况，0-未报关，1-已报关，由操作员填写
    lading_bill = fields.FileField(blank=True)  # 货运提单，由操作员上传
    lading_bill_name = fields.CharField(blank=True)
    delivery_time = fields.DateTimeField(blank=True)  # 交货时间，工厂装柜日期，操作员填写
    etd = fields.DateTimeField(blank=True)  # 出运时间，国际运输物流的ETD，操作员填写
    eta = fields.DateTimeField(blank=True)  # 到港时间，国际运输物流的ETA，操作员填写
    customs_declaration = fields.IntegerField(blank=True)  # 清关情况，0-未清关，1-已清关（点击可查看海外代理信息），由操作员填写
    agent_info = fields.CharField(blank=True)  # 海外代理信息，点击清关情况时可以查看
    depot_status = fields.IntegerField(blank=True)  # 0-未入仓，1-已入仓（点击可查看POD，操作员上传）
    pod = fields.FileField(blank=True)  # pod文件

    class Meta:
        indexes = [
            IndexModel([('w_no', 1)], unique=True)
        ]

    def to_json(self):
        return {
            'id': str(self._id),
            'w_no': self.w_no,
            'seller': self.seller.name,
            'wms_user': self.wms_user,
            'operator': self.operator.name,
            'depot': self.depot.name,
            'wms_info': self.wms_info,
            'cont_num': self.cont_num,
            'real_weight': self.real_weight,
            'volume_weight': self.volume_weight,
            'billing_weight': self.billing_weight,
            'fare': self.fare,
            'declared_value': self.declared_value,
            'customs_apply': {0: '未报关', 1: '已报关'}.get(self.customs_apply),
            'ca_code': self.customs_apply,
            'lading_bill': str(self._id) if self.lading_bill is not None else None,
            'delivery_time': self.delivery_time.strftime("%Y/%m/%d") if self.delivery_time is not None else "",
            'etd': self.etd.strftime("%Y/%m/%d") if self.etd is not None else "",
            'eta': self.eta.strftime("%Y/%m/%d") if self.eta is not None else "",
            'customs_declaration': {0: '未清关', 1: '已清关'}.get(self.customs_declaration),
            'cd_code': self.customs_declaration,
            'agent_info': self.agent_info,
            'depot_status': {0: '未入仓', 1: '已入仓'}.get(self.depot_status),
            'ds_code': self.depot_status,
            'pod': str(self._id) if self.pod is not None else None,
        }

    def lading_bill_ext(self):
        if self.lading_bill_name is not None:
            ext = os.path.splitext(self.lading_bill_name)[1]
            if ext == '':
                ext = os.path.splitext(self.lading_bill_name)[0]
            if ext.startswith('.'):
                # os.path.splitext retains . separator
                ext = ext[1:]
            return ext
        else:
            return ""


# 运单物流轨迹
class TrackingInfo(MongoModel):
    waybill = fields.ReferenceField(Waybill)
    event = fields.CharField()
    description = fields.CharField()
    location = fields.CharField()
    event_time = fields.DateTimeField(default=datetime.datetime.now)


# 登录日志
class UserLog(MongoModel):
    user = fields.ReferenceField(User)  # 所属用户
    ip = fields.CharField()  # 登录IP
    login_time = fields.DateTimeField(default=datetime.datetime.now)  # 登录时间

    def __repr__(self):
        return "<Userlog %r>" % self.user.name


# 订单
class Order(MongoModel):
    user = fields.ReferenceField(User)  # 所属用户
    AmazonOrderId = fields.CharField()
    SellerOrderId = fields.CharField()
    DefaultShipFromLocationAddress = fields.DictField()
    EarliestDeliveryDate = fields.DateTimeField()
    EarliestShipDate = fields.DateTimeField()
    FulfillmentChannel = fields.CharField()
    IsBusinessOrder = fields.BooleanField()
    IsGlobalExpressEnabled = fields.BooleanField()
    IsISPU = fields.BooleanField()
    IsPremiumOrder = fields.BooleanField()
    IsPrime = fields.BooleanField()
    IsReplacementOrder = fields.BooleanField()
    IsSoldByAB = fields.BooleanField()
    LastUpdateDate = fields.DateTimeField()
    LatestDeliveryDate = fields.DateTimeField()
    LatestShipDate = fields.DateTimeField()
    MarketplaceId = fields.CharField()
    NumberOfItemsShipped = fields.IntegerField()
    NumberOfItemsUnshipped = fields.IntegerField()
    OrderStatus = fields.CharField()
    OrderTotal = fields.DictField()
    OrderType = fields.CharField()
    PaymentMethod = fields.CharField()
    PaymentMethodDetails = fields.ListField()
    PurchaseDate = fields.DateTimeField()
    SalesChannel = fields.CharField()
    ShipServiceLevel = fields.CharField()
    ShipmentServiceLevelCategory = fields.CharField()
    OrderChannel = fields.CharField()
    PaymentExecutionDetail = fields.ListField()
    EasyShipShipmentStatus = fields.CharField()
    CbaDisplayableShippingLabel = fields.CharField()
    ReplacedOrderId = fields.CharField()
    PromiseResponseDueDate = fields.DateTimeField()
    IsEstimatedShipDateSet = fields.BooleanField()
    AssignedShipFromLocationAddress = fields.DictField()
    FulfillmentInstruction = fields.DictField()
    ShippingAddress = fields.DictField()
    has_items = fields.BooleanField(default=False)

    def __repr__(self):
        return "<Order %r>" % self.AmazonOrderId

    def order_items(self):
        return [item for item in OrderItem.objects.raw({'order': self._id})]

    def asins(self):
        return [item.ASIN for item in self.order_items()]

    def item_num(self):
        return sum([item.QuantityOrdered for item in self.order_items()])

    def order_amount(self):
        return float(self.OrderTotal.get('Amount', 0))

    def to_json(self):
        return {
            'AmazonOrderId': self.AmazonOrderId,
            'OrderStatus': self.OrderStatus,
            'OrderTotal': "%s%s" % (self.OrderTotal.get('CurrencyCode', ''), self.OrderTotal.get('Amount', 0)),
            'ShippingAddress': "%s %s %s %s %s %s %s %s %s %s " % (self.ShippingAddress.get('CountryCode', ''),
                                                                   self.ShippingAddress.get('City', ''),
                                                                   self.ShippingAddress.get('County', ''),
                                                                   self.ShippingAddress.get('District', ''),
                                                                   self.ShippingAddress.get('AddressLine1', ''),
                                                                   self.ShippingAddress.get('AddressLine2', ''),
                                                                   self.ShippingAddress.get('AddressLine3', ''),
                                                                   self.ShippingAddress.get('PostalCode', ''),
                                                                   self.ShippingAddress.get('Phone', ''),
                                                                   self.ShippingAddress.get('Name', '')),
            'NumberOfItemsShipped': self.NumberOfItemsShipped,
            'NumberOfItemsUnshipped': self.NumberOfItemsUnshipped,
            'PurchaseDate': self.PurchaseDate.strftime('%Y-%m-%d')
        }


# 订单商品
class OrderItem(MongoModel):
    order = fields.ReferenceField(Order)  # 所属订单
    ASIN = fields.CharField()
    ConditionId = fields.CharField()
    ConditionSubtypeId = fields.CharField()
    IsGift = fields.BooleanField()
    IsTransparency = fields.BooleanField()
    ItemPrice = fields.DictField()
    ItemTax = fields.DictField()
    OrderItemId = fields.CharField()
    ProductInfo = fields.DictField()
    PromotionDiscount = fields.DictField()
    PromotionDiscountTax = fields.DictField()
    QuantityOrdered = fields.IntegerField()
    QuantityShipped = fields.IntegerField()
    SellerSKU = fields.CharField()
    Title = fields.CharField()
    PointsGranted = fields.DictField()
    ShippingPrice = fields.DictField()
    ShippingTax = fields.DictField()
    ShippingDiscount = fields.DictField()
    ShippingDiscountTax = fields.DictField()
    PromotionIds = fields.ListField()
    CODFee = fields.DictField()
    CODFeeDiscount = fields.DictField()
    ConditionNote = fields.CharField()
    ScheduledDeliveryStartDate = fields.DateTimeField()
    ScheduledDeliveryEndDate = fields.DateTimeField()
    PriceDesignation = fields.CharField()
    TaxCollection = fields.DictField()
    SerialNumberRequired = fields.BooleanField()
    IossNumber = fields.CharField()
    DeemedResellerCategory = fields.CharField()

    def __repr__(self):
        return "<Item %r>" % self.order.AmazonOrderId

    def sku(self):
        if Inventory.objects.raw({'asin': self.ASIN}).count() > 0:
            inventory = Inventory.objects.raw({'asin': self.ASIN}).first()
            return inventory.sku

    def to_json(self):
        return {
            'AmazonOrderId': self.order.AmazonOrderId,
            'ASIN': self.ASIN,
            'sku': self.sku(),
            'QuantityOrdered': self.QuantityOrdered,
            'QuantityUnShipped': int(self.QuantityOrdered) - int(self.QuantityShipped)
        }


class Inventory(MongoModel):
    user = fields.ReferenceField(User)  # 所属用户
    sku = fields.CharField()
    asin = fields.CharField()
    price = fields.FloatField()
    quantity = fields.IntegerField()
    has_attrs = fields.BooleanField(default=False)
    AttributeSets = fields.ListField()
    Identifiers = fields.DictField()
    Relationships = fields.ListField()
    SalesRankings = fields.ListField()

    def __repr__(self):
        return "<Catalog %r>" % self.sku

    def attrset(self):
        if self.AttributeSets is not None and self.AttributeSets != []:
            return self.AttributeSets[0]
        else:
            return {}

    def item_dimensions(self):
        return self.attrset().get('ItemDimensions', {})

    def height(self):
        h = self.item_dimensions().get("Height", None)
        if h is not None:
            return str(round(h.get("value", 0), 2)) + h.get("Units", "")
        else:
            return ""

    def width(self):
        w = self.item_dimensions().get("Width", None)
        if w is not None:
            return str(round(w.get("value", 0), 2)) + w.get("Units", "")
        else:
            return ""

    def length(self):
        le = self.item_dimensions().get("Length", None)
        if le is not None:
            return str(round(le.get("value", 0), 2)) + le.get("Units", "")
        else:
            return ""

    def weight(self):
        w = self.item_dimensions().get("Weight", None)
        if w is not None:
            return str(round(w.get("value", 0), 2)) + w.get("Units", "")
        else:
            return ""

    def to_json(self):
        return {
            "sku": self.sku,
            "asin": self.asin,
            "price": self.price,
            "quantity": self.quantity,
            "Brand": self.attrset().get("Brand"),
            "Color": self.attrset().get("Color"),
            "Size": self.attrset().get("Size"),
            "Title": self.attrset().get("Title"),
            "SmallImageURL": self.attrset().get("SmallImage").get("URL") if self.attrset().get("SmallImage") is not None
            else "",
            "Height": self.height(),
            "Length": self.width(),
            "Width": self.length(),
            "Weight": self.weight()
        }
