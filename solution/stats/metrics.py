from prometheus_client import Counter, Gauge

campaign_impressions = Counter(
    "campaign_impressions_total",
    "Общее количество показов кампании",
    ["campaign_id"],
)
campaign_clicks = Counter(
    "campaign_clicks_total",
    "Общее количество кликов по кампании",
    ["campaign_id"],
)
campaign_conversion = Gauge(
    "campaign_conversion", "Конверсия кампании в процентах", ["campaign_id"]
)
campaign_spent_impressions = Gauge(
    "campaign_spent_impressions", "Затраты на показы кампании", ["campaign_id"]
)
campaign_spent_clicks = Gauge(
    "campaign_spent_clicks", "Затраты на клики кампании", ["campaign_id"]
)
campaign_spent_total = Gauge(
    "campaign_spent_total", "Общие затраты на кампанию", ["campaign_id"]
)

campaign_daily_impressions = Counter(
    "campaign_daily_impressions_total",
    "Ежедневное количество показов кампании",
    ["campaign_id", "date"],
)
campaign_daily_clicks = Counter(
    "campaign_daily_clicks_total",
    "Ежедневное количество кликов по кампании",
    ["campaign_id", "date"],
)
campaign_daily_conversion = Gauge(
    "campaign_daily_conversion",
    "Ежедневная конверсия кампании в процентах",
    ["campaign_id", "date"],
)
campaign_daily_spent_impressions = Gauge(
    "campaign_daily_spent_impressions",
    "Ежедневные затраты на показы кампании",
    ["campaign_id", "date"],
)
campaign_daily_spent_clicks = Gauge(
    "campaign_daily_spent_clicks",
    "Ежедневные затраты на клики кампании",
    ["campaign_id", "date"],
)
campaign_daily_spent_total = Gauge(
    "campaign_daily_spent_total",
    "Ежедневные общие затраты на кампанию",
    ["campaign_id", "date"],
)

advertiser_impressions = Counter(
    "advertiser_impressions_total",
    "Общее количество показов рекламодателя",
    ["advertiser_id"],
)
advertiser_clicks = Counter(
    "advertiser_clicks_total",
    "Общее количество кликов рекламодателя",
    ["advertiser_id"],
)
advertiser_conversion = Gauge(
    "advertiser_conversion",
    "Конверсия рекламодателя в процентах",
    ["advertiser_id"],
)
advertiser_spent_total = Gauge(
    "advertiser_spent_total", "Общие затраты рекламодателя", ["advertiser_id"]
)

advertiser_daily_impressions = Counter(
    "advertiser_daily_impressions_total",
    "Ежедневное количество показов рекламодателя",
    ["advertiser_id", "date"],
)
advertiser_daily_clicks = Counter(
    "advertiser_daily_clicks_total",
    "Ежедневное количество кликов рекламодателя",
    ["advertiser_id", "date"],
)
advertiser_daily_conversion = Gauge(
    "advertiser_daily_conversion",
    "Ежедневная конверсия рекламодателя в процентах",
    ["advertiser_id", "date"],
)
advertiser_daily_spent_total = Gauge(
    "advertiser_daily_spent_total",
    "Ежедневные общие затраты рекламодателя",
    ["advertiser_id", "date"],
)
