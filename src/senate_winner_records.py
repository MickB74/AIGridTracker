"""
Documented records of the 35 people who won a U.S. Senate seat in 2026.

Generated — do not hand-append. Each winner was researched after the
election (own releases, congress.gov, state legislative records, the
reputable press) and merged with what the site already held: the sitting
senators' entries that used to live in src/senator_records.py and the
winners' campaign entries in src/senate_races.py. Every item kept was
opened at its source URL and confirmed to name the winner doing or saying
the thing; an item whose page could not be opened was left out rather than
published on a search snippet. `kind` separates an *action* (bill, vote,
veto, formal letter, hearing question, lawsuit) from a *statement* (quote,
op-ed, campaign plank). `lean` summarises only the cited items.

Re-running research means re-curating, not appending: the curation pass
dedupes on source URL and drops existing items that failed a re-read.

Items dropped in curation, so nobody re-adds them:
* Gov. Cooper's 2023 veto of SB 678 (utility profits; the page never mentions data centers).
* Sen. Ossoff's FERC letter as carried by CBS News Atlanta (same act as the WRDW item; the stored version cited details not on the CBS page).
* Sen. Risch's ARC Act release and endorsement round-up (the data-center language is the U.S. Chamber's, not his).
* Lt. Gov. Stratton's quote in the Illinois AI Cabinet announcement (her quote does not mention data centers); also do NOT attribute a moratorium platform to her - the New Republic sentence is about Keisha Lance Bottoms.
* Rep. Letlow's Winter Storm Fern grid letter and Adam Hamilton's transmission-bidding plank (ratepayer items, not data centers).
* Josh Turek's Newsweek line about embracing 'the populist mood driving local moratoriums' (Newsweek's characterisation; he opposed a moratorium in both debates).
* Any item whose page could not be opened (e.g. Turek's WHO 13 quote, behind a bot wall).
* Sen. Warner's 'idiocy' remark as carried by E&E News (dated by article, not by remark; the WJLA item dates it to the 2026-03-25 Axios summit).
* Second sources for an act or statement already cited (WUKY on Barr's Paducah remarks, WABE on Ossoff's debate answer, WV Public and MetroNews on Capito's media calls).
* Sherrod Brown's 2015 Amazon release as quoted by Fox News (original release not located; his own 2026 account of backing a data center in 2015-16 is in the News 5 item).
* False leads: a '12-month moratorium' line attributed to Brown, a Paducah 'will lower energy prices' pledge attributed to Barr, and Sen. Warnock's moratorium call attributed to Ossoff.
"""

WINNER_RECORDS = {('AK', 'Mary Peltola'): {'lean': 'guardrails',
                          'summary': 'Peltola has no legislative record on data '
                                     'centers; what exists is campaign-trail '
                                     'statements. In September 2026 she said she takes '
                                     'her cue from the people of the region where a '
                                     'project is proposed and would not stop one a '
                                     'region supports, but called it a concern if a '
                                     'huge new project would make energy harder for '
                                     'households already on the grid. Newsweek, after '
                                     'the election, paraphrased her campaign position '
                                     'as local communities having a voice and data '
                                     'centers paying their own way.',
                          'background': "U.S. Representative for Alaska's at-large "
                                        'district, 2022-2025. No data-center item was '
                                        'found from her House tenure.',
                          'items': [{'what': 'Asked about data centers in Alaska after '
                                             'the Fairbanks Labor Day parade, Peltola '
                                             'said she takes her cue from the people '
                                             'of the region where a development is '
                                             'proposed and that if the region supports '
                                             'it, "who am I to stop it?" She added '
                                             'that broad concern about having enough '
                                             'electricity for ratepayers already on '
                                             'the grid, and about a huge new project '
                                             'making energy more challenging for '
                                             'households, "is a concern."',
                                     'date': '2026-09-07',
                                     'source': 'https://www.alaskasnewssource.com/2026/09/08/mary-peltola-attends-fairbanks-labor-day-parade/',
                                     'source_name': "Alaska's News Source (KTUU/KTVF)",
                                     'kind': 'statement'},
                                    {'what': "Newsweek reported (reporter's "
                                             'paraphrase, linked to a Facebook video, '
                                             'not a direct quote) that Peltola during '
                                             'the campaign emphasized that local '
                                             'communities should have a voice in the '
                                             'data-center discussion and that data '
                                             'centers should pay their own way. '
                                             'Newsweek said it had contacted her '
                                             'campaign; no response is reported.',
                                     'date': '',
                                     'source': 'https://www.newsweek.com/alaska-could-become-more-unwelcoming-data-centers-12741506',
                                     'source_name': 'Newsweek',
                                     'kind': 'statement'}],
                          'as_of': '2026-11-28'},
 ('AL', 'Barry Moore'): {'lean': 'consensus',
                         'summary': "The only thing located on Moore's record is his "
                                    'Yea vote on the Ratepayer Protection Act (H.R. '
                                    '9340), which passed the House 417-3 on September '
                                    "16, 2026. He is not among the bill's cosponsors. "
                                    'No statement by Moore on data centers was found '
                                    'in Alabama press or on his House site.',
                         'background': 'U.S. Representative from Alabama since 2021.',
                         'items': [{'what': 'Voted Yea on H.R. 9340, the Ratepayer '
                                            'Protection Act, on the motion to suspend '
                                            'the rules and pass as amended (House Roll '
                                            'Call 312; 417 yeas, 3 nays).',
                                    'date': '2026-09-16',
                                    'source': 'https://clerk.house.gov/Votes/2026312',
                                    'source_name': 'Clerk of the U.S. House, Roll Call '
                                                   '312',
                                    'kind': 'action'}],
                         'as_of': '2026-11-28'},
 ('AR', 'Tom Cotton'): {'lean': 'mixed',
                        'summary': 'Cotton introduced the DATA Act of 2026 to let data '
                                   'centers and other energy-intensive industries '
                                   'build fully off-grid power systems exempt from '
                                   'certain federal regulation, saying AI dominance '
                                   "should not come at the expense of Arkansans' "
                                   'energy costs. He cosponsored the Senate Ratepayer '
                                   'Protection Act and voted to advance the '
                                   'House-passed version, which failed 57-43. He also '
                                   'asked DOJ to investigate alleged Chinese-backed '
                                   'funding of opposition to data centers, while '
                                   "calling residents' cost and resource concerns "
                                   'valid, and has said local residents should be able '
                                   'to choose whether a data center is built near '
                                   'them.',
                        'background': 'U.S. Senator from Arkansas since 2015.',
                        'items': [{'what': 'Voted Yea on Senate passage of H.R. 2347 '
                                           'as amended, the Bipartisan American '
                                           'Affordability and Jobs Act of 2026 (Senate '
                                           'vote 270, passed 62-33) - a permitting '
                                           'bill whose supporters say it requires data '
                                           'centers to pay for the grid costs they '
                                           'create. No statement from Cotton about '
                                           'this vote was found.',
                                   'date': '2026-11-19',
                                   'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00270.xml',
                                   'source_name': 'U.S. Senate roll call vote 270 '
                                                  '(119th Congress, 2nd session)',
                                   'kind': 'action'},
                                  {'what': 'Voted Yea on cloture on the motion to '
                                           'proceed to H.R. 9340, the House-passed '
                                           'Ratepayer Protection Act (Senate vote '
                                           '254). The motion was rejected 57-43, short '
                                           'of the 60 required.',
                                   'date': '2026-09-30',
                                   'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.xml',
                                   'source_name': 'U.S. Senate roll call vote 254 '
                                                  '(119th Congress, 2nd session)',
                                   'kind': 'action'},
                                  {'what': 'Cosponsored S. 5028, the Ratepayer '
                                           'Protection Act (sponsor: Sen. Jon Husted). '
                                           'Cotton is listed as a cosponsor as of '
                                           'September 22, 2026; he was not an original '
                                           'cosponsor.',
                                   'date': '2026-09-22',
                                   'source': 'https://www.congress.gov/bill/119th-congress/senate-bill/5028/cosponsors',
                                   'source_name': 'Congress.gov, S. 5028 cosponsors',
                                   'kind': 'action'},
                                  {'what': 'Wrote Acting Attorney General Todd Blanche '
                                           'asking DOJ to investigate foreign '
                                           'influence efforts, including by the '
                                           'Chinese Communist Party, targeting the '
                                           'buildout of U.S. AI infrastructure and '
                                           'public opinion on data centers. The same '
                                           'letter says Americans have valid concerns '
                                           'about energy costs and natural-resource '
                                           "strain from data centers and that 'common "
                                           "sense regulations and legislation' should "
                                           'protect communities.',
                                   'date': '2026-06-10',
                                   'source': 'https://www.cotton.senate.gov/news/press-releases/cotton-to-doj-investigate-communist-china-influence-on-data-center-development',
                                   'source_name': 'Sen. Cotton press release',
                                   'kind': 'action'},
                                  {'what': 'Told KATV that data centers drawing on '
                                           "existing grid generation would cause 'a "
                                           "price spike', and described the DATA Act "
                                           'as balancing affordable electricity for '
                                           'Arkansas families with encouraging '
                                           'data-center investment in the state.',
                                   'date': '2026-01-15',
                                   'source': 'https://katv.com/news/local/cotton-introduces-bill-to-shield-arkansans-from-data-center-driven-electric-rate-hi-artificial-intelligence-ai-entergy-senator-tom-cotton-trump-electric-bill-power-plant-google-avaio-little-rock-meta-aws-public-service-commission-danni-hoefer-data-act',
                                   'source_name': 'KATV (ABC Little Rock)',
                                   'kind': 'statement'},
                                  {'what': 'Introduced the DATA Act of 2026 '
                                           '(introduced January 7; release dated '
                                           'January 8). Per his release it would '
                                           'exempt new, physically isolated off-grid '
                                           'electricity providers and certain '
                                           'consumer-regulated utilities from federal '
                                           'regulations, letting manufacturers, data '
                                           'centers and other energy-intensive '
                                           'industries build their own electricity '
                                           'systems, with eligibility limited to '
                                           'systems fully isolated from the bulk power '
                                           'grid.',
                                   'date': '2026-01-07',
                                   'source': 'https://www.cotton.senate.gov/news/press-releases/cotton-introduces-bill-to-lower-energy-costs-for-arkansans',
                                   'source_name': 'Sen. Cotton press release',
                                   'kind': 'action'},
                                  {'what': 'Arkansas Advocate reported that Cotton, '
                                           'like his two challengers, said in an '
                                           'interview that he supports giving '
                                           'Arkansans a vote on whether a data center '
                                           'is built near them, and that AI companies '
                                           "should be transparent about data centers' "
                                           'impacts on communities. This is the '
                                           "reporter's paraphrase of a September "
                                           'interview with 40/29 News; Cotton did not '
                                           "answer the Advocate's own questions.",
                                   'date': '',
                                   'source': 'https://www.newsfromthestates.com/article/issue-spotlight-what-candidates-arkansas-us-senate-race-say-about-ai-data-centers',
                                   'source_name': 'Arkansas Advocate (via News From '
                                                  'The States)',
                                   'kind': 'statement'}],
                        'as_of': '2026-11-28'},
 ('CO', 'John Hickenlooper'): {'lean': 'guardrails',
                               'summary': "Hickenlooper's record is from autumn 2026. "
                                          'He voted against advancing the House-passed '
                                          'Ratepayer Protection Act, saying it only '
                                          'asks states to consider ratepayer '
                                          'protections rather than requiring them, and '
                                          'said "If Big Tech wants a data center, Big '
                                          'Tech should pay for it." He then voted to '
                                          'advance and to pass the Bipartisan American '
                                          'Affordability and Jobs Act, a permitting '
                                          'bill he said would "make data centers pay '
                                          'their fair share," and has listed data '
                                          'centers paying their own way for energy '
                                          'among the AI policies he asks of the White '
                                          'House and Congress.',
                               'background': 'U.S. Senator from Colorado since 2021; '
                                             'former governor.',
                               'items': [{'what': 'Voted to pass the Bipartisan '
                                                  'American Affordability and Jobs Act '
                                                  '(H.R. 2347 as amended; Senate vote '
                                                  '270, passed 62-33). His release '
                                                  'says that, according to independent '
                                                  'analysis, the bill would require '
                                                  'data centers to pay for the '
                                                  'increased grid and energy costs '
                                                  'they create.',
                                          'date': '2026-11-19',
                                          'source': 'https://www.hickenlooper.senate.gov/press_releases/hickenlooper-welcomes-senate-passage-of-much-needed-permitting-reform-bill/',
                                          'source_name': 'Sen. Hickenlooper press '
                                                         'release',
                                          'kind': 'action'},
                                         {'what': 'Wrote to Sen. Schumer and Sen. Van '
                                                  'Hollen, candidates for Senate '
                                                  'Democratic leader, pressing for an '
                                                  'agenda on AI safety, affordability '
                                                  'and accountability; the letter '
                                                  "cites families' rising energy bills "
                                                  "and farmers' concern about data "
                                                  'centers draining limited water. The '
                                                  "letter's asks are about AI "
                                                  'regulation generally, not a '
                                                  'specific data-center measure.',
                                          'date': '2026-11-19',
                                          'source': 'https://www.hickenlooper.senate.gov/press_releases/hickenlooper-presses-senate-leadership-candidates-to-outline-ai-safety-affordability-and-accountability-agenda/',
                                          'source_name': 'Sen. Hickenlooper press '
                                                         'release',
                                          'kind': 'action'},
                                         {'what': 'Voted to advance the Bipartisan '
                                                  'American Affordability and Jobs Act '
                                                  '(a permitting bill) and said the '
                                                  'deal would make data centers pay '
                                                  'their fair share, while saying the '
                                                  'bill should be strengthened with '
                                                  'Tribal Nations and environmental '
                                                  'groups. Senate vote 257 (cloture on '
                                                  'the motion to proceed to H.R. 2347, '
                                                  '73-25) records him as Yea.',
                                          'date': '2026-11-09',
                                          'source': 'https://www.hickenlooper.senate.gov/press_releases/hickenlooper-votes-to-advance-long-overdue-permitting-reform-bill/',
                                          'source_name': 'Sen. Hickenlooper press '
                                                         'release',
                                          'kind': 'action'},
                                         {'what': 'At a Denver discussion with '
                                                  'residents and energy-assistance '
                                                  'leaders, where residents raised '
                                                  'concerns about footing the bill for '
                                                  'data centers, his office said he '
                                                  'spoke about the need to shield '
                                                  'ratepayers from paying for Big '
                                                  "Tech's data center infrastructure "
                                                  '(office summary, no direct quote).',
                                          'date': '2026-10-06',
                                          'source': 'https://www.hickenlooper.senate.gov/press_releases/icymi-hickenlooper-meets-with-coloradans-talks-food-energy-affordability/',
                                          'source_name': 'Sen. Hickenlooper press '
                                                         'release',
                                          'kind': 'statement'},
                                         {'what': 'Voted Nay on cloture on the motion '
                                                  'to proceed to H.R. 9340, the '
                                                  'House-passed Ratepayer Protection '
                                                  'Act (Senate vote 254); the motion '
                                                  'was rejected 57-43.',
                                          'date': '2026-09-30',
                                          'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.xml',
                                          'source_name': 'U.S. Senate roll call vote '
                                                         '254 (119th Congress, 2nd '
                                                         'session)',
                                          'kind': 'action'},
                                         {'what': 'Explained his opposition to the '
                                                  'Ratepayer Protection Act: he said '
                                                  'it asks states to consider '
                                                  'protections for ratepayers but does '
                                                  'not require them, and his office '
                                                  'said Senate Democrats had pushed a '
                                                  'provision that would have required '
                                                  'the largest new power users to pay '
                                                  'their fair share to connect.',
                                          'date': '2026-09-30',
                                          'source': 'https://www.hickenlooper.senate.gov/press_releases/hickenlooper-statement-on-republicans-sham-effort-to-shield-americans-from-data-centers-driving-up-energy-costs/',
                                          'source_name': 'Sen. Hickenlooper press '
                                                         'release',
                                          'kind': 'statement'},
                                         {'what': 'Sent a letter to President Trump '
                                                  'ahead of a White House meeting with '
                                                  'technology executives; his office '
                                                  'lists among the things he called on '
                                                  'Trump and technology leaders to '
                                                  'work with Congress on: protecting '
                                                  'communities from the costs of the '
                                                  'AI buildout, including ensuring '
                                                  'massive data centers pay their own '
                                                  'way for their energy consumption.',
                                          'date': '2026-09-29',
                                          'source': 'https://www.hickenlooper.senate.gov/press_releases/hickenlooper-calls-on-trump-ai-ceos-to-work-with-congress-on-responsible-ai-guardrails-ahead-of-white-house-meeting/',
                                          'source_name': 'Sen. Hickenlooper press '
                                                         'release',
                                          'kind': 'action'},
                                         {'what': 'His office said that in a video he '
                                                  'stressed community involvement, '
                                                  'protecting water resources and '
                                                  'ensuring ratepayers are not '
                                                  'subsidizing data centers, and that '
                                                  'he spoke on the Senate floor the '
                                                  "previous day about Coloradans' "
                                                  'anxiety over AI and data centers, '
                                                  'including spiking energy bills and '
                                                  'farm water shortages. (The '
                                                  'data-center sentence is his '
                                                  "office's summary of the video, not "
                                                  'a direct quote.)',
                                          'date': '2026-09-17',
                                          'source': 'https://www.hickenlooper.senate.gov/press_releases/hickenlooper-calls-for-congressional-action-hearings-on-ai-regulation/',
                                          'source_name': 'Sen. Hickenlooper press '
                                                         'release',
                                          'kind': 'statement'}],
                               'as_of': '2026-11-28'},
 ('DE', 'Chris Coons'): {'lean': 'mixed',
                         'summary': 'Coons introduced the Liquid Cooling for AI Act in '
                                    'November 2025 to have GAO and DOE assess liquid '
                                    'cooling for data centers, saying AI leadership '
                                    '"shouldn\'t have to mean skyrocketing energy '
                                    'bills for American families." In September 2026 '
                                    'he voted against advancing the House-passed '
                                    'Ratepayer Protection Act; no statement from him '
                                    'explaining that vote was found. In November 2026 '
                                    'he voted for the Bipartisan American '
                                    'Affordability and Jobs Act, a permitting bill he '
                                    'said ensures data centers pay their fair share '
                                    'and pay for upgrades to electricity systems.',
                         'background': 'U.S. Senator from Delaware since 2010.',
                         'items': [{'what': 'Voted for Senate passage of the '
                                            'Bipartisan American Affordability and '
                                            'Jobs Act of 2026 (H.R. 2347 as amended; '
                                            'Senate vote 270, 62-33) and said it would '
                                            'ensure data centers pay more than their '
                                            'fair share in the communities they '
                                            'impact. He said he had fought '
                                            'unsuccessfully for amendments to the '
                                            "bill's environmental and "
                                            'historic-preservation provisions.',
                                    'date': '2026-11-19',
                                    'source': 'https://www.coons.senate.gov/news/press-releases/senator-coons-statement-on-final-passage-of-permitting-reform-bill/',
                                    'source_name': 'Sen. Coons press release',
                                    'kind': 'action'},
                                   {'what': 'Announced he would support the Bipartisan '
                                            'American Affordability and Jobs Act of '
                                            '2026, a permitting bill, saying it '
                                            'ensures data centers pay their fair share '
                                            'and pay for upgrades to electricity '
                                            'systems; said he expected an amendment '
                                            'process to improve it. Senate vote 257 '
                                            'the same day (cloture on the motion to '
                                            'proceed to H.R. 2347, 73-25) records him '
                                            'as Yea.',
                                    'date': '2026-11-09',
                                    'source': 'https://www.coons.senate.gov/news/press-releases/senator-coons-statement-on-permitting-reform-bill/',
                                    'source_name': 'Sen. Coons press release',
                                    'kind': 'statement'},
                                   {'what': 'Voted Nay on cloture on the motion to '
                                            'proceed to H.R. 9340, the House-passed '
                                            'Ratepayer Protection Act (Senate vote '
                                            '254); the motion was rejected 57-43.',
                                    'date': '2026-09-30',
                                    'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.xml',
                                    'source_name': 'U.S. Senate roll call vote 254 '
                                                   '(119th Congress, 2nd session)',
                                    'kind': 'action'},
                                   {'what': 'Introduced the Liquid Cooling for AI Act '
                                            'with Sen. Dave McCormick: GAO to assess '
                                            'R&D needs for liquid cooling in data '
                                            'centers, DOE to evaluate the findings and '
                                            'report recommendations to Congress, and a '
                                            'liquid cooling advisory organization of '
                                            'industry experts. The release cites a '
                                            'Lawrence Berkeley National Laboratory '
                                            'report that data centers used 4.4% of '
                                            'U.S. electricity in 2023 and could reach '
                                            '12.8% by 2028.',
                                    'date': '2025-11-20',
                                    'source': 'https://www.coons.senate.gov/news/press-releases/senators-coons-mccormick-introduce-bill-to-boost-us-ai-leadership-with-energy-efficient-liquid-cooling-technology',
                                    'source_name': 'Sen. Coons press release',
                                    'kind': 'action'}],
                         'as_of': '2026-11-28'},
 ('FL', 'Ashley Moody'): {'lean': 'guardrails',
                          'summary': 'Moody cosponsored the Senate Ratepayer '
                                     'Protection Act in September 2026, voted to '
                                     'advance the House-passed version, and criticized '
                                     'Senate Democrats for blocking it, saying '
                                     'Floridians "should not be left to foot the bill" '
                                     'for data centers. In an August 2026 Fox News '
                                     'interview she said whether to host data centers '
                                     'should be up to the people of a community or '
                                     'state. In November 2026 she voted for the '
                                     'Bipartisan American Affordability and Jobs Act, '
                                     'a permitting bill; no statement from her on that '
                                     'vote was found.',
                          'background': 'Florida Attorney General 2019-2025; appointed '
                                        'to the U.S. Senate in January 2025. No '
                                        'data-center item was found from her time as '
                                        'attorney general.',
                          'items': [{'what': 'Voted Yea on Senate passage of H.R. 2347 '
                                             'as amended, the Bipartisan American '
                                             'Affordability and Jobs Act of 2026 '
                                             '(Senate vote 270, passed 62-33) - a '
                                             'permitting bill whose supporters say it '
                                             'requires data centers to pay for the '
                                             'grid costs they create. No statement '
                                             'from Moody about this vote was found.',
                                     'date': '2026-11-19',
                                     'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00270.xml',
                                     'source_name': 'U.S. Senate roll call vote 270 '
                                                    '(119th Congress, 2nd session)',
                                     'kind': 'action'},
                                    {'what': 'Voted Yea on cloture on the motion to '
                                             'proceed to H.R. 9340, the House-passed '
                                             'Ratepayer Protection Act (Senate vote '
                                             '254); the motion was rejected 57-43.',
                                     'date': '2026-09-30',
                                     'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.xml',
                                     'source_name': 'U.S. Senate roll call vote 254 '
                                                    '(119th Congress, 2nd session)',
                                     'kind': 'action'},
                                    {'what': 'After the cloture vote failed, issued a '
                                             'statement faulting Senate Democrats for '
                                             'blocking the Ratepayer Protection Act '
                                             '(and a separate congressional '
                                             'stock-trading bill).',
                                     'date': '2026-09-30',
                                     'source': 'https://www.moody.senate.gov/press-releases/senator-moody-democrats-are-the-party-of-no-continue-to-block-legislation-to-protect-ratepayers-and-ban-stock-trading-in-congress/',
                                     'source_name': 'Sen. Moody press release',
                                     'kind': 'statement'},
                                    {'what': 'Announced her cosponsorship of the '
                                             'Ratepayer Protection Act and criticized '
                                             'Senate Democrats for blocking it. Her '
                                             'release describes the bill as requiring '
                                             'state utility regulators and unregulated '
                                             'utilities to consider adopting '
                                             'large-load standards for recovery of the '
                                             'full incremental cost of upgrades, '
                                             'financial assurances before grid '
                                             'upgrades, and cost recovery if a large '
                                             'load exits its contract early. The '
                                             'release also says she backs local '
                                             'communities having the ultimate say over '
                                             'where data centers go.',
                                     'date': '2026-09-25',
                                     'source': 'https://www.moody.senate.gov/press-releases/senator-moody-cosponsors-legislation-to-protect-ratepayers-from-energy-consuming-data-centers/',
                                     'source_name': 'Sen. Moody press release',
                                     'kind': 'statement'},
                                    {'what': 'Cosponsored S. 5028, the Ratepayer '
                                             'Protection Act (sponsor: Sen. Jon '
                                             'Husted). Congress.gov lists her as a '
                                             'cosponsor as of September 17, 2026 (not '
                                             'an original cosponsor).',
                                     'date': '2026-09-17',
                                     'source': 'https://www.congress.gov/bill/119th-congress/senate-bill/5028/cosponsors',
                                     'source_name': 'Congress.gov, S. 5028 cosponsors',
                                     'kind': 'action'},
                                    {'what': "Said on Fox News' 'Sunday Morning "
                                             "Futures' that it should be up to the "
                                             'people of a community or a state to '
                                             'decide whether to host data centers, and '
                                             'that companies need to make their case, '
                                             'including that residents will not bear '
                                             'costs or environmental and health '
                                             'effects. Florida Politics summarised '
                                             'this as cities and counties deciding.',
                                     'date': '',
                                     'source': 'https://floridapolitics.com/archives/817705-ashley-moody-backs-local-control-on-data-center-question/',
                                     'source_name': 'Florida Politics',
                                     'kind': 'statement'}],
                          'as_of': '2026-11-28'},
 ('GA', 'Jon Ossoff'): {'lean': 'guardrails',
                        'summary': 'In April 2026 Ossoff wrote to FERC Chair Laura '
                                   'Swett opening an inquiry into whether AI data '
                                   "centers are raising Georgians' power bills. In "
                                   'September 2026 he was one of four Democrats who '
                                   'voted to advance the House-passed Ratepayer '
                                   'Protection Act, and in an October debate he said '
                                   'no Georgia family should "pay a dime more" to '
                                   'subsidize data centers and that no community '
                                   'should have one imposed on it. In November 2026 he '
                                   'voted against final passage of the Senate '
                                   'permitting bill; no statement from him explaining '
                                   'either vote was found.',
                        'background': 'U.S. Senator from Georgia since 2021.',
                        'items': [{'what': 'Voted Nay on Senate passage of H.R. 2347 '
                                           'as amended, the Bipartisan American '
                                           'Affordability and Jobs Act of 2026 (Senate '
                                           'vote 270, passed 62-33) - a permitting '
                                           'bill whose supporters say it requires data '
                                           'centers to pay for the grid costs they '
                                           'create and whose critics say it weakens '
                                           'environmental and historic-preservation '
                                           'review. He had voted Yea on the earlier '
                                           'procedural votes and on the substitute '
                                           'amendment. No statement from Ossoff '
                                           'explaining the vote was found.',
                                   'date': '2026-11-19',
                                   'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00270.xml',
                                   'source_name': 'U.S. Senate roll call vote 270 '
                                                  '(119th Congress, 2nd session)',
                                   'kind': 'action'},
                                  {'what': 'In the first Senate debate with Rep. Mike '
                                           'Collins (Atlanta News First / Gray Media, '
                                           'Thursday Oct. 8, 2026), asked how he would '
                                           'keep data-center strain on the grid from '
                                           'raising utility bills, said no Georgia '
                                           'family or small business should pay more '
                                           "to subsidize data centers' energy "
                                           'consumption and that no local community '
                                           'should have data centers imposed on it. He '
                                           'then said the 2025 budget bill gave $70 '
                                           'billion to data center developers (his '
                                           'figure) and challenged Collins to commit '
                                           "to repealing what he called 'that data "
                                           "center tax scam'.",
                                   'date': '2026-10-08',
                                   'source': 'https://www.atlantanewsfirst.com/2026/10/09/read-full-transcript-us-senate-debate-between-jon-ossoff-mike-collins/',
                                   'source_name': 'Atlanta News First (full debate '
                                                  'transcript)',
                                   'kind': 'statement'},
                                  {'what': 'Voted Yea on cloture on the motion to '
                                           'proceed to H.R. 9340, the House-passed '
                                           'Ratepayer Protection Act (Senate vote '
                                           '254); the motion was rejected 57-43. Roll '
                                           'Call reported he was one of four Democrats '
                                           'to support it.',
                                   'date': '2026-09-30',
                                   'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.xml',
                                   'source_name': 'U.S. Senate roll call vote 254 '
                                                  '(119th Congress, 2nd session)',
                                   'kind': 'action'},
                                  {'what': 'Wrote to FERC Chair Laura Swett announcing '
                                           "an investigation into AI data centers' "
                                           "potential impact on Georgians' power "
                                           'bills, asking for answers by June 1 to '
                                           'questions including whether FERC considers '
                                           'it credible and/or enforceable when '
                                           'technology companies say they will "pay '
                                           'their own way", what FERC is doing to '
                                           'improve load forecasting, how it will deal '
                                           'with load growth that exceeds predictions, '
                                           'and how it will take part in standardising '
                                           'interconnection for large loads like data '
                                           'centers.',
                                   'date': '2026-04-20',
                                   'source': 'https://www.wrdw.com/2026/04/20/ossoff-looks-into-ga-data-centers-impact-power-bills/',
                                   'source_name': 'WRDW (Augusta)',
                                   'kind': 'action'}],
                        'as_of': '2026-11-28'},
 ('IA', 'Josh Turek'): {'lean': 'guardrails',
                        'summary': 'In the two general-election debates Turek said '
                                   'data centers should not drive up utility costs, '
                                   'called for more federal regulation including '
                                   'closed-loop cooling to cut water use, and agreed '
                                   'data centers should not get tax breaks. He also '
                                   'said siting decisions belong to local officials '
                                   'and opposed a federal moratorium on data center '
                                   'construction. No bill, vote or written platform '
                                   'plank on data centers was found.',
                        'background': 'Iowa state representative from Council Bluffs. '
                                      'No Iowa House floor vote of his on a '
                                      'data-center bill was located.',
                        'items': [{'what': 'At the second and final debate (WHO-TV), '
                                           'Radio Iowa reported that both Hinson and '
                                           'Turek said local officials should decide '
                                           'where data centers may be built, and that '
                                           'both oppose a federal moratorium on data '
                                           "center construction. Reporter's "
                                           'paraphrase.',
                                   'date': '2026-10-13',
                                   'source': 'https://www.radioiowa.com/2026/10/14/two-u-s-senate-candidates-in-final-debate-before-iowas-nov-election/',
                                   'source_name': 'Radio Iowa',
                                   'kind': 'statement'},
                                  {'what': "WOI's report on the second debate says "
                                           'Hinson was more open to data center '
                                           'development agreements than Turek, and '
                                           'that both opposed a statewide moratorium '
                                           "on data centers. Reporter's "
                                           'characterisation; no Turek quote.',
                                   'date': '2026-10-13',
                                   'source': 'https://www.yahoo.com/news/politics/articles/ashley-hinson-josh-turek-face-044855332.html',
                                   'source_name': 'WOI Local 5 (via Yahoo News)',
                                   'kind': 'statement'},
                                  {'what': 'At the Iowa PBS debate, KCCI reported that '
                                           'both candidates said data centers should '
                                           'not drive up utility costs, and that Turek '
                                           'called for more federal regulation, '
                                           'including requiring data centers to use '
                                           'closed-loop cooling systems to reduce '
                                           "water use. This is the reporter's "
                                           'paraphrase, not a direct quote.',
                                   'date': '2026-10-07',
                                   'source': 'https://www.kcci.com/article/ashley-hinson-josh-turek-senate-debate-iowa/74072305',
                                   'source_name': 'KCCI',
                                   'kind': 'statement'},
                                  {'what': "Gray Media's report on the same Iowa PBS "
                                           'debate says the two candidates agreed that '
                                           'data centers should not get tax breaks. '
                                           'The article attributes this to both '
                                           'candidates jointly and gives no direct '
                                           'quote from Turek.',
                                   'date': '2026-10-07',
                                   'source': 'https://www.kttc.com/2026/10/08/where-us-senate-candidates-agreed-disagreed-1st-debate/',
                                   'source_name': 'KTTC (Gray Media Iowa State Capitol '
                                                  'Bureau)',
                                   'kind': 'statement'}],
                        'as_of': '2026-11-28'},
 ('ID', 'Jim Risch'): {'lean': 'mixed',
                       'summary': 'Risch voted on 2026-09-30 to advance the '
                                  'House-passed Ratepayer Protection Act (cloture '
                                  'failed 57-43) and voted for the Senate permitting '
                                  "bill in November 2026. He welcomed Meta's Kuna data "
                                  'center in 2022 as a source of jobs, and said at a '
                                  '2025 Senate hearing that he expects the country to '
                                  'be "inundated with demand for electricity" from AI. '
                                  'No statement from him was found on Idaho ratepayer '
                                  'costs or large-load tariffs.',
                       'background': 'U.S. Senator from Idaho since 2009; former '
                                     'governor.',
                       'items': [{'what': 'Voted Yea on Senate passage of H.R. 2347 as '
                                          'amended (Senate vote 270, passed 62-33), '
                                          'the vehicle for the Bipartisan American '
                                          'Affordability and Jobs Act, a permitting '
                                          'bill whose sponsors say it makes data '
                                          'centers pay for the grid upgrades they '
                                          'cause.',
                                  'date': '2026-11-19',
                                  'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00270.htm',
                                  'source_name': 'U.S. Senate roll call',
                                  'kind': 'action'},
                                 {'what': 'Voted Yea on the motion to invoke cloture '
                                          'on the motion to proceed to H.R. 9340 (the '
                                          'House-passed Ratepayer Protection Act, on '
                                          'recovering the full incremental cost of '
                                          'upgrades that serve large-load customers). '
                                          'The motion was rejected 57-43, with 60 '
                                          'needed.',
                                  'date': '2026-09-30',
                                  'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.htm',
                                  'source_name': 'U.S. Senate roll call vote 254, '
                                                 '119th Congress 2nd Session',
                                  'kind': 'action'},
                                 {'what': 'At a Senate Energy and Natural Resources '
                                          'Committee hearing, said he had doubted '
                                          'forecasts of AI-driven electricity demand '
                                          'but now expects the country to be '
                                          "'inundated with demand for electricity', "
                                          'and pointed to nuclear generation as the '
                                          'answer. The release does not mention data '
                                          'centers by name.',
                                  'date': '2025-07-23',
                                  'source': 'https://www.risch.senate.gov/?p=9623',
                                  'source_name': 'Sen. Risch press release',
                                  'kind': 'statement'},
                                 {'what': 'Statement in the Idaho Commerce '
                                          "announcement of Meta's Kuna data center "
                                          'welcoming it as a source of jobs.',
                                  'date': '2022-02-16',
                                  'source': 'https://commerce.idaho.gov/press/meta-announces-kuna-as-location-of-new-data-center/',
                                  'source_name': 'Idaho Department of Commerce press '
                                                 'release',
                                  'kind': 'statement'}],
                       'as_of': '2026-11-28'},
 ('IL', 'Juliana Stratton'): {'lean': 'guardrails',
                              'summary': 'In an October 2026 public-radio interview '
                                         "Stratton said data centers 'have to pay "
                                         "their fair share', that Illinoisans must not "
                                         "'shoulder the burden for the expansion', and "
                                         'that communities need transparency and a '
                                         "voice; she described Illinois's pause on "
                                         "data-center tax incentives as something 'we' "
                                         'did to slow things down. At a January 2026 '
                                         'primary debate she answered a data-center '
                                         'question by calling for more generation on '
                                         'the grid. No vote, bill or formal action on '
                                         'data centers was found.',
                              'background': 'Illinois lieutenant governor since 2019; '
                                            'state representative 2017-2019. The '
                                            'lieutenant governor does not vote on '
                                            'legislation, so the record is statements '
                                            'only.',
                              'items': [{'what': "Asked on Illinois Public Media's The "
                                                 '21st Show about a federal role in '
                                                 'regulating data-center growth, said '
                                                 "data centers 'have to pay their fair "
                                                 "share', must invest in the electric "
                                                 'grid, that Illinoisans cannot be '
                                                 'made to shoulder the burden of the '
                                                 'expansion, and that the state put a '
                                                 'pause on tax incentives to slow '
                                                 'things down. She said that at the '
                                                 "federal level 'we need to again look "
                                                 "at what the implications are' and "
                                                 'named no federal bill.',
                                         'date': '2026-10-13',
                                         'source': 'https://will.illinois.edu/21stshow/story/lt-gov-juliana-stratton-on-iran-war-ice-accountability-and-her-campaign-for-u.s-senate',
                                         'source_name': 'Illinois Public Media, The '
                                                        '21st Show (transcript)',
                                         'kind': 'statement'},
                                        {'what': 'In the same interview, said '
                                                 'developers must be transparent with '
                                                 'communities and that communities '
                                                 'must have the chance to voice '
                                                 "concerns, with 'community voice "
                                                 "being right at the center', and that "
                                                 'water and other natural resources '
                                                 'should be protected through '
                                                 'regulation.',
                                         'date': '2026-10-13',
                                         'source': 'https://will.illinois.edu/21stshow/story/lt-gov-juliana-stratton-on-iran-war-ice-accountability-and-her-campaign-for-u.s-senate',
                                         'source_name': 'Illinois Public Media, The '
                                                        '21st Show (transcript)',
                                         'kind': 'statement'},
                                        {'what': 'At the Sun-Times/WBEZ/University of '
                                                 'Chicago Democratic primary debate, '
                                                 'The Daily Line reported that the '
                                                 'candidates agreed data centers are a '
                                                 'good source of job creation, and '
                                                 'that Stratton said more generation '
                                                 'needs to be added to the grid to '
                                                 'meet rising demand, pointing to the '
                                                 "state law repealing Illinois's "
                                                 "nuclear moratorium. Reporter's "
                                                 'paraphrase.',
                                         'date': '2026-01-26',
                                         'source': 'https://www.thedailyline.com/leading-candidates-illinois-open-senate-seat-debate-federal-immigration-enforcement-campaign-finance',
                                         'source_name': 'The Daily Line',
                                         'kind': 'statement'}],
                              'as_of': '2026-11-28'},
 ('KS', 'Adam Hamilton'): {'lean': 'guardrails',
                           'summary': "Hamilton's campaign platform says data centers "
                                      'should be required to pay their fair share of '
                                      'electricity costs through binding rules and '
                                      'legislation rather than voluntary pledges. He '
                                      'has said the local community should decide '
                                      'whether a data center is built, that a data '
                                      "center's water cannot come at the expense of "
                                      'drinking water or irrigation, and that '
                                      'data-center builders should not get tax breaks. '
                                      'He has held no office, so the record is '
                                      'statements only.',
                           'background': 'United Methodist pastor in Leawood; has '
                                         'never held elected office, so the record is '
                                         'statements only.',
                           'items': [{'what': 'In a statement quoted in a fact-check '
                                              "of the Senate candidates' data-center "
                                              'positions, said data-center builders '
                                              'should not receive tax breaks.',
                                      'date': '2026-09-24',
                                      'source': 'https://www.yahoo.com/news/politics/articles/fact-check-u-senate-candidates-163652971.html',
                                      'source_name': 'Yahoo News (syndicated; byline '
                                                     'Matthew Kelly, original outlet '
                                                     'not shown on the page)',
                                      'kind': 'statement'},
                                     {'what': 'At the Kansas State Fair debate with '
                                              'Sen. Marshall, the Hutch Post reported '
                                              'that Hamilton agreed guardrails are '
                                              'needed on AI while the U.S. keeps '
                                              'competing with China and Russia, and '
                                              'questioned how Marshall could support '
                                              'both data-center tax benefits and local '
                                              "moratoriums. Reporter's paraphrase; the "
                                              'only direct quote is that this may be '
                                              "'one place where we both agree.'",
                                      'date': '2026-09-12',
                                      'source': 'https://hayspost.com/posts/4c1e12ef-0a89-47bc-9870-de2eb098f187',
                                      'source_name': 'Hutch Post (via Hays Post)',
                                      'kind': 'statement'},
                                     {'what': "In KSHB's primary voter guide on "
                                              'data-center development, said the local '
                                              'community should decide whether a '
                                              'project goes ahead, that data centers '
                                              'should pay their own way, and that a '
                                              "data center's water use cannot come at "
                                              'the expense of drinking water or '
                                              "irrigation or raise a neighbor's bill.",
                                      'date': '2026-07-16',
                                      'source': 'https://www.kshb.com/news/local-news/kansas/johnson-county/voters-guide-kansas-political-candidates-stances-on-data-center-development',
                                      'source_name': 'KSHB 41 voter guide',
                                      'kind': 'statement'},
                                     {'what': "Campaign issues page lists 'Require "
                                              'data centers to pay their fair share of '
                                              "electricity costs' under his "
                                              'affordability agenda, saying the '
                                              'companies behind data centers should '
                                              'cover their costs instead of burdening '
                                              'ratepayers and should earn the support '
                                              'of the towns and counties they move '
                                              'into, and that he would propose binding '
                                              'rules and legislation where others '
                                              'support voluntary pledges.',
                                      'date': '',
                                      'source': 'https://hamiltonforkansas.com/issues/',
                                      'source_name': 'Hamilton for Kansas campaign '
                                                     'site',
                                      'kind': 'statement'}],
                           'as_of': '2026-11-28'},
 ('KY', 'Andy Barr'): {'lean': 'mixed',
                       'summary': 'Barr campaigned on powering AI data centers with '
                                  'Kentucky coal, introduced a 2025 bill to give large '
                                  'AI data centers and the power plants serving them '
                                  'priority federal permitting, and says he personally '
                                  'lobbied the Energy Secretary for the $100 billion '
                                  'Paducah data center campus. He also voted for the '
                                  'House-passed Ratepayer Protection Act, said in the '
                                  'October debate that Kentuckians should not pay '
                                  'higher utility bills because of a data center, and '
                                  'says localities should decide whether to host them.',
                       'background': "U.S. Representative for Kentucky's 6th District "
                                     'since 2013.',
                       'items': [{'what': 'In the only televised Senate debate (WKYT), '
                                          'said Kentuckians should not pay higher '
                                          'utility bills if a data center moves into '
                                          "their town (reporter's paraphrase), that "
                                          'the U.S. must win the AI race against '
                                          'China, and that he believes in local '
                                          'control.',
                                  'date': '2026-10-19',
                                  'source': 'https://www.yahoo.com/news/politics/articles/iran-gas-ai-barr-booker-093023290.html',
                                  'source_name': 'Yahoo News (syndicated; byline '
                                                 'McKenna Horsley, original outlet not '
                                                 'shown on the page)',
                                  'kind': 'statement'},
                                 {'what': 'Told Spectrum News 1, in a campaign '
                                          'profile, that the country needs more data '
                                          'centers and more affordable, reliable '
                                          'power, and that localities should decide '
                                          'whether to host them. The article also says '
                                          'that in February he supported the '
                                          "administration's loosening of emission "
                                          'standards for coal-fired power plants while '
                                          'advocating for more hyper-scale data '
                                          "centers (reporter's characterisation).",
                                  'date': '2026-10-14',
                                  'source': 'https://spectrumnews1.com/ky/lexington/news/2026/10/14/andy-barr-senate-midterms',
                                  'source_name': 'Spectrum News 1 Kentucky',
                                  'kind': 'statement'},
                                 {'what': 'Campaign statement to WPSD, responding to '
                                          "Booker's attacks over the Paducah project, "
                                          'saying local communities rather than '
                                          'Washington should decide whether data '
                                          'centers are built.',
                                  'date': '2026-09-30',
                                  'source': 'https://www.wpsdlocal6.com/news/data-centers-spark-debate-in-kentucky-u-s-senate-race/article_1c2b1276-62c9-47ae-8ed0-5ce31f09c1e7.html',
                                  'source_name': 'WPSD Local 6',
                                  'kind': 'statement'},
                                 {'what': 'Voted Yea on H.R. 9340, the Ratepayer '
                                          'Protection Act, which passed the House '
                                          '417-3 under suspension of the rules.',
                                  'date': '2026-09-16',
                                  'source': 'https://clerk.house.gov/Votes/2026312',
                                  'source_name': 'Clerk of the U.S. House, Roll Call '
                                                 '312',
                                  'kind': 'action'},
                                 {'what': "Quoted in the Department of Energy's "
                                          'announcement of the Paducah Site data '
                                          'center campus (a more than $100 billion '
                                          'private investment), calling it historic '
                                          'and saying he personally advocated with the '
                                          'Energy Secretary to make the project '
                                          'happen.',
                                  'date': '2026-07-29',
                                  'source': 'https://www.energy.gov/articles/energy-department-announces-partnership-expand-reliable-affordable-energy-access-and-power',
                                  'source_name': 'U.S. Department of Energy press '
                                                 'release',
                                  'kind': 'action'},
                                 {'what': 'Senate campaign release on his coal plan '
                                          'says that as electricity demand from AI and '
                                          'data centers grows, reliable '
                                          'around-the-clock power is a national '
                                          'security issue, and lists among legislation '
                                          "he has 'led and supported' measures to "
                                          'speed permitting for power plants and '
                                          "transmission and to 'support AI data "
                                          "centers'. The release names no bill "
                                          'numbers.',
                                  'date': '2026-01-05',
                                  'source': 'https://barrforsenate.com/press-release/andy-barr-unveils-plan-to-revive-kentucky-coal-jobs-and-power-technologies-of-the-future/',
                                  'source_name': 'Andy Barr for Senate press release',
                                  'kind': 'statement'},
                                 {'what': 'Introduced H.R. 5927, the Securing Reliable '
                                          'Power for Advanced Technologies Act '
                                          '(sponsor; 0 cosponsors listed; referred to '
                                          'House Financial Services). The bill would '
                                          'amend the Defense Production Act to let the '
                                          "President designate 'critical artificial "
                                          "intelligence infrastructure' projects as "
                                          'priority national defense projects with '
                                          'concurrent federal permitting on a '
                                          'consolidated schedule. Its definition '
                                          'covers AI data centers with at least 50 '
                                          'megawatts of connected load, dispatchable '
                                          'baseload generation of at least 100 '
                                          'megawatts that does not rely primarily on '
                                          'intermittent renewables and is committed to '
                                          'serve them, associated transmission, and '
                                          'fuel supply infrastructure including coal '
                                          'mines and gas facilities. The portion of '
                                          'the text read contains no ratepayer '
                                          'cost-allocation provision; the full text '
                                          'was not read to the end.',
                                  'date': '2025-11-07',
                                  'source': 'https://www.congress.gov/bill/119th-congress/house-bill/5927/text',
                                  'source_name': 'Congress.gov',
                                  'kind': 'action'},
                                 {'what': "Campaign energy plan (PDF) lists 'Support "
                                          'AI data centers and advanced manufacturing '
                                          "that depend on affordable, nonstop power' "
                                          'among its legislative aims, alongside '
                                          'speeding permits for power plants and '
                                          'transmission lines, and says the plan will '
                                          'lower energy costs for Kentuckians.',
                                  'date': '',
                                  'source': 'https://barrforsenate.com/wp-content/uploads/2026/01/Andy-Barr-Energy-Plan.pdf',
                                  'source_name': "Andy Barr for Senate, 'Plan to "
                                                 'Revive Coal Jobs and Power the '
                                                 "Technologies of the Future'",
                                  'kind': 'statement'}],
                       'as_of': '2026-11-28'},
 ('LA', 'Julia Letlow'): {'lean': 'mixed',
                          'summary': 'Letlow voted for the House-passed Ratepayer '
                                     'Protection Act and said Americans should not pay '
                                     'for electricity used by data centers. She '
                                     "championed Meta's Richland Parish data center in "
                                     'her district, welcomed its $50 billion '
                                     'expansion, and, according to a document obtained '
                                     'by Gulf States Newsroom, signed a nondisclosure '
                                     'agreement with a Meta shell company about the '
                                     'project in June 2024. No statement was found on '
                                     'local objections to the project, its gas plants, '
                                     'or on moratoriums.',
                          'background': "U.S. Representative for Louisiana's 5th "
                                        'District since 2021; the district includes '
                                        "Meta's Richland Parish data center.",
                          'items': [{'what': "Louisiana Illuminator's roundup of data "
                                             "centers in the state's congressional "
                                             'races reports that Letlow cited her '
                                             'House vote for the Ratepayer Protection '
                                             'Act as proof of her support for holding '
                                             'data centers responsible for their '
                                             "promises. This is the reporter's "
                                             'paraphrase; the article carries no '
                                             'direct Letlow quote and does not say '
                                             'where or when she said it. (The page '
                                             "misspells her name 'Lettow'.)",
                                     'date': '2026-10-05',
                                     'source': 'https://lailluminator.com/2026/10/05/data-center-election-debate/',
                                     'source_name': 'Louisiana Illuminator',
                                     'kind': 'statement'},
                                    {'what': 'In a release on her vote for the '
                                             'Ratepayer Protection Act, said Americans '
                                             'should not pay the cost of increased '
                                             'electricity used by data centers, that '
                                             'responsibly developed data centers '
                                             'support jobs and tax revenue, and that '
                                             'Louisiana has taken steps to ensure data '
                                             'centers finance their own operations.',
                                     'date': '2026-09-17',
                                     'source': 'https://letlow.house.gov/media/press-releases/letlow-votes-ratepayer-protection-act',
                                     'source_name': 'Rep. Letlow press release',
                                     'kind': 'statement'},
                                    {'what': 'Voted Yea on H.R. 9340, the Ratepayer '
                                             'Protection Act, which passed the House '
                                             '417-3 under suspension of the rules.',
                                     'date': '2026-09-16',
                                     'source': 'https://clerk.house.gov/Votes/2026312',
                                     'source_name': 'Clerk of the U.S. House, Roll '
                                                    'Call 312',
                                     'kind': 'action'},
                                    {'what': "Statement welcoming Meta's $50 billion "
                                             'expansion in Richland Parish, saying she '
                                             'was thrilled Meta was committing to '
                                             'cover the full cost and protect '
                                             'ratepayers.',
                                     'date': '2026-07-13',
                                     'source': 'https://letlow.house.gov/media/press-releases/letlow-statement-meta-expansion-northeast-louisiana',
                                     'source_name': 'Rep. Letlow press release',
                                     'kind': 'statement'},
                                    {'what': 'Signed a nondisclosure agreement on June '
                                             '29, 2024 with Laidley LLC, which Gulf '
                                             'States Newsroom describes as a shell '
                                             'company of Meta Platforms, covering '
                                             "Meta's plans for its Richland Parish "
                                             'data center, according to the document '
                                             'the newsroom obtained. The report says '
                                             "the NDA's definition of confidential "
                                             'information includes the existence of '
                                             'the agreement itself. Her spokesperson '
                                             'said NDAs are common in economic '
                                             'development discussions and that this '
                                             'one was limited to protecting '
                                             'preliminary business information. (The '
                                             'same story reports her later Meta and '
                                             'Nvidia stock trades and late '
                                             'disclosures; her spokesperson said she '
                                             'did not direct the trades and was '
                                             'unaware of them.)',
                                     'date': '2024-06-29',
                                     'source': 'https://lailluminator.com/2026/08/11/letlow-nda-meta/',
                                     'source_name': 'Gulf States Newsroom via '
                                                    'Louisiana Illuminator',
                                     'kind': 'action'},
                                    {'what': 'Spoke at the public launch event for '
                                             "Meta's Richland Parish data center, "
                                             'which Gulf States Newsroom says came six '
                                             'months after she signed the NDA, and '
                                             'championed the project. The page gives '
                                             'no date for the event.',
                                     'date': '',
                                     'source': 'https://lailluminator.com/2026/08/11/letlow-nda-meta/',
                                     'source_name': 'Gulf States Newsroom via '
                                                    'Louisiana Illuminator',
                                     'kind': 'statement'}],
                          'as_of': '2026-11-28'},
 ('MA', 'Ed Markey'): {'lean': 'guardrails',
                       'summary': 'Markey has released a draft bill requiring a '
                                  'federal public-interest certificate before a data '
                                  'center is built, reintroduced the AI Environmental '
                                  'Impacts Act, and written to FERC, NARUC, ISO New '
                                  'England and the EPA pressing them to keep '
                                  'data-center costs and pollution off households. He '
                                  'voted against advancing the House-passed Ratepayer '
                                  'Protection Act on 2026-09-30 and, after the '
                                  'election, denounced the Senate-passed permitting '
                                  "bill as letting data centers be approved 'without "
                                  "concern for public health or public consent'.",
                       'background': 'U.S. Senator from Massachusetts since 2013.',
                       'items': [{'what': 'Statement after the Senate passed the '
                                          'Bipartisan American Affordability and Jobs '
                                          'Act, calling it an energy permitting bill '
                                          'that will let mines, pipelines, power '
                                          'plants and data centers be approved without '
                                          'concern for public health or public '
                                          'consent, and a win for Big Tech and Big '
                                          'Oil.',
                                  'date': '2026-11-19',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-blasts-senate-passage-of-wolf-in-sheeps-clothing-permitting-bill',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'statement'},
                                 {'what': 'Voted Nay on Senate passage of H.R. 2347 as '
                                          'amended (Senate vote 270, passed 62-33), '
                                          'the vehicle for the Bipartisan American '
                                          'Affordability and Jobs Act, a permitting '
                                          'bill whose sponsors say it makes data '
                                          'centers pay for the grid upgrades they '
                                          'cause.',
                                  'date': '2026-11-19',
                                  'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00270.htm',
                                  'source_name': 'U.S. Senate roll call',
                                  'kind': 'action'},
                                 {'what': 'Signed, with Sens. Kelly and Whitehouse, a '
                                          "letter opposing the EPA's proposal to "
                                          'eliminate the 30-day mandatory public '
                                          'notice period for proposed facilities, such '
                                          'as data centers, that may affect air '
                                          'quality.',
                                  'date': '2026-10-06',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/markey-joins-kelly-whitehouse-to-press-epa-on-rollback-of-public-input-rules-for-data-center-air-permits',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'action'},
                                 {'what': 'Statement on the bipartisan permitting '
                                          'reform proposal, saying data center '
                                          'developers are using ratepayers to '
                                          'subsidize their operations and that he was '
                                          'still reviewing the text.',
                                  'date': '2026-10-01',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-statement-on-bipartisan-permitting-reform-proposal',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'statement'},
                                 {'what': 'Voted Nay on the motion to invoke cloture '
                                          'on the motion to proceed to H.R. 9340 (the '
                                          'House-passed Ratepayer Protection Act). The '
                                          'motion was rejected 57-43, with 60 needed. '
                                          'No Markey statement explaining the vote was '
                                          'found.',
                                  'date': '2026-09-30',
                                  'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.htm',
                                  'source_name': 'U.S. Senate roll call vote 254, '
                                                 '119th Congress 2nd Session',
                                  'kind': 'action'},
                                 {'what': "Released a report, 'The EPA's Data Center "
                                          "Disaster', on EPA rollbacks of air, water "
                                          'and chemical rules that he says make it '
                                          'easier to build data centers and the fossil '
                                          'fuel infrastructure that powers them.',
                                  'date': '2026-09-30',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-releases-new-report-detailing-epa-capitulation-to-big-tech-dangerous-easing-of-regulations-to-build-data-centers-at-the-expense-of-transparency-and-communities-health',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'action'},
                                 {'what': 'Released a discussion draft of the '
                                          'Protecting Communities from Data Center '
                                          'Impacts Act, which would require data '
                                          'centers to receive a federal certificate '
                                          'before permitting and construction '
                                          'affirming they will not harm the public '
                                          'interest and meet minimum energy, '
                                          'environmental and economic standards, and '
                                          'would fund grants to build community '
                                          'capacity.',
                                  'date': '2026-07-13',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-releases-discussion-draft-of-legislation-to-create-a-national-framework-to-address-data-center-harm',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'action'},
                                 {'what': "Released 'The AI Accountability Agenda', "
                                          'which his office says includes new '
                                          'legislation requiring data centers to pay '
                                          'for necessary grid infrastructure and fund '
                                          'clean energy and storage to meet their '
                                          'capacity needs.',
                                  'date': '2026-07-10',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-releases-the-ai-accountability-agenda-taking-power-back-from-big-tech',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'statement'},
                                 {'what': 'Led, with Rep. Jennifer McClellan, a letter '
                                          'urging the EPA to withdraw a proposed rule '
                                          'that would let major polluting facilities, '
                                          'including data centers and fossil fuel '
                                          'plants, begin construction activities '
                                          'before securing Clean Air Act permits.',
                                  'date': '2026-06-30',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/sen-markey-rep-mcclellan-lead-colleagues-in-condemning-epas-attempt-to-let-data-centers-fossil-fuel-plants-and-other-major-facilities-evade-core-clean-air-act-protections',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'action'},
                                 {'what': 'Reintroduced, with Rep. Don Beyer, the AI '
                                          'Environmental Impacts Act of 2026, which '
                                          'would require AI data centers to report '
                                          'environmental and energy-related impacts '
                                          'with fines for non-compliance, direct NIST '
                                          'to set measurement standards, and require '
                                          'an EPA lifecycle study.',
                                  'date': '2026-06-09',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-rep-beyer-reintroduce-ai-environmental-impacts-act',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'action'},
                                 {'what': 'Wrote, with Sens. Blumenthal, Van Hollen '
                                          'and Booker, to the president of NARUC '
                                          'urging state utility commissions to protect '
                                          'residential and small-business ratepayers '
                                          'from data-center-driven rate hikes, '
                                          'including by rejecting rate filings that '
                                          'force ratepayers to subsidize data centers. '
                                          'The release contrasts this with the '
                                          "voluntary 'ratepayer protection pledge'.",
                                  'date': '2026-03-06',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-colleagues-call-for-state-energy-regulators-to-protect-ratepayers-from-data-center-related-cost-hikes',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'action'},
                                 {'what': 'Joined Sen. Peter Welch and four other New '
                                          'England senators in a letter asking ISO New '
                                          'England how it will protect residential '
                                          'ratepayers from data-center-driven price '
                                          'increases. The letter, signed jointly, says '
                                          'the AI industry should be responsible for '
                                          'these costs.',
                                  'date': '2026-01-28',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/markey-welch-new-england-senators-call-for-answers-about-how-new-regional-data-centers-will-drive-up-energy-costs-for-consumers',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'action'},
                                 {'what': 'Wrote to FERC Chair Laura Swett, with six '
                                          'senators cosigning, urging FERC to ensure '
                                          'that energy demand from data centers does '
                                          'not result in unjust or unreasonable rate '
                                          'hikes for households.',
                                  'date': '2025-11-13',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-leads-colleagues-in-urging-federal-energy-regulator-to-prevent-data-centers-from-dramatically-hiking-energy-costs-for-american-families',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'action'},
                                 {'what': 'Wrote to EPA Administrator Lee Zeldin '
                                          'opposing the decision to let major '
                                          'polluting facilities, including data '
                                          'centers and associated power generation, '
                                          'start pre-construction activities without '
                                          'required air quality permits.',
                                  'date': '2025-09-25',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/markey-presses-epa-administrator-lee-zeldin-on-decision-to-undermine-clean-air-act-to-prop-up-ai-data-centers',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'action'},
                                 {'what': "Hosted a virtual roundtable, 'The Data "
                                          'Center Next Door: Hidden Costs and Harms of '
                                          "Artificial Intelligence and Cryptomining', "
                                          'with Rep. Steve Cohen and community '
                                          'advocates, and released a storybook of '
                                          "residents' accounts of living near data "
                                          'center infrastructure.',
                                  'date': '2025-07-23',
                                  'source': 'https://www.markey.senate.gov/news/press-releases/the-data-center-next-door-as-trump-eviscerates-guardrails-senator-markey-hosts-roundtable-discussion-on-how-ai-data-centers-can-harm-environment-increase-costs-to-households-and-threaten-public-health',
                                  'source_name': 'Sen. Markey press release',
                                  'kind': 'action'}],
                       'as_of': '2026-11-28'},
 ('ME', 'Troy Jackson'): {'lean': 'guardrails',
                          'summary': 'As a candidate for governor in spring 2026 he '
                                     "said he would have signed Maine's vetoed "
                                     'temporary statewide data-center ban and released '
                                     'an AI plan requiring companies to build their '
                                     'own power and pay for grid upgrades. As the '
                                     'Senate nominee he said in an October debate that '
                                     'he is "not really supportive of data centers", '
                                     'wants federal or state guardrails, and that they '
                                     'must not raise electricity rates or harm water.',
                          'background': 'Former Maine Senate President. Ran for '
                                        'governor in the 2026 Democratic primary '
                                        'before becoming the Senate nominee. No '
                                        'data-center legislation from his time in the '
                                        'Maine Senate was located.',
                          'items': [{'what': 'At an Oct. 13 debate with Sen. Collins, '
                                             'said: "I\'m not really supportive of '
                                             "data centers, but I understand they're "
                                             'maybe something that we have to deal '
                                             'with," and that he is "very much in '
                                             'favor of making sure the federal '
                                             'government or the state of Maine puts '
                                             'guardrails on these things." Newsweek '
                                             'reported he said data centers in Maine '
                                             'must not raise electricity rates or harm '
                                             'water quality and should be slowed down '
                                             'so people can understand them.',
                                     'date': '2026-10-13',
                                     'source': 'https://newsweek.com/susan-collins-vs-troy-jackson-on-ai-data-centers-amid-maine-voters-fears-12621762',
                                     'source_name': 'Newsweek',
                                     'kind': 'statement'},
                                    {'what': 'Through a campaign spokesperson, called '
                                             'for AI regulations that give workers a '
                                             'seat at the table; the Bangor Daily News '
                                             'reported his campaign would only welcome '
                                             'data centers that create union jobs and '
                                             'protect natural resources, and that it '
                                             'criticised Collins for backing Energy '
                                             'Secretary Chris Wright. The article '
                                             'attributes no direct quote to Jackson '
                                             'himself.',
                                     'date': '2026-09-16',
                                     'source': 'https://www.bangordailynews.com/2026/09/16/politics/maine-politicians-responding-to-ai-warnings-joam40zk0w/',
                                     'source_name': 'Bangor Daily News',
                                     'kind': 'statement'},
                                    {'what': 'While running for governor, released an '
                                             '"Agency over AI" plan in Portland. '
                                             'Spectrum News reported the plan would '
                                             'require AI companies bringing data '
                                             'centers to Maine to build their own '
                                             'power sources and pay for grid upgrades, '
                                             'and that Jackson was among the '
                                             'candidates who said they would have '
                                             'signed the temporary statewide '
                                             'data-center ban Gov. Mills vetoed.',
                                     'date': '2026-06-03',
                                     'source': 'https://spectrumnewsnecn.com/necn/maine/politics/2026/06/04/jackson-says-ai--tech-billionaires--will-face-scrutiny-in-maine-if-he-s-elected-governor',
                                     'source_name': 'Spectrum News',
                                     'kind': 'statement'},
                                    {'what': 'Campaign statement to Newsweek set '
                                             'conditions for data centers coming to '
                                             'Maine: create good-paying union jobs, '
                                             'pay their fair share, protect natural '
                                             'resources and work with local '
                                             'communities; the campaign said Maine '
                                             'families should not subsidize the energy '
                                             'needs of some of the richest '
                                             'corporations in the world.',
                                     'date': '',
                                     'source': 'https://www.newsweek.com/ai-data-center-war-where-democrats-republicans-in-key-senate-races-stand-12354265',
                                     'source_name': 'Newsweek',
                                     'kind': 'statement'},
                                    {'what': 'Newsweek reported that earlier in 2026, '
                                             'while campaigning for governor, he '
                                             "criticised Gov. Mills's veto of the "
                                             'data-center moratorium and said a pause '
                                             'was needed.',
                                     'date': '',
                                     'source': 'https://newsweek.com/susan-collins-vs-troy-jackson-on-ai-data-centers-amid-maine-voters-fears-12621762',
                                     'source_name': 'Newsweek',
                                     'kind': 'statement'},
                                    {'what': 'The American Prospect reported that at a '
                                             'forum the week of Oct. 12 Jackson and '
                                             'Collins agreed data centers must not '
                                             'affect water usage or force ratepayers '
                                             'to pay more for electricity and that '
                                             "local agreements were key (reporter's "
                                             'paraphrase, not a direct quote).',
                                     'date': '',
                                     'source': 'https://prospect.org/2026/10/16/downvoting-data-centers-in-maine/',
                                     'source_name': 'The American Prospect',
                                     'kind': 'statement'},
                                    {'what': 'Roll Call reported that in a debate with '
                                             'Collins the week before Oct. 19 he '
                                             'called for "real guardrails" on data '
                                             'centers and backed safeguards so they '
                                             'would not raise power bills for other '
                                             'customers or harm local water supplies.',
                                     'date': '',
                                     'source': 'https://rollcall.com/2026/10/19/data-center-anxiety-plays-out-in-senate-campaign-debates/',
                                     'source_name': 'Roll Call',
                                     'kind': 'statement'}],
                          'as_of': '2026-11-28'},
 ('MI', 'Abdul El-Sayed'): {'lean': 'guardrails',
                            'summary': 'Published eight "Terms of Engagement for Data '
                                       'Centers" in January 2026: data centers pay for '
                                       'their own energy with no cost passed to '
                                       'ratepayers, no loss of reliability, '
                                       'closed-loop cooling, binding and enforceable '
                                       'community benefits agreements, a jobs '
                                       'guarantee, and no clean-energy loopholes. By '
                                       'July 2026 he said that until those terms exist '
                                       'at the federal level he supports local and '
                                       'state officials approving no more data centers '
                                       'and that "a moratorium makes sense"; E&E News '
                                       'reported he had not endorsed a nationwide '
                                       'moratorium. He told Planet Detroit he would '
                                       'back legislation barring state and local '
                                       'data-center tax breaks and ending NDAs.',
                            'background': 'Physician; former Detroit and Wayne County '
                                          'health director. Has not held legislative '
                                          'office, so the record is campaign '
                                          'statements only.',
                            'items': [{'what': 'E&E News reported that in a televised '
                                               'WOOD-TV primary debate in July he said '
                                               'he would make his terms of engagement '
                                               'law, called for a community benefits '
                                               'agreement with the money put in '
                                               'escrow, and said officials should be '
                                               'able to shut down non-compliant data '
                                               'centers. The article said he had not '
                                               'endorsed a nationwide data-center '
                                               'moratorium.',
                                       'date': '2026-07-31',
                                       'source': 'https://www.eenews.net/articles/michigan-senate-primary-puts-data-center-politics-to-the-test/',
                                       'source_name': 'E&E News',
                                       'kind': 'statement'},
                                      {'what': 'Planet Detroit reported that in a May '
                                               '28 primary debate he challenged a '
                                               "rival for supporting Michigan's "
                                               'data-center tax breaks, and that he '
                                               'told the outlet he would back '
                                               'legislation barring state and local '
                                               'tax breaks for data centers and ending '
                                               'nondisclosure agreements tied to them.',
                                       'date': '2026-06-11',
                                       'source': 'https://planetdetroit.org/2026/06/data-centers-michigan-senate-primary/',
                                       'source_name': 'Planet Detroit',
                                       'kind': 'statement'},
                                      {'what': 'Campaign page "Terms of Engagement for '
                                               'Data Centers" lists eight conditions: '
                                               'no rate hikes, community transparency, '
                                               'energy reliability guarantees, a jobs '
                                               'guarantee with penalties, water '
                                               'protection through closed-loop '
                                               'cooling, binding community benefits '
                                               'agreements, no clean-energy loopholes, '
                                               'and enforceability through actionable '
                                               'penalties. The page does not mention a '
                                               'moratorium, tax breaks or federal '
                                               'legislation.',
                                       'date': '2026-01-08',
                                       'source': 'https://abdulforsenate.com/2026/01/datacenters/',
                                       'source_name': 'Abdul El-Sayed campaign',
                                       'kind': 'statement'},
                                      {'what': 'Planet Detroit reported on the '
                                               "framework's release and that he told "
                                               'the outlet its priorities should be a '
                                               'guidepost for both local decisions and '
                                               'federal legislation, that federal '
                                               'legislation is needed because large '
                                               'tech companies target small townships, '
                                               'and that he is unlikely to get '
                                               'data-center legislation passed until '
                                               'President Trump leaves office.',
                                       'date': '2026-01-08',
                                       'source': 'https://planetdetroit.org/2026/01/el-sayed-data-centers-senate/',
                                       'source_name': 'Planet Detroit',
                                       'kind': 'statement'},
                                      {'what': 'Told The Gander he would champion '
                                               'federal standards for data centers; '
                                               'the outlet reported he wants federal '
                                               'rules that ensure promised jobs '
                                               'materialise, require community '
                                               'benefits agreements, and make data '
                                               'centers pay for their own power '
                                               "without raising customers' rates. He "
                                               'also said data centers can bring good '
                                               'union jobs if done right.',
                                       'date': '2025-12-18',
                                       'source': 'https://gandernewsroom.com/2025/12/18/michigans-us-senate-candidates-weigh-in-on-data-centers-and-ai',
                                       'source_name': 'The Gander',
                                       'kind': 'statement'},
                                      {'what': 'At a press conference at a data-center '
                                               'site in Saline (July 2026; the '
                                               'campaign release gives no calendar '
                                               'date), said that until terms of '
                                               'engagement exist at the federal level '
                                               'he would back local and state '
                                               'officials in not approving more data '
                                               'centers, and that "a moratorium makes '
                                               'sense" for states or localities.',
                                       'date': '',
                                       'source': 'https://abdulforsenate.com/2026/07/icymi-dr-abdul-el-sayed-joins-press-conference-at-the-barn-data-center-in-saline/',
                                       'source_name': 'Abdul El-Sayed campaign',
                                       'kind': 'statement'},
                                      {'what': 'Newsweek reported, citing a CBS 60 '
                                               'Minutes appearance, that he said "we '
                                               'need local and state moratoriums" '
                                               'until federal rules exist, that data '
                                               'centers "cannot touch our waterways at '
                                               'all", should use "all union labor", '
                                               'and need community benefits agreements '
                                               'negotiated transparently with local '
                                               'communities. The page gives no date '
                                               'for the remarks (published around the '
                                               'start of November 2026).',
                                       'date': '',
                                       'source': 'https://newsweek.com/el-sayed-issues-data-center-warning-voters-deathly-afraid-60-minutes-midterms-michigan-12648260',
                                       'source_name': 'Newsweek',
                                       'kind': 'statement'},
                                      {'what': 'Roll Call reported that at the '
                                               'Michigan Senate general-election '
                                               'debate in October he said he supports '
                                               '"terms of engagement" for data '
                                               'centers, without saying in the debate '
                                               'what those terms should be.',
                                       'date': '',
                                       'source': 'https://rollcall.com/2026/10/19/data-center-anxiety-plays-out-in-senate-campaign-debates/',
                                       'source_name': 'Roll Call',
                                       'kind': 'statement'}],
                            'as_of': '2026-11-28'},
 ('MN', 'Peggy Flanagan'): {'lean': 'guardrails',
                            'summary': 'The record is two reports of campaign '
                                       'statements. In a July primary debate she said '
                                       'it was troubling that data-center decisions '
                                       'move "at the speed of corporate interests and '
                                       'not of community." In September a Forum News '
                                       'Service report said she opposes major tax '
                                       'breaks for Big Tech, thinks data-center NDAs '
                                       'should be banned, and quoted her: "Communities '
                                       'get to call the shots." No action as '
                                       'lieutenant governor on data centers was '
                                       'located.',
                            'background': 'Lieutenant Governor of Minnesota since '
                                          '2019; former Minnesota House member. No '
                                          'data-center action from the lieutenant '
                                          "governor's office was located.",
                            'items': [{'what': 'Forum News Service reported that she '
                                               'opposes major tax breaks for Big Tech, '
                                               'thinks NDA use for data centers should '
                                               'be banned, and says they should be '
                                               'built with union labor and meet '
                                               "Minnesota's environmental standards "
                                               "(all reporter's paraphrase), and "
                                               'quoted a statement from her: '
                                               '"Communities get to call the shots." '
                                               'The report said none of the four '
                                               'candidates it covered said they would '
                                               'support a statewide or federal '
                                               'moratorium.',
                                       'date': '2026-09-11',
                                       'source': 'https://www.inforum.com/news/minnesota/where-do-minnesota-statewide-office-candidates-stand-on-data-centers',
                                       'source_name': 'Forum News Service (InForum)',
                                       'kind': 'statement'},
                                      {'what': 'In the MPR News DFL primary debate '
                                               'with Rep. Angie Craig, said of data '
                                               'centers that it is troubling to be '
                                               'moving at the speed of corporate '
                                               'interests rather than community. MPR '
                                               'reported she said residents across '
                                               'Minnesota and the country have big '
                                               'concerns about data centers. Her '
                                               '"existential threat" remark in the '
                                               'same debate was, per MPR, about AI '
                                               'getting out of control.',
                                       'date': '2026-07-27',
                                       'source': 'https://www.mprnews.org/story/2026/07/27/angie-craig-peggy-flanagan-senate-race-debate-hosted-by-mpr-news',
                                       'source_name': 'MPR News',
                                       'kind': 'statement'}],
                            'as_of': '2026-11-28'},
 ('MS', 'Scott Colom'): {'lean': 'guardrails',
                         'summary': 'At a Sept. 24, 2026 press conference in Jackson '
                                    'he called for a temporary ban on new data centers '
                                    'in Mississippi until a list of conditions is met, '
                                    'including data centers paying their own way and '
                                    'more transparency about the deals. He criticised '
                                    'his opponent for not signing on to the Ratepayer '
                                    'Protection Act. That one event is the whole '
                                    'documented record.',
                         'background': 'District attorney in the Columbus area before '
                                       'running; no legislative record.',
                         'items': [{'what': 'At a press conference in Jackson, called '
                                            'for a temporary ban on new data centers '
                                            'in Mississippi. Mississippi Today '
                                            'reported he has a list of conditions he '
                                            'wants met before any new data-center '
                                            'construction proceeds, including data '
                                            'centers paying their own way and more '
                                            'transparency about the deals, and that he '
                                            'said a pause would give the state a '
                                            'chance to study impacts and write '
                                            'regulations.',
                                    'date': '2026-09-24',
                                    'source': 'https://mississippitoday.org/2026/09/24/data-centers-ban-colom-hyde-smith/',
                                    'source_name': 'Mississippi Today',
                                    'kind': 'statement'},
                                   {'what': 'At the same press conference, said Sen. '
                                            'Hyde-Smith had not signed on to the '
                                            'Ratepayer Protection Act and "refuses to '
                                            'provide any oversight", tying that to an '
                                            'AI super PAC running ads on her behalf. '
                                            'The page does not record Colom himself '
                                            'pledging to cosponsor or vote for the '
                                            'bill.',
                                    'date': '2026-09-24',
                                    'source': 'https://mississippitoday.org/2026/09/24/data-centers-ban-colom-hyde-smith/',
                                    'source_name': 'Mississippi Today',
                                    'kind': 'statement'}],
                         'as_of': '2026-11-28'},
 ('MT', 'Kurt Alme'): {'lean': 'mixed',
                       'summary': 'Three campaign-season reports. He said data-center '
                                  'decisions should be left to local communities, that '
                                  'companies must "pay their own way", hire locally '
                                  'and not harm water or electricity rates, and that '
                                  'he would work for transparency and "clear '
                                  'guardrails". He also pointed to "positive tax base '
                                  'opportunities" and said a senator has an obligation '
                                  'to secure "the benefits of innovation". He has not '
                                  'backed a moratorium, and no action is on record.',
                       'background': 'Former U.S. Attorney for Montana and former '
                                     'state budget director. No legislative record.',
                       'items': [{'what': "NBC Montana's roundup of candidate "
                                          'positions quoted him saying data-center '
                                          'companies need to pay their own way and '
                                          'hire local jobs, cannot have adverse '
                                          'impacts on water, and that the decision '
                                          'should be left to local communities. The '
                                          'article says he supports the "Ratepayer '
                                          'Protection Act" (reporter\'s paraphrase).',
                                  'date': '2026-10-18',
                                  'source': 'https://nbcmontana.com/news/local/alme-bankhead-bodnar-austin-lay-out-policy-positions-in-race-for-senate',
                                  'source_name': 'NBC Montana',
                                  'kind': 'statement'},
                                 {'what': 'At the Montana Broadcasters Association '
                                          'U.S. Senate debate in Bozeman, said he '
                                          'would work for transparency, clear '
                                          'guardrails and for Montana communities to '
                                          'be heard. The Daily Montanan reported he '
                                          'said AI companies building data centers '
                                          'should be transparent about their costs to '
                                          'the community, pay their own way, hire '
                                          'locally, and not harm water supplies, water '
                                          'quality or electricity rates (paraphrase).',
                                  'date': '2026-10-11',
                                  'source': 'https://dailymontanan.com/2026/10/12/montana-us-senate-candidates-share-debate-stage/',
                                  'source_name': 'Daily Montanan',
                                  'kind': 'statement'},
                                 {'what': 'Responding to a Truth Social post in which '
                                          'President Trump said communities opposing '
                                          'data centers would end up "backwards and '
                                          'poor", told MTN he understood Trump\'s '
                                          'interest in economic development but that '
                                          'communities should make their own '
                                          'decisions. He called transparency, local '
                                          'hiring and protecting the community '
                                          'important guardrails, said companies will '
                                          'need to be open about electricity and water '
                                          'impacts (paraphrase), and said the '
                                          'Ratepayer Protection Pledge signed by Gov. '
                                          'Gianforte had positive steps but more could '
                                          'be done (paraphrase). He also cited '
                                          'tax-base opportunities and the benefits of '
                                          'innovation.',
                                  'date': '2026-08-31',
                                  'source': 'https://www.ktvh.com/news/montana-politics/montana-u-s-senate-candidates-discuss-how-to-manage-data-centers-ai',
                                  'source_name': 'KTVH / MTN News',
                                  'kind': 'statement'}],
                       'as_of': '2026-11-28'},
 ('NC', 'Roy Cooper'): {'lean': 'guardrails',
                        'summary': 'Throughout the 2026 campaign he said data centers '
                                   'must pay their own way with no costs passed to '
                                   'consumers, that large tech companies should be '
                                   'encouraged to build their own energy sources, and '
                                   'that local governments should control where they '
                                   'go; his campaign said that includes local '
                                   'moratoriums. He has not backed a federal '
                                   'moratorium or an outright ban. No governor-era '
                                   'action specifically on data centers was located.',
                        'background': 'Governor of North Carolina 2017-2024; state '
                                      'attorney general 2001-2016. No governor-era '
                                      'signing or veto specifically on data centers '
                                      'was located.',
                        'items': [{'what': 'Campaign issue page "Lowering Energy & '
                                           'Utility Costs" (last updated 2026-09-05) '
                                           'pledges to make data centers pay the full '
                                           'cost of the power they use, encourage '
                                           'large tech companies to build their own '
                                           'energy sources, involve local communities '
                                           'fully in any decision, and ban utility '
                                           'disconnections during dangerous heat and '
                                           'cold.',
                                   'date': '2026-09-05',
                                   'source': 'https://roycooper.com/?p=682',
                                   'source_name': 'Roy Cooper campaign',
                                   'kind': 'statement'},
                                  {'what': 'Fox News quoted him from an unnamed local '
                                           'interview saying data centers must pay for '
                                           'their own power and should build their own '
                                           'energy sources, and reported his campaign '
                                           'says local communities should have the '
                                           'final say on new projects, including local '
                                           'moratoriums. Fox described this as a shift '
                                           'from his time as governor and noted he has '
                                           'not called for an outright ban.',
                                   'date': '2026-08-30',
                                   'source': 'https://www.foxnews.com/politics/roy-cooper-changes-tune-data-centers-rising-power-costs-collide-senate-campaign',
                                   'source_name': 'Fox News',
                                   'kind': 'statement'},
                                  {'what': 'Campaign position via a spokesperson to '
                                           'Spectrum News: data centers must pay for '
                                           'all the energy they use without passing '
                                           'costs to consumers. Spectrum reported both '
                                           'he and his opponent support letting local '
                                           'communities block data centers and neither '
                                           'has voiced support for a federal '
                                           'moratorium; that numerous data centers '
                                           'were built while he was governor; and that '
                                           'his campaign says the tax breaks were '
                                           'signed in 2006 and expanded in 2015, '
                                           'before his term.',
                                   'date': '2026-08-27',
                                   'source': 'https://spectrumlocalnews.com/nc/charlotte/news/2026/08/27/data-centers-roy-cooper-whatley',
                                   'source_name': 'Spectrum News',
                                   'kind': 'statement'},
                                  {'what': 'After a campaign speech in Fayetteville, '
                                           'told reporters data centers must pay their '
                                           'own way with no costs passed to consumers, '
                                           'and that local governments should have '
                                           'control and input over where they are '
                                           'sited.',
                                   'date': '2026-04-07',
                                   'source': 'https://www.cityviewnc.com/?p=63630',
                                   'source_name': 'CityView NC',
                                   'kind': 'statement'}],
                        'as_of': '2026-11-28'},
 ('NE', 'Pete Ricketts'): {'lean': 'mixed',
                           'summary': 'As governor he announced and celebrated the '
                                      'Facebook and Google data centers in Papillion '
                                      'and, in 2022, signed a bill exempting certain '
                                      "large data centers' purchases from sales tax. "
                                      'As a senator in 2026 he cosponsored the '
                                      'Ratepayer Protection Act, voted to advance it '
                                      'on Sept. 30, and wrote that "data centers '
                                      'shouldn\'t get a free pass" and that local '
                                      'communities should set the terms before one is '
                                      'built.',
                           'background': 'U.S. Senator since January 2023; Governor of '
                                         'Nebraska 2015-2023. The record has both '
                                         'governor-era recruitment and incentives and '
                                         '2026 Senate actions on ratepayer costs.',
                           'items': [{'what': 'Voted Yea on Senate passage of H.R. '
                                              '2347 as amended (Senate vote 270, '
                                              'passed 62-33), the vehicle for the '
                                              'Bipartisan American Affordability and '
                                              'Jobs Act, a permitting bill whose '
                                              'sponsors say it makes data centers pay '
                                              'for the grid upgrades they cause.',
                                      'date': '2026-11-19',
                                      'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00270.htm',
                                      'source_name': 'U.S. Senate roll call',
                                      'kind': 'action'},
                                     {'what': 'In a release on his AI record, listed '
                                              'the Ratepayer Protection Act among '
                                              'legislation he has championed, '
                                              'describing it as giving states and '
                                              'local communities leverage to negotiate '
                                              'on data centers.',
                                      'date': '2026-10-14',
                                      'source': 'https://www.ricketts.senate.gov/news/press-releases/ricketts-champions-ai-innovation-and-safety/',
                                      'source_name': 'Sen. Ricketts press release',
                                      'kind': 'statement'},
                                     {'what': 'In his weekly column, wrote that data '
                                              'centers "shouldn\'t get a free pass", '
                                              'that he supports the Ratepayer '
                                              'Protection Act, that local communities '
                                              'should set the terms before a data '
                                              'center is built and should have a '
                                              'choice in allowing them, and that '
                                              'communities could negotiate for things '
                                              'like lower property taxes. He also '
                                              'wrote that the U.S. needs to beat China '
                                              'in the AI race.',
                                      'date': '2026-10-02',
                                      'source': 'https://www.ricketts.senate.gov/weekly_column/senator-ricketts-weekly-column-democrats-blocked-lower-energy-bills/',
                                      'source_name': 'Sen. Ricketts weekly column',
                                      'kind': 'statement'},
                                     {'what': 'Voted Yea on cloture on the motion to '
                                              'proceed to H.R. 9340 (Senate Vote No. '
                                              '254). The motion was rejected 57-43, '
                                              'short of the 60 votes needed.',
                                      'date': '2026-09-30',
                                      'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.htm',
                                      'source_name': 'U.S. Senate roll call vote',
                                      'kind': 'action'},
                                     {'what': 'Announced his cosponsorship of the '
                                              'Ratepayer Protection Act, introduced in '
                                              'the Senate by Sen. Jon Husted (the '
                                              'release cites the House version, H.R. '
                                              '9340, and gives no Senate bill number). '
                                              'The release says the bill would require '
                                              'data centers to pay the full utility '
                                              'cost needed to serve them.',
                                      'date': '2026-09-18',
                                      'source': 'https://www.ricketts.senate.gov/news/press-releases/ricketts-supports-ratepayer-protection-act/',
                                      'source_name': 'Sen. Ricketts press release',
                                      'kind': 'action'},
                                     {'what': 'At the Nebraska State Fair U.S. Senate '
                                              'debate, said local control governs data '
                                              'centers and that communities '
                                              'considering one should negotiate first, '
                                              'insisting on no impact on power rates '
                                              'and on water conservation through '
                                              'closed-loop systems, and can then ask '
                                              'for more in property taxes.',
                                      'date': '2026-09-01',
                                      'source': 'https://nebraskapublicmedia.org/en/news/news-articles/money-power-take-center-stage-during-ricketts-and-osborns-state-fair-debate/',
                                      'source_name': 'Nebraska Public Media',
                                      'kind': 'statement'},
                                     {'what': 'As governor, signed LB 1150, which lets '
                                              'certain "tier two" data centers apply '
                                              'for sales and use tax exemptions on '
                                              'some equipment purchases and rentals. '
                                              'Source is a tax-industry summary that '
                                              'names him as the signing governor, not '
                                              "the Legislature's own bill page.",
                                      'date': '2022-04-19',
                                      'source': 'https://www.salestaxinstitute.com/resources/certain-large-data-centers-purchases-exempt-from-sales-tax-in-nebraska',
                                      'source_name': 'Sales Tax Institute',
                                      'kind': 'action'},
                                     {'what': 'As governor, spoke at the '
                                              "groundbreaking of Google's $600 million "
                                              'data center in Papillion, saying he '
                                              "hoped it would rival Google's data "
                                              'centers in Iowa and crediting the '
                                              "state's workforce.",
                                      'date': '2019-10-04',
                                      'source': 'https://www.ketv.com/article/live-google-announces-groundbreaking-of-new-data-center-in-papillion/29366053',
                                      'source_name': 'KETV',
                                      'kind': 'statement'},
                                     {'what': 'As governor, announced that Facebook '
                                              'had selected Papillion for a data '
                                              'center and tied it to his '
                                              "administration's priority of growing "
                                              "the state's tech industry. The release "
                                              'does not mention tax incentives or '
                                              'legislation.',
                                      'date': '2017-04-04',
                                      'source': 'https://opportunity.nebraska.gov/gov-ricketts-announces-facebook-investment-in-the-silicon-prairie/',
                                      'source_name': 'Nebraska Department of Economic '
                                                     'Development',
                                      'kind': 'statement'}],
                           'as_of': '2026-11-28'},
 ('NH', 'Chris Pappas'): {'lean': 'guardrails',
                          'summary': 'As a House member Pappas voted for the Ratepayer '
                                     'Protection Act (417-3) and signed a bipartisan '
                                     "letter questioning Meta's use of the research "
                                     'tax credit for data-center construction. On the '
                                     'campaign trail he said New Hampshire is not the '
                                     'right place for AI data centers, that towns '
                                     'should be able to vet and reject proposals, and '
                                     'that ratepayers should not be on the hook; NHPR '
                                     'reports he supports a state-level moratorium.',
                          'background': "U.S. Representative for New Hampshire's 1st "
                                        'District since 2019.',
                          'items': [{'what': "NHPR's election guide reports that both "
                                             'Pappas and his Republican opponent John '
                                             'E. Sununu have said they support a '
                                             'state-level moratorium on data center '
                                             "construction. This is NHPR's "
                                             'characterisation; the page carries no '
                                             'direct Pappas quote on a moratorium.',
                                     'date': '2026-10-30',
                                     'source': 'https://www.nhpr.org/politics/2026-10-30/where-do-nh-candidates-stand-on-ai-and-data-centers-election-2026-midterms',
                                     'source_name': 'New Hampshire Public Radio',
                                     'kind': 'statement'},
                                    {'what': 'Signed a bipartisan House letter, led by '
                                             'Reps. Panetta and Steube, to Treasury '
                                             'Secretary Scott Bessent expressing '
                                             'concern about reports that Meta is '
                                             'seeking to use the federal research tax '
                                             'credit for its data center buildout. '
                                             "Panetta's release lists Chris Pappas "
                                             '(NH-01) among the signers.',
                                     'date': '2026-10-14',
                                     'source': 'https://panetta.house.gov/media/press-releases/rep-panetta-leads-bipartisan-letter-raising-concerns-about-metas-use-research',
                                     'source_name': 'Rep. Panetta press release',
                                     'kind': 'action'},
                                    {'what': 'In an NHPR candidate interview, said '
                                             'communities should be given power over '
                                             'data center development, that a town '
                                             'facing a proposal should have every '
                                             'opportunity to vet and reject it, and '
                                             'that ratepayers should not be on the '
                                             'hook for massive data center development '
                                             'in New Hampshire or anywhere else.',
                                     'date': '2026-10-09',
                                     'source': 'https://www.nhpr.org/2026-10-09/chris-pappas-nh-newhampshire-senate-2026-midterms-housing-affordability-ai-election',
                                     'source_name': 'New Hampshire Public Radio',
                                     'kind': 'statement'},
                                    {'what': 'In his release on the vote, said data '
                                             'centers and other large-load consumers '
                                             'should not get a free pass to raise '
                                             'electric rates and should pay their own '
                                             'way, and that he would keep fighting to '
                                             'put the decision on whether data center '
                                             'construction can move forward in the '
                                             'hands of Granite Staters.',
                                     'date': '2026-09-17',
                                     'source': 'https://pappas.house.gov/media/press-releases/pappas-helps-pass-bipartisan-ratepayer-protection-act',
                                     'source_name': 'Rep. Pappas press release',
                                     'kind': 'statement'},
                                    {'what': 'Voted Yea on H.R. 9340, the Ratepayer '
                                             'Protection Act, on the motion to suspend '
                                             'the rules and pass, as amended. The '
                                             'House Clerk records the vote as 417 '
                                             'yeas, 3 nays, 12 not voting (Roll Call '
                                             '312).',
                                     'date': '2026-09-16',
                                     'source': 'https://clerk.house.gov/evs/2026/roll312.xml',
                                     'source_name': 'Clerk of the U.S. House, Roll '
                                                    'Call 312',
                                     'kind': 'action'},
                                    {'what': 'Told Spectrum News that New Hampshire is '
                                             'not the right place for AI data centers '
                                             'and that Granite Staters should not be '
                                             'asked to foot the bill for out-of-state '
                                             'corporations that might develop them.',
                                     'date': '2026-09-08',
                                     'source': 'https://spectrumnewsnecn.com/necn/central-western-ma/news/2026/09/08/new-hampshire-data-centers-shaheen-pappas-ayotte',
                                     'source_name': 'Spectrum News',
                                     'kind': 'statement'}],
                          'as_of': '2026-11-28'},
 ('NJ', 'Cory Booker'): {'lean': 'guardrails',
                         'summary': 'Booker cosponsored the Power for the People Act '
                                    'and the AI Environmental Impacts Act, and signed '
                                    'letters to FERC, PJM and state utility regulators '
                                    'asking that data-center costs not be shifted to '
                                    'ratepayers. He voted against advancing the '
                                    'House-passed Ratepayer Protection Act after '
                                    'cosponsoring a Van Hollen amendment to it, and '
                                    'voted against the Senate permitting bill (H.R. '
                                    '2347, as amended) on 2026-11-19.',
                         'background': 'U.S. Senator from New Jersey since 2013.',
                         'items': [{'what': 'Voted Nay on Senate passage of H.R. 2347 '
                                            "as amended, the vehicle for the Senate's "
                                            'bipartisan permitting bill (referred to '
                                            'on the floor as BAAJA), which passed '
                                            '62-33. In the floor debate recorded on '
                                            'the same pages, supporter Sen. Whitehouse '
                                            'said the bill would force data centers to '
                                            'pay for the costs they impose on the '
                                            'grid, while opponent Sen. Merkley said it '
                                            'puts the pedal to the floor on data '
                                            'centers. The pages record no statement by '
                                            'Booker.',
                                    'date': '2026-11-19',
                                    'source': 'https://www.govinfo.gov/content/pkg/CREC-2026-11-19/html/CREC-2026-11-19-pt1-PgS5797-2.htm',
                                    'source_name': 'Congressional Record, Nov. 19, '
                                                   '2026 (S5797-S5804)',
                                    'kind': 'action'},
                                   {'what': 'Voted Nay on the motion to invoke cloture '
                                            'on the motion to proceed to H.R. 9340 '
                                            '(the House-passed Ratepayer Protection '
                                            'Act). Cloture was rejected 57-43, with 60 '
                                            'votes required, so the Senate did not '
                                            'take up the bill.',
                                    'date': '2026-09-30',
                                    'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.xml',
                                    'source_name': 'U.S. Senate Roll Call Vote 254 '
                                                   '(119th Congress, 2nd Session)',
                                    'kind': 'action'},
                                   {'what': 'Cosponsored Senate Amendment 6840 (Van '
                                            'Hollen) to H.R. 9340, the House-passed '
                                            'Ratepayer Protection Act. The amendment, '
                                            'which was ordered to lie on the table, '
                                            'adds a sense of Congress that ratepayers '
                                            'should not be forced to take on the '
                                            'financial risks and costs of '
                                            'infrastructure for data centers and that '
                                            'data center owners should be held '
                                            'accountable for the energy costs they '
                                            'cause.',
                                    'date': '2026-09-29',
                                    'source': 'https://www.govinfo.gov/content/pkg/CREC-2026-09-29/html/CREC-2026-09-29-pt1-PgS5178-3.htm',
                                    'source_name': 'Congressional Record, Sept. 29, '
                                                   '2026 (S5178-S5183)',
                                    'kind': 'action'},
                                   {'what': "Cosponsored Sen. Markey's AI "
                                            'Environmental Impacts Act of 2026, which '
                                            "Markey's release says would require AI "
                                            'data centers to report on their '
                                            'environmental and energy-related impacts, '
                                            'with fines for those that fail to comply.',
                                    'date': '2026-06-09',
                                    'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-rep-beyer-reintroduce-ai-environmental-impacts-act',
                                    'source_name': 'Sen. Markey press release',
                                    'kind': 'action'},
                                   {'what': 'Signed a letter with Sens. Markey, '
                                            'Blumenthal and Van Hollen to NARUC '
                                            'president Ann Rendahl urging state '
                                            'utility commissions to protect '
                                            'residential and small-business ratepayers '
                                            'from data-center-related rate hikes, '
                                            'including by rejecting rate filings that '
                                            'force ratepayers to subsidize data '
                                            'centers.',
                                    'date': '2026-03-06',
                                    'source': 'https://www.markey.senate.gov/news/press-releases/senator-markey-colleagues-call-for-state-energy-regulators-to-protect-ratepayers-from-data-center-related-cost-hikes',
                                    'source_name': 'Sen. Markey press release',
                                    'kind': 'action'},
                                   {'what': 'Cosponsored the Power for the People Act '
                                            "(Sen. Van Hollen's bill; the "
                                            'Congressional Record Index lists it as S. '
                                            "3682 under Booker's cosponsored bills). "
                                            'His release says it directs states to '
                                            'evaluate new rate classes for data '
                                            'centers and directs FERC to issue a rule '
                                            'on data centers paying for transmission '
                                            'upgrades, with prevailing-wage and '
                                            'apprenticeship standards.',
                                    'date': '2026-01-16',
                                    'source': 'https://www.booker.senate.gov/news/press/booker-van-hollen-colleagues-introduce-legislation-to-ensure-americans-arent-footing-the-bill-for-big-data-centers',
                                    'source_name': 'Sen. Booker press release',
                                    'kind': 'action'},
                                   {'what': 'Said in the same release that the costs '
                                            'of AI, especially higher electricity '
                                            'prices, must not be shifted onto working '
                                            'families in places like New Jersey, and '
                                            'that the bill ensures data centers pay '
                                            'the costs of their own development.',
                                    'date': '2026-01-16',
                                    'source': 'https://www.booker.senate.gov/news/press/booker-van-hollen-colleagues-introduce-legislation-to-ensure-americans-arent-footing-the-bill-for-big-data-centers',
                                    'source_name': 'Sen. Booker press release',
                                    'kind': 'statement'},
                                   {'what': 'Signed a letter led by Sen. Van Hollen '
                                            'and Rep. Beyer to PJM Board chair David '
                                            'Mills pressing PJM to put forward '
                                            'protections so customers do not bear the '
                                            'costs of rising data center energy '
                                            'demand; the letter says data center '
                                            'demand added over $16 billion in costs in '
                                            'the last two PJM capacity auctions.',
                                    'date': '2025-11-06',
                                    'source': 'https://www.vanhollen.senate.gov/news/press-releases/van-hollen-beyer-colleagues-urge-power-grid-operator-pjm-to-prioritize-consumers-access-to-reliable-affordable-electricity-over-large-corporate-interests',
                                    'source_name': 'Sen. Van Hollen press release',
                                    'kind': 'action'},
                                   {'what': 'With Sen. Andy Kim, led a letter from '
                                            "nine members of New Jersey's "
                                            'congressional delegation to PJM ahead of '
                                            'an anticipated 17% rate increase on June '
                                            '1, 2025; the letter says the 2024 '
                                            'capacity auction results reflect growing '
                                            'grid demand from data centers and asks '
                                            'what PJM is doing to lower rates.',
                                    'date': '2025-05-02',
                                    'source': 'https://www.kim.senate.gov/press_release/kim-booker-lead-members-of-nj-congressional-delegation-in-letter-to-pjm-interconnection-pjm-raising-serious-concerns-over-rate-increase-impacting-new-jersey-families/',
                                    'source_name': 'Sen. Kim press release',
                                    'kind': 'action'},
                                   {'what': 'With Sens. Van Hollen, Kelly and Kaine, '
                                            'wrote to FERC asking the commission to '
                                            'hold a technical conference on ensuring '
                                            'the data center boom does not result in '
                                            'unjust and unreasonable electricity '
                                            'bills, service disruptions or increased '
                                            'fossil-plant pollution.',
                                    'date': '2025-02-14',
                                    'source': 'https://www.vanhollen.senate.gov/news/press-releases/van-hollen-colleagues-call-on-ferc-to-ensure-affordable-reliable-electricity-service-for-americans-amid-rising-energy-demands-of-data-centers',
                                    'source_name': 'Sen. Van Hollen press release',
                                    'kind': 'action'}],
                         'as_of': '2026-11-28'},
 ('NM', 'Ben Ray Luján'): {'lean': 'guardrails',
                           'summary': 'Luján co-signed a September 2026 letter asking '
                                      'every state utility commission to adopt a '
                                      'data-center rate rider so data centers pay the '
                                      'full cost of the generation, transmission and '
                                      'distribution built for them, and signed a '
                                      "Finance Committee Democrats' letter questioning "
                                      "Meta's use of research tax credits for AI data "
                                      'centers. As a candidate he said data centers '
                                      'should not use drinking or agricultural water '
                                      'and should generate their own power. He voted '
                                      'against advancing the House-passed Ratepayer '
                                      'Protection Act and against the Senate '
                                      'permitting bill.',
                           'background': 'U.S. Senator from New Mexico since 2021; '
                                         'former U.S. Representative and member of the '
                                         'New Mexico Public Regulation Commission.',
                           'items': [{'what': 'Voted Nay on Senate passage of H.R. '
                                              '2347 as amended, the vehicle for the '
                                              'permitting bill, which passed 62-33.',
                                      'date': '2026-11-19',
                                      'source': 'https://www.govinfo.gov/content/pkg/CREC-2026-11-19/html/CREC-2026-11-19-pt1-PgS5797-2.htm',
                                      'source_name': 'Congressional Record, Nov. 19, '
                                                     '2026 (S5797-S5804)',
                                      'kind': 'action'},
                                     {'what': 'Voted against advancing the Senate '
                                              'permitting bill (the Bipartisan '
                                              'American Affordability and Jobs Act) in '
                                              'the Nov. 9 procedural vote, saying he '
                                              'shares concerns raised by tribal '
                                              'leaders and environmentalists and could '
                                              'not support advancing the bill in its '
                                              'current form. Source NM reports that '
                                              'sponsor Sen. Heinrich says the bill '
                                              'would hold data centers financially '
                                              'liable for new costs they impose on '
                                              "energy grids; Luján's statement as "
                                              'quoted does not mention data centers.',
                                      'date': '2026-11-09',
                                      'source': 'https://sourcenm.com/2026/11/09/us-senate-advances-new-mexico-us-sen-heinrichs-controversial-permit-reform-bill/',
                                      'source_name': 'Source New Mexico',
                                      'kind': 'action'},
                                     {'what': 'Joined Senate Finance Committee ranking '
                                              'member Ron Wyden and five other '
                                              'senators in a letter to Meta CEO Mark '
                                              'Zuckerberg asking Meta to justify its '
                                              'use of federal research and development '
                                              'tax credits to fund its buildout of AI '
                                              'data centers.',
                                      'date': '2026-10-15',
                                      'source': 'https://www.lujan.senate.gov/newsroom/press-releases/lujan-colleaguesquestion-metas-use-of-billions-in-research-and-development-tax-credits-to-subsidize-its-ai-data-center-construction-boom/',
                                      'source_name': 'Sen. Luján press release',
                                      'kind': 'action'},
                                     {'what': 'In a KVIA voter-guide questionnaire, '
                                              'said data centers should not use '
                                              'drinking water or agricultural water, '
                                              'should be required to generate their '
                                              'own power rather than strain the grid, '
                                              'and that New Mexicans should not pay a '
                                              'penny more for electricity.',
                                      'date': '2026-10-05',
                                      'source': 'https://kvia.com/voter-guide-2026/new-mexico-senator-district-3/2026/10/05/ben-ray-lujan-candidate-for-new-mexico-senator/',
                                      'source_name': 'KVIA voter guide',
                                      'kind': 'statement'},
                                     {'what': 'With Sens. Heinrich, Kelly and '
                                              "Cantwell, wrote to NARUC's president "
                                              'and first vice president asking that '
                                              'every state utility commission adopt a '
                                              'dedicated rate rider applying to every '
                                              'large data center, so that data centers '
                                              'pay the full cost of the generation, '
                                              'transmission and distribution built to '
                                              'serve them. The letter asks NARUC to '
                                              'take the issue up at its November '
                                              'annual meeting and report back.',
                                      'date': '2026-09-30',
                                      'source': 'https://www.lujan.senate.gov/newsroom/press-releases/lujan-heinrich-kelly-cantwell-call-on-states-to-stop-data-centers-from-passing-rising-costs-on-to-ratepayers/',
                                      'source_name': 'Sen. Luján press release',
                                      'kind': 'action'},
                                     {'what': 'Voted Nay on the motion to invoke '
                                              'cloture on the motion to proceed to '
                                              'H.R. 9340 (the House-passed Ratepayer '
                                              'Protection Act). Cloture was rejected '
                                              '57-43, with 60 votes required.',
                                      'date': '2026-09-30',
                                      'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.xml',
                                      'source_name': 'U.S. Senate Roll Call Vote 254 '
                                                     '(119th Congress, 2nd Session)',
                                      'kind': 'action'},
                                     {'what': 'Introduced, with Sen. Katie Britt, the '
                                              'Advancing Water Reuse Act, a 30 percent '
                                              'investment tax credit for water reuse '
                                              'projects, covering onsite water '
                                              'recycling systems at manufacturing, '
                                              'food processing and other industrial '
                                              'entities, including data center '
                                              'facilities. The 2026 Congressional '
                                              'Record Index lists it as S. 4506, '
                                              'introduced by Luján.',
                                      'date': '2026-05-13',
                                      'source': 'https://www.lujan.senate.gov/newsroom/press-releases/lujan-britt-unveil-bipartisan-bill-to-boost-industrial-water-reuse-protect-community-drinking-water-and-meet-public-and-private-demand-for-freshwater/',
                                      'source_name': 'Sen. Luján press release',
                                      'kind': 'action'}],
                           'as_of': '2026-11-28'},
 ('OH', 'Sherrod Brown'): {'lean': 'guardrails',
                           'summary': "Brown made his opponent's record on data-center "
                                      'tax breaks a central campaign theme, said '
                                      'Ohioans should not be forced to subsidize '
                                      'data-center costs, and said siting should be a '
                                      'local decision. He called for ending the data '
                                      'center tax breaks and dismissed the Ratepayer '
                                      'Protection Act as "toothless". He did not back '
                                      'a moratorium, and told News 5 Cleveland he had '
                                      'supported one data center around 2015-2016. The '
                                      'record is campaign statements: he held no '
                                      'office in 2025-2026.',
                           'background': 'U.S. Senator from Ohio 2007-2025; U.S. '
                                         'Representative 1993-2007. Held no office in '
                                         '2025-2026, so the recent record is campaign '
                                         'statements.',
                           'items': [{'what': 'At a Cleveland rally, dismissed '
                                              "Husted's Ratepayer Protection Act as "
                                              "'toothless', called Husted 'the face of "
                                              "data centers', and said Husted gave "
                                              'data-center corporations $2.5 billion '
                                              'in tax dollars while utility bills '
                                              "rose. The figures are Brown's claims as "
                                              'quoted.',
                                      'date': '2026-10-25',
                                      'source': 'https://ohiocapitaljournal.com/2026/10/25/former-president-obama-rallies-with-ohio-democratic-ticket-in-cleveland/',
                                      'source_name': 'Ohio Capital Journal',
                                      'kind': 'statement'},
                                     {'what': 'Told News 5 Cleveland, two weeks before '
                                              'the election, that his position is to '
                                              'take away data-center tax subsidies, '
                                              'let local communities give input and '
                                              'keep data centers out where they are '
                                              'not wanted, and never have electric '
                                              "ratepayers pay for data centers' "
                                              'electricity. In the same story, '
                                              "answering Husted's charge of hypocrisy, "
                                              'he said he had supported one data '
                                              'center around 2015-2016, when there '
                                              'were no big tax subsidies and the local '
                                              'communities knew about it.',
                                      'date': '2026-10-21',
                                      'source': 'https://www.news5cleveland.com/news/politics/ohio-politics/ohio-u-s-senate-candidates-make-their-case-to-voters-weary-of-data-centers',
                                      'source_name': 'News 5 Cleveland (WEWS)',
                                      'kind': 'statement'},
                                     {'what': 'Newsweek quotes a Brown post on X dated '
                                              "September 19 saying he shares Ohioans' "
                                              'worry about the number of data centers '
                                              'entering the state, and a campaign '
                                              "spokesperson's statement that Ohioans "
                                              'should get to decide if data centers '
                                              'are built in their communities and '
                                              'should never be forced to subsidize big '
                                              "corporations' electricity costs. The "
                                              'article is about the Senate blocking '
                                              "Husted's bill (Sept. 30, 2026); the "
                                              'page shows no year for the post, so '
                                              '2026 is inferred from context.',
                                      'date': '2026-09-19',
                                      'source': 'https://newsweek.com/sherrod-browns-ai-data-center-views-as-husteds-bill-blocked-by-democrats-12514153',
                                      'source_name': 'Newsweek',
                                      'kind': 'statement'},
                                     {'what': 'Speaking with reporters in Westerville, '
                                              'listed what he wants on data centers: '
                                              'local input on siting, union labor to '
                                              'build them, no over-the-top tax breaks '
                                              'for big tech companies, and Ohioans not '
                                              'paying the electric bills of '
                                              'out-of-state corporations. He also said '
                                              'reasonable regulation is needed on '
                                              'companies that come in.',
                                      'date': '2026-09-18',
                                      'source': 'https://abc6onyourside.com/news/local/brown-targets-data-center-tax-breaks-and-rising-electric-bills-in-ohio-husted-politics-election-midterm-senate',
                                      'source_name': 'WSYX ABC 6 Columbus',
                                      'kind': 'statement'},
                                     {'what': 'In an interview reported by Ohio '
                                              'Capital Journal, said Husted had “been '
                                              'the front guy on all these data '
                                              'centers, 200 in Ohio, getting huge '
                                              'over-the-top tax breaks, and raising '
                                              'utility rates,” and that no one should '
                                              'pay higher electric rates because '
                                              'out-of-state corporations put data '
                                              'centers in Ohio.',
                                      'date': '2026-08-21',
                                      'source': 'https://ohiocapitaljournal.com/2026/08/21/leaked-memo-about-data-centers-shows-gop-worried-about-ohios-u-s-senate-race/',
                                      'source_name': 'Ohio Capital Journal',
                                      'kind': 'statement'},
                                     {'what': 'Ohio Capital Journal reports that Brown '
                                              "attacked Husted's support for "
                                              'data-center tax breaks in two July ads '
                                              'and, in a third, promised to make data '
                                              'centers pay the full cost of their '
                                              'electricity use; that he has called to '
                                              'end the data center tax breaks and says '
                                              'local communities should have a say on '
                                              'construction; and that he has not '
                                              'embraced a halt in construction.',
                                      'date': '2026-08-10',
                                      'source': 'https://ohiocapitaljournal.com/2026/08/10/ohio-u-s-senate-candidates-offer-contrasting-visions-for-data-centers/',
                                      'source_name': 'Ohio Capital Journal',
                                      'kind': 'statement'},
                                     {'what': 'In a statement to Ohio Capital Journal, '
                                              'said Ohioans should not be forced to '
                                              'subsidize data-center costs and that '
                                              'Ohioans should get to decide whether '
                                              'data centers are built in their '
                                              'community.',
                                      'date': '2026-08-10',
                                      'source': 'https://ohiocapitaljournal.com/2026/08/10/ohio-u-s-senate-candidates-offer-contrasting-visions-for-data-centers/',
                                      'source_name': 'Ohio Capital Journal',
                                      'kind': 'statement'},
                                     {'what': 'Ohio Capital Journal reports that '
                                              'Brown, in a June Spectrum News '
                                              'interview, said data center operators '
                                              'have to process water properly and '
                                              'recirculate it; and that as a '
                                              'first-term senator in 2010 he secured '
                                              '$2.8 million for a Dayton-area research '
                                              'center developing water cooling '
                                              'technology for large data centers.',
                                      'date': '2026-08-10',
                                      'source': 'https://ohiocapitaljournal.com/2026/08/10/ohio-u-s-senate-candidates-offer-contrasting-visions-for-data-centers/',
                                      'source_name': 'Ohio Capital Journal',
                                      'kind': 'statement'},
                                     {'what': 'Signal Cleveland reports that in a '
                                              'Spectrum News interview about two weeks '
                                              'before his first anti-data-center ad, '
                                              'Brown said the state should eliminate '
                                              'the data-center tax breaks, and that '
                                              'his campaign told Signal that Ohioans, '
                                              'not Husted, should decide whether data '
                                              'centers are built in their community. '
                                              'The story notes this put him at odds '
                                              'with building-trades unions that back '
                                              'the industry. (Gives the direct quote '
                                              "behind the 'has called to end the tax "
                                              "breaks' paraphrase already on file.)",
                                      'date': '2026-07-09',
                                      'source': 'https://signalcleveland.org/hes-trying-to-win-this-election-sherrod-brown-attacks-jon-husted-support-of-data-centers-in-break-with-labor-construction-unions/',
                                      'source_name': 'Signal Cleveland',
                                      'kind': 'statement'},
                                     {'what': 'At a campaign stop in Ironton, asked '
                                              'about the federal plan for a '
                                              '10-gigawatt data center near Piketon, '
                                              'said people locally were not told, that '
                                              'residents of Lawrence, Scioto and Pike '
                                              'counties should make the decision, and '
                                              'that people should not pay higher '
                                              'electric bills because of it.',
                                      'date': '2026-07-07',
                                      'source': 'https://irontontribune.com/2026/07/11/brown-locals-should-decide-on-data-centers/',
                                      'source_name': 'The Ironton Tribune',
                                      'kind': 'statement'}],
                           'as_of': '2026-11-28'},
 ('OK', 'Kevin Hern'): {'lean': 'consensus',
                        'summary': "The only thing found on the record is Hern's Yea "
                                   'vote for the Ratepayer Protection Act, which '
                                   'passed the House 417-3. No statement by Hern about '
                                   'data centers, large-load electricity costs or '
                                   'siting was located in Oklahoma press or on his '
                                   'House site.',
                        'background': "U.S. Representative for Oklahoma's 1st District "
                                      'since 2018.',
                        'items': [{'what': 'Voted Yea on H.R. 9340, the Ratepayer '
                                           'Protection Act, on the motion to suspend '
                                           'the rules and pass, as amended. The House '
                                           'Clerk records 417 yeas, 3 nays, 12 not '
                                           'voting (Roll Call 312).',
                                   'date': '2026-09-16',
                                   'source': 'https://clerk.house.gov/evs/2026/roll312.xml',
                                   'source_name': 'Clerk of the U.S. House, Roll Call '
                                                  '312',
                                   'kind': 'action'}],
                        'as_of': '2026-11-28'},
 ('OR', 'Jeff Merkley'): {'lean': 'guardrails',
                          'summary': 'Merkley voted against the Senate permitting bill '
                                     'in November 2026, saying it deregulated the '
                                     'buildout of data centers, allowed them on public '
                                     'lands and removed tools states and localities '
                                     'use to fight new data centers, while also saying '
                                     'data centers should pay their fair share for the '
                                     'resources they use. He co-signed letters to '
                                     'Interior Secretary Burgum on data centers on '
                                     "public lands and to Oregon's data center "
                                     'advisory committee, and voted against advancing '
                                     'the House-passed Ratepayer Protection Act. He '
                                     'says he will chair the Senate Environment and '
                                     'Public Works Committee in 2027.',
                          'background': 'U.S. Senator from Oregon since 2009.',
                          'items': [{'what': 'In a statement on Senate passage of the '
                                             'permitting bill, said he could not '
                                             'support it and listed among his concerns '
                                             'that it deregulated the buildout of data '
                                             'centers and allowed data centers to be '
                                             'built on public lands; said Senate '
                                             'Republicans blocked votes on amendments '
                                             'addressing these issues; and said that '
                                             'as incoming EPW chairman he wants '
                                             'permitting legislation to go through '
                                             'committee in 2027.',
                                     'date': '2026-11-20',
                                     'source': 'https://www.merkley.senate.gov/merkley-statement-on-senate-passage-of-permitting-legislation/',
                                     'source_name': 'Sen. Merkley press release',
                                     'kind': 'statement'},
                                    {'what': 'Voted Nay on Senate passage of H.R. 2347 '
                                             'as amended (the vehicle for the '
                                             'permitting bill), which passed 62-33.',
                                     'date': '2026-11-19',
                                     'source': 'https://www.govinfo.gov/content/pkg/CREC-2026-11-19/html/CREC-2026-11-19-pt1-PgS5797-2.htm',
                                     'source_name': 'Congressional Record, Nov. 19, '
                                                    '2026 (S5797-S5804)',
                                     'kind': 'action'},
                                    {'what': 'On the Senate floor, objected to the '
                                             'unanimous-consent agreement on amendment '
                                             'votes for the permitting bill. He said '
                                             "the bill 'puts the pedal to the floor on "
                                             "data centers', described his amendment "
                                             'to stop jet-engine generators powering '
                                             'data centers from being exempted from '
                                             'clean air and noise provisions, and '
                                             "backed Sen. Wyden's amendment to keep "
                                             'data centers off public lands; his '
                                             'request to add those amendments was '
                                             'objected to.',
                                     'date': '2026-11-19',
                                     'source': 'https://www.govinfo.gov/content/pkg/CREC-2026-11-19/html/CREC-2026-11-19-pt1-PgS5797-2.htm',
                                     'source_name': 'Congressional Record, Nov. 19, '
                                                    '2026 (S5797-S5804)',
                                     'kind': 'action'},
                                    {'what': 'In a statement before the first '
                                             'procedural vote on the permitting bill, '
                                             'said data centers should pay their fair '
                                             'share for the resources they use and '
                                             'praised those portions of the bill, but '
                                             'said he would vote against it because it '
                                             'could make it easier to build data '
                                             'centers powered by behind-the-meter '
                                             'natural gas plants and eliminates tools '
                                             'states and localities use to fight new '
                                             'data centers.',
                                     'date': '2026-11-09',
                                     'source': 'https://www.merkley.senate.gov/sen-merkley-statement-on-senate-permitting-legislation/',
                                     'source_name': 'Sen. Merkley press release',
                                     'kind': 'statement'},
                                    {'what': 'With Sens. Wyden and Padilla, wrote to '
                                             'Interior Secretary Doug Burgum demanding '
                                             'answers about his role in helping broker '
                                             'deals to build data centers on public '
                                             'lands, after the department released '
                                             'calendars showing meetings with data '
                                             'center developers.',
                                     'date': '2026-10-29',
                                     'source': 'https://www.merkley.senate.gov/wyden-padilla-merkley-demand-answers-over-sec-burgums-role-in-hijacking-public-lands-for-data-centers/',
                                     'source_name': 'Sen. Merkley press release',
                                     'kind': 'action'},
                                    {'what': 'Voted Nay on the motion to invoke '
                                             'cloture on the motion to proceed to H.R. '
                                             '9340 (the House-passed Ratepayer '
                                             'Protection Act). Cloture was rejected '
                                             '57-43, with 60 votes required.',
                                     'date': '2026-09-30',
                                     'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.xml',
                                     'source_name': 'U.S. Senate Roll Call Vote 254 '
                                                    '(119th Congress, 2nd Session)',
                                     'kind': 'action'},
                                    {'what': "With Sen. Wyden, wrote to Oregon's state "
                                             'data center advisory committee asking it '
                                             'to consider constituent concerns '
                                             'including rising energy demand, higher '
                                             'electricity costs for consumers, water '
                                             'quality and quantity, steam and noise '
                                             'from cooling, rezoning of productive '
                                             'agricultural land, tribal rights and '
                                             'consultation, and transparency.',
                                     'date': '2026-07-02',
                                     'source': 'https://www.merkley.senate.gov/wyden-merkley-ask-state-data-center-advisory-committee-to-consider-multiple-issues-raised-by-oregonians/',
                                     'source_name': 'Sen. Merkley press release',
                                     'kind': 'action'}],
                          'as_of': '2026-11-28'},
 ('RI', 'Jack Reed'): {'lean': 'guardrails',
                       'summary': 'Reed signed a January 2026 letter from six New '
                                  'England senators asking ISO New England how it will '
                                  'protect residential ratepayers from '
                                  'data-center-driven price increases. He voted '
                                  'against advancing the House-passed Ratepayer '
                                  'Protection Act in September 2026 and voted for the '
                                  'Senate permitting bill in November 2026. No '
                                  'statement by Reed explaining either vote was found.',
                       'background': 'U.S. Senator from Rhode Island since 1997.',
                       'items': [{'what': 'Voted Yea on Senate passage of H.R. 2347 as '
                                          "amended, the vehicle for the Senate's "
                                          'bipartisan permitting bill, which passed '
                                          '62-33. In the floor debate on the same '
                                          'pages, co-author Sen. Whitehouse said the '
                                          'bill would force data centers to pay for '
                                          'the costs they impose on the grid, while '
                                          'Sen. Merkley said it puts the pedal to the '
                                          'floor on data centers. The pages record no '
                                          'statement by Reed.',
                                  'date': '2026-11-19',
                                  'source': 'https://www.govinfo.gov/content/pkg/CREC-2026-11-19/html/CREC-2026-11-19-pt1-PgS5797-2.htm',
                                  'source_name': 'Congressional Record, Nov. 19, 2026 '
                                                 '(S5797-S5804)',
                                  'kind': 'action'},
                                 {'what': 'Voted Nay on the motion to invoke cloture '
                                          'on the motion to proceed to H.R. 9340 (the '
                                          'House-passed Ratepayer Protection Act). '
                                          'Cloture was rejected 57-43, with 60 votes '
                                          'required.',
                                  'date': '2026-09-30',
                                  'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.xml',
                                  'source_name': 'U.S. Senate Roll Call Vote 254 '
                                                 '(119th Congress, 2nd Session)',
                                  'kind': 'action'},
                                 {'what': 'With Sens. Whitehouse, Welch, Shaheen, '
                                          'Blumenthal and Markey, wrote to ISO New '
                                          'England president and CEO Vamsi Chadalavada '
                                          'asking what strategies the grid operator '
                                          'will use to protect residential ratepayers '
                                          'from data-center-driven price increases. '
                                          'The letter says the senators believe tech '
                                          'companies, not American families, should be '
                                          'required to foot the bill for their load.',
                                  'date': '2026-01-28',
                                  'source': 'https://www.reed.senate.gov/news/releases/reed-and-whitehouse-seek-answers-about-how-new-regional-data-centers-could-drive-up-energy-health_environmental-costs-for-consumers',
                                  'source_name': 'Sen. Reed press release',
                                  'kind': 'action'}],
                       'as_of': '2026-11-28'},
 ('SC', 'Annie Andrews'): {'lean': 'guardrails',
                           'summary': 'Campaigned on a two-year moratorium on '
                                      'data-center development, with rules written '
                                      'during the pause so that data centers pay for '
                                      'themselves and customer rates do not rise, and '
                                      "on a 'return to real local control'. After "
                                      "winning she was quoted saying 'If a community "
                                      "says no, the answer is no.' She has held no "
                                      'elected office, so the record is statements '
                                      'only.',
                           'background': 'Pediatrician; has never held elected office, '
                                         'so the record is statements only.',
                           'items': [{'what': "In WSOC-TV's post-election report, "
                                              "quoted saying 'If a community says no, "
                                              "the answer is no,' and that she has "
                                              'called for a two-year moratorium on '
                                              'data-center development to empower '
                                              'local communities and local elected '
                                              'officials to negotiate with the '
                                              'companies.',
                                      'date': '2026-11-04',
                                      'source': 'https://www.wsoctv.com/news/local/data-center-debate-continues-south-carolina-after-andrews-victory/RMMHTFFSIBCJJCWXEIMGKWMPWI/',
                                      'source_name': 'WSOC-TV',
                                      'kind': 'statement'},
                                     {'what': 'Publicly criticised outside spending '
                                              'for her opponent by what she described '
                                              'as data-center-linked super PACs, '
                                              "saying Graham 'has repeatedly said we "
                                              'have to have data centers and we need '
                                              "to build data centers here.' The dollar "
                                              "figures in the story are Andrews' own "
                                              'claims as reported by WACH, not '
                                              'independently verified there.',
                                      'date': '2026-10-27',
                                      'source': 'https://abcnews4.com/news/state/dr-annie-andrews-demands-answers-after-report-of-15m-data-center-cash-for-graham',
                                      'source_name': 'WACH / ABC News 4',
                                      'kind': 'statement'},
                                     {'what': 'At the Oct. 11 SC ETV debate, proposed '
                                              'a two-year moratorium; per the '
                                              "Gazette's paraphrase, regulations "
                                              'developed during the pause should '
                                              'ensure data centers pay for themselves '
                                              "so customers' rates do not go up. She "
                                              "said she wants a 'return to real local "
                                              "control' and accused her opponent of "
                                              "wanting to build data centers 'faster "
                                              "and faster.'",
                                      'date': '2026-10-11',
                                      'source': 'https://scdailygazette.com/2026/10/12/social-security-data-centers-and-healthcare-senate-candidates-exchange-jabs-while-talking-policy/',
                                      'source_name': 'SC Daily Gazette',
                                      'kind': 'statement'},
                                     {'what': 'In the same debate, as quoted by WRDW, '
                                              'said data centers are being built in '
                                              "communities' backyards without "
                                              'community input.',
                                      'date': '2026-10-11',
                                      'source': 'https://www.wrdw.com/2026/10/12/sc-senate-candidates-clash-over-data-center-expansion-debate/',
                                      'source_name': 'WRDW',
                                      'kind': 'statement'},
                                     {'what': 'In Walterboro, called for a two-year '
                                              'pause on new data-center projects in '
                                              'South Carolina, saying it would give '
                                              'communities more protection; said of '
                                              'developers and local officials that '
                                              "companies are 'dangling a few carrots, "
                                              'and then the communities are getting '
                                              "steamrolled.' The station reports she "
                                              'argued large data centers get billions '
                                              'in tax breaks while families face high '
                                              'costs (reporter paraphrase).',
                                      'date': '2026-09-28',
                                      'source': 'https://www.live5news.com/2026/09/28/senate-candidate-dr-annie-andrews-calls-moratorium-data-centers/',
                                      'source_name': 'WCSC Live 5 News',
                                      'kind': 'statement'}],
                           'as_of': '2026-11-28'},
 ('SD', 'Mike Rounds'): {'lean': 'mixed',
                         'summary': 'Voted on 2026-09-30 to advance the House-passed '
                                    'Ratepayer Protection Act (H.R. 9340), which '
                                    'failed 57-43. In November 2026 he was the only '
                                    'Republican to vote against the Bipartisan '
                                    'American Affordability and Jobs Act, the '
                                    'permitting bill whose sponsors say it makes data '
                                    'centers pay for grid upgrades; his stated reason '
                                    'was transmission-line siting and landowner '
                                    'rights, not the data-center provisions. KOTA '
                                    'reported him saying data centers should go only '
                                    'where communities welcome them.',
                         'background': 'U.S. Senator from South Dakota since 2015; '
                                       'former governor.',
                         'items': [{'what': 'Voted Nay on Senate passage of H.R. 2347 '
                                            'as amended (the legislative vehicle for '
                                            'the Bipartisan American Affordability and '
                                            'Jobs Act), which passed 62-33. He also '
                                            'voted Nay on the Capito substitute '
                                            'amendment (vote 267, 2026-11-18) and on '
                                            'the cloture votes (257, 264, 268).',
                                    'date': '2026-11-19',
                                    'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00270.htm',
                                    'source_name': 'U.S. Senate roll call vote 270',
                                    'kind': 'action'},
                                   {'what': 'Was the lone Republican to vote against '
                                            'advancing the Bipartisan American '
                                            'Affordability and Jobs Act. His statement '
                                            'objected that the bill would transfer '
                                            'contested transmission-line siting cases '
                                            'to FERC if not resolved within 12 months, '
                                            "'giving a weighted advantage to the "
                                            "developer.' The article does not mention "
                                            'data centers.',
                                    'date': '2026-11-10',
                                    'source': 'https://www.dakotanewsnow.com/2026/11/11/rounds-lone-republican-oppose-permitting-bill/',
                                    'source_name': 'Dakota News Now',
                                    'kind': 'action'},
                                   {'what': 'Voted Yea on cloture on the motion to '
                                            'proceed to H.R. 9340, described on the '
                                            'Senate vote page as a bill to establish a '
                                            'federal standard on recovering the full '
                                            'incremental costs of upgrades that serve '
                                            'large-load customers. The motion failed '
                                            '57-43.',
                                    'date': '2026-09-30',
                                    'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.htm',
                                    'source_name': 'U.S. Senate roll call vote 254',
                                    'kind': 'action'},
                                   {'what': 'KOTA reported (paraphrase) that Rounds '
                                            'says data centers should be built only '
                                            'where local communities welcome them and, '
                                            'near term, through extensive dialogue '
                                            'with residents. His direct quotes on the '
                                            'page are about space: he said he believes '
                                            'the vast majority of new data centers '
                                            'will probably be based in space '
                                            'long-term.',
                                    'date': '2026-09-05',
                                    'source': 'https://www.kotatv.com/2026/09/05/rapid-city-data-center-backlash-epa-rules-meta-cash-space-tech/',
                                    'source_name': 'KOTA Territory TV',
                                    'kind': 'statement'}],
                         'as_of': '2026-11-28'},
 ('TN', 'Bill Hagerty'): {'lean': 'mixed',
                          'summary': 'Has promoted Tennessee as a home for data '
                                     'centers, AI and the nuclear power to run them. '
                                     'In August 2026 he told WBIR data centers will '
                                     "'have to make the investment' in capacity and "
                                     'the grid. He voted to advance the Ratepayer '
                                     'Protection Act (failed 57-43) and voted for '
                                     'Senate passage of the Bipartisan American '
                                     'Affordability and Jobs Act, the permitting bill '
                                     'whose sponsors say it makes data centers pay for '
                                     'grid upgrades.',
                          'background': 'U.S. Senator from Tennessee since 2021.',
                          'items': [{'what': 'Voted Yea on Senate passage of H.R. 2347 '
                                             'as amended (the legislative vehicle for '
                                             'the Bipartisan American Affordability '
                                             'and Jobs Act), which passed 62-33; also '
                                             'Yea on the Capito substitute amendment '
                                             '(vote 267) and the related cloture votes '
                                             '(257, 264, 268).',
                                     'date': '2026-11-19',
                                     'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00270.htm',
                                     'source_name': 'U.S. Senate roll call vote 270',
                                     'kind': 'action'},
                                    {'what': 'Voted Yea on cloture on the motion to '
                                             'proceed to H.R. 9340, described on the '
                                             'Senate vote page as a bill to establish '
                                             'a federal standard on recovering the '
                                             'full incremental costs of upgrades that '
                                             'serve large-load customers. The motion '
                                             'failed 57-43.',
                                     'date': '2026-09-30',
                                     'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.htm',
                                     'source_name': 'U.S. Senate roll call vote 254',
                                     'kind': 'action'},
                                    {'what': 'Asked by WBIR in Knoxville about AI data '
                                             'centers (which the station notes several '
                                             'East Tennessee governments have placed '
                                             "12-month moratoriums on), said 'we made "
                                             'it very clear to the data centers that '
                                             "they're going to have to make the "
                                             'investment, not only in our capacity but '
                                             "in our grid and support all of that.'",
                                     'date': '2026-08-11',
                                     'source': 'https://www.yahoo.com/news/politics/articles/sen-bill-hagerty-discusses-economic-194530943.html',
                                     'source_name': 'WBIR 10News (via Yahoo News)',
                                     'kind': 'statement'},
                                    {'what': "Quoted in Kairos Power's announcement of "
                                             'a deal under which its Hermes 2 plant in '
                                             'Oak Ridge supplies up to 50 MW to the '
                                             'TVA grid that powers Google data centers '
                                             'in Tennessee and Alabama; Hagerty said '
                                             'he was pleased to see the three join '
                                             'forces to deliver nuclear energy in '
                                             'Tennessee. His quote does not itself '
                                             'mention data centers.',
                                     'date': '2025-08-18',
                                     'source': 'https://www.kairospower.com/updates/google-kairos-power-tva-collaborate-to-meet-americas-growing-energy-needs',
                                     'source_name': 'Kairos Power news release',
                                     'kind': 'statement'},
                                    {'what': 'In a Bitcoin Magazine interview, said '
                                             "Tennessee can become 'the energy hub of "
                                             "America' and that the state will see "
                                             'more mining operations, data centers and '
                                             'AI opportunities; the article '
                                             'paraphrases him as discussing building '
                                             'nuclear facilities to power mining and '
                                             "AI processing and citing xAI's Memphis "
                                             'operation.',
                                     'date': '2025-06-16',
                                     'source': 'https://bitcoinmagazine.com/politics/senator-hagertys-vision-beyond-the-genius-act-make-tennessee-a-hub-for-bitcoin-mining',
                                     'source_name': 'Bitcoin Magazine',
                                     'kind': 'statement'}],
                          'as_of': '2026-11-28'},
 ('TX', 'James Talarico'): {'lean': 'guardrails',
                            'summary': "Ran on a 'Hold Data Centers Accountable' plan: "
                                       'federal minimum standards, repeal of the Texas '
                                       'data-center sales-tax exemption, large energy '
                                       'users paying their own infrastructure and '
                                       'interconnection costs, closed-loop water '
                                       'systems, and local authority to approve or '
                                       'reject projects. He declined to back a '
                                       'moratorium. As a Texas House member he voted '
                                       'yes on second reading of SB 6 (2025), the '
                                       'large-load interconnection and cost bill, and '
                                       'was recorded absent on final passage.',
                            'background': 'Texas House member from the Austin area '
                                          'since 2018.',
                            'items': [{'what': 'FOX 4 summarised his plan as: repeal '
                                               'tax incentives for data centers, more '
                                               "local say, an 'AI Dividend' giving "
                                               'every American a share of AI company '
                                               'profits, AI companies paying for their '
                                               'own electricity infrastructure, and '
                                               'accountability for water pollution '
                                               'plus paying for their own water '
                                               'infrastructure (all reporter '
                                               'paraphrase of the plan).',
                                       'date': '2026-09-30',
                                       'source': 'https://www.fox4news.com/election/james-talarcio-ken-paxton-texas-data-center-plan',
                                       'source_name': 'FOX 4 Dallas-Fort Worth',
                                       'kind': 'statement'},
                                      {'what': "Responding to Ken Paxton's data-center "
                                               'platform, said Paxton had taken '
                                               'data-center industry money, voted for '
                                               "the tax break, and 'refused to use his "
                                               'power as attorney general to respond '
                                               "to Texans' requests to block data "
                                               'center development in their '
                                               "communities' (a reference, per the "
                                               "Tribune, to Hood County's pending "
                                               'request for an opinion on a county '
                                               'moratorium). The Tribune describes '
                                               "Talarico's plan as going further than "
                                               "Paxton's by giving local officials "
                                               'approval power, and also reports that '
                                               'Reid Hoffman gave $10 million to a '
                                               'super PAC supporting Talarico.',
                                       'date': '2026-08-24',
                                       'source': 'https://www.texastribune.org/2026/08/24/ken-paxton-james-talarico-data-centers-senate-texas/',
                                       'source_name': 'Texas Tribune',
                                       'kind': 'statement'},
                                      {'what': 'At a San Antonio stop, said data '
                                               'centers that will not create good '
                                               "union jobs 'shouldn't be in our "
                                               "communities'; the paper reports "
                                               '(paraphrase) that he told reporters he '
                                               'does not support a total moratorium on '
                                               'new data-center construction and '
                                               'prefers regulation.',
                                       'date': '2026-07-31',
                                       'source': 'https://www.sacurrent.com/news/politics-and-elections/u-s-senate-candidate-james-talarico-rejects-data-center-moratorium-calls-for-stronger-regulations/',
                                       'source_name': 'San Antonio Current',
                                       'kind': 'statement'},
                                      {'what': 'Released a data-center plan at an '
                                               'Austin news conference: minimum '
                                               'federal requirements for grid, '
                                               'environment, jobs and transparency; '
                                               'repeal of the state data-center '
                                               'sales-tax exemption; large energy '
                                               'users pay their own infrastructure and '
                                               'grid interconnection costs; '
                                               'closed-loop water systems; local '
                                               'authority to approve and reject '
                                               'projects; release of facility-level '
                                               'tax-break records. He did not call for '
                                               "a moratorium. He said: 'Data centers "
                                               'are jacking up utility bills across '
                                               "the state of Texas.'",
                                       'date': '2026-07-22',
                                       'source': 'https://www.texastribune.org/2026/07/22/texas-james-talarico-data-centers-regulation-senate-2026/',
                                       'source_name': 'Texas Tribune',
                                       'kind': 'statement'},
                                      {'what': 'Texas House Journal, third reading '
                                               '(final House passage) of SB 6: '
                                               'Talarico is listed as Absent on Record '
                                               '3643, which passed the bill 103-25. No '
                                               'statement of vote from him on that '
                                               'record appears in the journal text '
                                               'read.',
                                       'date': '2025-05-27',
                                       'source': 'https://journals.house.texas.gov/HJRNL/89R/HTML/89RDAY75FINAL.HTM',
                                       'source_name': 'Texas House Journal, 89th '
                                                      'Legislature, Day 75',
                                       'kind': 'action'},
                                      {'what': 'Texas House Journal, second reading of '
                                               "CSSB 6 ('relating to the planning for, "
                                               'interconnection and operation of, and '
                                               'costs related to providing service for '
                                               "certain electrical loads'): Talarico "
                                               'is listed among the Yeas on Record '
                                               '3558, which passed the bill to third '
                                               'reading 117-24.',
                                       'date': '2025-05-26',
                                       'source': 'https://journals.house.texas.gov/HJRNL/89R/HTML/89RDAY74FINAL.HTM',
                                       'source_name': 'Texas House Journal, 89th '
                                                      'Legislature, Day 74',
                                       'kind': 'action'},
                                      {'what': 'At a CNN town hall, per Newsweek, said '
                                               "he had rolled out a plan to 'crack "
                                               'down on these giant data center '
                                               "companies': 'force them to pay for "
                                               'their own energy instead of jacking up '
                                               "our utility bills,' 'force them to "
                                               "recycle their water,' and 'force them "
                                               'to get the consent of the people who '
                                               'live in these communities before they '
                                               "start building.'",
                                       'date': '',
                                       'source': 'https://newsweek.com/james-talarico-targets-data-centers-over-texas-energy-bills-water-crisis-12571822',
                                       'source_name': 'Newsweek',
                                       'kind': 'statement'}],
                            'as_of': '2026-11-28'},
 ('VA', 'Mark Warner'): {'lean': 'guardrails',
                         'summary': 'Cosponsored the Power for the People Act '
                                    '(data-center rate classes, FERC rule on '
                                    'transmission-upgrade costs) and introduced his '
                                    'own Data Center Tax Accountability and Disclosure '
                                    'Act (S.5054) (public disclosure of energy, water, '
                                    'emissions and backup generation; bonus '
                                    'depreciation conditioned on efficiency '
                                    'standards). He called a data-center moratorium '
                                    "'idiocy' in March 2026, voted against advancing "
                                    'the House-passed Ratepayer Protection Act, voted '
                                    'for the Senate permitting bill (BAAJA), and after '
                                    're-election called for a federal baseline '
                                    'requiring data centers to bring their own power '
                                    'and water.',
                         'background': 'U.S. Senator from Virginia since 2009; former '
                                       'governor.',
                         'items': [{'what': 'Voted Yea on Senate passage of H.R. 2347 '
                                            'as amended (the legislative vehicle for '
                                            'the Bipartisan American Affordability and '
                                            'Jobs Act, the permitting bill whose '
                                            'sponsors say it makes data centers pay '
                                            'for the grid upgrades they cause), which '
                                            'passed 62-33; also Yea on the Capito '
                                            'substitute (vote 267) and the related '
                                            'cloture votes (257, 264, 268).',
                                    'date': '2026-11-19',
                                    'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00270.htm',
                                    'source_name': 'U.S. Senate roll call vote 270',
                                    'kind': 'action'},
                                   {'what': 'In a post-election interview with WJLA, '
                                            'called for a federal baseline under which '
                                            'a data center of any size must bring its '
                                            'own power and its own water.',
                                    'date': '2026-11-04',
                                    'source': 'https://wjla.com/news/local/data-center-virginia-power-resources-pjm-hashmi-stricter-regulations-suhas-warner-vindman-reelection-campaigns-infrastructure-controversy',
                                    'source_name': 'WJLA (ABC7 Washington)',
                                    'kind': 'statement'},
                                   {'what': 'Voted Nay on cloture on the motion to '
                                            'proceed to H.R. 9340 (the House-passed '
                                            'Ratepayer Protection Act, described on '
                                            'the Senate page as establishing a federal '
                                            'standard on recovering the full '
                                            'incremental costs of upgrades serving '
                                            'large-load customers). The motion failed '
                                            '57-43. Newsweek reported (paraphrase, no '
                                            'direct quote) that he said the bill '
                                            'merely directs states to consider a '
                                            'standard and that Congress needs broader '
                                            'requirements on electricity costs, water, '
                                            'transparency and community impacts.',
                                    'date': '2026-09-30',
                                    'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.htm',
                                    'source_name': 'U.S. Senate roll call vote 254',
                                    'kind': 'action'},
                                   {'what': 'Submitted Senate Amendment 6837 to H.R. '
                                            '9340 (the Ratepayer Protection Act), '
                                            'which would have added a section '
                                            'exempting AI data centers from bonus '
                                            'depreciation (unless LEED Gold/Platinum '
                                            'or an equivalent standard) and a section '
                                            'requiring disclosures from data centers '
                                            'with power demand of 25 megawatts or '
                                            'more. The amendment was ordered to lie on '
                                            'the table; congress.gov lists no further '
                                            'action.',
                                    'date': '2026-09-28',
                                    'source': 'https://www.congress.gov/amendment/119th-congress/senate-amendment/6837/text',
                                    'source_name': 'Congress.gov (S.Amdt.6837, '
                                                   'Congressional Record S5078)',
                                    'kind': 'action'},
                                   {'what': 'WHRO reported that Warner and Rep. Suhas '
                                            'Subramanyam have introduced similar bills '
                                            'requiring data centers to disclose energy '
                                            'and water use, emissions and backup '
                                            "generation; quoted Warner's statement "
                                            'that big tech companies, not residents, '
                                            'must pay for the energy data centers use.',
                                    'date': '2026-09-16',
                                    'source': 'https://www.whro.org/virginia-government/2026-09-16/virginias-federal-lawmakers-lock-in-on-regulating-data-centers',
                                    'source_name': 'WHRO Public Media',
                                    'kind': 'statement'},
                                   {'what': "Said local governments' deals with data "
                                            'centers should be public before any '
                                            "benefits are granted: 'all the "
                                            'non-disclosure agreements need to be '
                                            'disclosed so the community can make the '
                                            "judgment.' The article also reports his "
                                            'proposal would require data centers not '
                                            "to add to consumers' electric bills, use "
                                            'clean power including clean backup, meet '
                                            'water-use standards and keep setbacks '
                                            'from residential neighborhoods '
                                            "(reporter's description).",
                                    'date': '2026-07-23',
                                    'source': 'https://www.warner.senate.gov/?p=36998',
                                    'source_name': 'The Alexandria Brief (reposted on '
                                                   'warner.senate.gov)',
                                    'kind': 'statement'},
                                   {'what': 'Announced he is introducing the Data '
                                            'Center Tax Accountability and Disclosure '
                                            'Act: large AI data centers would publicly '
                                            'disclose energy and water consumption, '
                                            'emissions, backup generation and other '
                                            'operational impacts, and federal bonus '
                                            'depreciation would be conditioned on '
                                            'meeting efficiency and sustainability '
                                            'standards. The release says the bill is '
                                            'supported by the Chesapeake Bay '
                                            'Foundation, the Sierra Club and the '
                                            'Virginia League of Conservation Voters. '
                                            'No bill number is given on the page.',
                                    'date': '2026-07-21',
                                    'source': 'https://www.warner.senate.gov/newsroom/press-releases/warner-rolls-out-comprehensive-ai-legislative-agenda-focused-on-responsible-innovation-workers-and-national-security/',
                                    'source_name': 'Sen. Warner press release',
                                    'kind': 'action'},
                                   {'what': 'Congress.gov lists Warner as sponsor of '
                                            'S.5054, the Data Center Tax '
                                            'Accountability and Disclosure Act of '
                                            '2026, introduced 2026-07-21 and referred '
                                            'to the Senate Finance Committee (1 '
                                            'cosponsor). The same listing shows '
                                            'S.3682, the Power for the People Act of '
                                            '2026, as sponsored by Sen. Van Hollen '
                                            '(introduced 2026-01-15), consistent with '
                                            'Warner being a cosponsor rather than the '
                                            'sponsor.',
                                    'date': '2026-07-21',
                                    'source': 'https://www.congress.gov/member/mark-warner/W000805',
                                    'source_name': 'Congress.gov member page (filtered '
                                                   'to 119th Congress, "data centers")',
                                    'kind': 'action'},
                                   {'what': 'Cosponsored the Power for the People Act '
                                            'with Sens. Van Hollen, Durbin, '
                                            'Blumenthal, Booker, Duckworth, Smith, '
                                            'Welch and Alsobrooks. Per his office the '
                                            'bill directs states to evaluate new rate '
                                            'classes for data centers, directs FERC to '
                                            'issue a rule on data centers paying for '
                                            'transmission upgrades, sets up an '
                                            'interconnection system rewarding data '
                                            'centers that bring their own new '
                                            'generation, use clean energy and pay '
                                            'prevailing wages, and funds better load '
                                            'forecasting.',
                                    'date': '2026-06-02',
                                    'source': 'https://www.warner.senate.gov/newsroom/press-releases/warner-sponsors-bill-to-ensure-virginians-arent-stuck-footing-the-bill-for-big-data-centers/',
                                    'source_name': 'Sen. Warner press release',
                                    'kind': 'action'},
                                   {'what': 'At an Axios AI summit in Washington, said '
                                            'of a proposed data-center construction '
                                            "moratorium: 'That would be idiocy. A data "
                                            "center moratorium simply means China's "
                                            "gonna move quicker.'",
                                    'date': '2026-03-25',
                                    'source': 'https://wjla.com/news/nation-world/senator-mark-warner-proposed-ai-technology-data-center-moratorium-construction-idiocy',
                                    'source_name': 'WJLA (ABC7 Washington)',
                                    'kind': 'statement'}],
                         'as_of': '2026-11-28'},
 ('WV', 'Shelley Moore Capito'): {'lean': 'mixed',
                                  'summary': 'Recruits data centers to West Virginia '
                                             "('We want them') and has said local "
                                             'projects building their own power would '
                                             "not hurt, and might improve, residents' "
                                             'power situation. As Environment and '
                                             'Public Works chairman she led the '
                                             'Bipartisan American Affordability and '
                                             'Jobs Act, the permitting bill the Senate '
                                             'passed 62-33 on 2026-11-19; in floor '
                                             'remarks she said it includes the '
                                             "Ratepayer Protection Act, 'legislation "
                                             'that will make potential data centers '
                                             "pay their own way.' She also voted to "
                                             'advance the stand-alone Ratepayer '
                                             'Protection Act in September.',
                                  'background': 'U.S. Senator from West Virginia since '
                                                '2015.',
                                  'items': [{'what': 'The Senate passed her bill 62-33 '
                                                     '(Capito Yea; the substitute '
                                                     'adopted the day before was '
                                                     'Capito Amdt. No. 6883). WOWK '
                                                     'reported that sponsors said the '
                                                     'bill does not touch data-center '
                                                     'permitting but does require data '
                                                     'centers to pay for the increased '
                                                     'cost of their energy '
                                                     'consumption.',
                                             'date': '2026-11-19',
                                             'source': 'https://www.capito.senate.gov/news/in-the-news/senate-approves-capitos-permitting-reform-bill',
                                             'source_name': 'WOWK (reposted on '
                                                            'capito.senate.gov)',
                                             'kind': 'action'},
                                            {'what': 'In Senate floor remarks as the '
                                                     'Senate advanced BAAJA 73-25, '
                                                     "said the bill's energy section "
                                                     'includes the Ratepayer '
                                                     'Protection Act, legislation that '
                                                     'will make potential data centers '
                                                     'pay their own way instead of '
                                                     'consumers facing higher utility '
                                                     'bills. The release says she '
                                                     'introduced BAAJA with '
                                                     'Whitehouse, Lee and Heinrich.',
                                             'date': '2026-11-10',
                                             'source': 'https://www.capito.senate.gov/news/press-releases/senate-advances-bipartisanamerican-affordability-and-jobs-act',
                                             'source_name': 'Sen. Capito press release',
                                             'kind': 'statement'},
                                            {'what': 'With Sens. Lee, Whitehouse and '
                                                     'Heinrich, released the '
                                                     'substitute amendment to the '
                                                     'Bipartisan American '
                                                     'Affordability and Jobs Act of '
                                                     '2026. In the release Heinrich '
                                                     '(not Capito) says the bill '
                                                     "'makes sure data centers pay for "
                                                     'the energy they use and the grid '
                                                     "upgrades they cause'; Capito's "
                                                     'own quote urges swift passage '
                                                     "'to make life more affordable "
                                                     "for American families.'",
                                             'date': '2026-11-07',
                                             'source': 'https://www.capito.senate.gov/news/press-releases/capito-lee-whitehouse-and-heinrich-release-substitute-amendment-to-bipartisan-american-affordability-and-jobs-act-of-2026',
                                             'source_name': 'Sen. Capito press release',
                                             'kind': 'action'},
                                            {'what': 'Voted Yea on cloture on the '
                                                     'motion to proceed to H.R. 9340, '
                                                     'described on the Senate vote '
                                                     'page as a bill to establish a '
                                                     'federal standard on recovering '
                                                     'the full incremental costs of '
                                                     'upgrades that serve large-load '
                                                     'customers. The motion failed '
                                                     '57-43.',
                                             'date': '2026-09-30',
                                             'source': 'https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00254.htm',
                                             'source_name': 'U.S. Senate roll call '
                                                            'vote 254',
                                             'kind': 'action'},
                                            {'what': 'In a Roll Call story on the '
                                                     'Tucker County data-center fight, '
                                                     'a Capito spokesperson said in a '
                                                     'statement that she has '
                                                     'emphasized local involvement, '
                                                     'responsible stewardship and '
                                                     'protection of utility payers '
                                                     'alongside job creation and '
                                                     'community development, and that '
                                                     'she remains in touch with local '
                                                     "leaders. Spokesperson's "
                                                     "statement, not Capito's own "
                                                     'words. The same story says the '
                                                     'group Tucker United reached out '
                                                     'to members of Congress who '
                                                     'represent the area and had not '
                                                     'received a response.',
                                             'date': '2026-08-12',
                                             'source': 'https://rollcall.com/2026/08/12/data-centers-coming-is-congress-ready/',
                                             'source_name': 'Roll Call',
                                             'kind': 'statement'},
                                            {'what': 'E&E News reported that Capito '
                                                     'said she is supportive of the '
                                                     'concept of the Ratepayer '
                                                     'Protection Act, and that while '
                                                     "data centers are an 'important "
                                                     "topic' with 'major pushback', "
                                                     'the issue had not become part of '
                                                     'the permitting negotiations she '
                                                     "was leading. Reporter's "
                                                     'paraphrase with two quoted '
                                                     'phrases. (By November the '
                                                     'permitting bill she co-authored '
                                                     'did carry the Ratepayer '
                                                     'Protection Act, per her own '
                                                     'floor remarks already on file.)',
                                             'date': '2026-06-25',
                                             'source': 'https://www.eenews.net/articles/data-center-energy-bill-hits-speed-bump/',
                                             'source_name': 'E&E News by POLITICO',
                                             'kind': 'statement'},
                                            {'what': 'WCHS reported (paraphrase) that '
                                                     'Capito said data-center '
                                                     'companies must have early and '
                                                     'strong community engagement and '
                                                     'that transparency about the '
                                                     'process and effects on residents '
                                                     'could go a long way. In direct '
                                                     'quotes she said proposed '
                                                     'projects will build their own '
                                                     "power behind the grid, so 'it "
                                                     "won't impact it and it could "
                                                     'actually maybe improve the '
                                                     'situation because there will be '
                                                     "excess power probably created,' "
                                                     'and that the data center seeking '
                                                     'to locate in Putnam County has '
                                                     'guaranteed to replenish and '
                                                     'clean the water it takes from '
                                                     'the Ohio.',
                                             'date': '2026-04-24',
                                             'source': 'https://www.capito.senate.gov/news/in-the-news/west-virginia-senator-says-early-community-engagement-from-data-centers-is-key',
                                             'source_name': 'WCHS / Fox 8-11 (reposted '
                                                            'on capito.senate.gov)',
                                             'kind': 'statement'},
                                            {'what': 'On her Thursday media call with '
                                                     'West Virginia reporters (the '
                                                     'call behind the WCHS item '
                                                     'already on file, which is dated '
                                                     'a week later), said community '
                                                     'members should be heard early '
                                                     'and that transparency is what '
                                                     'communities need, while also '
                                                     "saying there are 'wild "
                                                     "accusations' about the "
                                                     'downsides. MetroNews reports she '
                                                     'said she does not believe data '
                                                     'centers will create a lot of '
                                                     'jobs but will create a lot of '
                                                     'tax revenue.',
                                             'date': '2026-04-16',
                                             'source': 'https://wvmetronews.com/2026/04/16/capito-says-early-community-engagement-key-in-data-center-development/',
                                             'source_name': 'WV MetroNews',
                                             'kind': 'statement'},
                                            {'what': 'On a call with statewide media, '
                                                     'discussing an effort her office '
                                                     'was involved in to bring a data '
                                                     "center to Logan County, said 'We "
                                                     'want them in West Virginia. They '
                                                     'are massive investments, '
                                                     'billions of dollars of '
                                                     "investments,' and 'The appetite "
                                                     'for power is going to be so '
                                                     "huge. Everyone's going to win "
                                                     "here.'",
                                             'date': '2024-12-12',
                                             'source': 'https://wvpublic.org/story/energy-environment/we-want-them-capito-supports-efforts-to-build-a-data-center/',
                                             'source_name': 'West Virginia Public '
                                                            'Broadcasting',
                                             'kind': 'statement'}],
                                  'as_of': '2026-11-28'},
 ('WY', 'Harriet Hageman'): {'lean': 'guardrails',
                             'summary': "As Wyoming's U.S. House member she "
                                        'cosponsored the Ratepayer Protection Act '
                                        '(H.R. 9340) on 2026-07-20 and voted for it '
                                        'when it passed the House 417-3. In July 2026 '
                                        "she wrote to Meta's CEO demanding answers "
                                        "about bacterial contamination of Cheyenne's "
                                        "reuse water system traced to Meta's data "
                                        'center, and told Cowboy State Daily that '
                                        'companies coming to Wyoming should talk with '
                                        'city leaders, hold public meetings and do '
                                        'public outreach. No statement on moratoriums, '
                                        'tax incentives or siting rules was found.',
                             'background': "U.S. Representative for Wyoming's at-large "
                                           'district since 2023.',
                             'items': [{'what': 'Voted Yea on House passage of H.R. '
                                                '9340, the Ratepayer Protection Act, '
                                                'under suspension of the rules; it '
                                                'passed 417-3 (Roll Call 312).',
                                        'date': '2026-09-16',
                                        'source': 'https://clerk.house.gov/Votes/2026312',
                                        'source_name': 'Clerk of the U.S. House, Roll '
                                                       'Call 312',
                                        'kind': 'action'},
                                       {'what': 'Cosponsored H.R. 9340, the Ratepayer '
                                                'Protection Act (sponsor: Rep. Gabe '
                                                'Evans), joining on 2026-07-20; she is '
                                                'one of 42 cosponsors and not an '
                                                'original cosponsor.',
                                        'date': '2026-07-20',
                                        'source': 'https://www.congress.gov/bill/119th-congress/house-bill/9340/cosponsors',
                                        'source_name': 'Congress.gov',
                                        'kind': 'action'},
                                       {'what': 'In a phone interview with Cowboy '
                                                'State Daily after her letter to Meta, '
                                                'said Meta called her office within 24 '
                                                'hours and that she joined a second '
                                                'call with Meta officials. She said '
                                                'she has encouraged Meta and other '
                                                'businesses coming to Wyoming to work '
                                                'with the communities where they '
                                                'intend to locate: talk with city '
                                                'leaders, hold public meetings and do '
                                                'public outreach. The paper reports '
                                                'she sees her approach on this less as '
                                                'a federal lawmaker and more as an '
                                                'advocate for Wyoming. (Evidence quote '
                                                'omits one short sentence, "Talk about '
                                                'what you intend to do.", to stay '
                                                'within 40 words.)',
                                        'date': '2026-07-14',
                                        'source': 'https://cowboystatedaily.com/2026/07/14/on-second-thought-no-press-conference-on-cheyenne-meta-data-center-contamination/',
                                        'source_name': 'Cowboy State Daily',
                                        'kind': 'statement'},
                                       {'what': 'Sent a letter to Meta CEO Mark '
                                                'Zuckerberg seeking answers about the '
                                                'discharge of the bacterium '
                                                "Cupriavidus gilardii into Cheyenne's "
                                                'municipal reuse water system from '
                                                "Meta's data center. Per her release, "
                                                'the Cheyenne Board of Public '
                                                "Utilities revoked the contractor's "
                                                'discharge privileges in March, '
                                                'residents were not told until the end '
                                                'of June, and local utility officials '
                                                'said drinking water was not '
                                                'threatened.',
                                        'date': '2026-07-09',
                                        'source': 'https://hageman.house.gov/media/press-releases/hageman-demands-answers-meta-over-data-center-water-contamination',
                                        'source_name': 'Rep. Hageman press release',
                                        'kind': 'action'},
                                       {'what': "Cowboy State Daily's report of her "
                                                'July 9 letter to Meta CEO Mark '
                                                'Zuckerberg quotes the letter itself '
                                                '(the earlier pass cited only her '
                                                'release): she wrote that many are '
                                                'rightfully concerned about high water '
                                                'consumption by data centers, that the '
                                                'contamination seemingly came from a '
                                                'closed-loop cooling system marketed '
                                                'as a solution to that, and asked '
                                                'among other things whether '
                                                'closed-loop cooling can scale down '
                                                'water consumption safely. SAME ACTION '
                                                'as the existing 2026-07-09 letter '
                                                'item - a second source with the '
                                                "letter's wording, not a second "
                                                'action.',
                                        'date': '2026-07-09',
                                        'source': 'https://cowboystatedaily.com/2026/07/09/hageman-demands-answers-from-zuckerberg-about-cheyenne-data-center-contamination/',
                                        'source_name': 'Cowboy State Daily',
                                        'kind': 'action'},
                                       {'what': 'In a Townhall.com interview (reposted '
                                                'on her House site), the columnist '
                                                'reports that, in the wake of backlash '
                                                'against data centers, Hageman said '
                                                'rising electricity demand can be '
                                                'addressed with abundant, reliable '
                                                'energy projects and done thoughtfully '
                                                'without ceding the AI race to China. '
                                                "That sentence is the columnist's "
                                                "paraphrase; Hageman's direct quotes "
                                                'are about reliable and affordable '
                                                "energy and do not use the words 'data "
                                                "center'.",
                                        'date': '2026-05-23',
                                        'source': 'https://hageman.house.gov/media/in-the-news/rep-hageman-channels-wyoming-way-energy-natural-resources-issues',
                                        'source_name': 'Townhall (opinion column by '
                                                       'Gabriella Hoffman), reposted '
                                                       'on hageman.house.gov',
                                        'kind': 'statement'}],
                             'as_of': '2026-11-28'}}
