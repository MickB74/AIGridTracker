# PA DEP data-center tracker sync — 2026-08-21

Source: https://gis.dep.pa.gov/DataCenterPermitTracker/

- DEP projects on file: **57**
- DEP permit records: **108**
- Added to projects.json: **51**
- Refreshed: **0**
- Skipped (already tracked by hand): **6**

## Skipped — hand-written row already covers this

Left alone on purpose. If the DEP row carries detail ours lacks (a permit trail, exact coordinates), fold it in by hand.

- DEP 10000002 *Salem Township Data Center Development (Amazon Web Services)* (Salem Township (Luzerne County)) → `aws-salem-township-pa`
- DEP 10000009 *Falls Township Data Center Development (Amazon Web Services)* (Falls Township (Bucks County)) → `aws-falls-township-pa`
- DEP 10000011 *Pennsylvania Digital 1 (PAX-1) (Pennsylvania Data Center Partners)* (Middlesex Township (Cumberland County)) → `pa-data-center-partners-cumberland-pa`
- DEP 10000014 *Project Phoenix (Aligned Data Centers)* (Shippingport Borough (Beaver County)) → `aligned-shippingport-pa`
- DEP 10000022 *Starpointe Data Center (Prime Data Centers)* (Hanover Township (Washington County)) → `hanover-township-starpointe-pa`
- DEP 10000041 *Smithfield Gateway Project (DEPG Moiser Assoc. LP / DEPG of Shawnee II Assoc. LP)* (Smithfield Township (Monroe County)) → `smithfield-gateway-data-center`

## Added, but worth a second look

These sit in the same municipality as a project we already track under a different name. Usually a genuinely separate campus — Archbald Borough has five — but this is where a duplicate would hide.

- `qts-salem-salem-township-pa` (Salem Township (Luzerne County)) vs `aws-salem-township-pa`
- `pittsburgh-international-race-complex-data-center-big-beaver-borough-pa` (Big Beaver Borough (Beaver County)) vs `powder-mill-works-lawrence-pa`, `aligned-shippingport-pa`
- `4-3-salem-township-data-center-salem-township-pa` (Salem Township (Luzerne County)) vs `aws-salem-township-pa`
- `londonderry-data-center-londonderry-township-pa` (Londonderry Township (Dauphin County)) vs `microsoft-three-mile-island-pa`

## Added

- `project-hazelnut-hazle-township-pa` — Project Hazelnut (NorthPoint Development), Hazle Township (Luzerne County) — 14 permit events
- `project-gravity-archbald-borough-pa` — Project Gravity (Archbald 25 Developer LLC), Archbald Borough (Lackawanna County) — 2 permit events
- `kline-township-data-center-development-kline-township-pa` — Kline Township Data Center Development (Amazon Web Services), Kline Township (Schuylkill County) — 6 permit events
- `project-boson-highway-auto-data-center-archbald-borough-pa` — Project Boson / Highway Auto Data Center (Kriger Construction Company), Archbald Borough (Lackawanna County) — 2 permit events
- `project-atlas-south-whitehall-township-pa` — Project Atlas (Edged US / CDE Acquisitions), South Whitehall Township (Lehigh County) — 4 permit events
- `carbon-node-east-panther-creek-nesquehoning-borough-pa` — Carbon Node East / Panther Creek (Keel Infrastructure), Nesquehoning Borough (Carbon County) — 3 permit events
- `qts-salem-salem-township-pa` — QTS Salem (QTS Data Centers), Salem Township (Luzerne County) — 3 permit events
- `project-forge-data-center-east-whiteland-township-pa` — Project Forge Data Center (Sentinel Green Fig LLC), East Whiteland Township (Chester County) — 2 permit events
- `216-greenfield-road-lancaster-city-pa` — 216 Greenfield Road (Chirisa Technology Parks), Lancaster City (Lancaster County) — 1 permit event
- `homer-city-redevelopment-llc-unnamed-data-center-center-township-pa` — Unnamed Data Center (Homer City Redevelopment LLC), Center Township (Indiana County)
- `highridge-data-center-butler-township-pa` — Highridge Data Center (NorthPoint Development), Butler Township (Schuylkill County) — 3 permit events
- `wyalusing-energy-center-wyalusing-township-pa` — Wyalusing Energy Center (Klondike Digital Infrastructure), Wyalusing Township (Bradford County) — 1 permit event
- `project-hummingbird-monongahela-township-pa` — Project Hummingbird (International Electric Power), Monongahela Township (Greene County)
- `pittsburgh-international-race-complex-data-center-big-beaver-borough-pa` — Pittsburgh International Race Complex Data Center (Wampum I LLC), Big Beaver Borough (Beaver County)
- `springdale-data-center-springdale-borough-pa` — Springdale Data Center (Allegheny DC Property Co. LLC), Springdale Borough (Allegheny County) — 3 permit events
- `keystone-connect-upper-burrell-township-pa` — Keystone Connect (TECfusions), Upper Burrell Township (Westmoreland County) — 5 permit events
- `sharon-data-center-project-city-of-sharon-pa` — Sharon Data Center Project (Keel Infrastructure), City of Sharon (Mercer County) — 1 permit event
- `spring-mountain-quakake-tunnel-spring-mountain-packer-banks-townships-pa` — Spring Mountain Quakake Tunnel (NorthPoint Development), Spring Mountain / Packer / Banks Townships (Carbon County)
- `linde-corporation-unnamed-data-center-clinton-township-pa` — Unnamed Data Center (Linde Corporation), Clinton Township (Wayne County)
- `nescopeck-valley-view-wood-data-center-nescopeck-township-pa` — Nescopeck / Valley View Wood Data Center, Nescopeck Township (Luzerne County)
- `archbald-i-llc-archbald-ii-llc-unnamed-data-centers-archbald-borough-pa` — Unnamed Data Centers (Archbald I LLC / Archbald II LLC), Archbald Borough (Lackawanna County)
- `wildcat-ridge-archbald-borough-pa` — Wildcat Ridge (Pine Line Inc), Archbald Borough (Lackawanna County)
- `patrinely-provident-real-estate-data-center-archbald-borough-pa` — Patrinely-Provident Real Estate Data Center, Archbald Borough (Lackawanna County)
- `lower-mount-bethel-technology-center-lower-mount-bethel-township-pa` — Lower Mount Bethel Technology Center (Peron Development), Lower Mount Bethel Township (Northampton County)
- `river-pointe-data-center-upper-mount-bethel-township-pa` — River Pointe Data Center, Upper Mount Bethel Township (Northampton County)
- `gouldsboro-data-center-project-project-gold-clifton-covington-townships-pa` — Gouldsboro Data Center Project / Project Gold (Quantm Group LLC / 1778 Rich Pike LLC), Clifton / Covington Townships (Lackawanna County)
- `newport-ridge-data-energy-center-newport-township-pa` — Newport Ridge Data & Energy Center, Newport Township (Luzerne County)
- `project-green-mountain-archbald-borough-pa` — Project Green Mountain (Green Mountain 6 LLC), Archbald Borough (Lackawanna County)
- `verdantas-prologis-unnamed-data-center-allen-township-pa` — Unnamed Data Center (Verdantas / Prologis), Allen Township (Northampton County)
- `lbt-investment-group-llc-unnamed-data-center-sugarloaf-township-pa` — Unnamed Data Center (LBT Investment Group LLC), Sugarloaf Township (Luzerne County)
- `emaus-ave-warehouse-city-of-allentown-pa` — Emaus Ave Warehouse (Quantm LLC), City of Allentown (Lehigh County)
- `brewster-land-company-llc-unnamed-data-center-dorrance-township-pa` — Unnamed Data Center (Brewster Land Company LLC), Dorrance Township (Luzerne County)
- `breaker-street-data-center-jessup-borough-pa` — Breaker Street Data Center (Breaker Street Associates LLC), Jessup Borough (Lackawanna County)
- `sunnyside-road-data-center-jessup-borough-pa` — Sunnyside Road Data Center (Sunnyside Road Associates LLC), Jessup Borough (Lackawanna County)
- `pocono-manor-investors-unnamed-data-center-tobyhanna-township-pa` — Unnamed Data Center (Pocono Manor Investors), Tobyhanna Township (Monroe County)
- `west-hazelton-data-center-west-hazelton-borough-pa` — West Hazelton Data Center (One Trinity Real Estate), West Hazelton Borough (Luzerne County)
- `scranton-materials-data-center-ransom-township-pa` — Scranton Materials Data Center, Ransom Township (Lackawanna County)
- `dickson-city-data-center-dickson-city-borough-pa` — Dickson City Data Center (Dickson City Development LLC), Dickson City Borough (Lackawanna County)
- `tekpark-data-center-expansion-upper-macungie-township-pa` — TekPark Data Center Expansion (TierPoint), Upper Macungie Township (Lehigh County)
- `ksr-unnamed-data-center-plains-township-pa` — Unnamed Data Center (KSR), Plains Township (Luzerne County)
- `avison-young-unnamed-data-center-city-of-wilkes-barre-pa` — Unnamed Data Center (Avison Young), City of Wilkes-Barre (Luzerne County)
- `4-3-salem-township-data-center-salem-township-pa` — 4-3 Salem Township Data Center (4-3 Glen Brook Group), Salem Township (Luzerne County)
- `hunlock-data-center-hunlock-township-pa` — Hunlock Data Center (Castleton Commodities), Hunlock Township (Luzerne County)
- `frackville-data-new-caste-township-pa` — Frackville Data (KRNL Data Centers), New Caste Township (Schuylkill County)
- `hendricks-unnamed-data-center-penn-forest-township-pa` — Unnamed Data Center (Hendricks), Penn Forest Township (Carbon County)
- `amazon-web-services-unnamed-data-center-center-township-pa` — Unnamed Data Center (Amazon Web Services), Center Township (Indiana County)
- `fezzik-energy-unnamed-data-center-midland-borough-pa` — Unnamed Data Center (Fezzik Energy), Midland Borough (Beaver County)
- `londonderry-data-center-londonderry-township-pa` — Londonderry Data Center, Londonderry Township (Dauphin County)
- `highlands-east-data-center-lower-swatara-swatara-townships-pa` — Highlands East Data Center, Lower Swatara / Swatara Townships (Dauphin County)
- `highlands-west-data-center-lower-swatara-swatara-townships-pa` — Highlands West Data Center, Lower Swatara / Swatara Townships (Dauphin County)
- `zediker-station-data-center-south-strabane-township-pa` — Zediker Station Data Center (CNX), South Strabane Township (Washington County)

