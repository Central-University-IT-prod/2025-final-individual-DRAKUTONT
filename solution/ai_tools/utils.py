from django.conf import settings
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.auth import APIKeyAuth


def send_request(system_text: str, user_text: str, temperature: float):
    sdk = YCloudML(
        folder_id=settings.YANDEX_GPT_CATALOG_ID,
        auth=APIKeyAuth(settings.YANDEX_GPT_API_KEY),
    )

    messages = [
        {
            "role": "system",
            "text": system_text,
        },
        {
            "role": "user",
            "text": user_text,
        },
    ]

    model = sdk.models.completions(settings.YANDEX_GPT_MODEL_TYPE)
    model = model.configure(temperature=temperature)
    return model.run(messages)


def moderation_ad_text(ad_text: str) -> bool:
    result = send_request(
        system_text=settings.MODERATION_PROMT,
        user_text=ad_text,
        temperature=0.1,
    )

    return result.alternatives[0].text == "Текст прошел валидацию"


def generation_ad_text(
    product_name: str,
    target_action: str,
    target_audience: str,
) -> dict:
    promt = (
        f"Продукт/услуга: {product_name}."
        f"Целевое действие: {target_action}."
        f"Целевая аудитория: {target_audience}."
    )
    result = send_request(
        system_text=settings.GENERATION_PROMT,
        user_text=promt,
        temperature=0.3,
    )

    return result.alternatives[0].text
