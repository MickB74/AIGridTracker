"""
Documented records of sitting U.S. senators on AI data centers.

Generated from a researched review queue and curated by hand: every item was
opened at its source URL and confirmed to name the senator doing or saying
the thing. Same rules as src/senate_races.py: full-name keys, per-item
source + date, `lean` summarises only the cited items, silence is absent
here rather than recorded as neutral. `kind` separates an *action* (bill,
letter, hearing question, investigation) from a *statement* (quote, op-ed,
campaign line) — the senators page renders them apart, and only actions are
ever graded on the officials scorecard (src/official_grades.py).

Items dropped in curation, so nobody re-adds them: Sen. Sheehy's X post
(only Townhall carried it), Sen. Kennedy's interchange earmark (not a
position), and Sen. Risch's ARC Act release (the data-center language there
is from endorsing groups, not the senator), and Sen. Kaine's press-availability
quote as carried by Blue Virginia (a partisan blog; his E&E News quote stands).
"""

SENATOR_RECORDS = {('AK', 'Lisa Murkowski'): {'lean': 'mixed',
                            'summary': 'Murkowski co-introduced the 2024 Department of '
                                       'Energy AI Act, which directs DOE to study the '
                                       'growth of computing data centers and their '
                                       'electrical load; no 2025-2026 statement on '
                                       'data center siting, cost or water was located.',
                            'items': [{'what': 'Introduced the Department of Energy AI '
                                               'Act with Sen. Joe Manchin; the bill '
                                               'directs DOE to "study the growth of '
                                               'computing data centers and the '
                                               'electrical power load." Her quoted '
                                               'remarks concern AI for science and '
                                               'permitting, not data centers.',
                                       'date': '2024-07-10',
                                       'source': 'https://www.murkowski.senate.gov/press/release/murkowski-manchin-introduce-bipartisan-legislation-to-advance-department-of-energy-ai-research-for-science-security-and-technology',
                                       'source_name': 'Sen. Murkowski press release',
                                       'kind': 'action'}],
                            'as_of': '2026-09-05'},
 ('AK', 'Dan Sullivan'): {'lean': 'accelerate',
                          'summary': 'Sullivan told the Alaska Legislature in February '
                                     '2026 he is pressing for federal AI data centers '
                                     'on Air Force bases in Alaska, and in August 2026 '
                                     'said a rumored Navy data center at Spruce Cape, '
                                     'Kodiak, would be "a bad idea" he would work to '
                                     'stop.',
                          'items': [{'what': 'In his annual address to the Alaska '
                                             'Legislature, said he is pressing for '
                                             '"new federal data centers on Air Force '
                                             'bases in Alaska for AI computing," which '
                                             'he said would help the military, raise '
                                             'domestic demand for Alaska gas and lower '
                                             'the cost of building and financing the '
                                             'gas pipeline; noted the Air Force had '
                                             'issued a request for information on '
                                             'Alaska data centers the day before at '
                                             'his urging.',
                                     'date': '2026-02-18',
                                     'source': 'https://www.sullivan.senate.gov/newsroom/press-releases/sullivan-touts-alaska-comeback-historic-opportunities-in-annual-address-to-legislature',
                                     'source_name': 'Sen. Sullivan press release '
                                                    '(address to Legislature)',
                                     'kind': 'statement'},
                                    {'what': 'Asked in Kodiak about a rumored Navy '
                                             'data center at the Naval Special Warfare '
                                             'detachment on Spruce Cape, said "I had '
                                             'never heard of that issue until last '
                                             'week," "I think it\'s a rumor," and "if '
                                             "it's true, I think it's a bad idea and I "
                                             'will work to stop it."',
                                     'date': '2026-08-12',
                                     'source': 'https://www.kodiakdailymirror.com/news/article_44944d6a-cbd1-4a30-bc5b-0585dbea48eb.html',
                                     'source_name': 'Kodiak Daily Mirror',
                                     'kind': 'statement'}],
                          'as_of': '2026-09-05'},
 ('AL', 'Katie Boyd Britt'): {'lean': 'guardrails',
                              'summary': 'Britt co-sponsors the Advancing Water Reuse '
                                         'Act (S. 3585) with Sen. Luján, which would '
                                         'create a 30% tax credit for on-site water '
                                         'recycling including at data centers; says '
                                         'siting decisions belong at the local level, '
                                         'opposes both a moratorium and "a data center '
                                         'on every corner," and wants the Trump '
                                         "administration's voluntary Ratepayer "
                                         'Protection Pledge turned into law.',
                              'items': [{'what': 'Introduced the Advancing Water Reuse '
                                                 'Act (S. 3585) with Sen. Ben Ray '
                                                 'Luján (D-NM): a tax credit for '
                                                 'on-site water recycling at '
                                                 '"manufacturing, food processing, and '
                                                 'other industrial entities, including '
                                                 'data center facilities"; Britt\'s '
                                                 'statement cites water demand from '
                                                 '"advanced manufacturing, artificial '
                                                 'intelligence, and other growth '
                                                 'industries."',
                                         'date': '2026-05-13',
                                         'source': 'https://www.lujan.senate.gov/newsroom/press-releases/lujan-britt-unveil-bipartisan-bill-to-boost-industrial-water-reuse-protect-community-drinking-water-and-meet-public-and-private-demand-for-freshwater/',
                                         'source_name': 'Sen. Luján press release '
                                                        '(joint with Britt)',
                                         'kind': 'action'},
                                        {'what': 'Said data center decisions "need to '
                                                 'be made on a local level," that '
                                                 'communities that reject a proposal '
                                                 '"shouldn\'t be forced" to proceed, '
                                                 'and that neither "a data center on '
                                                 'every corner" nor "a full '
                                                 'moratorium" is the right avenue; '
                                                 'backs the White House Ratepayer '
                                                 'Protection Pledge.',
                                         'date': '2026-08-20',
                                         'source': 'https://aldailynews.com/britt-wants-to-find-a-middle-ground-on-data-centers/',
                                         'source_name': 'Alabama Daily News',
                                         'kind': 'statement'},
                                        {'what': "Defended the Trump administration's "
                                                 'nonbinding Ratepayer Protection '
                                                 'Pledge as "an outstanding first step '
                                                 'to protecting Alabamians and '
                                                 'ratepayers," and said communities '
                                                 'should weigh "the amount of power '
                                                 'that\'s taken" against tax revenue.',
                                         'date': '2026-09-01',
                                         'source': 'https://www.alreporter.com/2026/09/01/britt-talks-data-center-accountability-defends-trump-admin-ratepayer-pledge/',
                                         'source_name': 'Alabama Political Reporter',
                                         'kind': 'statement'},
                                        {'what': 'Told Semafor she would "love to see" '
                                                 'the Ratepayer Protection Pledge '
                                                 '"turned into law," and that "we do '
                                                 'not need a national moratorium, and '
                                                 'we do not need a data center on '
                                                 'every corner."',
                                         'date': '2026-09-04',
                                         'source': 'https://www.semafor.com/article/09/04/2026/britt-congress-should-turn-trumps-data-center-pledge-into-law',
                                         'source_name': 'Semafor',
                                         'kind': 'statement'}],
                              'as_of': '2026-09-05'},
 ('AL', 'Tommy Tuberville'): {'lean': 'mixed',
                              'summary': 'Tuberville, running for Alabama governor, '
                                         'has defended data centers and attributed '
                                         'local opposition to Chinese social-media '
                                         'influence, and in a September 2026 op-ed '
                                         'said local communities should decide whether '
                                         'to host one, data centers should sit in '
                                         "Alabama's highest property-tax bracket and "
                                         'pay the full cost of transmission, '
                                         'substations and water systems, and he would '
                                         'freeze Alabama Power rates.',
                              'items': [{'what': 'Campaigning at an Alabama Sheriffs '
                                                 'Association event, said opponents '
                                                 '"are listening to all this nonsense '
                                                 "they see on social media that's "
                                                 'coming from China because China does '
                                                 'not want us to grow," called '
                                                 'environmental and noise objections '
                                                 '"bull crap," and touted data center '
                                                 'tax revenue for schools and law '
                                                 'enforcement.',
                                         'date': '2026-07-14',
                                         'source': 'https://www.wbrc.com/2026/07/15/tuberville-reaffirms-data-center-support-says-opposition-driven-by-china/',
                                         'source_name': 'WBRC',
                                         'kind': 'statement'},
                                        {'what': 'Op-ed "My game plan for data '
                                                 'centers": "Local communities will '
                                                 'decide whether a data center is '
                                                 'right for them"; data centers go in '
                                                 '"Alabama\'s highest property-tax '
                                                 'bracket" with no abatements; '
                                                 'companies must "pay the total cost '
                                                 'of the transmission lines, '
                                                 'substations and water systems" they '
                                                 'need; pledges to freeze Alabama '
                                                 'Power rates through 2029 and beyond.',
                                         'date': '2026-09-01',
                                         'source': 'https://www.alreporter.com/2026/09/01/opinion-my-game-plan-for-data-centers/',
                                         'source_name': 'Alabama Political Reporter '
                                                        '(Tuberville op-ed)',
                                         'kind': 'statement'}],
                              'as_of': '2026-09-05'},
 ('AR', 'John Boozman'): {'lean': 'accelerate',
                          'summary': 'At a January 2026 EPW permitting-reform hearing '
                                     'Boozman cited the multi-billion-dollar West '
                                     'Memphis data center as an investment Arkansas '
                                     'landed because of "a reliable, affordable, and '
                                     'an all-the-above energy supply"; no position on '
                                     'who pays for data center power was located.',
                          'items': [{'what': 'At a Senate Environment and Public Works '
                                             'hearing on permitting reform, '
                                             'highlighted AI and cloud investments '
                                             'including the West Memphis data center '
                                             'and said "Arkansas was able to land '
                                             'these investments in part because of a '
                                             'reliable, affordable, and an '
                                             'all-the-above energy supply, including '
                                             'solar energy," backing permitting '
                                             'reform.',
                                     'date': '2026-01-29',
                                     'source': 'https://www.boozman.senate.gov/public/index.cfm/2026/1/boozman-backs-commonsense-permitting-reform-cites-arkansas-leadership',
                                     'source_name': 'Sen. Boozman press release (EPW '
                                                    'hearing)',
                                     'kind': 'statement'}],
                          'as_of': '2026-09-05'},
 ('AR', 'Tom Cotton'): {'lean': 'mixed',
                        'summary': 'Cotton introduced the DATA Act of 2026 to let data '
                                   'centers and other energy-intensive industries '
                                   'build off-grid electricity systems exempt from '
                                   'certain Federal Power Act regulation so their load '
                                   "does not raise Arkansans' bills, and in June 2026 "
                                   'asked DOJ to investigate alleged Chinese-backed '
                                   'funding of opposition to data center development '
                                   "while acknowledging residents' cost and resource "
                                   'concerns are valid.',
                        'items': [{'what': 'Introduced the DATA Act of 2026, which '
                                           'would exempt new isolated electricity '
                                           'generation and supply systems built to '
                                           'serve new loads (manufacturers, data '
                                           'centers and other energy-intensive '
                                           'industries) from certain federal '
                                           'regulation so they can operate independent '
                                           'of the existing grid. Cotton: "American '
                                           'dominance in artificial intelligence and '
                                           'other crucial emerging industries should '
                                           'not come at the expense of Arkansans '
                                           'paying higher energy costs."',
                                   'date': '2026-01-08',
                                   'source': 'https://www.cotton.senate.gov/news/press-releases/cotton-introduces-bill-to-lower-energy-costs-for-arkansans',
                                   'source_name': 'Sen. Cotton press release',
                                   'kind': 'action'},
                                  {'what': 'Wrote Acting Attorney General Todd Blanche '
                                           'asking DOJ to investigate alleged Chinese '
                                           'Communist Party-linked funding of U.S. '
                                           'nonprofits producing anti-data-center '
                                           'content, while stating "Americans '
                                           'certainly have valid concerns about '
                                           'potential rising energy costs and strains '
                                           'on natural resources related to data '
                                           'centers" but "we can\'t allow any effort '
                                           'by foreign adversaries to extort these '
                                           'fears and undermine our technological '
                                           'development."',
                                   'date': '2026-06-10',
                                   'source': 'https://www.cotton.senate.gov/news/press-releases/cotton-to-doj-investigate-communist-china-influence-on-data-center-development',
                                   'source_name': 'Sen. Cotton press release',
                                   'kind': 'action'}],
                        'as_of': '2026-09-05'},
 ('AZ', 'Ruben Gallego'): {'lean': 'guardrails',
                           'summary': 'Gallego calls data centers a "necessary evil" '
                                      'for AI competition but says residents "should '
                                      'be held harmless" on electricity bills, backs '
                                      "rolling back Arizona's data center tax "
                                      'exemption, and in December 2025 said a '
                                      'hyperscaler drawing heavy load should pay the '
                                      'differential rather than residents and small '
                                      'businesses.',
                           'items': [{'what': 'On the Volts podcast discussing his '
                                              'energy plan, said that if data centers '
                                              'strain the grid "the resident and the '
                                              'small business owner should not be '
                                              'having to pay the differential caused '
                                              'by these companies," that legislation '
                                              'should ensure "the individual consumer '
                                              'will be held harmless" while the '
                                              'large-load customer pays the '
                                              'difference, and that data centers '
                                              'should "bring your own energy" such as '
                                              'SMRs rather than restarting old coal or '
                                              'gas plants.',
                                      'date': '2025-12-17',
                                      'source': 'https://www.volts.wtf/p/sen-ruben-gallego-has-a-new-energy',
                                      'source_name': 'Volts (David Roberts) podcast '
                                                     'transcript',
                                      'kind': 'statement'},
                                     {'what': 'Announcing his energy plan, said '
                                              'utilities are mostly regulated at the '
                                              'state and local level but the "federal '
                                              'government can invest in technology to '
                                              'divert energy from data centers during '
                                              'lulls in demand."',
                                      'date': '2025-12-04',
                                      'source': 'https://news.azpm.org/p/azpmnews/2025/12/4/227532-sen-gallego-proposes-slate-of-energy-policies-focusing-on-cost-and-reliability/',
                                      'source_name': 'AZPM',
                                      'kind': 'statement'},
                                     {'what': 'Told reporters in Phoenix data centers '
                                              'are a "necessary evil" for the AI race '
                                              'but "Your local resident should be held '
                                              "harmless. We shouldn't be paying more "
                                              'in electricity bills because data '
                                              'centers are here"; called for rolling '
                                              "back Arizona's 2013 data center tax "
                                              'exemption, said some data centers "end '
                                              'up paying, on average, less than some '
                                              'of the homeowners who are right next to '
                                              'them," and "I fear that we may not have '
                                              'enough water and we may not have enough '
                                              'power generation to be able to hold '
                                              'harmless everyone else."',
                                      'date': '2026-05-07',
                                      'source': 'https://www.phoenixnewtimes.com/news/arizona-sen-gallego-supports-nixing-tax-breaks-data-centers-40665119/',
                                      'source_name': 'Phoenix New Times',
                                      'kind': 'statement'},
                                     {'what': 'Co-leads (with Padilla, Hickenlooper, '
                                              'Cortez Masto, King) a draft Senate '
                                              'Energy Democrats transmission bill '
                                              'expanding FERC transmission authority; '
                                              "the senators' release does not mention "
                                              'data centers, though press coverage '
                                              'frames it as addressing AI data center '
                                              'demand.',
                                      'date': '2026-03-25',
                                      'source': 'https://www.padilla.senate.gov/newsroom/press-releases/watch-padilla-unveils-new-effort-to-lower-energy-costs-strengthen-transmission-lines/',
                                      'source_name': 'Sen. Padilla press release',
                                      'kind': 'action'}],
                           'as_of': '2026-09-05'},
 ('AZ', 'Mark Kelly'): {'lean': 'guardrails',
                        'summary': 'Kelly signed a February 2025 letter asking FERC to '
                                   'convene a technical conference on data center load '
                                   'and affordable rates, released an "AI for America" '
                                   'roadmap in September 2025 proposing an '
                                   'industry-funded AI Horizon Fund partly to keep '
                                   'electricity costs off households, and in March '
                                   '2026 previewed legislation to bring communities '
                                   'into data center siting with enforceable '
                                   'commitments and utility-rate protections.',
                        'items': [{'what': 'Co-signed a letter (with Sens. Van Hollen, '
                                           'Booker and Kaine) asking FERC to "host a '
                                           'technical conference" on ensuring '
                                           'sufficient new generation for data center '
                                           'demand while keeping rates affordable and '
                                           'respecting state energy policy.',
                                   'date': '2025-02-14',
                                   'source': 'https://www.vanhollen.senate.gov/news/press-releases/van-hollen-colleagues-call-on-ferc-to-ensure-affordable-reliable-electricity-service-for-americans-amid-rising-energy-demands-of-data-centers',
                                   'source_name': 'Sen. Van Hollen press release',
                                   'kind': 'action'},
                                  {'what': 'Released the "AI for America" roadmap, '
                                           'noting data center power use could reach '
                                           'up to 12% of national electricity demand '
                                           'and proposing an AI Horizon Fund financed '
                                           'by AI companies; "As AI companies thrive, '
                                           'they must be good partners and invest in '
                                           'our workers, our economy, and our energy '
                                           'future."',
                                   'date': '2025-09-17',
                                   'source': 'https://www.kelly.senate.gov/newsroom/press-releases/kelly-releases-ai-for-america-a-roadmap-to-make-ai-work-for-all-americans-not-just-big-companies/',
                                   'source_name': 'Sen. Kelly press release',
                                   'kind': 'statement'},
                                  {'what': 'At the American AI Festival previewed '
                                           'unnamed legislation to "Bring developers '
                                           'and communities together at the beginning '
                                           'to work through the details—what a project '
                                           'means for energy, water, infrastructure, '
                                           'and jobs—and put real commitments on the '
                                           'table," with public input, enforceable '
                                           'agreements, local hiring and utility-rate '
                                           'protections.',
                                   'date': '2026-03-27',
                                   'source': 'https://www.kelly.senate.gov/newsroom/press-releases/icymi-at-american-ai-festival-kelly-previews-new-legislation-to-bring-communities-in-as-ai-infrastructure-expands/',
                                   'source_name': 'Sen. Kelly press release',
                                   'kind': 'statement'}],
                        'as_of': '2026-09-05'},
 ('CA', 'Adam B. Schiff'): {'lean': 'guardrails',
                            'summary': 'Schiff introduced the Energy Cost Fairness and '
                                       'Reliability Act in May 2026 to make large-load '
                                       'facilities such as data centers pay 100% of '
                                       'the grid upgrades needed to serve them, show '
                                       'demand flexibility and bring their own '
                                       'generation before connecting.',
                            'items': [{'what': 'Introduced the Energy Cost Fairness '
                                               'and Reliability Act: large-load '
                                               'facilities pay 100% of network upgrade '
                                               'costs, must demonstrate demand '
                                               'flexibility and provide their own '
                                               'power to interconnect, FERC to enable '
                                               'non-firm transmission service, and '
                                               'stronger interconnection screening '
                                               'against speculative projects. Schiff: '
                                               '"Hard-working Americans should not be '
                                               'left to foot the tab for rising energy '
                                               'costs. There needs to be guardrails '
                                               'that protect Americans\' pocketbooks."',
                                       'date': '2026-05-18',
                                       'source': 'https://www.schiff.senate.gov/news/press-releases/news-sen-schiff-unveils-major-legislation-to-ensure-fair-and-affordable-energy-costs-for-americans-amid-data-center-buildouts/',
                                       'source_name': 'Sen. Schiff press release',
                                       'kind': 'action'}],
                            'as_of': '2026-09-05'},
 ('CO', 'Michael F. Bennet'): {'lean': 'guardrails',
                               'summary': "Bennet's campaign for Colorado governor "
                                          'commits to requiring new data centers to '
                                          'cover the cost of the energy they use and '
                                          'help finance the infrastructure they need, '
                                          'and to align with state clean-energy and '
                                          'water-conservation goals; as a senator he '
                                          'co-signed an October 2025 letter to DOE '
                                          'noting AI and data centers are driving '
                                          'energy demand.',
                               'items': [{'what': 'Campaign energy platform: "Massive '
                                                  'energy users like data centers '
                                                  "shouldn't drive up utility bills "
                                                  'for Colorado families"; would '
                                                  '"require new data centers to cover '
                                                  'the cost of the energy they consume '
                                                  'and to help finance the '
                                                  'infrastructure they need," and '
                                                  'require new projects to align with '
                                                  "Colorado's clean energy, emissions, "
                                                  'water conservation and workforce '
                                                  'goals.',
                                          'date': '2026',
                                          'source': 'https://www.michaelbennet.com/priorities/energy/',
                                          'source_name': 'Bennet for Governor campaign '
                                                         'site',
                                          'kind': 'statement'},
                                         {'what': 'Co-signed (with Hickenlooper and '
                                                  'four House members) a letter to '
                                                  'Energy Secretary Wright on '
                                                  'cancelled Colorado energy projects '
                                                  'stating: "In an era where '
                                                  'artificial intelligence and data '
                                                  'centers are driving a rise in '
                                                  'energy demand, we must meet these '
                                                  'challenges by investing in '
                                                  'responsible and affordable energy '
                                                  'solutions, rather than '
                                                  'destabilizing them."',
                                          'date': '2025-10-14',
                                          'source': 'https://www.hickenlooper.senate.gov/press_releases/hickenlooper-bennet-neguse-degette-crow-pettersen-demand-answers-after-trump-admin-cut-600m-for-colorado-energy-projects/',
                                          'source_name': 'Sen. Hickenlooper press '
                                                         'release',
                                          'kind': 'action'}],
                               'as_of': '2026-09-05'},
 ('CT', 'Richard Blumenthal'): {'lean': 'guardrails',
                                'summary': 'Beyond the GRID Act, Blumenthal joined '
                                           'Warren and Van Hollen in December 2025 '
                                           'letters asking Google, Microsoft, Amazon, '
                                           'Meta and others whether data center costs '
                                           'are being passed to ratepayers, and in '
                                           'March 2026 as PSI ranking member wrote all '
                                           '50 state utility regulators seeking '
                                           "records on NDAs that hide data centers' "
                                           'energy and water use.',
                                'items': [{'what': 'With Sens. Warren and Van Hollen, '
                                                   'sent letters to Google, Microsoft, '
                                                   'Amazon, Meta and three other '
                                                   'companies probing whether "tech '
                                                   'companies are passing on the costs '
                                                   'of building and operating their '
                                                   'data centers to ordinary '
                                                   'Americans," including who bears '
                                                   'grid-upgrade costs if the AI boom '
                                                   'subsides.',
                                           'date': '2025-12-16',
                                           'source': 'https://www.warren.senate.gov/news/in-the-news/senators-investigate-role-of-a-i-data-centers-in-rising-electricity-costs/',
                                           'source_name': 'Sen. Warren press office '
                                                          '(in the news)',
                                           'kind': 'action'},
                                          {'what': 'As Ranking Member of the Permanent '
                                                   'Subcommittee on Investigations, '
                                                   'wrote public utility regulators in '
                                                   'all 50 states requesting documents '
                                                   'on non-disclosure agreements or '
                                                   'other restrictions that keep data '
                                                   "centers' energy use, water access, "
                                                   'infrastructure strain and economic '
                                                   'effects from public view: '
                                                   '"American families deserve full '
                                                   "transparency over Big Tech's "
                                                   'expansion of data centers across '
                                                   'the country and in their '
                                                   'communities."',
                                           'date': '2026-03-31',
                                           'source': 'https://www.blumenthal.senate.gov/newsroom/press/release/blumenthal-investigates-big-techs-use-of-non-disclosure-agreements-to-conceal-impact-of-energy-guzzling-data-centers',
                                           'source_name': 'Sen. Blumenthal press '
                                                          'release',
                                           'kind': 'action'}],
                                'as_of': '2026-09-05'},
 ('DE', 'Christopher A. Coons'): {'lean': 'mixed',
                                  'summary': 'Coons introduced the Liquid Cooling for '
                                             'AI Act with Sen. McCormick in November '
                                             '2025, directing GAO and DOE to assess '
                                             "liquid cooling to cut data centers' "
                                             'electricity and water use, saying AI '
                                             'leadership "shouldn\'t have to mean '
                                             'skyrocketing energy bills for American '
                                             'families."',
                                  'items': [{'what': 'Introduced the Liquid Cooling '
                                                     'for AI Act (with Sen. Dave '
                                                     'McCormick): GAO to assess R&D '
                                                     'needs for liquid cooling in data '
                                                     'centers, DOE to report '
                                                     'recommendations, and an industry '
                                                     'advisory body; the release cites '
                                                     "LBNL's finding that data centers "
                                                     'used 4.4% of U.S. electricity in '
                                                     '2023 and could reach 12.8% by '
                                                     '2028. Coons: "Leading the world '
                                                     "in AI innovation shouldn't have "
                                                     'to mean skyrocketing energy '
                                                     'bills for American families or '
                                                     'giving up ground in the fight '
                                                     'against climate change."',
                                             'date': '2025-11-20',
                                             'source': 'https://www.coons.senate.gov/news/press-releases/senators-coons-mccormick-introduce-bill-to-boost-us-ai-leadership-with-energy-efficient-liquid-cooling-technology',
                                             'source_name': 'Sen. Coons press release',
                                             'kind': 'action'}],
                                  'as_of': '2026-09-05'},
 ('FL', 'Rick Scott'): {'lean': 'guardrails',
                        'summary': 'Scott introduced a concurrent resolution '
                                   '(S.Con.Res.30) with Sen. Marshall endorsing the '
                                   "Trump administration's Ratepayer Protection "
                                   'Pledge, saying data centers are "already putting a '
                                   'substantial financial burden on American families" '
                                   "and Florida families should not support Big Tech's "
                                   'expansion "with their electricity bills."',
                        'items': [{'what': 'Introduced, with Sen. Roger Marshall, a '
                                           'concurrent resolution expressing the sense '
                                           'of Congress that the Ratepayer Protection '
                                           'Pledge — under which tech companies commit '
                                           'to cover their own electricity and '
                                           'grid-infrastructure costs — is sound '
                                           'national policy. Scott: "Big Data centers '
                                           'are already putting a substantial '
                                           'financial burden on American families... '
                                           "Florida families shouldn't be supporting "
                                           "Big Tech companies' expansions with their "
                                           'electricity bills."',
                                   'date': '2026-04-02',
                                   'source': 'https://www.rickscott.senate.gov/2026/4/sens-rick-scott-roger-marshall-introduce-resolution-supporting-pres-trump-s-ratepayer-protection-pledge',
                                   'source_name': 'Sen. Rick Scott press release',
                                   'kind': 'action'}],
                        'as_of': '2026-09-05'},
 ('GA', 'Jon Ossoff'): {'lean': 'guardrails',
                        'summary': "Ossoff's April 2026 letter to FERC Chair Laura "
                                   'Swett asked how the agency will ensure tech '
                                   'companies "pay their own way" and what it will do '
                                   'if data center construction raises utility costs '
                                   'beyond forecasts, with a response requested by '
                                   'June 1, 2026.',
                        'items': [{'what': 'Sent a letter to FERC Chairman Laura Swett '
                                           'opening an inquiry into whether AI data '
                                           "center growth is raising Georgians' power "
                                           'bills, asking how FERC will ensure '
                                           'technology companies "pay their own way" '
                                           'and what it will do if data center '
                                           'construction raises utility costs beyond '
                                           "predictions; cited the Georgia PSC's "
                                           'December 2025 approval of 9,885 MW of new '
                                           'Georgia Power generation for large loads '
                                           'and said Georgians are "suffering from '
                                           'sky-high power bills." Response requested '
                                           'by June 1, 2026. Georgia PSC commissioners '
                                           'publicly disputed the premise.',
                                   'date': '2026-04-20',
                                   'source': 'https://www.cbsnews.com/atlanta/news/ossoff-investigating-ai-data-center-are-impacting-rising-power-bills-in-georgia/',
                                   'source_name': 'CBS News Atlanta',
                                   'kind': 'action'}],
                        'as_of': '2026-09-05'},
 ('GA', 'Raphael G. Warnock'): {'lean': 'guardrails',
                                'summary': 'Warnock led a January 2026 letter to FERC '
                                           'to shield households from data center '
                                           'costs, secured $50 million in FY2026 '
                                           'appropriations for communities facing data '
                                           'center energy and water demands, asked EPA '
                                           'in July 2026 for water-protection guidance '
                                           'for towns negotiating with data center '
                                           'developers, and in August 2026 called for '
                                           'a Georgia data center moratorium unless '
                                           "residents' bills, pollution, NDAs and tax "
                                           'giveaways are addressed.',
                                'items': [{'what': 'With Sen. Markey and five other '
                                                   'senators, wrote FERC Chair Laura '
                                                   'Swett urging the commission to '
                                                   'prevent data center demand from '
                                                   'producing unjust or unreasonable '
                                                   'electricity cost increases for '
                                                   'households, warning AI and crypto '
                                                   'data centers could add over 10,000 '
                                                   'MW of demand with costs passed to '
                                                   'residential ratepayers.',
                                           'date': '2026-01-05',
                                           'source': 'https://www.warnock.senate.gov/newsroom/press-releases/warnock-markey-push-trump-admin-to-shield-americans-from-data-center-energy-costs/',
                                           'source_name': 'Sen. Warnock press release',
                                           'kind': 'action'},
                                          {'what': 'Secured $50 million in the FY2026 '
                                                   'government funding law to help '
                                                   'communities address energy and '
                                                   'water pressures from '
                                                   'resource-intensive projects '
                                                   'including data centers: "This '
                                                   'bipartisan legislation will help '
                                                   'give Georgians and Americans '
                                                   'relief from the energy and water '
                                                   'pressures of new '
                                                   'resource-intensive projects."',
                                           'date': '2026-01-16',
                                           'source': 'https://www.warnock.senate.gov/newsroom/press-releases/warnock-secures-50m-to-address-growing-energy-and-water-demands-from-data-centers/',
                                           'source_name': 'Sen. Warnock press release',
                                           'kind': 'action'},
                                          {'what': 'Wrote EPA Administrator Zeldin '
                                                   'requesting best-practice guidance '
                                                   'for communities protecting water '
                                                   'supplies from data center '
                                                   'expansion, with a written response '
                                                   'and briefing within four weeks: '
                                                   '"Small, rural communities have '
                                                   'been left to negotiate on their '
                                                   'own with multi-million-dollar '
                                                   'corporations whose well-staffed '
                                                   'legal teams may negotiate dozens '
                                                   'of deals at a time." Cited '
                                                   "OpenAI's Effingham County project "
                                                   'and 24 Georgia local moratoria.',
                                           'date': '2026-07-23',
                                           'source': 'https://www.warnock.senate.gov/newsroom/press-releases/warnock-calls-for-community-protections-from-data-centers/',
                                           'source_name': 'Sen. Warnock press release',
                                           'kind': 'action'},
                                          {'what': "Speaking in Guyton near OpenAI's "
                                                   'proposed Effingham County site, '
                                                   'called for a data center pause in '
                                                   'Georgia — "In the absence of '
                                                   'Congress not getting its act '
                                                   'together and putting some '
                                                   'common-sense guardrails in place, '
                                                   'local communities and states find '
                                                   'themselves in a race to the '
                                                   'bottom" — with conditions: no '
                                                   "increase in residents' water or "
                                                   'electric bills, no '
                                                   'water/air/noise/light pollution, '
                                                   'no NDAs, no "sweetheart tax '
                                                   'giveaways"; "This is not OpenAI '
                                                   'County — this is Effingham '
                                                   'County."',
                                           'date': '2026-08-28',
                                           'source': 'https://thecurrentga.org/2026/08/28/warnock-calls-for-data-center-moratorium-in-georgia/',
                                           'source_name': 'The Current (Georgia)',
                                           'kind': 'statement'}],
                                'as_of': '2026-09-05'},
 ('HI', 'Brian Schatz'): {'lean': 'guardrails',
                          'summary': 'Schatz has said on the Senate floor that AI data '
                                     'centers are the main driver of rising '
                                     'electricity demand, and in a December 2025 '
                                     'interview agreed that data centers should fund '
                                     'distributed solar and storage on homes in '
                                     'exchange for grid capacity.',
                          'items': [{'what': "Senate floor remarks: 'Energy demand is "
                                             'soaring for the first time in decades, '
                                             'largely not exclusively, but largely '
                                             "because of AI data centers,' arguing "
                                             'wind and solar are the fastest way to '
                                             'meet that demand; no position on who '
                                             'pays.',
                                     'date': '2025-06-29',
                                     'source': 'https://www.schatz.senate.gov/news/press-releases/schatz-republicans-are-ripping-people-off-plunging-country-into-energy-crisis-to-cut-taxes-for-billionaires',
                                     'source_name': 'Sen. Schatz press release (floor '
                                                    'remarks)',
                                     'kind': 'statement'},
                                    {'what': 'In an interview on the Volts podcast, '
                                             "agreed ('100%') with the proposal that "
                                             'data centers needing grid capacity '
                                             'should fund distributed solar, storage '
                                             'and heat pumps on homes, and said it '
                                             "would be 'a rounding error' for highly "
                                             'profitable AI firms to also fund carbon '
                                             'dioxide removal.',
                                     'date': '2025-12-31',
                                     'source': 'https://www.volts.wtf/p/sen-brian-schatz-wants-permitting',
                                     'source_name': 'Volts (David Roberts) interview '
                                                    'transcript',
                                     'kind': 'statement'}],
                          'as_of': '2026-09-05'},
 ('IA', 'Chuck Grassley'): {'lean': 'guardrails',
                            'summary': 'Asked about data centers at a June 2026 '
                                       'employee Q&A in Sioux City, Grassley said '
                                       'siting is a state and local decision and '
                                       'Congress is not acting on it.',
                            'items': [{'what': 'At a Q&A with Chesterman Company '
                                               'employees in Sioux City, asked about '
                                               "data centers, Grassley said 'These are "
                                               "state and local decisions to make,' "
                                               'and discussed their positives and '
                                               'negatives and possible legislation on '
                                               'their construction.',
                                       'date': '2026-06-30',
                                       'source': 'https://www.nwestiowa.com/moville_record/sen-chuck-grassley-visits-chesterman-co-in-sioux-city/article_f72e1fb2-6509-4d08-a335-c0a1a61e2e6f.html',
                                       'source_name': 'Moville Record / nwestiowa.com',
                                       'kind': 'statement'}],
                            'as_of': '2026-09-05'},
 ('ID', 'Mike Crapo'): {'lean': 'accelerate',
                        'summary': "Crapo issued a statement welcoming Meta's Kuna, "
                                   'Idaho data center as a step for job growth when it '
                                   'was announced in 2022.',
                        'items': [{'what': 'Statement in the Idaho Commerce '
                                           "announcement of Meta's $800 million Kuna "
                                           "data center: 'This is a promising step for "
                                           'job growth and opportunities in the '
                                           "community,' noting the center is expected "
                                           'to be supported by renewable energy.',
                                   'date': '2022-02-16',
                                   'source': 'https://commerce.idaho.gov/press/meta-announces-kuna-as-location-of-new-data-center/',
                                   'source_name': 'Idaho Department of Commerce press '
                                                  'release',
                                   'kind': 'statement'}],
                        'as_of': '2026-09-05'},
 ('ID', 'James E. Risch'): {'lean': 'accelerate',
                            'summary': "Risch welcomed Meta's Kuna data center in 2022 "
                                       'as a source of jobs and in 2026 co-introduced '
                                       'the ARC Act, a nuclear cost-overrun program '
                                       'his office promotes as answering '
                                       'data-center-driven power demand.',
                            'items': [{'what': 'Statement in the Idaho Commerce '
                                               "announcement of Meta's Kuna data "
                                               "center: 'The creation of new jobs is "
                                               'of utmost importance in a community '
                                               'growing as rapidly as the Treasure '
                                               "Valley,' saying the center 'will "
                                               'provide hardworking Idahoans with '
                                               "good-paying jobs.'",
                                       'date': '2022-02-16',
                                       'source': 'https://commerce.idaho.gov/press/meta-announces-kuna-as-location-of-new-data-center/',
                                       'source_name': 'Idaho Department of Commerce '
                                                      'press release',
                                       'kind': 'statement'}],
                            'as_of': '2026-09-05'},
 ('IL', 'Richard J. Durbin'): {'lean': 'guardrails',
                               'summary': 'In March 2026 Durbin introduced the Data '
                                          'Center Water and Energy Transparency Act '
                                          '(S. 4213), requiring data centers to report '
                                          'energy and water use to states and federal '
                                          'agencies.',
                               'items': [{'what': 'Introduced the Data Center Water '
                                                  'and Energy Transparency Act (S. '
                                                  '4213), requiring data center '
                                                  'operators to report energy and '
                                                  'water consumption to their states, '
                                                  'prospective facilities to report '
                                                  'five-year estimates, and states to '
                                                  'aggregate the data for EPA, DOE and '
                                                  'USDA, with EPA fines for '
                                                  "non-compliance. Durbin: 'If you've "
                                                  'noticed a sharp increase in your '
                                                  'utility bills lately, it may be '
                                                  'from the growth of energy-hungry '
                                                  "data centers.'",
                                          'date': '2026-03-25',
                                          'source': 'https://www.durbin.senate.gov/newsroom/press-releases/as-utility-costs-rise-durbin-introduces-new-legislation-to-bring-transparency-to-energy-and-water-consumption-by-data-centers',
                                          'source_name': 'Sen. Durbin press release',
                                          'kind': 'action'}],
                               'as_of': '2026-09-05'},
 ('KS', 'Roger Marshall'): {'lean': 'guardrails',
                            'summary': 'Marshall introduced a Senate resolution '
                                       'backing the Ratepayer Protection Pledge, has '
                                       'said Kansans should not pay higher bills for '
                                       'data centers, opposes tax incentives for them, '
                                       'and supports the county moratoriums in Kansas.',
                            'items': [{'what': 'Introduced with Sen. Rick Scott a '
                                               'concurrent resolution supporting the '
                                               'Ratepayer Protection Pledge, under '
                                               'which tech companies commit to pay '
                                               'their own electricity and '
                                               'grid-infrastructure costs. Marshall: '
                                               "'Kansans shouldn't have to pay higher "
                                               'utility bills so that big tech '
                                               'companies can power their data '
                                               "centers.'",
                                       'date': '2026-04-02',
                                       'source': 'https://www.rickscott.senate.gov/2026/4/sens-rick-scott-roger-marshall-introduce-resolution-supporting-pres-trump-s-ratepayer-protection-pledge',
                                       'source_name': 'Sen. Rick Scott press release '
                                                      '(joint with Marshall)',
                                       'kind': 'action'},
                                      {'what': "At Semafor's World of Work event, said "
                                               'he does not want tax incentives for '
                                               "data centers or for them to 'drive up "
                                               "other people's electricity costs,' "
                                               'pointed to higher rates near '
                                               "Panasonic's Kansas plant as a warning, "
                                               "and said of Kansas counties' "
                                               "moratoriums: 'I certainly support "
                                               "their moratoriums,' adding those "
                                               'decisions belong at the local level.',
                                       'date': '2026-07-22',
                                       'source': 'https://www.semafor.com/article/07/22/2026/republican-senator-roger-marshall-rails-against-ai-data-centers',
                                       'source_name': 'Semafor',
                                       'kind': 'statement'},
                                      {'what': 'Press release applauding the expansion '
                                               'of the Ratepayer Protection Pledge: '
                                               "'I've heard from Kansans who are "
                                               'concerned that infrastructure costs '
                                               'for data centers could be pushed onto '
                                               'households, small businesses, schools, '
                                               "hospitals, and farms.'",
                                       'date': '2026-07-24',
                                       'source': 'https://www.marshall.senate.gov/newsroom/press-releases/senator-marshall-applauds-president-trump-for-expanding-ratepayer-protection-pledge/',
                                       'source_name': 'Sen. Marshall press release',
                                       'kind': 'statement'},
                                      {'what': 'Quoted in a KSHB voter guide ahead of '
                                               'the August 4, 2026 Kansas primary: '
                                               "'Kansas isn't going to hand over our "
                                               'land, water, or power grid to Big Tech '
                                               'companies that turn a profit while '
                                               'local families foot the bill with '
                                               "taxpayer giveaways.'",
                                       'date': '2026-07',
                                       'source': 'https://www.kshb.com/news/local-news/kansas/johnson-county/voters-guide-kansas-political-candidates-stances-on-data-center-development',
                                       'source_name': 'KSHB 41 Kansas City',
                                       'kind': 'statement'}],
                            'as_of': '2026-09-05'},
 ('KY', 'Rand Paul'): {'lean': 'guardrails',
                       'summary': 'Paul has said neither the federal government nor '
                                  'the governor should regulate where data centers go '
                                  'and that each county should decide for itself.',
                       'items': [{'what': 'During a visit to Fort Knox, on data center '
                                          "siting: 'I don't think the federal "
                                          'government should regulate where data '
                                          'centers are placed or built, nor do I think '
                                          'the governor should. Each county should '
                                          'make this decision at the most local '
                                          "level.' He added that counties with a large "
                                          'tax base might not want one while poorer '
                                          'counties might.',
                                  'date': '2026-08-11',
                                  'source': 'https://www.thenewsenterprise.com/news/local/during-brief-visit-at-fort-knox-rand-paul-discusses-data-centers-mcconnell-and-fauci/article_08796f57-df70-5ace-b59f-89191c200183.html',
                                  'source_name': 'The News-Enterprise (Elizabethtown, '
                                                 'KY)',
                                  'kind': 'statement'}],
                       'as_of': '2026-09-05'},
 ('LA', 'Bill Cassidy'): {'lean': 'accelerate',
                          'summary': "Cassidy has praised Meta's Richland Parish data "
                                     'center for raising the local tax base and '
                                     'teacher pay.',
                          'items': [{'what': "Quoted praising Meta's Richland Parish "
                                             "data center: 'Economic growth increases "
                                             "the tax base and sales tax revenue' and "
                                             "'Teacher bonuses there are up to $50,000 "
                                             "this year.'",
                                     'date': '2026-08-23',
                                     'source': 'https://www.yahoo.com/news/politics/articles/see-the-moment-when-republican-politicians-turned-against-data-centers-090000267.html',
                                     'source_name': 'Washington Post (syndicated on '
                                                    'Yahoo News)',
                                     'kind': 'statement'}],
                          'as_of': '2026-09-05'},
 ('MA', 'Edward J. Markey'): {'lean': 'guardrails',
                              'summary': 'Markey has released a discussion draft '
                                         'requiring federal certification of data '
                                         'centers, reintroduced the AI Environmental '
                                         'Impacts Act, and led letters to ISO New '
                                         'England and state utility regulators asking '
                                         'them to shield ratepayers from data center '
                                         'costs.',
                              'items': [{'what': 'Led a letter from six New England '
                                                 'senators to ISO New England asking '
                                                 'how it will protect residential '
                                                 'ratepayers from price increases '
                                                 'driven by data center expansion. '
                                                 "Markey: 'As the ones who stand to "
                                                 'benefit most, the '
                                                 'multi-billion-dollar AI industry '
                                                 'should be responsible for these '
                                                 "costs.'",
                                         'date': '2026-01-28',
                                         'source': 'https://www.markey.senate.gov/news/press-releases/markey-welch-new-england-senators-call-for-answers-about-how-new-regional-data-centers-will-drive-up-energy-costs-for-consumers',
                                         'source_name': 'Sen. Markey press release',
                                         'kind': 'action'},
                                        {'what': 'Led a letter with Sens. Blumenthal, '
                                                 'Van Hollen and Booker to the '
                                                 'president of NARUC urging state '
                                                 'utility commissions to reject rate '
                                                 'filings that shift data center costs '
                                                 'onto households and small '
                                                 'businesses.',
                                         'date': '2026-03-06',
                                         'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-colleagues-call-for-state-energy-regulators-to-protect-ratepayers-from-data-center-related-cost-hikes',
                                         'source_name': 'Sen. Markey press release',
                                         'kind': 'action'},
                                        {'what': 'Reintroduced with Rep. Beyer the AI '
                                                 'Environmental Impacts Act of 2026, '
                                                 'requiring AI data centers to report '
                                                 'environmental and energy impacts '
                                                 'with fines for non-compliance, NIST '
                                                 'measurement standards, and an EPA '
                                                 'lifecycle study.',
                                         'date': '2026-06-09',
                                         'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-rep-beyer-reintroduce-ai-environmental-impacts-act',
                                         'source_name': 'Sen. Markey press release',
                                         'kind': 'action'},
                                        {'what': 'Released a discussion draft of the '
                                                 'Protecting Communities from Data '
                                                 'Center Impacts Act, which would '
                                                 'require a federal public-interest '
                                                 'certificate before a data center is '
                                                 'permitted, set minimum energy, '
                                                 'environmental and economic '
                                                 'standards, and fund community '
                                                 'monitoring grants. Markey: '
                                                 "'Communities are organizing and "
                                                 'demanding action to protect their '
                                                 'air, water, energy bills, and '
                                                 'quality of life from the tsunami of '
                                                 "data centers around the country.'",
                                         'date': '2026-07-13',
                                         'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-releases-discussion-draft-of-legislation-to-create-a-national-framework-to-address-data-center-harm',
                                         'source_name': 'Sen. Markey press release',
                                         'kind': 'action'}],
                              'as_of': '2026-09-05'},
 ('MA', 'Elizabeth Warren'): {'lean': 'guardrails',
                              'summary': 'Warren opened an investigation into whether '
                                         "Big Tech data centers are raising families' "
                                         'utility bills, pushed EIA with Sen. Hawley '
                                         'to require mandatory data center energy '
                                         "reporting, and probed private equity firms' "
                                         'data center investments.',
                              'items': [{'what': 'With Sens. Van Hollen and '
                                                 'Blumenthal, sent letters to Google, '
                                                 'Microsoft, Amazon, Meta, CoreWeave, '
                                                 'Digital Realty and Equinix asking '
                                                 'how they will keep data center grid '
                                                 "costs off consumers' bills. Warren: "
                                                 "'Through these utility price "
                                                 'increases, American families '
                                                 'bankroll the electricity costs of '
                                                 "trillion-dollar tech companies.'",
                                         'date': '2025-12-16',
                                         'source': 'https://www.warren.senate.gov/newsroom/press-releases/senator-warren-lawmakers-open-investigation-into-big-tech-data-centers-role-in-driving-up-families-utility-costs',
                                         'source_name': 'Sen. Warren press release',
                                         'kind': 'action'},
                                        {'what': "Released the companies' responses: "
                                                 'Google committed to pay for all '
                                                 'electricity it uses and contribute '
                                                 'to growth-related costs; Microsoft, '
                                                 'CoreWeave and Equinix backed '
                                                 'separate rate classes for data '
                                                 "centers. Warren: 'These commitments "
                                                 'do not explain how Big Tech '
                                                 'companies – not American consumers – '
                                                 'will bear the full cost of data '
                                                 "centers.'",
                                         'date': '2026-01-22',
                                         'source': 'https://www.warren.senate.gov/newsroom/press-releases/warren-senators-secure-new-commitments-from-big-tech-on-electricity-costs-but-companies-dodge-accountability-for-hiking-families-utility-bills/',
                                         'source_name': 'Sen. Warren press release',
                                         'kind': 'action'},
                                        {'what': 'With Sen. Hawley, wrote to the EIA '
                                                 'administrator in March 2026 asking '
                                                 'for a mandatory annual energy-use '
                                                 'survey of data centers and other '
                                                 'large loads; EIA then announced a '
                                                 'mandatory data center survey to be '
                                                 'completed by September 30, 2026. '
                                                 "Warren: 'Americans deserve to know "
                                                 'how much energy data centers are '
                                                 "sucking up and what that's doing to "
                                                 "their utility bills.'",
                                         'date': '2026-04-15',
                                         'source': 'https://www.warren.senate.gov/newsroom/press-releases/warren-hawley-secure-mandatory-energy-use-reporting-requirements-for-data-centers',
                                         'source_name': 'Sen. Warren press release',
                                         'kind': 'action'},
                                        {'what': 'Sent letters to KKR, BlackRock, '
                                                 'Brookfield Infrastructure Partners '
                                                 'and Blackstone asking for details of '
                                                 'their data center investments and '
                                                 'how they ensure Americans are not '
                                                 'left paying for them, with responses '
                                                 'due June 27.',
                                         'date': '2026-06-15',
                                         'source': 'https://www.banking.senate.gov/newsroom/minority/warren-probes-major-private-equity-firms-on-investments-in-data-centers-as-utility-costs-rise',
                                         'source_name': 'Senate Banking Committee '
                                                        '(minority) press release',
                                         'kind': 'action'}],
                              'as_of': '2026-09-05'},
 ('MD', 'Angela D. Alsobrooks'): {'lean': 'guardrails',
                                  'summary': 'Alsobrooks joined the Maryland '
                                             "delegation's July 2026 letter urging "
                                             'FERC to relieve Maryland ratepayers of '
                                             'transmission costs driven by '
                                             'out-of-state data centers.',
                                  'items': [{'what': 'Signed, with Sen. Van Hollen and '
                                                     'seven Maryland House members, a '
                                                     'letter urging FERC to act '
                                                     'quickly on the Maryland Office '
                                                     "of People's Counsel complaint "
                                                     'and to require PJM to protect '
                                                     'Maryland ratepayers from '
                                                     'transmission costs assigned to '
                                                     'them for out-of-state data '
                                                     'center demand.',
                                             'date': '2026-07-28',
                                             'source': 'https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due',
                                             'source_name': 'Rep. April McClain '
                                                            'Delaney press release '
                                                            '(joint delegation letter)',
                                             'kind': 'action'}],
                                  'as_of': '2026-09-05'},
 ('MD', 'Chris Van Hollen'): {'lean': 'guardrails',
                              'summary': 'Beyond the Power for the People Act, Van '
                                         'Hollen co-led the Warren investigation into '
                                         'Big Tech data center costs, a NARUC letter '
                                         'on ratepayer protection, a probe of '
                                         'gas-powered data center plans, and the '
                                         "Maryland delegation's FERC letter.",
                              'items': [{'what': 'With Sens. Warren and Blumenthal, '
                                                 'sent letters to Google, Microsoft, '
                                                 'Amazon, Meta, CoreWeave, Digital '
                                                 'Realty and Equinix asking how they '
                                                 'will prevent data center grid costs '
                                                 'from being passed to consumers.',
                                         'date': '2025-12-16',
                                         'source': 'https://www.warren.senate.gov/newsroom/press-releases/senator-warren-lawmakers-open-investigation-into-big-tech-data-centers-role-in-driving-up-families-utility-costs',
                                         'source_name': 'Sen. Warren press release '
                                                        '(joint)',
                                         'kind': 'action'},
                                        {'what': 'Signed the Markey-led letter to the '
                                                 'president of NARUC urging state '
                                                 'utility commissions to reject rate '
                                                 'filings that shift data center costs '
                                                 'onto households and small '
                                                 'businesses.',
                                         'date': '2026-03-06',
                                         'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-colleagues-call-for-state-energy-regulators-to-protect-ratepayers-from-data-center-related-cost-hikes',
                                         'source_name': 'Sen. Markey press release '
                                                        '(joint)',
                                         'kind': 'action'},
                                        {'what': 'At a Maryland delegation meeting on '
                                                 "energy affordability: 'the surge of "
                                                 'data center development across our '
                                                 "region is only making things worse' "
                                                 "and 'Consumers should not have to "
                                                 'pay one dime in additional '
                                                 'electricity costs to support data '
                                                 'centers for the richest companies on '
                                                 "the planet.'",
                                         'date': '2026-03-12',
                                         'source': 'https://www.vanhollen.senate.gov/news/press-releases/maryland-congressional-delegation-holds-meeting-to-discuss-energy-affordability-and-reliability',
                                         'source_name': 'Sen. Van Hollen press release',
                                         'kind': 'statement'},
                                        {'what': 'With Sens. Whitehouse and Heinrich, '
                                                 'sent letters to Meta, OpenAI, xAI, '
                                                 'Fermi America, American Intelligence '
                                                 '& Power, Joule, Crusoe and '
                                                 'Fundamental Data about twelve '
                                                 'planned gas-powered data center '
                                                 'projects, asking why they rely on '
                                                 'gas, whether they will capture CO2, '
                                                 'and their expected returns; '
                                                 'responses due March 27.',
                                         'date': '2026-03-13',
                                         'source': 'https://www.vanhollen.senate.gov/news/press-releases/van-hollen-whitehouse-heinrich-probe-ai-companies-about-plans-for-colossal-gas-powered-data-centers',
                                         'source_name': 'Sen. Van Hollen press release',
                                         'kind': 'action'},
                                        {'what': 'Signed, with Sen. Alsobrooks and '
                                                 'seven Maryland House members, a '
                                                 'letter urging FERC to relieve '
                                                 'Maryland ratepayers of transmission '
                                                 'costs assigned for out-of-state data '
                                                 'center demand and to require PJM to '
                                                 'adopt stronger protections.',
                                         'date': '2026-07-28',
                                         'source': 'https://mcclaindelaney.house.gov/media/press-releases/maryland-democrats-urge-ferc-protect-marylanders-rising-electricity-costs-due',
                                         'source_name': 'Rep. April McClain Delaney '
                                                        'press release (joint '
                                                        'delegation letter)',
                                         'kind': 'action'}],
                              'as_of': '2026-09-05'},
 ('ME', 'Susan M. Collins'): {'lean': 'mixed',
                              'summary': 'Says data-center projects should be judged '
                                         'case by case, shares concern about their '
                                         'energy draw and cost pressure, and has '
                                         'favored siting them at former mill sites '
                                         'with hydropower.',
                              'items': [{'what': 'Told the Bangor Daily News '
                                                 'data-center projects should be '
                                                 'handled case by case, favoring '
                                                 'former mill sites because "there is '
                                                 'usually hydropower right there," '
                                                 'while saying "I do share the concern '
                                                 'of data centers gobbling up too much '
                                                 'energy and putting stress on the '
                                                 'cost of energy."',
                                         'date': '2026-08-19',
                                         'source': 'https://www.bangordailynews.com/2026/08/19/politics/elections/susan-collins-cautious-on-maine-data-centers/',
                                         'source_name': 'Bangor Daily News',
                                         'kind': 'statement'},
                                        {'what': 'Joined Sen. King at the Millinocket '
                                                 'celebration welcoming Nautilus Data '
                                                 "Technologies' water-cooled, "
                                                 'hydro-powered data center to the '
                                                 'former Great Northern Paper mill '
                                                 'site, calling it "one of the '
                                                 'greenest facilities in the world."',
                                         'date': '2021-06-05',
                                         'source': 'https://www.king.senate.gov/newsroom/press-releases/senators-collins-king-attend-millinocket-celebration-welcoming-nautilus-data-technologies-to-former-paper-mill',
                                         'source_name': 'Sen. King press release',
                                         'kind': 'statement'}],
                              'as_of': '2026-09-05'},
 ('ME', 'Angus S. King, Jr.'): {'lean': 'accelerate',
                                'summary': 'Has welcomed hydro-powered data-center '
                                           'projects at former Maine mill sites but '
                                           'has no located 2025-2026 bill, letter, or '
                                           'statement on data-center energy costs or '
                                           'siting.',
                                'items': [{'what': 'Joined Sen. Collins at the '
                                                   'Millinocket celebration welcoming '
                                                   "Nautilus Data Technologies' "
                                                   'water-cooled, 100% hydro-powered '
                                                   'data center to the former Great '
                                                   'Northern Paper mill site, saying '
                                                   '"sustainable projects like this '
                                                   "are the blueprint for Maine's "
                                                   'future" and "create good jobs that '
                                                   'strengthen our communities."',
                                           'date': '2021-06-05',
                                           'source': 'https://www.king.senate.gov/newsroom/press-releases/senators-collins-king-attend-millinocket-celebration-welcoming-nautilus-data-technologies-to-former-paper-mill',
                                           'source_name': 'Sen. King press release',
                                           'kind': 'statement'}],
                                'as_of': '2026-09-05'},
 ('MN', 'Amy Klobuchar'): {'lean': 'guardrails',
                           'summary': 'Campaigning for governor, says data centers '
                                      'raise rates and have hurt the environment, '
                                      'calls for local control, transparency, and '
                                      "environmental standards, and backs Minnesota's "
                                      '2025 law making data centers pay their full '
                                      'energy costs.',
                           'items': [{'what': 'In a KFGO interview during her run for '
                                              'governor said data centers "cause '
                                              "people's rates to go up, they have hurt "
                                              "the environment, and that just can't "
                                              'keep happening," criticized '
                                              'non-disclosure agreements keeping '
                                              'projects "in the dark," and called for '
                                              'local control over siting decisions.',
                                      'date': '2026-08-12',
                                      'source': 'https://kfgo.com/2026/08/12/1339958/',
                                      'source_name': 'KFGO',
                                      'kind': 'statement'},
                                     {'what': 'Through spokesman Darwin Forsyth, said '
                                              'she "supports robust environmental '
                                              'standards for any proposed data centers '
                                              'as well as greater transparency and '
                                              'local control over decisions to build," '
                                              "called Minnesota's 2025 law requiring "
                                              'data centers to pay the full cost of '
                                              'their energy use "a good start," and '
                                              'said her focus would be protecting '
                                              "Minnesotans' energy bills and water; "
                                              'she did not answer questions on local '
                                              'moratoriums or NDAs.',
                                      'date': '2026-08-03',
                                      'source': 'https://www.hometownsource.com/psa/where-do-the-candidates-for-governor-stand-on-data-centers/article_f465d0f7-72e4-4da9-b0c0-ddaab49ac458.html',
                                      'source_name': 'Hometown Source (Minnesota '
                                                     'Reformer syndication)',
                                      'kind': 'statement'}],
                           'as_of': '2026-09-05'},
 ('MN', 'Tina Smith'): {'lean': 'guardrails',
                        'summary': 'Cosponsors the Power for the People Act, which '
                                   'would require data-center operators rather than '
                                   'consumers to pay for the energy infrastructure '
                                   'they need.',
                        'items': [{'what': 'Named as an original cosponsor of Sen. Van '
                                           "Hollen's Power for the People Act, which "
                                           'directs states to evaluate data-center '
                                           'rate classes, instructs FERC to ensure '
                                           'data centers pay for local transmission '
                                           'upgrades, and creates an interconnection '
                                           'system pushing data centers to offset grid '
                                           'impact with new generation and storage '
                                           'under labor standards.',
                                   'date': '2026-01-15',
                                   'source': 'https://www.vanhollen.senate.gov/news/press-releases/van-hollen-leads-new-bill-to-ensure-americans-arent-footing-the-bill-for-big-data-centers',
                                   'source_name': 'Sen. Van Hollen press release',
                                   'kind': 'action'}],
                        'as_of': '2026-09-05'},
 ('MO', 'Josh Hawley'): {'lean': 'guardrails',
                         'summary': 'Introduced the bipartisan GRID Act to require '
                                    'data centers to use power sources separate from '
                                    'the grid and disclose usage, demanded answers '
                                    'from Ameren on data-center deals and rate '
                                    'increases, and asked EIA with Sen. Warren for '
                                    'mandatory data-center energy reporting.',
                         'items': [{'what': 'Introduced the Guaranteeing Rate '
                                            'Insulation from Data Centers (GRID) Act '
                                            'with Sen. Blumenthal, requiring data '
                                            'centers to obtain power from sources '
                                            'separate from the grid (10-year '
                                            'transition for existing facilities), '
                                            'giving consumers grid priority, and '
                                            'requiring public disclosure of '
                                            'electricity use; said "American families '
                                            'should not have to shoulder the burden of '
                                            'rising electricity costs produced by data '
                                            'centers."',
                                    'date': '2026-02-11',
                                    'source': 'https://www.hawley.senate.gov/hawley-blumenthal-introduce-bill-to-prevent-data-centers-from-increasing-electricity-costs-for-americans',
                                    'source_name': 'Sen. Hawley press release',
                                    'kind': 'action'},
                                   {'what': 'Sent a letter to Ameren CEO Martin Lyons '
                                            'asking whether Ameren analyzed how '
                                            'discounted data-center contracts will '
                                            'affect residential prices and whether it '
                                            'prioritized household rate stability, '
                                            'saying Missourians "should not be forced '
                                            'to subsidize corporate projects while '
                                            'struggling to keep their lights on."',
                                    'date': '2025-10-15',
                                    'source': 'https://www.hawley.senate.gov/?p=6560',
                                    'source_name': 'Sen. Hawley press release',
                                    'kind': 'action'},
                                   {'what': 'After Missouri Senate President Pro Tem '
                                            "Cindy O'Laughlin called his data-center "
                                            'concerns misleading, said she "told me to '
                                            'stop asking questions about data centers '
                                            'and higher electricity rates. Not a '
                                            'chance."',
                                    'date': '2025-10-17',
                                    'source': 'https://www.hawley.senate.gov/hawley-doubles-down-on-surging-data-center-concerns-in-response-to-state-legislator',
                                    'source_name': 'Sen. Hawley press release',
                                    'kind': 'statement'},
                                   {'what': 'With Sen. Warren, wrote EIA Administrator '
                                            'Tristan Abbey asking for a mandatory '
                                            'annual reporting requirement for data '
                                            'centers and other large loads covering '
                                            'hourly/annual/peak consumption, rates '
                                            'paid, upfront payments, demand response, '
                                            'and how transmission upgrade costs are '
                                            'allocated; response requested by April 9, '
                                            '2026.',
                                    'date': '2026-03-26',
                                    'source': 'https://www.warren.senate.gov/newsroom/press-releases/warren-hawley-lead-bipartisan-push-for-mandatory-energy-use-reporting-requirements-for-data-centers/',
                                    'source_name': 'Sen. Warren press release',
                                    'kind': 'action'},
                                   {'what': 'Told Missourinet "I think we ought to say '
                                            'in the law that the data centers have to '
                                            'pay for their own electricity, the data '
                                            'centers have to pay for their own water '
                                            'supply," and that he does not want bills '
                                            'rising because "some corporation came in '
                                            'and sucked up all the power."',
                                    'date': '2026-02-27',
                                    'source': 'https://www.missourinet.com/2026/02/27/missouris-josh-hawley-says-major-tech-companies-should-pay-for-energy-and-water-usage-generated-by-their-data-centers/',
                                    'source_name': 'Missourinet',
                                    'kind': 'statement'},
                                   {'what': 'Told St. Louis Public Radio, on '
                                            'introducing the GRID Act, that tech '
                                            'companies "can absolutely afford to pay '
                                            'for their own electricity, and they '
                                            'should," and that residents cannot know a '
                                            'project\'s effect on them "if they don\'t '
                                            'know exactly what the drawdown on power '
                                            'is going to be."',
                                    'date': '2026-02-11',
                                    'source': 'https://www.stlpr.org/health-science-environment/2026-02-11/josh-hawley-data-centers-build-power-plants-missouri',
                                    'source_name': 'St. Louis Public Radio',
                                    'kind': 'statement'}],
                         'as_of': '2026-09-05'},
 ('MS', 'Cindy Hyde-Smith'): {'lean': 'guardrails',
                              'summary': 'At a FERC oversight hearing, pressed '
                                         'commissioners on mechanisms to make '
                                         'large-load customers such as data centers '
                                         'pay upfront so residential rates do not '
                                         'rise.',
                              'items': [{'what': 'At the Senate Energy and Natural '
                                                 "Resources Committee's FERC oversight "
                                                 'hearing, said Mississippi "continues '
                                                 'to be at the forefront of '
                                                 'safeguarding ratepayers by ensuring '
                                                 'companies, like data centers, pay '
                                                 'their fair share for large loads," '
                                                 'and asked commissioners what '
                                                 'mechanisms FERC is implementing for '
                                                 'large-load customers to make upfront '
                                                 'payments and minimum financial '
                                                 'commitments to keep rates from '
                                                 'rising.',
                                         'date': '2026-07-23',
                                         'source': 'https://www.hydesmith.senate.gov/hyde-smith-ferc-commissioners-examine-affordability-data-centers-proliferate',
                                         'source_name': 'Sen. Hyde-Smith press release',
                                         'kind': 'action'}],
                              'as_of': '2026-09-05'},
 ('MS', 'Roger F. Wicker'): {'lean': 'accelerate',
                             'summary': "Has celebrated Amazon's $10 billion "
                                        'hyperscale data-center project in Madison '
                                        'County as a historic investment, with no '
                                        'located statement on its power or ratepayer '
                                        'impact.',
                             'items': [{'what': 'Statement on the groundbreaking of '
                                                "Amazon Web Services' $10 billion, "
                                                'two-campus hyperscale data-center '
                                                'project in Madison County, calling it '
                                                '"a historic investment in our state" '
                                                'and pledging to keep Mississippi '
                                                'attractive to business.',
                                        'date': '2024-05-20',
                                        'source': 'https://www.wicker.senate.gov/2024/5/senator-wicker-celebrates-groundbreaking-of-largest-economic-development-project-in-state-history',
                                        'source_name': 'Sen. Wicker press release',
                                        'kind': 'statement'}],
                             'as_of': '2026-09-05'},
 ('MT', 'Steve Daines'): {'lean': 'accelerate',
                          'summary': 'Announced a 50 MW hydro-powered data center on '
                                     'CSKT land in 2022 and has framed reliable power '
                                     'for data centers as the backbone of prosperity, '
                                     'with no located position on cost allocation or '
                                     'community safeguards.',
                          'items': [{'what': 'Chairing a Senate Foreign Relations '
                                             'subcommittee hearing on European energy '
                                             'reform, said "whether it be for data '
                                             'centers, manufacturing, or defense '
                                             'production, reliable power is the '
                                             'backbone of our future prosperity."',
                                     'date': '2026-02-04',
                                     'source': 'https://www.daines.senate.gov/2026/02/04/daines-discusses-need-for-energy-reform-in-europe/',
                                     'source_name': 'Sen. Daines press release',
                                     'kind': 'statement'},
                                    {'what': "Announced at his Montana 'On the Rise' "
                                             'Economic Summit a Bitzero investment to '
                                             'build a 50 MW data center powered by '
                                             'Confederated Salish and Kootenai Tribes '
                                             'hydropower, saying it would "support '
                                             'good-paying jobs in Montana" and keep '
                                             'the state "at the forefront of the '
                                             'energy and technology sector."',
                                     'date': '2022-06-02',
                                     'source': 'https://daines.senate.gov/news/press-releases/new-data-center-powered-by-cskt-hydro-announced-at-daines-economic-summit',
                                     'source_name': 'Sen. Daines press release',
                                     'kind': 'statement'}],
                          'as_of': '2026-09-05'},
 ('NC', 'Ted Budd'): {'lean': 'accelerate',
                      'summary': 'Calls for permitting reform and more power '
                                 'generation to meet data-center demand, says siting '
                                 'decisions belong at the local level, and was '
                                 'skeptical of a data-center moratorium.',
                      'items': [{'what': 'At a Washington Post Live event said the '
                                         'U.S. needs to add about 85 gigawatts a year '
                                         'to keep pace with demand and "that goes back '
                                         'to permitting reform," that "power is good" '
                                         'and the country needs more energy, that '
                                         'data-center construction decisions should be '
                                         'made "at a local level," and was skeptical '
                                         "of Sen. Sanders' moratorium proposal while "
                                         'saying he would need to read the text.',
                                 'date': '2026-02-25',
                                 'source': 'https://www.nextgov.com/artificial-intelligence/2026/02/lawmakers-both-parties-back-data-center-permitting-reform/411700/',
                                 'source_name': 'Nextgov/FCW',
                                 'kind': 'statement'}],
                      'as_of': '2026-09-05'},
 ('ND', 'Kevin Cramer'): {'lean': 'accelerate',
                          'summary': "Has welcomed Applied Digital's North Dakota "
                                     'data-center buildout as having a bright future '
                                     "given the state's abundant energy, with no "
                                     'located position on ratepayer cost allocation.',
                          'items': [{'what': 'Letter read by his constituent-services '
                                             "representative at Applied Digital's "
                                             'Ellendale data-center energizing '
                                             'ceremony, saying that with North '
                                             'Dakota\'s "wide open spaces, abundant '
                                             'energy and ideal climate, there is a '
                                             'bright future for additional development '
                                             'within our state."',
                                     'date': '2023-06-16',
                                     'source': 'https://www.jamestownsun.com/news/applied-digital-celebrates-energizing-of-facility-in-ellendale-nd',
                                     'source_name': 'Jamestown Sun',
                                     'kind': 'statement'}],
                          'as_of': '2026-09-05'},
 ('ND', 'John Hoeven'): {'lean': 'accelerate',
                         'summary': "Has promoted data centers as North Dakota's third "
                                    'wave of economic growth after agriculture and '
                                    'energy, with no located position on ratepayer '
                                    'cost allocation.',
                         'items': [{'what': "Letter read at Applied Digital's "
                                            'Ellendale data-center energizing ceremony '
                                            'saying "technology is serving as the '
                                            "third wave of our state's economic growth "
                                            'following expansion in agriculture and '
                                            'energy" and that the facility provides '
                                            'infrastructure and computing capacity '
                                            'across industries.',
                                    'date': '2023-06-16',
                                    'source': 'https://www.jamestownsun.com/news/applied-digital-celebrates-energizing-of-facility-in-ellendale-nd',
                                    'source_name': 'Jamestown Sun',
                                    'kind': 'statement'},
                                   {'what': "Spoke at the groundbreaking of Midco's "
                                            '$12 million Tier III data center in '
                                            'Fargo, calling fast, secure data services '
                                            'vital across energy, health care, and '
                                            'other sectors and the facility important '
                                            'infrastructure for attracting national '
                                            'companies.',
                                    'date': '2017-08-15',
                                    'source': 'https://www.hoeven.senate.gov/newsroom/press-releases/hoeven-new-data-center-will-be-vital-tech-infrastructure-for-north-dakota-help-bring-national-companies-to-the-region',
                                    'source_name': 'Sen. Hoeven press release',
                                    'kind': 'statement'}],
                         'as_of': '2026-09-05'},
 ('NE', 'Pete Ricketts'): {'lean': 'mixed',
                           'summary': 'Says data-center decisions should be governed '
                                      'by local control and that communities should '
                                      'negotiate protections for power rates, water, '
                                      'and tax payments before approving projects.',
                           'items': [{'what': 'At the Nebraska State Fair U.S. Senate '
                                              'debate said "when it comes to data '
                                              'centers, local control is the name of '
                                              'the game," that communities "should '
                                              'negotiate first" and are "in the '
                                              'driver\'s seat," and should insist "you '
                                              "shouldn't impact my power rates. You "
                                              'should conserve water - closed-loop '
                                              'systems," then ask for more in property '
                                              'taxes.',
                                      'date': '2026-09-01',
                                      'source': 'https://nebraskapublicmedia.org/en/news/news-articles/money-power-take-center-stage-during-ricketts-and-osborns-state-fair-debate/',
                                      'source_name': 'Nebraska Public Media',
                                      'kind': 'statement'}],
                           'as_of': '2026-09-05'},
 ('NH', 'Jeanne Shaheen'): {'lean': 'guardrails',
                            'summary': "Signed a New England senators' letter asking "
                                       'ISO New England how it will protect '
                                       'residential ratepayers from data-center-driven '
                                       'price increases, saying tech companies rather '
                                       'than families should pay for their load.',
                            'items': [{'what': 'Signed, with Sens. Welch, Blumenthal, '
                                               'Reed, Markey, and Whitehouse, a letter '
                                               'to ISO New England CEO Vamsi '
                                               'Chadalavada requesting the strategies '
                                               'ISO-NE plans to protect residential '
                                               'ratepayers from data-center-driven '
                                               'price increases, arguing that the AI '
                                               'industry, not families, should bear '
                                               'those costs.',
                                       'date': '2026-01-23',
                                       'source': 'https://www.shaheen.senate.gov/news/press/shaheen-joins-colleagues-in-searching-for-answers-about-how-new-regional-data-centers-will-drive-up-energy-costs-for-new-england-communities',
                                       'source_name': 'Sen. Shaheen press release',
                                       'kind': 'action'}],
                            'as_of': '2026-09-05'},
 ('NJ', 'Cory A. Booker'): {'lean': 'guardrails',
                            'summary': 'Beyond cosponsoring the Power for the People '
                                       'Act, Booker signed a March 2026 letter asking '
                                       'state utility regulators to reject rate '
                                       'filings that make ratepayers subsidize data '
                                       'centers and co-led a May 2025 letter pressing '
                                       'PJM on the data-center-driven capacity price '
                                       'increase.',
                            'items': [{'what': 'Signed a letter with Sens. Markey, '
                                               'Blumenthal and Van Hollen to NARUC '
                                               'president Ann Rendahl urging state '
                                               'public utility commissions to reject '
                                               'rate filings that force residential '
                                               'and small-business ratepayers to '
                                               'subsidize AI data centers and to adopt '
                                               'protective policies coordinated with '
                                               'utilities, grid operators and federal '
                                               'regulators.',
                                       'date': '2026-03-06',
                                       'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-colleagues-call-for-state-energy-regulators-to-protect-ratepayers-from-data-center-related-cost-hikes',
                                       'source_name': 'Sen. Markey press release',
                                       'kind': 'action'},
                                      {'what': 'Co-led, with Sen. Andy Kim and seven '
                                               'NJ House members, a letter to PJM '
                                               'Interconnection ahead of a ~17% June '
                                               '2025 rate increase; the letter says '
                                               'the 2024 capacity auction results '
                                               '"reflect the growing demand on the '
                                               'grid from data centers and advanced '
                                               'computer technology" and asks PJM what '
                                               'it is doing to lower rates, speed '
                                               'interconnection and prevent future '
                                               'price spikes.',
                                       'date': '2025-05-02',
                                       'source': 'https://www.kim.senate.gov/press_release/kim-booker-lead-members-of-nj-congressional-delegation-in-letter-to-pjm-interconnection-pjm-raising-serious-concerns-over-rate-increase-impacting-new-jersey-families/',
                                       'source_name': 'Sen. Kim press release',
                                       'kind': 'action'}],
                            'as_of': '2026-09-05'},
 ('NJ', 'Andy Kim'): {'lean': 'mixed',
                      'summary': 'Co-led a 2025 delegation letter pressing PJM on the '
                                 'data-center-driven rate increase, and separately '
                                 'introduced a bill encouraging co-location of AI data '
                                 'centers with advanced nuclear reactors on military '
                                 'installations.',
                      'items': [{'what': 'Co-led, with Sen. Booker and seven NJ House '
                                         'members, a letter to PJM Interconnection '
                                         'ahead of a ~17% June 2025 rate increase; the '
                                         'letter attributes the 2024 capacity auction '
                                         'results to "the growing demand on the grid '
                                         'from data centers and advanced computer '
                                         'technology" and asks PJM what it is doing to '
                                         'lower rates, speed interconnection and '
                                         'prevent future price spikes.',
                                 'date': '2025-05-02',
                                 'source': 'https://www.kim.senate.gov/press_release/kim-booker-lead-members-of-nj-congressional-delegation-in-letter-to-pjm-interconnection-pjm-raising-serious-concerns-over-rate-increase-impacting-new-jersey-families/',
                                 'source_name': 'Sen. Kim press release',
                                 'kind': 'action'},
                                {'what': 'Introduced with Sen. Tim Sheehy the Advanced '
                                         'Reactor Modernization for Operational '
                                         'Resilience (ARMOR) Act of 2025, which '
                                         'authorizes up to 50-year military contracts '
                                         'for power from advanced nuclear reactors '
                                         'and, per the release, encourages "the '
                                         'co-location of AI infrastructure and data '
                                         'centers" at those installations.',
                                 'date': '2025-07-23',
                                 'source': 'https://www.kim.senate.gov/press_release/senators-kim-and-sheehy-introduce-legislation-to-harness-nuclear-energy-and-bolster-national-defense/',
                                 'source_name': 'Sen. Kim press release',
                                 'kind': 'action'}],
                      'as_of': '2026-09-05'},
 ('NM', 'Martin Heinrich'): {'lean': 'guardrails',
                             'summary': 'Beyond the GRID Savings Act already on file, '
                                        'Heinrich co-signed a bipartisan letter '
                                        'backing FERC rulemaking on large-load '
                                        'interconnection, said at a March 2026 hearing '
                                        'that data centers must bear their own '
                                        'connection costs, and told Latitude Media '
                                        'that developers show "a healthy dose of '
                                        'arrogance" toward host communities.',
                             'items': [{'what': 'With Sen. Mike Lee, sent a bipartisan '
                                                "letter urging FERC to take up DOE's "
                                                'Section 403 proposal for a rulemaking '
                                                'on large-load interconnection; '
                                                'Heinrich called it "a step in the '
                                                'right direction" and said the rule '
                                                'should "ensure that households '
                                                "aren't left covering the increased "
                                                'demand from large new energy users."',
                                        'date': '2025-11-21',
                                        'source': 'https://www.heinrich.senate.gov/newsroom/press-releases/heinrich-lee-back-doe-proposal-requiring-ferc-action-on-large-load-grid-connections',
                                        'source_name': 'Sen. Heinrich press release',
                                        'kind': 'action'},
                                       {'what': 'At a Senate Energy and Natural '
                                                'Resources hearing on the power grid, '
                                                'said "new large loads, especially '
                                                'data centers, must bear the costs '
                                                'associated with them coming online" '
                                                'rather than shifting them to other '
                                                'ratepayers, and that 1% demand '
                                                'flexibility from large loads could '
                                                'unlock 126 GW of capacity.',
                                        'date': '2026-03-26',
                                        'source': 'https://www.heinrich.senate.gov/newsroom/press-releases/ranking-member-heinrich-offers-solutions-to-energy-affordability-crisis-worsening-under-trump-administration',
                                        'source_name': 'Sen. Heinrich press release',
                                        'kind': 'statement'},
                                       {'what': 'In a Latitude Media interview '
                                                'reposted by his office, said '
                                                'data-center developers should follow '
                                                "SunZia's community-first approach, "
                                                'that "there\'s a healthy dose of '
                                                'arrogance in some of these" '
                                                'proposals, and that a developer '
                                                'should be able to tell a community '
                                                '"we\'re actually going to be able to '
                                                'lower your electricity bills."',
                                        'date': '2026-06-23',
                                        'source': 'https://www.heinrich.senate.gov/newsroom/in-the-news/latitude-media-sen-heinrich-on-what-data-centers-can-learn-from-sunzia',
                                        'source_name': 'Latitude Media (via Sen. '
                                                       'Heinrich site)',
                                        'kind': 'statement'},
                                       {'what': 'At a July 2025 ENR hearing on '
                                                'electricity demand growth, questioned '
                                                'Vantage Data Centers EVP Jeff Tench '
                                                'about how Interior Department reviews '
                                                'delaying wind and solar on federal '
                                                'land affect data-center business and '
                                                'grid reliability.',
                                        'date': '2025-07-24',
                                        'source': 'https://www.heinrich.senate.gov/newsroom/press-releases/heinrich-criticizes-trump-administration-for-working-to-stall-energy-projects-and-raise-costs-on-families',
                                        'source_name': 'Sen. Heinrich press release',
                                        'kind': 'action'}],
                             'as_of': '2026-09-05'},
 ('NM', 'Ben Ray Luján'): {'lean': 'guardrails',
                           'summary': 'Introduced a bipartisan bill creating a 30% tax '
                                      'credit for onsite water-recycling systems at '
                                      'industrial facilities, explicitly including '
                                      'data centers.',
                           'items': [{'what': 'Introduced with Sen. Katie Britt the '
                                              'Advancing Water Reuse Act, a 30% '
                                              'investment tax credit for onsite water '
                                              'recycling systems at "manufacturing, '
                                              'food processing, and other industrial '
                                              'entities, including data center '
                                              'facilities," to replace '
                                              'freshwater/groundwater draws with '
                                              'recycled water.',
                                      'date': '2026-05-13',
                                      'source': 'https://www.lujan.senate.gov/newsroom/press-releases/lujan-britt-unveil-bipartisan-bill-to-boost-industrial-water-reuse-protect-community-drinking-water-and-meet-public-and-private-demand-for-freshwater/',
                                      'source_name': 'Sen. Luján press release',
                                      'kind': 'action'}],
                           'as_of': '2026-09-05'},
 ('NV', 'Catherine Cortez Masto'): {'lean': 'guardrails',
                                    'summary': 'Requested FY2027 earmark funding for a '
                                               'Desert Research Institute tool to help '
                                               'Nevadans weigh the water, energy and '
                                               'community trade-offs of rapid '
                                               'data-center growth.',
                                    'items': [{'what': 'Submitted a $1,570,000 FY2027 '
                                                       'community project request for '
                                                       'the Desert Research '
                                                       "Institute's Computing "
                                                       'Infrastructure Evaluation '
                                                       'Tool, "a cost-benefit '
                                                       'framework to help Nevadans '
                                                       'weigh trade-offs of rapid data '
                                                       'center growth, considering '
                                                       'water and energy resources, '
                                                       'economic stability, and '
                                                       'community well-being," plus '
                                                       '$2,107,000 for a UNLV Energy '
                                                       'Platform for Data Centers '
                                                       'research project.',
                                               'date': '2026',
                                               'source': 'https://www.cortezmasto.senate.gov/help/federal-funds/appropriations/senator-cortez-mastos-fy-2027-submitted-community-project-requests/',
                                               'source_name': 'Sen. Cortez Masto '
                                                              'FY2027 community '
                                                              'project requests',
                                               'kind': 'action'}],
                                    'as_of': '2026-09-05'},
 ('NY', 'Kirsten E. Gillibrand'): {'lean': 'guardrails',
                                   'summary': "Backed Gov. Hochul's one-year "
                                              'hyperscale data-center pause and says '
                                              'communities need guarantees on bills, '
                                              'water and air, while declining to take '
                                              'a position on the Stream project in '
                                              'Alabama, NY.',
                                   'items': [{'what': 'Issued a statement supporting '
                                                      "Gov. Hochul's executive order "
                                                      'pausing hyperscale data-center '
                                                      'construction for one year, '
                                                      'saying New Yorkers need '
                                                      '"ironclad guarantees that their '
                                                      "energy bills won't spike, their "
                                                      'water will be protected, and '
                                                      'their air will remain clean."',
                                              'date': '2026-07-14',
                                              'source': 'https://www.gillibrand.senate.gov/news/press/release/gillibrand-statement-on-new-york-state-data-center-moratorium/',
                                              'source_name': 'Sen. Gillibrand press '
                                                             'release',
                                              'kind': 'statement'},
                                             {'what': 'Asked about the proposed $19.5B '
                                                      'STREAM data center at the STAMP '
                                                      'site in Alabama, NY, said '
                                                      '"People are worried about '
                                                      "higher energy costs. They're "
                                                      'worried about emissions. '
                                                      "They're worried about polluting "
                                                      'water," that communities should '
                                                      'decide, and that developers '
                                                      'should use closed-loop cooling '
                                                      'and renewables rather than '
                                                      'ratepayer-funded grid upgrades, '
                                                      'while saying she lacked enough '
                                                      'information to take a position '
                                                      'on the project.',
                                              'date': '2026-06-25',
                                              'source': 'https://www.thedailynewsonline.com/news/gillibrand-cites-data-center-concerns-but-doesn-t-take-stand-on-stream-project/article_1a092e25-311c-41ef-8753-bea73e21ba8d.html',
                                              'source_name': 'The Daily News (Batavia, '
                                                             'NY)',
                                              'kind': 'statement'}],
                                   'as_of': '2026-09-05'},
 ('NY', 'Charles E. Schumer'): {'lean': 'guardrails',
                                'summary': 'Said Senate Democrats would push to make '
                                           'data centers "pay their fair share" and '
                                           'use more clean energy if they regain the '
                                           'majority.',
                                'items': [{'what': 'Told reporters that data centers '
                                                   'should "pay their fair share and '
                                                   'use more clean energy" and that '
                                                   'Democrats would pursue data-center '
                                                   'reform if they retake the Senate, '
                                                   'adding "We know how important they '
                                                   "are, and we've heard the message "
                                                   'loud and clear."',
                                           'date': '2026-07-14',
                                           'source': 'https://news.bgov.com/bloomberg-government-news/schumer-urges-more-clean-energy-to-fuel-important-data-centers',
                                           'source_name': 'Bloomberg Government',
                                           'kind': 'statement'}],
                                'as_of': '2026-09-05'},
 ('OH', 'Jon Husted'): {'lean': 'guardrails',
                        'summary': 'Beyond the Ratepayer Protection Act on file, '
                                   'Husted attended the March 2026 White House '
                                   'roundtable where hyperscalers signed the Ratepayer '
                                   'Protection Pledge, and says data-center siting is '
                                   'a local decision.',
                        'items': [{'what': 'Attended a White House roundtable with '
                                           'President Trump, Energy Secretary Wright '
                                           'and tech executives at which Amazon, '
                                           'Google, Meta and Microsoft committed to '
                                           'the Ratepayer Protection Pledge to fund '
                                           'their own data-center power; Husted said '
                                           '"Requiring companies to fund their own '
                                           'power protects working people from higher '
                                           'bills."',
                                   'date': '2026-03-04',
                                   'source': 'https://www.husted.senate.gov/media/press-releases/husted-attends-roundtable-with-president-on-lowering-energy-costs-for-communities-near-data-centers/',
                                   'source_name': 'Sen. Husted press release',
                                   'kind': 'statement'},
                                  {'what': 'Told Spectrum News "What we\'re requiring '
                                           'the data centers to do is to produce their '
                                           'own power so that the local ratepayers '
                                           'don\'t have to foot the bill," and that '
                                           'data-center siting decisions "should be '
                                           'made by local residents and local '
                                           'communities, not the federal government."',
                                   'date': '2026-07-28',
                                   'source': 'https://spectrumnews1.com/oh/columbus/news/2026/07/28/data-center-husted-ohio',
                                   'source_name': 'Spectrum News 1 Ohio',
                                   'kind': 'statement'}],
                        'as_of': '2026-09-05'},
 ('OH', 'Bernie Moreno'): {'lean': 'guardrails',
                           'summary': 'Publicly demanded that Carlyle-owned Ark Data '
                                      'Centers return a $4.5M Ohio subsidy and sign '
                                      'the Ratepayer Protection Pledge, and announced '
                                      'a plan for a federal tax clawing back 100% of '
                                      'state and local data-center incentives.',
                           'items': [{'what': 'Issued a release urging Carlyle Group '
                                              'to relinquish a $4.5M Ohio subsidy for '
                                              "Ark Data Centers' Akron/Independence "
                                              'expansion (10 jobs), sign the Ratepayer '
                                              'Protection Pledge and commit to more '
                                              'jobs, saying "When corporations like '
                                              'Carlyle demand massive amounts of '
                                              'electricity to fund their projects, '
                                              "it's everyday Ohioans who get stuck "
                                              'with the bill."',
                                      'date': '2026-03-16',
                                      'source': 'https://www.moreno.senate.gov/press-releases/moreno-slams-tax-breaks-to-pe-giant-for-data-center-project-creating-just-10-jobs/',
                                      'source_name': 'Sen. Moreno press release',
                                      'kind': 'statement'},
                                     {'what': 'At the Ohio Energy Affordability Summit '
                                              'announced he will introduce legislation '
                                              'imposing a federal tax equal to 100% of '
                                              'any state or local tax incentive given '
                                              'to a data center, saying "I don\'t want '
                                              'a single taxpayer dollar going to '
                                              'support these data centers."',
                                      'date': '2026-09-03',
                                      'source': 'https://www.cpapracticeadvisor.com/2026/09/03/ohio-senator-wants-to-wipe-out-data-center-tax-breaks-nationwide/189722/',
                                      'source_name': 'CPA Practice Advisor',
                                      'kind': 'statement'}],
                           'as_of': '2026-09-05'},
 ('OK', 'Alan Armstrong'): {'lean': 'accelerate',
                            'summary': 'Frames data centers as a reason to pass his '
                                       'permitting-reform bill, saying they will not '
                                       'invest without reliable, competitively priced '
                                       'energy.',
                            'items': [{'what': 'Promoting his American Energy and '
                                               'Mineral Infrastructure Act, said "A '
                                               'manufacturer, a data center, an '
                                               'industrial facility will not commit '
                                               'billions of dollars to a region if it '
                                               'cannot obtain reliable energy at a '
                                               'competitive price."',
                                       'date': '2026-07-16',
                                       'source': 'https://okenergytoday.com/2026/07/sen-armstrong-says-energy/',
                                       'source_name': 'Oklahoma Energy Today',
                                       'kind': 'statement'}],
                            'as_of': '2026-09-05'},
 ('OR', 'Jeff Merkley'): {'lean': 'guardrails',
                          'summary': "With Sen. Wyden, wrote Gov. Kotek's data center "
                                     'advisory committee listing constituent concerns '
                                     'about energy demand, consumer electricity costs, '
                                     'water, noise, farmland rezoning and tribal '
                                     'consultation.',
                          'items': [{'what': 'Co-signed with Sen. Wyden a letter to '
                                             "Gov. Tina Kotek's Oregon Data Center "
                                             'Advisory Committee asking it to consider '
                                             'rising energy demand, increased '
                                             'electricity costs for consumers, water '
                                             'quantity and quality, steam and noise '
                                             'from cooling, rezoning of agricultural '
                                             'land, tribal treaty consultation, and '
                                             'public transparency on environmental and '
                                             'infrastructure impacts.',
                                     'date': '2026-07-02',
                                     'source': 'https://www.merkley.senate.gov/wyden-merkley-ask-state-data-center-advisory-committee-to-consider-multiple-issues-raised-by-oregonians/',
                                     'source_name': 'Sen. Merkley press release',
                                     'kind': 'action'}],
                          'as_of': '2026-09-05'},
 ('OR', 'Ron Wyden'): {'lean': 'guardrails',
                       'summary': 'Pressed Google, Apple, Meta and Amazon on '
                                  'data-center water use, co-signed a letter to '
                                  "Oregon's data center advisory committee, and as "
                                  'Finance ranking member released a white paper '
                                  'proposing to strip data centers of federal '
                                  'investment incentives and levy a new excise tax.',
                       'items': [{'what': 'Sent letters to the CEOs of Google, Apple, '
                                          'Meta and Amazon demanding answers on '
                                          'data-center water impacts in drought-prone '
                                          'Oregon (over 100 data centers), asking '
                                          'about closed-loop cooling, groundwater '
                                          'withdrawal, contaminant mitigation, public '
                                          'water tracking and community transparency, '
                                          'with a May 29 response deadline.',
                                  'date': '2026-04-30',
                                  'source': 'https://www.wyden.senate.gov/news/press-releases/wyden-demands-big-tech-execs-answer-questions-about-data-centers-water-impact',
                                  'source_name': 'Sen. Wyden press release',
                                  'kind': 'action'},
                                 {'what': 'Co-signed with Sen. Merkley a letter to '
                                          "Gov. Kotek's Oregon Data Center Advisory "
                                          'Committee raising energy demand, consumer '
                                          'electricity costs, water, noise, farmland '
                                          'rezoning, tribal consultation and '
                                          'transparency.',
                                  'date': '2026-07-02',
                                  'source': 'https://www.merkley.senate.gov/wyden-merkley-ask-state-data-center-advisory-committee-to-consider-multiple-issues-raised-by-oregonians/',
                                  'source_name': 'Sen. Merkley press release',
                                  'kind': 'action'},
                                 {'what': 'As Finance Committee ranking member '
                                          'released a white paper proposing to remove '
                                          'existing tax investment incentives as '
                                          'applied to data centers and create a Data '
                                          'Center Public Investment excise tax, with '
                                          'revenue for workers displaced by AI; said '
                                          'communities "are rightfully questioning '
                                          'whether the rapid buildout of data centers '
                                          'across the nation will benefit them, as '
                                          'local disruptions rise."',
                                  'date': '2026-08-06',
                                  'source': 'https://www.finance.senate.gov/ranking-members-news/wyden-unveils-proposal-to-ensure-data-centers-pay-for-disruptions-caused-to-communities',
                                  'source_name': 'Senate Finance Committee (Ranking '
                                                 'Member) release',
                                  'kind': 'action'}],
                       'as_of': '2026-09-05'},
 ('PA', 'John Fetterman'): {'lean': 'accelerate',
                            'summary': "Beyond the 'China First' remark on file, "
                                       'Fetterman posted that he rejects "political '
                                       'pandering and hyperbole over data centers" and '
                                       "said he agrees with President Trump's defense "
                                       'of data centers.',
                            'items': [{'what': 'Posted on X, as quoted by TribLive: '
                                               '"AI supremacy and energy dominance '
                                               'underpins our national security" and '
                                               '"I reject the political pandering and '
                                               'hyperbole over data centers," adding '
                                               '"America must lead in the development '
                                               "of AI, otherwise we live under China's "
                                               'rules."',
                                       'date': '2026-08-24',
                                       'source': 'https://community.triblive.com/news/4122896',
                                       'source_name': 'TribLive',
                                       'kind': 'statement'},
                                      {'what': 'Posted on X, as quoted by the '
                                               'Philadelphia Inquirer, that he agreed '
                                               "with President Trump's defense of data "
                                               'centers: "There\'s nothing more '
                                               'damaging to a Democrat than agreeing '
                                               'with Trump AND data centers — but '
                                               'what\'s right is right," and "We must '
                                               'win the war for AI supremacy over '
                                               'China."',
                                       'date': '2026-08-31',
                                       'source': 'https://www.inquirer.com/politics/nation/fetterman-trump-data-centers-ai-20260831.html',
                                       'source_name': 'Philadelphia Inquirer',
                                       'kind': 'statement'}],
                            'as_of': '2026-09-05'},
 ('PA', 'David McCormick'): {'lean': 'mixed',
                             'summary': 'Convened the 2025 Pittsburgh Energy and '
                                        'Innovation Summit that announced $90B+ in '
                                        'data-center and energy investment, and in '
                                        '2026 laid out an "AI covenant" that includes '
                                        'rate protection, closed-loop water and local '
                                        'decision-making.',
                             'items': [{'what': 'Hosted the Pennsylvania Energy and '
                                                'Innovation Summit with President '
                                                'Trump, where companies announced more '
                                                'than $90 billion in data-center, '
                                                'energy and workforce investments '
                                                '(CoreWeave $6B Lancaster, Blackstone '
                                                '$25B NE PA, ECP $5B York); the fact '
                                                'sheet mentions no ratepayer or '
                                                'community safeguards.',
                                        'date': '2025-07-15',
                                        'source': 'https://www.mccormick.senate.gov/news/press-releases/fact-sheet-more-than-90-billion-in-investments-announced-at-senator-mccormicks-pennsylvania-energy-and-innovation-summit/',
                                        'source_name': 'Sen. McCormick press release',
                                        'kind': 'action'},
                                       {'what': 'In a City & State Q&A reposted by his '
                                                'office, described an "AI covenant" '
                                                'for data centers: "You need to '
                                                'protect rates for the people in the '
                                                'community... give them rate '
                                                'protection or bring more energy than '
                                                'you use," "You need to protect the '
                                                'water... via a closed loop," and "The '
                                                'ultimate decision-making power is '
                                                'going to reside with the communities '
                                                '– township supervisors, county '
                                                'commissioners and the people."',
                                        'date': '2026-07-28',
                                        'source': 'https://www.mccormick.senate.gov/news/in-the-news/the-city-state-qa-dave-mccormick/',
                                        'source_name': 'City & State PA (via Sen. '
                                                       'McCormick site)',
                                        'kind': 'statement'}],
                             'as_of': '2026-09-05'},
 ('RI', 'Jack Reed'): {'lean': 'guardrails',
                       'summary': "Co-led a New England senators' letter asking ISO "
                                  'New England how it will shield residential '
                                  'ratepayers from data-center-driven price increases.',
                       'items': [{'what': 'With Sen. Whitehouse, Sen. Welch and three '
                                          'other New England senators, wrote ISO New '
                                          'England CEO Vamsi Chadalavada asking what '
                                          'strategies the grid operator will use to '
                                          'protect residential customers from '
                                          'data-center-driven price increases; Reed '
                                          'said "We believe it is necessary to require '
                                          'tech companies, not American families, to '
                                          'foot the bill for their load."',
                                  'date': '2026-01-28',
                                  'source': 'https://www.reed.senate.gov/news/releases/reed-and-whitehouse-seek-answers-about-how-new-regional-data-centers-could-drive-up-energy-health_environmental-costs-for-consumers',
                                  'source_name': 'Sen. Reed press release',
                                  'kind': 'action'}],
                       'as_of': '2026-09-05'},
 ('RI', 'Sheldon Whitehouse'): {'lean': 'guardrails',
                                'summary': 'Co-led the January 2026 ISO New England '
                                           'letter on data-center-driven rate '
                                           'increases and in December 2024 urged the '
                                           'White House not to fast-track data-center '
                                           'buildout at the expense of clean-air, '
                                           'clean-water and household-cost '
                                           'protections.',
                                'items': [{'what': 'With Sen. Reed and four other New '
                                                   'England senators, wrote ISO New '
                                                   'England asking how it will shield '
                                                   'residential ratepayers from '
                                                   'data-center-driven price '
                                                   'increases; said "As the ones who '
                                                   'stand to benefit most, the '
                                                   'multi-billion-dollar AI industry '
                                                   'should be responsible for these '
                                                   'costs."',
                                           'date': '2026-01-29',
                                           'source': 'https://www.whitehouse.senate.gov/news/release/reed-whitehouse-seek-answers-about-how-new-regional-data-centers-could-drive-up-energy-health-environmental-costs-for-consumers/',
                                           'source_name': 'Sen. Whitehouse press '
                                                          'release',
                                           'kind': 'action'},
                                          {'what': 'Led a letter with Sens. Schatz, '
                                                   'Welch, Markey and Warren urging '
                                                   'the Biden White House to '
                                                   'reconsider a proposed executive '
                                                   'order fast-tracking AI data-center '
                                                   'construction, asking it to keep '
                                                   'clean air and water standards and '
                                                   "not prioritize tech companies' "
                                                   'energy needs over households; said '
                                                   'large companies "should not" be '
                                                   'relieved of bringing new clean '
                                                   'energy "while passing higher '
                                                   'energy costs on to working '
                                                   'families."',
                                           'date': '2024-12-17',
                                           'source': 'https://www.whitehouse.senate.gov/news/release/whitehouse-colleagues-urge-white-house-to-reconsider-potential-executive-action-on-fast-track-data-center-buildout-for-ai/',
                                           'source_name': 'Sen. Whitehouse press '
                                                          'release',
                                           'kind': 'action'}],
                                'as_of': '2026-09-05'},
 ('SC', 'Darline Graham'): {'lean': 'mixed',
                            'summary': 'Says she supports data centers but that there '
                                       'must be community involvement, guidelines and '
                                       'guardrails.',
                            'items': [{'what': 'In the South Carolina GOP Senate '
                                               'debate said: "Obviously, I just said '
                                               "I'm for data centers, but I also said "
                                               'that there needs to be community '
                                               'involvement, community guidelines, '
                                               'community guardrails."',
                                       'date': '2026-08-18',
                                       'source': 'https://www.nbcnews.com/politics/2026-election/darline-graham-defends-resume-south-carolina-debate-saying-national-se-rcna593244',
                                       'source_name': 'NBC News',
                                       'kind': 'statement'}],
                            'as_of': '2026-09-05'},
 ('SC', 'Tim Scott'): {'lean': 'mixed',
                       'summary': "In a July 2026 op-ed welcomed Google's Lowcountry "
                                  'data centers while insisting families and small '
                                  'businesses should not pay higher electric bills for '
                                  'them, praising the Ratepayer Protection Pledge.',
                       'items': [{'what': 'Authored a Post and Courier commentary '
                                          'saying data centers are vital to '
                                          'competitiveness and national security, that '
                                          '"Hardworking families and small businesses '
                                          'should not have higher electric bills '
                                          'because of the energy demands of massive '
                                          'global corporations," and praising '
                                          "Google's commitment to the Ratepayer "
                                          'Protection Pledge to secure 100% of its '
                                          'added energy needs without passing costs to '
                                          'ratepayers.',
                                  'date': '2026-07-23',
                                  'source': 'https://www.postandcourier.com/opinion/commentary/tim-scott-google-ai-data-center-electricity/article_1d0b0933-9c98-4188-b9d7-e783fdce8166.html',
                                  'source_name': 'The Post and Courier (op-ed by Sen. '
                                                 'Scott)',
                                  'kind': 'statement'}],
                       'as_of': '2026-09-05'},
 ('SD', 'Mike Rounds'): {'lean': 'mixed',
                         'summary': 'Told KOTA that data centers should go only where '
                                    'local residents actively welcome them, and '
                                    'predicted most new data centers will eventually '
                                    'be built in space.',
                         'items': [{'what': 'In a KOTA Territory TV interview on Rapid '
                                            'City data-center backlash and a proposed '
                                            'EPA permit change, Rounds said data '
                                            'centers must go only where they are '
                                            'actively welcomed by local populations '
                                            'and must remain grounded in extensive '
                                            'discussion with local residents; he added '
                                            'that long-term most new data centers will '
                                            'probably be based in space.',
                                    'date': '2026-09-05',
                                    'source': 'https://www.kotatv.com/2026/09/05/rapid-city-data-center-backlash-epa-rules-meta-cash-space-tech/',
                                    'source_name': 'KOTA Territory TV',
                                    'kind': 'statement'}],
                         'as_of': '2026-09-05'},
 ('SD', 'John Thune'): {'lean': 'mixed',
                        'summary': 'Says data centers should be self-sufficient in '
                                   'power and should not be built where there is no '
                                   'local support, while pushing permitting reform to '
                                   'meet data-center-driven demand.',
                        'items': [{'what': "Told KELOLAND that data centers 'need to "
                                           'be self-sufficient. They ought to be able '
                                           'to take care of their own utilities, their '
                                           'own power, and that ought to be a given '
                                           'any place they go in the country. But they '
                                           "shouldn't be going places where there "
                                           "isn't support for them at the local "
                                           "level.'",
                                   'date': '2026-08-31',
                                   'source': 'https://talkingpointsmemo.com/where-things-stand/thune-tries-to-carve-out-lane-for-gop-on-data-centers-beyond-trumps-poor-people-bombast',
                                   'source_name': 'Talking Points Memo (quoting '
                                                  'KELOLAND interview)',
                                   'kind': 'statement'},
                                  {'what': 'In an August 2026 South Dakota appearance, '
                                           'Thune called energy permitting reform a '
                                           'rare bipartisan opportunity, citing '
                                           "utilities' rapidly growing demand "
                                           "'including that associated with data "
                                           "centers'; he framed faster permitting as "
                                           'the way to add generation and '
                                           'transmission.',
                                   'date': '2026-08-20',
                                   'source': 'https://www.kotatv.com/2026/08/20/thune-calls-energy-development-permitting-reform-rare-opportunity-bipartisan-action/',
                                   'source_name': 'KOTA Territory TV / South Dakota '
                                                  'Searchlight',
                                   'kind': 'statement'},
                                  {'what': "Floor remarks 'Energy Security is National "
                                           "Security' warned that 'the boom in data "
                                           'center construction – in particular to '
                                           'power the rise of artificial intelligence '
                                           '– is placing, and will place, vast new '
                                           "demands upon the grid,' arguing for more "
                                           'conventional energy supply.',
                                   'date': '2025-02-25',
                                   'source': 'https://www.republicanleader.senate.gov/newsroom/remarks/thune-energy-security-is-national-security',
                                   'source_name': 'Senate Majority Leader Thune floor '
                                                  'remarks',
                                   'kind': 'statement'}],
                        'as_of': '2026-09-05'},
 ('TN', 'Marsha Blackburn'): {'lean': 'mixed',
                              'summary': 'Her TRUMP AMERICA AI Act framework would '
                                         'make data-center operators bear the full '
                                         'cost of energy and water infrastructure with '
                                         'no impact on ratepayers, and she publicly '
                                         'asked DC Blox to revisit a data-center site '
                                         'next to the Nashville Zoo while backing data '
                                         'centers generally.',
                              'items': [{'what': 'Unveiled the TRUMP AMERICA AI Act '
                                                 'national AI framework, which '
                                                 "'requires data center operators to "
                                                 'be responsible for the full cost of '
                                                 'all energy and water infrastructure '
                                                 'needed for their operation, '
                                                 'including construction, maintenance, '
                                                 'and upgrades with no impact on '
                                                 "ratepayers.'",
                                         'date': '2025-12-19',
                                         'source': 'https://www.blackburn.senate.gov/2025/12/technology/blackburn-unveils-national-policy-framework-for-artificial-intelligence',
                                         'source_name': 'Sen. Blackburn press release',
                                         'kind': 'action'},
                                        {'what': 'Released a discussion draft of the '
                                                 "TRUMP AMERICA AI Act that 'directs "
                                                 'the U.S. Secretary of Energy to '
                                                 'enter into agreements with owners '
                                                 'and operators of data centers to '
                                                 'protect consumers from rate '
                                                 'increases and adverse impacts of '
                                                 "data center development'; entities "
                                                 'that decline become ineligible for '
                                                 'federal incentives the Secretary '
                                                 'identifies.',
                                         'date': '2026-03-18',
                                         'source': 'https://www.blackburn.senate.gov/index.php/2026/3/technology/blackburn-releases-discussion-draft-of-national-policy-framework-for-artificial-intelligence/3b3b6458-b6c7-478b-9859-374949586765',
                                         'source_name': 'Sen. Blackburn press release',
                                         'kind': 'action'},
                                        {'what': 'Posted a video questioning the '
                                                 "location of DC Blox's proposed data "
                                                 'center next to the Nashville Zoo and '
                                                 "calling on the developer to 'revisit "
                                                 "this placement,' while making clear "
                                                 'she supports data centers more '
                                                 'broadly.',
                                         'date': '2026-06-15',
                                         'source': 'https://nashvillebanner.com/2026/06/15/marsha-blackburn-data-center-christa-pike/',
                                         'source_name': 'Nashville Banner',
                                         'kind': 'statement'}],
                              'as_of': '2026-09-05'},
 ('TN', 'Bill Hagerty'): {'lean': 'guardrails',
                          'summary': 'Said in Knoxville that data centers will have to '
                                     'invest in grid capacity themselves so consumers '
                                     'are not bearing the burden, responding to East '
                                     'Tennessee moratoriums.',
                          'items': [{'what': 'During a Knoxville visit, asked about '
                                             "East Tennessee local governments' "
                                             '12-month data-center moratoriums, '
                                             "Hagerty said 'we made it very clear to "
                                             "the data centers that they're going to "
                                             'have to make the investment, not only in '
                                             "our capacity but in our grid,' and that "
                                             'tech companies must ensure consumers are '
                                             "not 'bearing the burden' of the "
                                             'facilities.',
                                     'date': '2026-08-11',
                                     'source': 'https://www.yahoo.com/news/politics/articles/sen-bill-hagerty-discusses-economic-194530943.html',
                                     'source_name': 'WBIR (via Yahoo News)',
                                     'kind': 'statement'}],
                          'as_of': '2026-09-05'},
 ('TX', 'Ted Cruz'): {'lean': 'mixed',
                      'summary': 'Toured and applauded the Oracle/OpenAI Stargate data '
                                 'center in Abilene, and later said data-center '
                                 "concerns are 'real and reasonable' and that "
                                 "developers should pay affected residents' electric "
                                 'bills.',
                      'items': [{'what': 'Press release after touring Oracle and '
                                         "OpenAI's Stargate AI data center in Abilene: "
                                         "'Texas is leading the way to make sure the "
                                         'United States beats China in the AI race. '
                                         'This is the beginning of a long-term effort '
                                         'to invest in American jobs, supply the '
                                         'additional power needed for AI, and deliver '
                                         'products and services that will benefit all '
                                         "Americans.'",
                                 'date': '2025-09-24',
                                 'source': 'https://www.cruz.senate.gov/newsroom/press-releases/sen-cruz-tours-oracle-and-openais-ai-data-center-in-abilene-applauds-announcement-of-further-investment-in-texas',
                                 'source_name': 'Sen. Cruz press release',
                                 'kind': 'statement'},
                                {'what': "On NewsNation's 'Katie Pavlich Tonight', "
                                         "Cruz said 'the concerns being raised about "
                                         "data centers are real and reasonable' and "
                                         'suggested developers offer residents direct '
                                         "payments or tell them 'your electricity bill "
                                         'is zero for the rest of your life. We will '
                                         "pay your electric bill—forever.'",
                                 'date': '2026-08-25',
                                 'source': 'https://www.yahoo.com/news/politics/articles/data-centers-offer-cash-financial-020733395.html',
                                 'source_name': 'NewsNation (via Yahoo News)',
                                 'kind': 'statement'}],
                      'as_of': '2026-09-05'},
 ('UT', 'John R. Curtis'): {'lean': 'mixed',
                            'summary': 'After the Stratos data-center controversy in '
                                       'Utah, Curtis said data-center siting is a '
                                       'local issue but that he wants to work on '
                                       'federal transparency standards for data-center '
                                       'energy and water metrics.',
                            'items': [{'what': 'Told Roll Call, on the Utah '
                                               "data-center uproar, 'I have almost no "
                                               "data on the water usage. I've heard "
                                               "it's closed-loop, but I don't know "
                                               "that,' called siting 'a local issue,' "
                                               'and said he was open to a '
                                               'congressional certification system for '
                                               'AI facilities similar to LEED building '
                                               'standards.',
                                       'date': '2026-06-11',
                                       'source': 'https://rollcall.com/2026/06/11/data-center-uproar-utah-congress-watching-waiting/',
                                       'source_name': 'Roll Call',
                                       'kind': 'statement'},
                                      {'what': 'Told Utah News Dispatch, citing '
                                               "distrust after the Stratos project's "
                                               'quick approval through the Military '
                                               'Installation Development Authority, '
                                               "that 'we do have some real uncertainty "
                                               "about these data centers. What's "
                                               "behind the meter? What's not?' and "
                                               "that 'something that I want to work on "
                                               'at the federal level is bringing some '
                                               'reliable, predictable measuring '
                                               "techniques' so the public has standard "
                                               'metrics; he said the industry had '
                                               "'failed' at explaining why the "
                                               'facilities are needed.',
                                       'date': '2026-07-07',
                                       'source': 'https://www.heraldextra.com/news/2026/jul/07/after-utah-data-center-controversy-curtis-calls-for-federal-transparency-standards/',
                                       'source_name': 'Utah News Dispatch (via Daily '
                                                      'Herald)',
                                       'kind': 'statement'}],
                            'as_of': '2026-09-05'},
 ('UT', 'Mike Lee'): {'lean': 'mixed',
                      'summary': 'As Energy Committee chair he held a 2025 hearing on '
                                 'data-center-driven demand, said in 2026 that '
                                 'existing ratepayers should not subsidize data '
                                 "centers and backed FERC's large-load order, but said "
                                 'data-center legislation is not currently a priority.',
                      'items': [{'what': 'Chaired a Senate Energy and Natural '
                                         'Resources hearing on surging electricity '
                                         "demand, saying 'America's electricity demand "
                                         "is surging. We're entering a new era driven "
                                         'by data centers, AI computing, electric '
                                         "vehicles, and manufacturing returning home.'",
                                 'date': '2025-07-23',
                                 'source': 'https://www.energy.senate.gov/2025/7/chairman-lee-holds-hearing-to-address-urgent-challenges-facing-america-s-skyrocketing-energy-demands',
                                 'source_name': 'Senate Energy and Natural Resources '
                                                'Committee release',
                                 'kind': 'action'},
                                {'what': 'Told E&E News he had no immediate plans to '
                                         "take up data-center legislation: 'I don't "
                                         'currently have that identified as a '
                                         "priority,' while saying he was 'happy to "
                                         "look at' the Ratepayer Protection Act.",
                                 'date': '2026-06',
                                 'source': 'https://www.eenews.net/articles/house-committee-narrows-data-center-energy-bill-3/',
                                 'source_name': 'E&E News',
                                 'kind': 'statement'},
                                {'what': "At the committee's FERC oversight hearing, "
                                         "Lee said he supported FERC's Large Load "
                                         "Order, called it 'not a one-size-fits-all "
                                         "solution,' and agreed that 'existing "
                                         'ratepayers should not subsidize the cost of '
                                         "data centers.'",
                                 'date': '2026-07-22',
                                 'source': 'https://www.publicpower.org/periodical/article/senate-energy-natural-resources-committee-holds-ferc-oversight-hearing',
                                 'source_name': 'American Public Power Association',
                                 'kind': 'statement'}],
                      'as_of': '2026-09-05'},
 ('VA', 'Tim Kaine'): {'lean': 'mixed',
                       'summary': 'Opposes a statewide data-center moratorium and '
                                  "points to Virginia's energy-consumption tax as the "
                                  'way to make data centers pay their full electricity '
                                  'costs.',
                       'items': [{'what': 'Told E&E News he opposes a data-center '
                                          "moratorium: 'I think a moratorium would "
                                          'send the message to other nations, "Hey, '
                                          'the U.S. is giving up leadership in this '
                                          'space," and I don\'t want to send that '
                                          "message.'",
                                  'date': '2026-04-22',
                                  'source': 'https://www.eenews.net/articles/data-center-moratorium-a-fault-line-in-dem-primaries/',
                                  'source_name': 'E&E News',
                                  'kind': 'statement'}],
                       'as_of': '2026-09-05'},
 ('VA', 'Mark R. Warner'): {'lean': 'mixed',
                            'summary': 'ADDITIONAL: in July 2026 rolled out the Data '
                                       'Center Tax Accountability and Disclosure Act, '
                                       'which requires large AI data centers to '
                                       'disclose energy, water, emissions and '
                                       'backup-generation data and conditions bonus '
                                       'depreciation on efficiency standards; in April '
                                       "2026 he called a moratorium 'idiocy'.",
                            'items': [{'what': 'Rolled out an AI legislative agenda '
                                               'including the Data Center Tax '
                                               'Accountability and Disclosure Act, '
                                               'which requires large AI data centers '
                                               'to publicly disclose energy and water '
                                               'consumption, emissions, backup '
                                               'generation and other operational '
                                               'impacts, conditions federal bonus '
                                               'depreciation on meeting efficiency and '
                                               'sustainability standards, and '
                                               'dedicates the resulting revenue to a '
                                               'National Workforce Transition Fund.',
                                       'date': '2026-07-21',
                                       'source': 'https://www.warner.senate.gov/newsroom/press-releases/warner-rolls-out-comprehensive-ai-legislative-agenda-focused-on-responsible-innovation-workers-and-national-security/',
                                       'source_name': 'Sen. Warner press release',
                                       'kind': 'action'},
                                      {'what': 'Dismissed the proposed data-center '
                                               "moratorium as 'idiocy' at an Axios "
                                               'event, per E&E News.',
                                       'date': '2026-04-22',
                                       'source': 'https://www.eenews.net/articles/data-center-moratorium-a-fault-line-in-dem-primaries/',
                                       'source_name': 'E&E News',
                                       'kind': 'statement'}],
                            'as_of': '2026-09-05'},
 ('VT', 'Bernard Sanders'): {'lean': 'guardrails',
                             'summary': 'Introduced the AI Data Center Moratorium Act '
                                        '(S.4214) with Rep. Ocasio-Cortez to halt new '
                                        'AI data centers until federal safeguards, '
                                        'including against higher utility costs and '
                                        'community harm, are in place.',
                             'items': [{'what': 'Announced the Artificial Intelligence '
                                                'Data Center Moratorium Act of 2026 '
                                                'with Rep. Alexandria Ocasio-Cortez: a '
                                                'federal moratorium on new or expanded '
                                                'AI data centers until Congress enacts '
                                                'safeguards ensuring AI does not '
                                                "increase 'electricity or utility "
                                                'prices, harm communities or destroy '
                                                "the environment'; introduced as "
                                                'S.4214.',
                                        'date': '2026-03-25',
                                        'source': 'https://www.sanders.senate.gov/press-releases/news-sanders-ocasio-cortez-announce-ai-data-center-moratorium-act/',
                                        'source_name': 'Sen. Sanders press release',
                                        'kind': 'action'}],
                             'as_of': '2026-09-05'},
 ('VT', 'Peter Welch'): {'lean': 'guardrails',
                         'summary': 'ADDITIONAL: co-signed a January 2026 letter to '
                                    'ISO New England asking how it will shield '
                                    'residential customers from data-center-driven '
                                    'cost increases and saying the AI industry should '
                                    'bear those costs.',
                         'items': [{'what': 'Signed, with Sens. Markey, Shaheen, '
                                            'Blumenthal, Reed and Whitehouse, a letter '
                                            'to ISO New England CEO Vamsi Chadalavada '
                                            'asking how the grid operator will protect '
                                            'residential ratepayers from '
                                            'data-center-driven price increases, '
                                            "stating 'the multi-billion-dollar AI "
                                            'industry should be responsible for these '
                                            "costs.'",
                                    'date': '2026-01-28',
                                    'source': 'https://www.markey.senate.gov/news/press-releases/markey-welch-new-england-senators-call-for-answers-about-how-new-regional-data-centers-will-drive-up-energy-costs-for-consumers',
                                    'source_name': 'Sen. Markey press release',
                                    'kind': 'action'}],
                         'as_of': '2026-09-05'},
 ('WA', 'Maria Cantwell'): {'lean': 'accelerate',
                            'summary': "Dismissed environmental groups' call for a "
                                       'data-center moratorium, saying they should '
                                       'instead push an all-of-the-above energy plan '
                                       'that builds renewables to meet demand.',
                            'items': [{'what': "Asked about environmental groups' call "
                                               'for a data-center moratorium, Cantwell '
                                               "said advocates 'should call for an "
                                               'above-all energy plan that allows for '
                                               'the construction of renewables to play '
                                               "into that demand for the future,' "
                                               "adding 'we're growing, so we need more "
                                               "energy sources.'",
                                       'date': '2025-12-10',
                                       'source': 'https://www.eenews.net/articles/lawmakers-oppose-greens-call-for-data-center-moratorium/',
                                       'source_name': 'E&E News',
                                       'kind': 'statement'}],
                            'as_of': '2026-09-05'},
 ('WI', 'Tammy Baldwin'): {'lean': 'guardrails',
                           'summary': 'Says data-center developers must commit to '
                                      'local communities that residents will not '
                                      'shoulder the energy and water costs, and that '
                                      'any moratorium is for the state Legislature to '
                                      'consider.',
                           'items': [{'what': "Told Wisconsin Watch: 'The developers "
                                              'of these need to have commitments to '
                                              "the local community that they won't "
                                              "see, that they won't have to shoulder "
                                              'the costs of the energy use and water '
                                              "use by these data centers,' and said "
                                              'any data-center moratorium should first '
                                              'be considered by the state Legislature.',
                                      'date': '2026-01-22',
                                      'source': 'https://wisconsinwatch.org/2026/01/wisconsin-data-centers-politics-ai-port-washington-federal-lawmakers/',
                                      'source_name': 'Wisconsin Watch',
                                      'kind': 'statement'}],
                           'as_of': '2026-09-05'},
 ('WI', 'Ron Johnson'): {'lean': 'mixed',
                         'summary': "Called data centers' impact on Wisconsin's "
                                    "electric grid a 'very serious concern' and "
                                    'questioned whether local officials had factored '
                                    'it in properly.',
                         'items': [{'what': "Told Wisconsin Watch that data centers' "
                                            "impact on the state's electrical grid is "
                                            "a 'very serious concern,' adding he is "
                                            "unsure local officials have 'really "
                                            "factored it in properly.'",
                                    'date': '2026-01-22',
                                    'source': 'https://wisconsinwatch.org/2026/01/wisconsin-data-centers-politics-ai-port-washington-federal-lawmakers/',
                                    'source_name': 'Wisconsin Watch',
                                    'kind': 'statement'}],
                         'as_of': '2026-09-05'},
 ('WV', 'Shelley Moore Capito'): {'lean': 'mixed',
                                  'summary': 'Actively recruits data centers to West '
                                             "Virginia ('we want them') while saying "
                                             'operators must engage communities early '
                                             'and be transparent about local effects.',
                                  'items': [{'what': 'On efforts to bring a data '
                                                     "center to Logan County, said 'We "
                                                     'want them in West Virginia. They '
                                                     'are massive investments, '
                                                     "billions of dollars,' and 'The "
                                                     'appetite for power is going to '
                                                     "be so huge. Everyone's going to "
                                                     "win here.'",
                                             'date': '2024-12-12',
                                             'source': 'https://wvpublic.org/story/energy-environment/we-want-them-capito-supports-efforts-to-build-a-data-center/',
                                             'source_name': 'West Virginia Public '
                                                            'Broadcasting',
                                             'kind': 'statement'},
                                            {'what': 'Said data-center companies must '
                                                     'have early and strong community '
                                                     'engagement and that '
                                                     "'transparency about the process "
                                                     'and the effects on local '
                                                     "residents could go a long way'; "
                                                     'said proposed projects plan to '
                                                     'build their own power, which '
                                                     "'could actually maybe improve "
                                                     'the situation because there will '
                                                     'be excess power probably '
                                                     "created,' and that water drawn "
                                                     'from the Ohio would be '
                                                     'replenished and cleaned.',
                                             'date': '2026-04-24',
                                             'source': 'https://www.capito.senate.gov/news/in-the-news/west-virginia-senator-says-early-community-engagement-from-data-centers-is-key',
                                             'source_name': 'Fox 8 (reposted on '
                                                            'capito.senate.gov)',
                                             'kind': 'statement'}],
                                  'as_of': '2026-09-05'},
 ('WV', 'James C. Justice'): {'lean': 'mixed',
                              'summary': 'Touts data-center investment in Mason County '
                                         'and tells companies coming to West Virginia '
                                         "they must 'take care of everybody' on "
                                         'electricity bills, water, noise and the '
                                         'environment.',
                              'items': [{'what': 'Press release applauding American '
                                                 "Power and Intelligence Corporation's "
                                                 'multi-billion-dollar data center and '
                                                 'microgrid campus in Mason County, a '
                                                 'project he first announced with '
                                                 'Fidelis New Energy as governor in '
                                                 "2023: 'I truly could not be prouder "
                                                 'to see the seeds of our work from '
                                                 "years ago begin to bloom.'",
                                         'date': '2026-01-28',
                                         'source': 'https://www.justice.senate.gov/press-releases/senator-justice-touts-multi-billion-dollar-investment-in-mason-county-through-fidelis-new-energy/',
                                         'source_name': 'Sen. Justice press release',
                                         'kind': 'statement'},
                                        {'what': 'At the West Virginia Chamber of '
                                                 'Commerce annual meeting, urged '
                                                 'attendees not to fear data centers '
                                                 'but said companies must be '
                                                 "responsible neighbors: 'If you're "
                                                 'going to come to West Virginia and '
                                                 "you're going to do something in West "
                                                 'Virginia, you need to be taking care '
                                                 'of everybody. The environment, the '
                                                 'water, the electricity bills, the '
                                                 "noise. You've got to take care of "
                                                 "everybody, and there's a way to do "
                                                 "it.'",
                                         'date': '2026-09-03',
                                         'source': 'https://www.newsandsentinel.com/news/business/2026/09/capito-justice-focus-remarks-on-energy-at-90th-annual-w-va-chamber-meeting/',
                                         'source_name': 'Parkersburg News and Sentinel',
                                         'kind': 'statement'}],
                              'as_of': '2026-09-05'},
 ('WY', 'John Barrasso'): {'lean': 'mixed',
                           'summary': 'Backs faster data-center construction powered '
                                      'by coal and other Wyoming energy, while saying '
                                      'data centers on federal land deserve meaningful '
                                      'state, local and public input.',
                           'items': [{'what': 'Senate floor speech praising the Trump '
                                              "AI Action Plan because 'it tears down "
                                              "barriers to building new data centers,' "
                                              'arguing that data centers need steady, '
                                              'reliable power and that more American '
                                              'energy means data centers grow in '
                                              'America rather than overseas.',
                                      'date': '2025-07-30',
                                      'source': 'https://www.barrasso.senate.gov/barrasso-whoever-powers-the-ai-revolution-will-win-the-ai-arms-race/',
                                      'source_name': 'Sen. Barrasso floor speech',
                                      'kind': 'statement'},
                                     {'what': 'On a proposal to site data centers on '
                                              'public lands, told Cowboy State Daily: '
                                              "'Development of federal land, including "
                                              'the construction of new data centers, '
                                              'deserves meaningful input from state '
                                              'and local governments and the public. '
                                              'The people of Wyoming expect to have '
                                              "their voices heard.'",
                                      'date': '2026-08-24',
                                      'source': 'https://cowboystatedaily.com/2026/08/23/a-data-center-is-proposed-for-public-lands-in-nevada-could-wyoming-be-next/',
                                      'source_name': 'Cowboy State Daily',
                                      'kind': 'statement'}],
                           'as_of': '2026-09-05'},
 ('WY', 'Cynthia M. Lummis'): {'lean': 'accelerate',
                               'summary': 'Introduced the POWER Up Act giving FERC '
                                          'jurisdiction over interconnection of 100 '
                                          'MW-plus loads such as data centers to the '
                                          'interstate grid while preserving state '
                                          'authority over siting and retail rates, and '
                                          'wrote that Wyoming baseload energy should '
                                          "power America's AI.",
                               'items': [{'what': 'Introduced the POWER Up Act, which '
                                                  'amends the Federal Power Act to '
                                                  'clarify FERC jurisdiction over the '
                                                  'interconnection of large-load '
                                                  'facilities (projected peak demand '
                                                  'of 100 MW or more) to interstate '
                                                  'transmission, requires FERC to '
                                                  'issue standardized interconnection '
                                                  'procedures within 18 months, and '
                                                  'explicitly preserves state and '
                                                  'local jurisdiction over siting, '
                                                  'permitting, construction, retail '
                                                  'rates, local distribution and '
                                                  "generation. Lummis: 'When a "
                                                  'facility wants to draw as much '
                                                  'power as a city, that is not an '
                                                  'ordinary retail question. It is a '
                                                  "grid question.'",
                                          'date': '2026-06-17',
                                          'source': 'https://www.lummis.senate.gov/press-releases/lummis-introduces-legislation-to-modernize-rules-for-high-power-grid-connections/',
                                          'source_name': 'Sen. Lummis press release',
                                          'kind': 'action'},
                                         {'what': 'Op-ed in Cowboy State Daily arguing '
                                                  'Wyoming baseload energy should '
                                                  "power U.S. AI data centers ('If we "
                                                  "don't power America's AI with "
                                                  'Wyoming energy, China will build '
                                                  'their AI dominance on their coal '
                                                  "instead'), citing 100 MW-plus AI "
                                                  'training clusters; it does not '
                                                  'address ratepayer or community '
                                                  'impacts.',
                                          'date': '2025-09-23',
                                          'source': 'https://www.lummis.senate.gov/press-releases/icymi-op-ed-from-senator-lummis-in-csd-wyoming-baseload-energy-is-trumps-secret-weapon-in-ai-war-against-china/',
                                          'source_name': 'Sen. Lummis press release '
                                                         '(op-ed reprint)',
                                          'kind': 'statement'}],
                               'as_of': '2026-09-05'}}
