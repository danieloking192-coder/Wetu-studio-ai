# WETU Monetization Contract

WETU can be distributed as a free app with paid upgrades or subscriptions. Revenue is not guaranteed; the product must keep provider compute cost below the value of paid usage.

## Internal usage units
WETU uses its own units to meter user consumption. These units are independent from OpenArt, Runway, fal.ai, or any other provider credits.

Initial defaults:
- FREE: 30 units/month, 5 generations/day, short video allowance.
- CREATOR: 500 units/month, 40 generations/day.
- PRO: 2,500 units/month, 200 generations/day.

These are product limits, not provider quota promises.

## Cost-control rules
- default delivery: 480p mobile saver;
- 720p for normal mobile use;
- 1080p only when requested or appropriate;
- provider calls are bounded and logged;
- failed generations can refund internal units;
- provider credentials stay server-side;
- no generation starts without a usage reservation.

## Apple
The final iOS build can use free plus in-app purchase/subscription models. Apple commission and eligibility depend on the applicable program and region, so plan entitlements stay separate from payment-provider code until the iOS release stage.
