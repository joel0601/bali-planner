#!/usr/bin/env python3
"""
航班 & 酒店实时查询工具

支持三种模式：
1. 搜索链接生成（免费，无需 API Key）
   - Google Flights / Trip.com 机票搜索
   - Agoda / Booking.com 酒店搜索
2. Amadeus API 实时报价（需免费注册 developer.amadeus.com）
3. 知识库参考价格（离线回退）

用法:
  python3 scripts/flight_hotel.py flight PEK DPS 2025-09-15 2025-10-12
  python3 scripts/flight_hotel.py hotel Bali 2025-09-15 2025-10-12 2
"""

import sys
import json
import urllib.parse
from datetime import datetime

# ── 配置 ──────────────────────────────────────────
# 设置环境变量以启用 Amadeus API:
#   export AMADEUS_API_KEY="xxx"
#   export AMADEUS_API_SECRET="xxx"
# 免费注册: https://developers.amadeus.com/

AIRPORT_CODES = {
    "北京": "PEK",
    "上海": "PVG",
    "广州": "CAN",
    "深圳": "SZX",
    "成都": "CTU",
    "杭州": "HGH",
    "香港": "HKG",
    "台北": "TPE",
    "新加坡": "SIN",
    "吉隆坡": "KUL",
    "巴厘岛": "DPS",
    "登巴萨": "DPS",
    "雅加达": "CGK",
}

REGION_HOTELS = {
    "仓古": "Canggu",
    "canggu": "Canggu",
    "乌布": "Ubud",
    "ubud": "Ubud",
    "乌鲁瓦图": "Uluwatu",
    "uluwatu": "Uluwatu",
    "水明漾": "Seminyak",
    "seminyak": "Seminyak",
    "库塔": "Kuta",
    "kuta": "Kuta",
    "金巴兰": "Jimbaran",
    "jimbaran": "Jimbaran",
    "努沙杜瓦": "Nusa Dua",
    "nusa dua": "Nusa Dua",
}

# ── 价格参考（离线回退）──────────────────────────
FLIGHT_PRICE_REFERENCE = {
    ("PEK", "DPS"): {"low": 2000, "mid": 3500, "high": 6000, "note": "北京直飞约7h，转机居多"},
    ("PVG", "DPS"): {"low": 1800, "mid": 3000, "high": 5000, "note": "上海有直飞，约6h"},
    ("CAN", "DPS"): {"low": 1500, "mid": 2500, "high": 4500, "note": "广州直飞约5h，价格最优"},
    ("HKG", "DPS"): {"low": 1200, "mid": 2200, "high": 4000, "note": "香港直飞约5h，廉航多"},
    ("SZX", "DPS"): {"low": 1600, "mid": 2800, "high": 4800, "note": "深圳出发需转机为主"},
}

HOTEL_PRICE_REFERENCE = {
    "Canggu": {"budget": "¥100-300/晚（青旅/民宿）", "comfort": "¥300-800/晚（精品泳池别墅）", "luxury": "¥800-2000/晚"},
    "Ubud": {"budget": "¥80-250/晚", "comfort": "¥250-700/晚", "luxury": "¥700-3000/晚"},
    "Uluwatu": {"budget": "¥150-400/晚", "comfort": "¥400-1200/晚", "luxury": "¥1200-8000/晚"},
    "Seminyak": {"budget": "¥150-400/晚", "comfort": "¥400-1000/晚", "luxury": "¥1000-5000/晚"},
    "Kuta": {"budget": "¥80-200/晚", "comfort": "¥200-600/晚", "luxury": "¥600-2000/晚"},
    "Jimbaran": {"budget": "¥200-500/晚", "comfort": "¥500-1500/晚", "luxury": "¥1500-5000/晚"},
    "Nusa Dua": {"budget": "¥200-500/晚", "comfort": "¥500-1500/晚", "luxury": "¥1500-8000/晚"},
}


def resolve_airport(city):
    """城市名 → 机场代码"""
    for name, code in AIRPORT_CODES.items():
        if name in city or city.upper() in [code, name.upper()]:
            return code
    return city.upper()[:3]


def generate_flight_links(origin, dest, date_out, date_back):
    """生成各大 OTA 机票搜索链接"""
    origin_code = resolve_airport(origin)
    dest_code = resolve_airport(dest)
    out = date_out.replace("-", "")
    back = date_back.replace("-", "") if date_back else ""

    links = {}

    # Google Flights
    q = f"Flights to {dest_code} from {origin_code} on {date_out}"
    if date_back:
        q += f" return {date_back}"
    links["Google Flights"] = f"https://www.google.com/travel/flights?q={urllib.parse.quote(q)}"

    # Trip.com
    trip_url = f"https://flights.trip.com/flights/{origin_code.lower()}-to-{dest_code.lower()}/?dcity={origin_code.lower()}&acity={dest_code.lower()}&ddate={date_out}"
    if date_back:
        trip_url += f"&rdate={date_back}"
    links["Trip.com"] = trip_url

    # 去哪儿
    qunar_url = f"https://flight.qunar.com/site/oneway_list.htm?fromCity={origin_code}&toCity={dest_code}&fromDate={date_out}"
    if date_back:
        qunar_url = qunar_url.replace("oneway_list", "roundtrip_list") + f"&toDate={date_back}"
    links["去哪儿"] = qunar_url

    return links, origin_code, dest_code


def generate_hotel_links(region, checkin, checkout, guests=2):
    """生成酒店搜索链接"""
    region_en = REGION_HOTELS.get(region, region)
    chin = checkin.replace("-", "")
    chout = checkout.replace("-", "")

    links = {}

    # Agoda
    agoda_url = f"https://www.agoda.com/search?city={urllib.parse.quote(region_en)}&checkIn={checkin}&checkOut={checkout}&rooms=1&adults={guests}"
    links["Agoda"] = agoda_url

    # Booking.com
    booking_url = f"https://www.booking.com/searchresults.html?ss={urllib.parse.quote(region_en + ', Bali, Indonesia')}&checkin={checkin}&checkout={checkout}&group_adults={guests}&no_rooms=1"
    links["Booking.com"] = booking_url

    # Trip.com 酒店
    trip_hotel = f"https://hotels.trip.com/hotels/list?city={urllib.parse.quote(region_en)}&checkIn={checkin}&checkOut={checkout}&adult={guests}"
    links["Trip.com 酒店"] = trip_hotel

    return links, region_en


def get_flight_reference(origin_code, dest_code):
    """获取参考价格"""
    key = (origin_code, dest_code)
    if key in FLIGHT_PRICE_REFERENCE:
        return FLIGHT_PRICE_REFERENCE[key]
    return {"low": 2000, "mid": 4000, "high": 8000, "note": "无城市特定数据，请以实际搜索为准"}


def get_hotel_reference(region_en):
    """获取酒店参考价格"""
    return HOTEL_PRICE_REFERENCE.get(region_en, {"budget": "¥100-400/晚", "comfort": "¥300-1000/晚", "luxury": "¥1000+"})


def try_amadeus_flight(origin_code, dest_code, date_out, date_back):
    """尝试 Amadeus API 实时查询（需 API Key）"""
    import os
    api_key = os.environ.get("AMADEUS_API_KEY")
    api_secret = os.environ.get("AMADEUS_API_SECRET")

    if not api_key or not api_secret:
        return None

    try:
        # 获取 token
        import urllib.request
        token_data = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": api_secret,
        }).encode()
        req = urllib.request.Request(
            "https://test.api.amadeus.com/v1/security/oauth2/token",
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req) as resp:
            token = json.loads(resp.read())["access_token"]

        # 搜索航班
        params = {
            "originLocationCode": origin_code,
            "destinationLocationCode": dest_code,
            "departureDate": date_out,
            "adults": "1",
            "max": "5",
        }
        if date_back:
            params["returnDate"] = date_back

        query_string = urllib.parse.urlencode(params)
        req2 = urllib.request.Request(
            f"https://test.api.amadeus.com/v2/shopping/flight-offers?{query_string}",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req2) as resp:
            data = json.loads(resp.read())

        results = []
        for offer in data.get("data", [])[:3]:
            price = float(offer["price"]["grandTotal"])
            # 汇率约 1 EUR = 7.8 CNY
            results.append({"price_eur": round(price, 2), "price_cny": round(price * 7.8)})

        return results
    except Exception as e:
        return f"API 查询失败: {e}"


def main():
    if len(sys.argv) < 4:
        print("用法:")
        print("  机票: python3 flight_hotel.py flight <出发城市> <到达城市> <出发日期> [返回日期]")
        print("  酒店: python3 flight_hotel.py hotel <区域> <入住日期> <退房日期> [人数]")
        print()
        print("示例:")
        print("  python3 flight_hotel.py flight 北京 巴厘岛 2025-09-15 2025-10-12")
        print("  python3 flight_hotel.py hotel 仓古 2025-09-15 2025-09-18 2")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "flight":
        origin = sys.argv[2]
        dest = sys.argv[3]
        date_out = sys.argv[4]
        date_back = sys.argv[5] if len(sys.argv) > 5 else None

        links, origin_code, dest_code = generate_flight_links(origin, dest, date_out, date_back)
        ref = get_flight_reference(origin_code, dest_code)

        print(f"✈️  {origin}({origin_code}) → {dest}({dest_code})")
        print(f"📅 {date_out}" + (f" → {date_back}" if date_back else " (单程)"))
        print()
        print("💰 历史参考价格（往返含税，每人）：")
        print(f"   低价: ¥{ref['low']} | 均价: ¥{ref['mid']} | 高价: ¥{ref['high']}")
        print(f"   💡 {ref['note']}")
        print()
        print("🔗 实时搜索链接：")
        for name, url in links.items():
            print(f"   [{name}]({url})")
        print()

        # 尝试实时 API
        amadeus = try_amadeus_flight(origin_code, dest_code, date_out, date_back)
        if amadeus and isinstance(amadeus, list):
            print("🟢 Amadeus 实时报价：")
            for i, o in enumerate(amadeus):
                print(f"   #{i+1} €{o['price_eur']} (约 ¥{o['price_cny']})")
        elif amadeus:
            print(f"⚠️ {amadeus}")
            print("   💡 免费注册 Amadeus API: https://developers.amadeus.com/")
        else:
            print("💡 获取实时报价：注册免费 Amadeus API Key 后设置环境变量")
            print("   export AMADEUS_API_KEY='your_key'")
            print("   export AMADEUS_API_SECRET='your_secret'")

    elif mode == "hotel":
        region = sys.argv[2]
        checkin = sys.argv[3]
        checkout = sys.argv[4]
        guests = int(sys.argv[5]) if len(sys.argv) > 5 else 2

        links, region_en = generate_hotel_links(region, checkin, checkout, guests)
        ref = get_hotel_reference(region_en)

        nights = (datetime.strptime(checkout, "%Y-%m-%d") - datetime.strptime(checkin, "%Y-%m-%d")).days

        print(f"🏨 {region}({region_en}) | {guests}人 | {nights}晚")
        print(f"📅 {checkin} → {checkout}")
        print()
        print("💰 参考价格（每晚）：")
        print(f"   穷游: {ref['budget']}")
        print(f"   舒适: {ref['comfort']}")
        print(f"   奢华: {ref['luxury']}")
        print()
        print("🔗 实时搜索链接：")
        for name, url in links.items():
            print(f"   [{name}]({url})")


if __name__ == "__main__":
    main()
