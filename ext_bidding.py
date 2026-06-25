"""Erweiterungs-Tools: Ziel-CPA / Ziel-ROAS.
Wird von server.py via Auto-Loader registriert: register(mcp, get_client, DEFAULT_CUSTOMER_ID, DRY_RUN)."""
import json


def register(mcp, get_client, DEFAULT_CUSTOMER_ID, DRY_RUN):
    @mcp.tool()
    def set_campaign_target_cpa(campaign_id: str, target_cpa_eur: float, customer_id: str = "") -> str:
        """Setzt einen Ziel-CPA (EUR) auf eine Kampagne mit Strategie MAXIMIZE_CONVERSIONS.
        Schreibt campaign.maximize_conversions.target_cpa_micros (kein Strategiewechsel).
        target_cpa_eur=0 entfernt das Ziel. Kampagne muss bereits MAXIMIZE_CONVERSIONS nutzen."""
        client = get_client()
        cid = customer_id or DEFAULT_CUSTOMER_ID
        svc = client.get_service("CampaignService")
        op = client.get_type("CampaignOperation")
        camp = op.update
        camp.resource_name = svc.campaign_path(cid, campaign_id)
        camp.maximize_conversions.target_cpa_micros = int(round(target_cpa_eur * 1_000_000))
        op.update_mask.paths.append("maximize_conversions.target_cpa_micros")
        req = client.get_type("MutateCampaignsRequest")
        req.customer_id = cid
        req.operations.append(op)
        req.validate_only = DRY_RUN
        resp = svc.mutate_campaigns(request=req)
        return json.dumps({"dry_run": DRY_RUN, "resource_name": resp.results[0].resource_name if resp.results else None, "campaign_id": campaign_id, "target_cpa_eur": target_cpa_eur})

    @mcp.tool()
    def set_campaign_target_roas(campaign_id: str, target_roas: float, customer_id: str = "") -> str:
        """Setzt einen Ziel-ROAS (z.B. 4.0 = 400 %) auf eine Kampagne mit Strategie MAXIMIZE_CONVERSION_VALUE.
        Schreibt campaign.maximize_conversion_value.target_roas. target_roas=0 entfernt das Ziel.
        Kampagne muss bereits MAXIMIZE_CONVERSION_VALUE nutzen."""
        client = get_client()
        cid = customer_id or DEFAULT_CUSTOMER_ID
        svc = client.get_service("CampaignService")
        op = client.get_type("CampaignOperation")
        camp = op.update
        camp.resource_name = svc.campaign_path(cid, campaign_id)
        camp.maximize_conversion_value.target_roas = target_roas
        op.update_mask.paths.append("maximize_conversion_value.target_roas")
        req = client.get_type("MutateCampaignsRequest")
        req.customer_id = cid
        req.operations.append(op)
        req.validate_only = DRY_RUN
        resp = svc.mutate_campaigns(request=req)
        return json.dumps({"dry_run": DRY_RUN, "resource_name": resp.results[0].resource_name if resp.results else None, "campaign_id": campaign_id, "target_roas": target_roas})
