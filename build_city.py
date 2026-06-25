"""
Wiederverwendbarer Builder: Search-Kampagne (3 fokussierte Anzeigengruppen
Lippen/Jawline/Profhilo) fuer eine Stadt anlegen.
VALIDATE=1 -> nur validieren (validate_only), keine echten Writes.
Brand-Ausschluss laeuft bereits konto-weit (account-level negative list).
Fokus Neukunden: Search-CustomerAcquisition (optimize, ohne Bestandskunden-Bonus) wird gesetzt, falls moeglich.
"""
import os, server

VALIDATE = os.environ.get("VALIDATE", "0") == "1"
c = server.get_client()
cid = server.DEFAULT_CUSTOMER_ID

# ---- Stadt-Konfiguration (Aachen) ----
CITY = "Aachen"
GEO_ID = "1004576"           # Aachen City
DAILY_EUR = 80.0
LANGS = ["1000", "1001"]      # DE, EN
BASE = "https://go.myhealthandbeauty.com/standorte/aachen/aquis-plaza"

ADGROUPS = {
    "Lippen": {
        "url": f"{BASE}/hyaluron/lippen-aufspritzen",
        "path1": "aachen", "path2": "lippen",
        "keywords": {
            "EXACT": ["lippen aufspritzen aachen", "lippen aufspritzen", "lippenunterspritzung",
                      "hyaluron lippen", "lip filler aachen", "russian lips aachen"],
            "PHRASE": ["lippen aufspritzen kosten", "lippen aufspritzen preise", "lippen vergroessern",
                       "lippen aufspritzen lassen", "hyaluron lippen aachen", "lippen mit hyaluron",
                       "russian lips", "lippenkontur hyaluron"],
        },
        "headlines": ["Lippen aufspritzen Aachen", "Lippenunterspritzung 149€", "Hyaluron Lippen Aachen",
                      "Lippen aufspritzen ab 149€", "Russian Lips Aachen", "Lippen vergrößern Aachen",
                      "Natürlich vollere Lippen", "Durchgeführt von Ärzten", "Über 40.000 Kunden",
                      "Kostenlose Beratung", "Jetzt Termin buchen", "Aquis Plaza Aachen",
                      "Premium Hyaluronsäure", "Sanfte Behandlung", "Termin online buchen"],
        "descriptions": [
            "Natürlich vollere Lippen mit hochwertiger Hyaluronsäure in Aachen – ab 149€.",
            "Hochwertige Lippenbehandlung von erfahrenen, zertifizierten Ärzten in Aachen.",
            "Lippen aufspritzen ab 149€ im Aquis Plaza Aachen – jetzt Termin sichern!",
            "Über 40.000 glückliche Kunden. Kostenlose Beratung – jetzt online buchen.",
        ],
    },
    "Jawline": {
        "url": f"{BASE}/hyaluron/jawline",
        "path1": "aachen", "path2": "jawline",
        "keywords": {
            "EXACT": ["jawline aachen", "jawline filler", "jawline unterspritzen", "kinnaufbau",
                      "jawline aufbau", "kinn aufspritzen"],
            "PHRASE": ["jawline hyaluron", "kinnaufbau hyaluron", "jawline aufspritzen",
                       "kinnkorrektur ohne op", "kinn unterspritzen", "jawline mit hyaluron",
                       "jawline kosten"],
        },
        "headlines": ["Jawline Aachen ab 199€", "Jawline Filler Aachen", "Jawline unterspritzen",
                      "Kinnaufbau mit Hyaluron", "Jawline & Kinnaufbau", "Jawline ab 199€",
                      "Kinnkorrektur ohne OP", "Konturierte Jawline", "Durchgeführt von Ärzten",
                      "Über 40.000 Kunden", "Kostenlose Beratung", "Jetzt Termin buchen",
                      "Jawline Hyaluron Aachen", "Aquis Plaza Aachen", "Termin online buchen"],
        "descriptions": [
            "Definierte Jawline mit hochwertiger Hyaluronsäure in Aachen – ab 199€.",
            "Hochwertige Jawline-Filler von erfahrenen, zertifizierten Ärzten in Aachen.",
            "Jawline & Kinnaufbau ab 199€ im Aquis Plaza Aachen – jetzt Termin sichern!",
            "Über 40.000 glückliche Kunden. Kostenlose Beratung – jetzt online buchen.",
        ],
    },
    "Profhilo": {
        "url": f"{BASE}/skinbooster/profhilo",
        "path1": "aachen", "path2": "profhilo",
        "keywords": {
            "EXACT": ["profhilo aachen", "profhilo", "profhilo behandlung", "skinbooster aachen"],
            "PHRASE": ["profhilo kosten", "profhilo behandlung kosten", "profhilo hals",
                       "profhilo hyaluron", "skinbooster", "biorevitalisierung", "profhilo preis"],
        },
        "headlines": ["Profhilo Aachen ab 299€", "Profhilo Behandlung 299€", "Profhilo Filler Aachen",
                      "Profhilo Preis ab 299€", "Skinbooster Aachen", "Profhilo für den Hals",
                      "Hautverjüngung Aachen", "Zertifizierte Ärzte", "Intensive ärztl. Analyse",
                      "Über 40.000 Kunden", "Kostenlose Beratung", "Jetzt Termin buchen",
                      "Profhilo Hyaluron 299€", "Aquis Plaza Aachen", "Termin online buchen"],
        "descriptions": [
            "Strahlende, festere Haut mit Profhilo in Aachen – ab 299€.",
            "Hochwertige Profhilo-Behandlung von erfahrenen, zertifizierten Ärzten in Aachen.",
            "Profhilo ab 299€ im Aquis Plaza Aachen – jetzt Termin sichern!",
            "Über 40.000 glückliche Kunden. Kostenlose Beratung – jetzt online buchen.",
        ],
    },
}

def vlimit(items, n, what):
    bad = [x for x in items if len(x) > n]
    if bad:
        raise SystemExit(f"!! {what}: zu lang (>{n}): {bad}")

# Pre-Check Laengen
for ag, cfg in ADGROUPS.items():
    vlimit(cfg["headlines"], 30, f"{ag} headlines")
    vlimit(cfg["descriptions"], 90, f"{ag} descriptions")
    if len(cfg["path1"]) > 15 or len(cfg["path2"]) > 15:
        raise SystemExit(f"!! {ag} path zu lang")
print("Laengen-Check OK")

# ---- 1) Budget (vorhandenes wiederverwenden, sonst neu) ----
bsvc = c.get_service("CampaignBudgetService")
ga = c.get_service("GoogleAdsService")
EXISTING_BUDGET = os.environ.get("BUDGET_ID", "").strip()
if EXISTING_BUDGET:
    budget_rn = bsvc.campaign_budget_path(cid, EXISTING_BUDGET)
    print("Budget (wiederverwendet):", budget_rn)
else:
    bop = c.get_type("CampaignBudgetOperation")
    b = bop.create
    b.name = f"Search | {CITY} | Pilot (Lippen/Jawline/Profhilo) {os.environ.get('STAMP','')}"
    b.amount_micros = int(DAILY_EUR * 1_000_000)
    b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
    b.explicitly_shared = False
    breq = c.get_type("MutateCampaignBudgetsRequest")
    breq.customer_id = cid; breq.operations.append(bop); breq.validate_only = VALIDATE
    bres = bsvc.mutate_campaign_budgets(request=breq)
    budget_rn = bres.results[0].resource_name
    print("Budget:", budget_rn)

# ---- 2) Kampagne (vorhandene wiederverwenden, sonst neu) ----
csvc = c.get_service("CampaignService")
EXISTING_CAMP = os.environ.get("CAMPAIGN_ID", "").strip()
if EXISTING_CAMP:
    camp_rn = csvc.campaign_path(cid, EXISTING_CAMP)
    print("Kampagne (wiederverwendet):", camp_rn)
else:
    cop = c.get_type("CampaignOperation")
    camp = cop.create
    camp.name = f"Search | {CITY} | Pilot | Lippen/Jawline/Profhilo"
    camp.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.SEARCH
    camp.status = c.enums.CampaignStatusEnum.PAUSED  # erst PAUSED, scharf nach Verifikation
    camp.campaign_budget = budget_rn
    camp.maximize_conversions = c.get_type("MaximizeConversions")
    camp.bidding_strategy_type = c.enums.BiddingStrategyTypeEnum.MAXIMIZE_CONVERSIONS
    ns = camp.network_settings
    ns.target_google_search = True
    ns.target_search_network = True      # Suchnetzwerk-Partner
    ns.target_content_network = False    # Display AUS (sauberer Search-Intent)
    ns.target_partner_search_network = False
    camp.geo_target_type_setting.positive_geo_target_type = c.enums.PositiveGeoTargetTypeEnum.PRESENCE_OR_INTEREST
    camp.geo_target_type_setting.negative_geo_target_type = c.enums.NegativeGeoTargetTypeEnum.PRESENCE
    camp.contains_eu_political_advertising = c.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    creq = c.get_type("MutateCampaignsRequest")
    creq.customer_id = cid; creq.operations.append(cop); creq.validate_only = VALIDATE
    cres = csvc.mutate_campaigns(request=creq)
    camp_rn = cres.results[0].resource_name
    print("Kampagne:", camp_rn)

# ---- 3) Geo + Sprache ----
cc_svc = c.get_service("CampaignCriterionService")
geo_svc = c.get_service("GeoTargetConstantService")
crit_ops = []
# Geo
op = c.get_type("CampaignCriterionOperation")
op.create.campaign = camp_rn
op.create.location.geo_target_constant = geo_svc.geo_target_constant_path(GEO_ID)
crit_ops.append(op)
# Sprachen
for lg in LANGS:
    op = c.get_type("CampaignCriterionOperation")
    op.create.campaign = camp_rn
    op.create.language.language_constant = f"languageConstants/{lg}"
    crit_ops.append(op)
ccreq = c.get_type("MutateCampaignCriteriaRequest")
ccreq.customer_id = cid; ccreq.operations.extend(crit_ops); ccreq.validate_only = VALIDATE
cc_svc.mutate_campaign_criteria(request=ccreq)
print("Geo+Sprache gesetzt")

if VALIDATE:
    print("VALIDATE-Modus: Ad-Groups/Keywords/Ads benoetigen echte campaign_rn -> uebersprungen im Validate.")
    raise SystemExit(0)

# ---- 4) Ad Groups + Keywords + RSAs ----
ag_svc = c.get_service("AdGroupService")
agc_svc = c.get_service("AdGroupCriterionService")
aga_svc = c.get_service("AdGroupAdService")
results = {}
for agname, cfg in ADGROUPS.items():
    # Ad Group
    agop = c.get_type("AdGroupOperation")
    ag = agop.create
    ag.name = agname
    ag.campaign = camp_rn
    ag.type_ = c.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ag.status = c.enums.AdGroupStatusEnum.ENABLED
    agreq = c.get_type("MutateAdGroupsRequest")
    agreq.customer_id = cid; agreq.operations.append(agop)
    ag_rn = ag_svc.mutate_ad_groups(request=agreq).results[0].resource_name
    ag_id = ag_rn.split("/")[-1]

    # Keywords
    kops = []
    for mt, kws in cfg["keywords"].items():
        for kw in kws:
            kop = c.get_type("AdGroupCriterionOperation")
            kc = kop.create
            kc.ad_group = ag_rn
            kc.status = c.enums.AdGroupCriterionStatusEnum.ENABLED
            kc.keyword.text = kw
            kc.keyword.match_type = c.enums.KeywordMatchTypeEnum[mt]
            kops.append(kop)
    kreq = c.get_type("MutateAdGroupCriteriaRequest")
    kreq.customer_id = cid; kreq.operations.extend(kops)
    nkw = len(agc_svc.mutate_ad_group_criteria(request=kreq).results)

    # RSA
    adop = c.get_type("AdGroupAdOperation")
    aga = adop.create
    aga.ad_group = ag_rn
    aga.status = c.enums.AdGroupAdStatusEnum.ENABLED
    ad = aga.ad
    ad.final_urls.append(cfg["url"])
    rsa = ad.responsive_search_ad
    rsa.path1 = cfg["path1"]; rsa.path2 = cfg["path2"]
    rsa.headlines.extend([server._text_asset(c, h) for h in cfg["headlines"]])
    rsa.descriptions.extend([server._text_asset(c, d) for d in cfg["descriptions"]])
    adreq = c.get_type("MutateAdGroupAdsRequest")
    adreq.customer_id = cid; adreq.operations.append(adop)
    ad_rn = aga_svc.mutate_ad_group_ads(request=adreq).results[0].resource_name
    results[agname] = {"ad_group_id": ag_id, "keywords": nkw, "ad": ad_rn.split("/")[-1]}
    print(f"  AG {agname}: id={ag_id} kws={nkw} ad={ad_rn.split('/')[-1]}")

print("\nFERTIG. campaign_id:", camp_rn.split("/")[-1])
print("RESULTS:", results)
