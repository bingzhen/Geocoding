import jpype
import re
import os

jpype.startJVM(jpype.getDefaultJVMPath(), "-ea",
               "-Djava.class.path=" + os.path.abspath(__file__).replace('AddressMatching.py', 'AddressMatching-1.3.0.jar'))

class Address(object):
    def __init__(self, provinceId=None, province=None, cityId=None, city=None, districtId=None, district=None,
                 streetId=None, street=None, townId=None, town=None, villageId=None, village=None, road=None,
                 roadNum=None, buildingNum=None, text=None, java=None):
        self.provinceId = int(provinceId) if provinceId else provinceId
        self.province = province
        self.cityId = int(cityId) if cityId else cityId
        self.city = city
        self.districtId = int(districtId) if districtId else districtId
        self.district = district
        self.streetId = int(streetId) if streetId else streetId
        self.street = street
        self.townId = townId
        self.town = town
        self.villageId = villageId if villageId is not None else None
        self.village = village
        self.road = road
        self.roadNum = roadNum
        self.buildingNum = buildingNum
        self.text = text
        self._AddressClass = jpype.JClass('org.bitlap.geocoding.model.Address')
        self._java = java if java is not None else self._AddressClass(self.provinceId, self.province, self.cityId,
                                                                      self.city, self.districtId, self.district,
                                                                      self.streetId, self.street, self.townId,
                                                                      self.town,
                                                                      self.villageId, self.village, self.road,
                                                                      self.roadNum, self.buildingNum, self.text)

    def __str__(self):
        return (f"Address(provinceId={self.provinceId}, province={self.province}, " +
                f"cityId={self.cityId}, city={self.city}, " +
                f"districtId={self.districtId}, district={self.district}, " +
                f"streetId={self.streetId}, street={self.street}, " +
                f"townId={self.townId}, town={self.town}, " +
                f"villageId={self.villageId}, village={self.village}, " +
                f"road={self.road}, " +
                f"roadNum={self.roadNum}, " +
                f"buildingNum={self.buildingNum}, " +
                f"text={self.text})")

    def __repr__(self):
        return (f"Address(\n\tprovinceId={self.provinceId}, province={self.province}, " +
                f"\n\tcityId={self.cityId}, city={self.city}, " +
                f"\n\tdistrictId={self.districtId}, district={self.district}, " +
                f"\n\tstreetId={self.streetId}, street={self.street}, " +
                f"\n\ttownId={self.townId}, town={self.town}, " +
                f"\n\tvillageId={self.villageId}, village={self.village}, " +
                f"\n\troad={self.road}, " +
                f"\n\troadNum={self.roadNum}, " +
                f"\n\tbuildingNum={self.buildingNum}, " +
                f"\n\ttext={self.text}\n)")

    @property
    def __dict__(self):
        return {
            'provinceId': self.provinceId,
            'province': self.province,
            'cityId': self.cityId,
            'city': self.city,
            'districtId': self.districtId,
            'district': self.district,
            'streetId': self.streetId,
            'street': self.street,
            'townId': self.townId,
            'town': self.town,
            'villageId': self.villageId,
            'village': self.village,
            'road': self.road,
            'roadNum': self.roadNum,
            'buildingNum': self.buildingNum,
            'text': self.text
        }

    @property
    def __java__(self):
        return self._java

def normalizing(address: str):
    """
    地址标准化

    :param address: 文本地址
    :return:
    """
    geocoding = jpype.JClass('org.bitlap.geocoding.GeocodingX')(strict=True)
    address_nor_java = geocoding.normalizing(str(address))
    pattern = re.compile(
        "Address\(\n\tprovinceId=(.*?), province=(.*?), " +
        "\n\tcityId=(.*?), city=(.*?), " +
        "\n\tdistrictId=(.*?), district=(.*?), " +
        "\n\tstreetId=(.*?), street=(.*?), " +
        "\n\ttownId=(.*?), town=(.*?), " +
        "\n\tvillageId=(.*?), village=(.*?), " +
        "\n\troad=(.*?), " +
        "\n\troadNum=(.*?), " +
        "\n\tbuildingNum=(.*?), " +
        "\n\ttext=(.*?)\n\)"
        , re.S)
    try:
        info = re.findall(pattern, str(address_nor_java.toString()))[0]
        info = [None if i == 'null' or i == 'nan' else i for i in info]
        return Address(info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[7], info[8], info[9],
                       info[10], info[11], info[12], info[13], info[14], info[15], address_nor_java)
    except AttributeError:
        return Address

def similarity(text1: str, text2: str):
    """
    地址相似度计算

    :param text1: 地址1, 文本地址
    :param text2: 地址2, 文本地址
    :return:
    """
    
    Address_1 = normalizing(text1)
    Address_2 = normalizing(text2)
    geocoding = jpype.JClass('org.bitlap.geocoding.Geocoding')
    pattern = re.compile("similarity=(.*?)\n\)", re.S)
    if type(Address_1) == type(Address_2) == Address:
        return eval(re.findall(pattern,
                               str(geocoding.similarityWithResult(Address_1.__java__,
                                                                  Address_2.__java__).toString()))[0])
    else:
        raise TypeError(
            "地址字符需至少包含省、市、区/县、乡/街道四级地理信息中的一级，若原地址中未包含相关信息，请认为将其加在地址字符串的最前端。")
