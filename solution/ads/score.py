from advertisers.models import Campaign, Impression
from clients.models import Client
from score.models import MLScore


def linear_normalization(values: list) -> list:
    min_v, max_v = min(values), max(values)
    return (
        [1.0] * len(values)
        if min_v == max_v
        else [(v - min_v) / (max_v - min_v) for v in values]
    )


def max_normalization(values: list) -> list:
    max_v = max(values) or 1
    return [v / max_v for v in values]


def select_best_campaign(
    client: Client, campaigns: list[Campaign], current_day: int
):
    filtered = [
        campaign
        for campaign in campaigns
        if not Impression.objects.filter(
            client=client, campaign=campaign
        ).exists()
        and campaign.impressions_count <= campaign.impressions_limit * 1.03
    ]

    if not filtered:
        return None

    profits, relevances, limit_factors = [], [], []

    for campaign in filtered:
        ml_score = MLScore.objects.filter(
            client=client,
            advertiser=campaign.advertiser,
        ).first()
        relevances.append(ml_score.score if ml_score else 0)

    max_ml_score = max(relevances) or 1

    for i, campaign in enumerate(filtered):
        click_prob = relevances[i] / max_ml_score

        profit = float(campaign.cost_per_impression) + click_prob * float(
            campaign.cost_per_click
        )
        profits.append(profit)

        progress = campaign.impressions_count / (
            campaign.impressions_limit or 1
        )
        total_days = campaign.end_date - campaign.start_date + 1
        days_left = (campaign.end_date - current_day + 1) / total_days

        if progress < 0.95:
            limit_factor = 1.0 + min(0.85, (0.95 - progress) * days_left)

        elif progress <= 1.0:
            limit_factor = 1.0

        else:
            excess = (progress - 1.0) / 0.01
            limit_factor = max(0, 1.0 - excess * 0.10)

        limit_factors.append(limit_factor)

    if len(filtered) < 10:
        profit_norms = max_normalization(profits)
        relevance_norms = max_normalization(relevances)
    else:
        profit_norms = linear_normalization(profits)
        relevance_norms = linear_normalization(relevances)

    best_campaign, best_score = None, float("-inf")
    for i, campaign in enumerate(filtered):
        score = (
            0.5 * profit_norms[i]
            + 0.25 * relevance_norms[i]
            + 0.15 * limit_factors[i]
        )

        if score > best_score:
            best_score, best_campaign = score, campaign

    return best_campaign
