

def generate_product_adjust_url(base_url, influencer_id, post_id,user_id,item_id, date):
    base_adjust_url = "https://app.adjust.com/5uoyix8"
    deep_link = f"underarmour://{base_url.split('https://www.underarmour.com.tr/')[-1]}"
    utm_source = "influencer"
    utm_medium = "affiliate"
    utm_campaign = f"{influencer_id}-{post_id}-{user_id}-{item_id}_{date}"
    adgroup = utm_campaign
    adj_campaign = utm_campaign
    redirect_url = f"{base_url}?utm_source={utm_source}&utm_medium={utm_medium}&utm_campaign={utm_campaign}"

    adjust_url = (
        f"{base_adjust_url}?"
        f"deep_link={deep_link}&"
        f"utm_source={utm_source}&"
        f"utm_medium={utm_medium}&"
        f"utm_campaign={utm_campaign}&"
        f"adgroup={adgroup}&"
        f"adj_campaign={adj_campaign}&"
        f"redirect={redirect_url}"
    )

    return adjust_url

