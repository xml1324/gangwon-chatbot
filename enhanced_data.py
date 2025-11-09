# 확장된 강원도 관광 데이터 (설문 결과 반영)

# 숙소 상세 데이터 (가격, 객실 타입, 식사 정보 포함)
ACCOMMODATION_DATA = [
    {
        "name": "레이크힐스호텔",
        "category": "호텔",
        "location": "춘천시 신북읍",
        "price_per_night": {
            "standard": 120000,
            "deluxe": 180000,
            "suite": 280000
        },
        "room_types": {
            "standard": {"capacity": 2, "beds": "더블 1개", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기"]},
            "deluxe": {"capacity": 4, "beds": "더블 2개", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "커피머신", "욕조"]},
            "suite": {"capacity": 4, "beds": "킹 1개, 소파베드", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "커피머신", "욕조", "거실"]}
        },
        "meals": {
            "breakfast_included": True,
            "breakfast_price": 15000,
            "breakfast_type": "뷔페",
            "restaurant": True
        },
        "facilities": ["주차장(무료)", "수영장", "피트니스", "사우나", "키즈룸"],
        "distance_to_attractions": {
            "남이섬": "15km (차로 20분)",
            "소양강스카이워크": "8km (차로 12분)",
            "춘천역": "12km (차로 18분)"
        },
        "rating": 4.3,
        "cleanliness_score": 4.5,
        "recent_bookings": 127,
        "coordinates": {"lat": 37.8228, "lng": 127.7669}
    },
    {
        "name": "춘천베어스호텔",
        "category": "비즈니스호텔",
        "location": "춘천시 중앙로",
        "price_per_night": {
            "standard": 80000,
            "deluxe": 120000
        },
        "room_types": {
            "standard": {"capacity": 2, "beds": "퀸 1개", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기"]},
            "deluxe": {"capacity": 3, "beds": "퀸 1개, 싱글 1개", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "소파"]}
        },
        "meals": {
            "breakfast_included": False,
            "breakfast_price": 12000,
            "breakfast_type": "한식/양식",
            "restaurant": True
        },
        "facilities": ["주차장(무료)", "비즈니스센터", "회의실"],
        "distance_to_attractions": {
            "춘천역": "0.5km (도보 7분)",
            "명동거리": "1km (도보 12분)",
            "소양강스카이워크": "10km (차로 15분)"
        },
        "rating": 4.2,
        "cleanliness_score": 4.4,
        "recent_bookings": 89,
        "coordinates": {"lat": 37.8813, "lng": 127.7298}
    },
    {
        "name": "강릉씨베이호텔",
        "category": "리조트",
        "location": "강릉시 창해로",
        "price_per_night": {
            "ocean_view": 200000,
            "family_suite": 320000,
            "premium_suite": 450000
        },
        "room_types": {
            "ocean_view": {"capacity": 2, "beds": "킹 1개", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "발코니"]},
            "family_suite": {"capacity": 4, "beds": "더블 2개", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "발코니", "주방", "거실"]},
            "premium_suite": {"capacity": 6, "beds": "킹 1개, 더블 1개", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "발코니", "주방", "거실", "욕조"]}
        },
        "meals": {
            "breakfast_included": True,
            "breakfast_price": 20000,
            "breakfast_type": "뷔페",
            "restaurant": True
        },
        "facilities": ["주차장(무료)", "수영장(실내/야외)", "스파", "레스토랑", "바비큐장", "키즈클럽"],
        "distance_to_attractions": {
            "경포해변": "2km (차로 5분)",
            "강릉커피거리": "3km (차로 7분)",
            "강릉역": "8km (차로 12분)"
        },
        "rating": 4.8,
        "cleanliness_score": 4.9,
        "recent_bookings": 203,
        "coordinates": {"lat": 37.7956, "lng": 128.9164}
    },
    {
        "name": "속초마레몬스콘도",
        "category": "콘도",
        "location": "속초시 해오름로",
        "price_per_night": {
            "studio": 150000,
            "two_bedroom": 250000,
            "three_bedroom": 350000
        },
        "room_types": {
            "studio": {"capacity": 4, "beds": "더블 1개, 소파베드", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "주방", "세탁기"]},
            "two_bedroom": {"capacity": 6, "beds": "더블 2개, 소파베드", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "주방", "세탁기", "거실"]},
            "three_bedroom": {"capacity": 8, "beds": "더블 3개", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "주방", "세탁기", "거실", "발코니"]}
        },
        "meals": {
            "breakfast_included": False,
            "breakfast_price": 0,
            "breakfast_type": "자체 조리 가능",
            "restaurant": False
        },
        "facilities": ["주차장(무료)", "수영장", "놀이터", "편의점"],
        "distance_to_attractions": {
            "속초해수욕장": "1km (도보 15분)",
            "속초중앙시장": "3km (차로 8분)",
            "설악산": "15km (차로 20분)"
        },
        "rating": 4.6,
        "cleanliness_score": 4.5,
        "recent_bookings": 156,
        "coordinates": {"lat": 38.2070, "lng": 128.5918}
    },
    {
        "name": "평창휘닉스파크호텔",
        "category": "리조트",
        "location": "평창군 봉평면",
        "price_per_night": {
            "standard": 180000,
            "deluxe": 250000,
            "suite": 400000
        },
        "room_types": {
            "standard": {"capacity": 2, "beds": "트윈", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기"]},
            "deluxe": {"capacity": 4, "beds": "더블 2개", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "소파"]},
            "suite": {"capacity": 4, "beds": "킹 1개", "amenities": ["Wi-Fi", "TV", "냉장고", "드라이기", "거실", "욕조", "발코니"]}
        },
        "meals": {
            "breakfast_included": True,
            "breakfast_price": 18000,
            "breakfast_type": "뷔페",
            "restaurant": True
        },
        "facilities": ["주차장(무료)", "스키장", "워터파크", "골프장", "키즈카페", "사우나"],
        "distance_to_attractions": {
            "평창올림픽플라자": "25km (차로 30분)",
            "대관령양떼목장": "20km (차로 25분)",
            "진부역": "18km (차로 22분)"
        },
        "rating": 4.9,
        "cleanliness_score": 4.8,
        "recent_bookings": 245,
        "coordinates": {"lat": 37.5811, "lng": 128.3289}
    }
]

# 맛집 상세 데이터
RESTAURANT_DATA = [
    {
        "name": "춘천명물막국수",
        "category": "한식",
        "specialty": "막국수",
        "location": "춘천시 신북읍",
        "price_range": {
            "막국수": 9000,
            "비빔막국수": 9000,
            "편육": 25000,
            "수육": 30000
        },
        "average_cost_per_person": 12000,
        "operating_hours": "10:00-20:00",
        "closed_days": "월요일",
        "parking": "가능 (20대)",
        "waiting_time": "주말 30-40분",
        "rating": 4.5,
        "distance_to_attractions": {
            "남이섬": "5km (차로 8분)",
            "소양강스카이워크": "12km (차로 18분)"
        },
        "popular_menu": ["막국수", "비빔막국수", "수육"],
        "coordinates": {"lat": 37.8228, "lng": 127.7369}
    },
    {
        "name": "춘천닭갈비골목",
        "category": "한식",
        "specialty": "닭갈비",
        "location": "춘천시 명동길",
        "price_range": {
            "닭갈비": 12000,
            "볶음밥": 2000,
            "치즈닭갈비": 14000
        },
        "average_cost_per_person": 15000,
        "operating_hours": "11:00-22:00",
        "closed_days": "연중무휴",
        "parking": "공영주차장 이용",
        "waiting_time": "주말 20-30분",
        "rating": 4.6,
        "distance_to_attractions": {
            "춘천역": "1.5km (차로 5분)",
            "소양강스카이워크": "8km (차로 12분)"
        },
        "popular_menu": ["닭갈비", "치즈닭갈비", "볶음밥"],
        "coordinates": {"lat": 37.8813, "lng": 127.7198}
    },
    {
        "name": "강릉커피거리",
        "category": "카페거리",
        "specialty": "커피전문점",
        "location": "강릉시 창해로",
        "price_range": {
            "아메리카노": 5000,
            "라떼": 6000,
            "디저트": 7000
        },
        "average_cost_per_person": 8000,
        "operating_hours": "카페별 상이 (대부분 09:00-22:00)",
        "closed_days": "카페별 상이",
        "parking": "공영주차장 이용",
        "waiting_time": "주말 10-20분",
        "rating": 4.8,
        "distance_to_attractions": {
            "경포해변": "1km (도보 15분)",
            "강릉역": "5km (차로 10분)"
        },
        "popular_menu": ["핸드드립 커피", "플랫화이트", "에스프레소"],
        "coordinates": {"lat": 37.7956, "lng": 128.9064}
    },
    {
        "name": "속초중앙시장",
        "category": "시장",
        "specialty": "해산물",
        "location": "속초시 중앙로",
        "price_range": {
            "회": 30000,
            "닭강정": 12000,
            "오징어순대": 5000
        },
        "average_cost_per_person": 15000,
        "operating_hours": "06:00-21:00",
        "closed_days": "설날, 추석",
        "parking": "공영주차장 (유료)",
        "waiting_time": "주말 15-25분",
        "rating": 4.5,
        "distance_to_attractions": {
            "속초해수욕장": "2km (차로 7분)",
            "설악산": "12km (차로 18분)"
        },
        "popular_menu": ["닭강정", "회", "오징어순대"],
        "coordinates": {"lat": 38.2070, "lng": 128.5818}
    }
]

# 관광지 상세 데이터
ATTRACTION_DATA = [
    {
        "name": "남이섬",
        "category": "명소",
        "location": "춘천시 남산면",
        "entrance_fee": {
            "adult": 16000,
            "teenager": 13000,
            "child": 10000
        },
        "operating_hours": "07:30-21:00 (계절별 상이)",
        "recommended_duration": "3-4시간",
        "parking": {
            "available": True,
            "fee": 5000,
            "spaces": 500
        },
        "best_season": ["봄(벚꽃)", "가을(단풍)", "겨울(설경)"],
        "facilities": ["레스토랑", "카페", "자전거 대여", "전기차"],
        "rating": 4.9,
        "distance_from_seoul": "63km (차로 1시간 10분)",
        "coordinates": {"lat": 37.7911, "lng": 127.5267}
    },
    {
        "name": "소양강스카이워크",
        "category": "명소",
        "location": "춘천시 신북읍",
        "entrance_fee": {
            "adult": 3000,
            "teenager": 2000,
            "child": 1000
        },
        "operating_hours": "09:00-18:00",
        "recommended_duration": "1-2시간",
        "parking": {
            "available": True,
            "fee": 0,
            "spaces": 100
        },
        "best_season": ["봄", "가을"],
        "facilities": ["화장실", "매점"],
        "rating": 4.8,
        "distance_from_seoul": "75km (차로 1시간 20분)",
        "coordinates": {"lat": 37.9451, "lng": 127.8678}
    },
    {
        "name": "경포대",
        "category": "명소",
        "location": "강릉시 경포로",
        "entrance_fee": {
            "adult": 0,
            "teenager": 0,
            "child": 0
        },
        "operating_hours": "24시간 (해돋이 명소)",
        "recommended_duration": "2-3시간",
        "parking": {
            "available": True,
            "fee": 2000,
            "spaces": 300
        },
        "best_season": ["여름(해수욕)", "사계절(일출)"],
        "facilities": ["화장실", "샤워장", "산책로"],
        "rating": 4.8,
        "distance_from_seoul": "230km (차로 2시간 40분)",
        "coordinates": {"lat": 37.7956, "lng": 128.9064}
    },
    {
        "name": "설악산국립공원",
        "category": "명소",
        "location": "속초시",
        "entrance_fee": {
            "adult": 3500,
            "teenager": 1000,
            "child": 500
        },
        "operating_hours": "일출 1시간 전 ~ 일몰 1시간 후",
        "recommended_duration": "반나절 ~ 1일",
        "parking": {
            "available": True,
            "fee": 5000,
            "spaces": 400
        },
        "best_season": ["가을(단풍)", "겨울(설경)"],
        "facilities":["케이블카", "식당", "매점", "화장실"],
        "rating": 4.9,
        "distance_from_seoul": "210km (차로 2시간 30분)",
        "coordinates": {"lat": 38.1194, "lng": 128.4656}
    }
]

# 패키지 견적 데이터
PACKAGE_TEMPLATES = [
    {
        "name": "춘천 1박 2일 가족 여행",
        "duration": "1박 2일",
        "group_size": 4,
        "itinerary": [
            {
                "day": 1,
                "schedule": [
                    {"time": "10:00", "activity": "남이섬 도착", "cost": 64000, "notes": "입장료 포함"},
                    {"time": "13:00", "activity": "춘천명물막국수 점심", "cost": 48000, "notes": "4인 기준"},
                    {"time": "15:00", "activity": "소양강스카이워크", "cost": 12000, "notes": "입장료"},
                    {"time": "18:00", "activity": "레이크힐스호텔 체크인", "cost": 180000, "notes": "디럭스룸, 조식 포함"},
                    {"time": "19:00", "activity": "호텔 내 레스토랑 저녁", "cost": 80000, "notes": "4인 기준"}
                ]
            },
            {
                "day": 2,
                "schedule": [
                    {"time": "08:00", "activity": "호텔 조식", "cost": 0, "notes": "숙박 포함"},
                    {"time": "10:00", "activity": "체크아웃", "cost": 0, "notes": ""},
                    {"time": "10:30", "activity": "강촌레일파크", "cost": 60000, "notes": "4인 기준"},
                    {"time": "13:00", "activity": "춘천닭갈비 점심", "cost": 60000, "notes": "4인 기준"}
                ]
            }
        ],
        "total_cost": 504000,
        "cost_per_person": 126000,
        "included": ["숙박(조식 포함)", "입장료", "식사 3회"],
        "excluded": ["개인 경비", "교통비", "간식비"]
    },
    {
        "name": "강릉 2박 3일 커플 여행",
        "duration": "2박 3일",
        "group_size": 2,
        "itinerary": [
            {
                "day": 1,
                "schedule": [
                    {"time": "14:00", "activity": "강릉씨베이호텔 체크인", "cost": 200000, "notes": "오션뷰, 조식 포함"},
                    {"time": "16:00", "activity": "경포해변 산책", "cost": 0, "notes": "무료"},
                    {"time": "18:00", "activity": "해산물 저녁", "cost": 60000, "notes": "2인 기준"}
                ]
            },
            {
                "day": 2,
                "schedule": [
                    {"time": "08:00", "activity": "호텔 조식", "cost": 0, "notes": "숙박 포함"},
                    {"time": "10:00", "activity": "강릉커피거리 투어", "cost": 16000, "notes": "커피+디저트"},
                    {"time": "13:00", "activity": "점심", "cost": 30000, "notes": "2인 기준"},
                    {"time": "15:00", "activity": "정동진 레일바이크", "cost": 35000, "notes": "2인 기준"},
                    {"time": "18:00", "activity": "저녁", "cost": 50000, "notes": "2인 기준"}
                ]
            },
            {
                "day": 3,
                "schedule": [
                    {"time": "08:00", "activity": "호텔 조식", "cost": 0, "notes": "숙박 포함"},
                    {"time": "10:00", "activity": "체크아웃", "cost": 0, "notes": ""},
                    {"time": "10:30", "activity": "선교장 방문", "cost": 10000, "notes": "입장료"},
                    {"time": "12:00", "activity": "점심 후 귀가", "cost": 30000, "notes": "2인 기준"}
                ]
            }
        ],
        "total_cost": 631000,
        "cost_per_person": 315500,
        "included": ["숙박 2박(조식 포함)", "입장료", "일부 식사"],
        "excluded": ["교통비", "개인 경비", "쇼핑비"]
    }
]

# 계절별 추천
SEASONAL_RECOMMENDATIONS = {
    "spring": {
        "attractions": ["남이섬(벚꽃)", "강촌레일파크", "경포대"],
        "activities": ["벚꽃 구경", "자전거 라이딩", "봄나물 축제"],
        "weather_tip": "일교차가 크니 겉옷 준비하세요",
        "recommended_duration": "2박 3일"
    },
    "summer": {
        "attractions": ["경포해변", "속초해수욕장", "남이섬"],
        "activities": ["해수욕", "수상스포츠", "워터파크"],
        "weather_tip": "자외선 차단제와 모자 필수",
        "recommended_duration": "2박 3일"
    },
    "autumn": {
        "attractions": ["설악산", "남이섬(단풍)", "대관령"],
        "activities": ["단풍 구경", "등산", "드라이브"],
        "weather_tip": "등산화와 따뜻한 옷 준비",
        "recommended_duration": "1박 2일 ~ 2박 3일"
    },
    "winter": {
        "attractions": ["평창휘닉스파크", "용평리조트", "정동진(일출)"],
        "activities": ["스키", "스노보드", "눈썰매"],
        "weather_tip": "방한복과 핫팩 필수",
        "recommended_duration": "2박 3일"
    }
}
