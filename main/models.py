# coding:utf-8
import datetime
from werkzeug.security import check_password_hash
from pymodm import connect, fields, MongoModel, EmbeddedMongoModel
from pymongo.operations import IndexModel
from config import Config

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
