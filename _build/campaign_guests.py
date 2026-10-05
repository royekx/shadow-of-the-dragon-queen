"""
campaign_guests.py - the guest players' page (guests/index.html).

One page for people sitting in for a session: who they are in the story,
how the game works, and a tab per ready-made character. Everything on it
is static, and it carries none of the site's navigation. To reuse it for
another session, rewrite `story`, `title` and `subtitle`; the sheets can
stay as they are.

Player-known framing only, same as the rest of the site: the story below
says nothing a villager in Bracken Hollow could not tell a stranger.

Sheets are plain level 3 characters with the subclass left off (2014
rules, standard array, average hit points).
"""

GUESTS = dict(
    eyebrow='Guest Players',
    title='Welcome to Bracken Hollow',
    subtitle='One evening of Dungeons & Dragons. Read the top of this page, choose a character, and you are ready.',

    # YouTube id of a short "how to play" video, shown at the top of the
    # How to Play section. None leaves the block off the page.
    video=None,

    story=[
        'The two of you travel together, on an errand your Dungeon Master will tell you about. '
        'A few days ago you stopped for the night in Bracken Hollow, '
        'a quiet forest village off the road east of Kalaman. When you tried to leave, the road led '
        'straight back in.',
        'Three moons hang over the village in a standing eclipse, and each hour of it brings its own '
        'danger. At the worst of them, a stone monument on the hill wakes and one villager vanishes. '
        'An old soldier, Sergeant Boyd, keeps people fed and indoors, and you have stayed close to him. '
        'Two travelers stood little chance against it.',
        'Then five strangers walked in, climbed the hill, and brought it down. It will rise again at the '
        'next eclipse, and they mean to break the spell before then. You have decided to help.',
    ],
    # The line under "Choose Your Character".
    choose='Each sheet lists everything that character can do, and both of you may choose the same one. '
           'Your character\'s name and look are yours to decide.',

    basics=[
        ('Say what you do.',
         'You can try anything. Describe what your character does, and the Dungeon Master (DM) tells '
         'you what happens or what to roll.'),
        ('The d20 decides.',
         'When the outcome is uncertain, roll the twenty-sided die, add the number from your sheet, '
         'and say the total. Higher is better.'),
        ('Armor Class and Hit Points.',
         'AC is the number an attack must reach to hit you. HP is how much harm you can take. '
         'At 0 HP you fall, and a friend can get you back up.'),
        ('Your turn in a fight.',
         'Move up to your speed and take one action, usually an attack or a spell. Some abilities are '
         "a bonus action (a quick extra) or a reaction (an answer on someone else's turn)."),
        ('Checks and saves.',
         'A check is you attempting something: d20 plus that skill or ability number. A saving throw '
         'is you resisting something: d20 plus the save number beside that ability.'),
        ('Reading your sheet.',
         '"+5 to hit" is d20 + 5. "1d8+3" is one eight-sided die plus 3. "Roll twice" is two d20s, '
         'keeping the higher or lower as stated. Tick a box when you spend a limited use.'),
    ],

    # abilities: (name, modifier, save, proficient in that save)
    # attacks:   (name, to hit, damage, reach)
    # blocks:    title, optional pools [(label, [(sub-label, boxes)], note)],
    #            rows [(name, tag, text)], optional note
    sheets=[
        dict(
            slug='fighter', name='Fighter', play='Simplest',
            pitch='I want to stand in front and hit things.',
            about='You are a trained warrior in heavy armor. You are the hardest person here to hurt, and '
                  'you land a solid blow almost every turn. Your place is between the danger and your '
                  'friends. This is the most straightforward character of the five.',
            ac='18', ac_note='chain mail and shield', hp='28', speed='30 ft', init='+1',
            abilities=[('Strength', '+3', '+5', True), ('Dexterity', '+1', '+1', False),
                       ('Constitution', '+2', '+4', True), ('Intelligence', '-1', '-1', False),
                       ('Wisdom', '+1', '+1', False), ('Charisma', '+0', '+0', False)],
            attacks_label='Attacks', attack_head='Weapon',
            attacks=[('Longsword', 'd20 +5', '1d8+5 slashing', 'A foe next to you'),
                     ('Javelin', 'd20 +5', '1d6+3 piercing', 'Thrown, up to 30 ft. You carry four.')],
            blocks=[dict(title='Special Abilities', rows=[
                ('Second Wind', 'bonus action', 'Catch your breath and regain 1d10+3 HP. Returns after a short rest.', 1),
                ('Action Surge', '', 'Take a second action this turn, usually another attack. Returns after a short rest.', 1),
            ])],
            skills=[('Athletics', '+5'), ('Perception', '+3'), ('Survival', '+3'), ('Intimidation', '+2')],
            turn=['Move next to the biggest threat.',
                  'Attack with your longsword.',
                  'Badly hurt? Use Second Wind. Big moment? Use Action Surge and attack again.'],
        ),
        dict(
            slug='ranger', name='Ranger', play='Simple, three spells',
            pitch='I want to strike from a distance and read the wild.',
            about='You are a hunter and tracker, at home in the forest. You are deadly with a bow, quick '
                  'to notice trouble, and the one who finds the trail when everyone else is lost. You '
                  'also carry a few spells drawn from the wild.',
            ac='15', ac_note='studded leather', hp='25', speed='30 ft', init='+3',
            abilities=[('Strength', '+1', '+3', True), ('Dexterity', '+3', '+5', True),
                       ('Constitution', '+1', '+1', False), ('Intelligence', '+0', '+0', False),
                       ('Wisdom', '+2', '+2', False), ('Charisma', '-1', '-1', False)],
            attacks_label='Attacks', attack_head='Weapon',
            attacks=[('Longbow', 'd20 +7', '1d8+3 piercing', 'Up to 150 ft'),
                     ('Shortsword', 'd20 +5', '1d6+3 piercing', 'A foe next to you')],
            blocks=[
                dict(title='Spells',
                     pools=[('Spell slots', [('', 3)],
                             'Each spell you cast spends one. Targets need 12 or higher on a save to resist.')],
                     rows=[
                         ('Hunter\'s Mark', 'bonus action', 'Mark one foe you can see. Each of your hits on it deals an extra 1d6 damage, for up to an hour.', 0),
                         ('Ensnaring Strike', 'bonus action', 'Your next hit sprouts vines. The target makes a Strength save or is held in place.', 0),
                         ('Cure Wounds', 'action', 'Touch someone to restore 1d8+2 HP.', 0),
                     ],
                     note='Hunter\'s Mark and Ensnaring Strike both take your focus, so keep one going at a time.'),
                dict(title='Traits', rows=[
                    ('Favored Enemy: beasts', '', 'Roll twice and keep the higher when you track beasts or recall what you know of them. Wolves count.', 0),
                    ('Natural Explorer: forest', '', 'In woodland you keep your bearings and find food and water with ease.', 0),
                ]),
            ],
            skills=[('Stealth', '+5'), ('Perception', '+4'), ('Survival', '+4'), ('Nature', '+2')],
            turn=['Stay back where you have a clear shot.',
                  'First turn: Hunter\'s Mark on the main threat, then shoot.',
                  'Every turn after: shoot the marked target.'],
        ),
        dict(
            slug='sorcerer', name='Sorcerer', play='A handful of spells',
            pitch='I want to throw fire.',
            about='Magic runs in your blood and answers when you call. You deal the most damage of the '
                  'five and you are the easiest to hurt, so keep your friends between you and the danger. '
                  'A small pool of Sorcery Points lets you bend your spells.',
            ac='14', ac_note='Mage Armor, already cast', hp='20', speed='30 ft', init='+1',
            abilities=[('Strength', '-1', '-1', False), ('Dexterity', '+1', '+1', False),
                       ('Constitution', '+2', '+4', True), ('Intelligence', '+0', '+0', False),
                       ('Wisdom', '+1', '+1', False), ('Charisma', '+3', '+5', True)],
            attacks_label='Cantrips: free, every turn', attack_head='Cantrip',
            attacks=[('Fire Bolt', 'd20 +5', '1d10 fire', 'Up to 120 ft')],
            also=[('Mage Hand', 'A ghostly hand moves small things within 30 ft.'),
                  ('Light', 'An object glows like a torch.'),
                  ('Prestidigitation', 'Small harmless tricks: sparks, a breeze, a clean cloak.')],
            blocks=[
                dict(title='Spells',
                     pools=[('Spell slots', [('1st', 3), ('2nd', 2)],
                             'A spell spends one slot of its level. Targets resist on a save of 13 or higher.')],
                     rows=[
                         ('Burning Hands', '1st', 'A 15 ft cone of flame. Each creature in it makes a Dexterity save: 3d6 fire, or half on a success.', 0),
                         ('Scorching Ray', '2nd', 'Three rays, up to 120 ft, at one target or several. Roll d20 +5 for each. 2d6 fire per hit.', 0),
                         ('Shield', '1st, reaction', 'When an attack hits you, gain +5 AC until your next turn. That may turn the hit into a miss.', 0),
                     ]),
                dict(title='Sorcery Points',
                     pools=[('Points', [('', 3)], 'Spend one as you cast a spell.')],
                     rows=[
                         ('Empowered', '', 'Reroll up to three of the spell\'s damage dice and keep the new results.', 0),
                         ('Careful', '', 'Choose up to three friends caught in your blast. They pass the save automatically.', 0),
                     ]),
            ],
            skills=[('Persuasion', '+5'), ('Deception', '+5'), ('Insight', '+3'), ('Arcana', '+2')],
            turn=['Most turns: Fire Bolt from behind your friends.',
                  'Enemies bunched together: Burning Hands.',
                  'One tough enemy: Scorching Ray.',
                  'An attack hits you: Shield.'],
        ),
        dict(
            slug='artificer', name='Artificer', play='A handful of spells',
            pitch='I want gadgets and clever fixes.',
            about='You are an inventor who works magic through devices of your own making. Your reinforced '
                  'gear keeps you sturdy while you solve problems: mend the wounded, light up hidden '
                  'enemies, sharpen a friend\'s roll.',
            ac='18', ac_note='scale mail and shield', hp='24', speed='30 ft', init='+1',
            abilities=[('Strength', '-1', '-1', False), ('Dexterity', '+1', '+1', False),
                       ('Constitution', '+2', '+4', True), ('Intelligence', '+3', '+5', True),
                       ('Wisdom', '+1', '+1', False), ('Charisma', '+0', '+0', False)],
            attacks_label='Cantrips: free, every turn', attack_head='Cantrip',
            attacks=[('Ray of Frost', 'd20 +6', '1d8 cold', '60 ft. Slows the target by 10 ft for a turn.')],
            also=[('Guidance', 'Touch a friend. They add 1d4 to one skill check of their choice within the next minute.')],
            blocks=[
                dict(title='Spells',
                     pools=[('Spell slots', [('', 3)],
                             'Each spell you cast spends one. Targets need 13 or higher on a save to resist.')],
                     rows=[
                         ('Cure Wounds', '', 'Touch someone to restore 1d8+3 HP.', 0),
                         ('Faerie Fire', '', 'Creatures in a 20 ft square within 60 ft make a Dexterity save or glow. Attacks against a glowing creature roll twice and keep the higher.', 0),
                         ('Thunderwave', '', 'A 15 ft blast in front of you. Each creature makes a Constitution save: 2d8 thunder and pushed 10 ft, or half damage and no push on a success.', 0),
                         ('Detect Magic', '', 'For 10 minutes you sense magic within 30 ft of you.', 0),
                     ],
                     note='Guidance and Faerie Fire both take your focus, so keep one going at a time.'),
                dict(title='Traits', rows=[
                    ('Magical Tinkering', '', 'Touch a tiny object to make it glow, play a recorded sound, or display a short message.', 0),
                    ('Infusions', '', 'Your improvements to your armor and tools are already counted in the numbers on this sheet.', 0),
                ]),
            ],
            skills=[('Investigation', '+5'), ('Arcana', '+5'), ('Perception', '+3'), ('Thieves\' tools', '+3')],
            turn=['Most turns: Ray of Frost.',
                  'A friend is hurt: Cure Wounds.',
                  'Several enemies: Faerie Fire, so everyone hits more often.',
                  'Before a friend\'s skill check: Guidance.'],
        ),
        dict(
            slug='bard', name='Bard', play='Most options',
            pitch='I want to talk my way through it and lift my friends.',
            about='You work magic through words, music, and nerve. You are the best talker at the table and '
                  'the best at making everyone around you better. This sheet has the most options of the '
                  'five, so it suits someone who enjoys choices.',
            ac='13', ac_note='leather armor', hp='21', speed='30 ft', init='+3',
            abilities=[('Strength', '-1', '-1', False), ('Dexterity', '+2', '+4', True),
                       ('Constitution', '+1', '+1', False), ('Intelligence', '+0', '+0', False),
                       ('Wisdom', '+1', '+1', False), ('Charisma', '+3', '+5', True)],
            attacks_label='Attacks and cantrips: free, every turn', attack_head='Attack',
            attacks=[('Rapier', 'd20 +4', '1d8+2 piercing', 'A foe next to you'),
                     ('Vicious Mockery', 'Wisdom save', '1d4 psychic', '60 ft. Its next attack rolls twice, keeps the lower.')],
            also=[('Minor Illusion', 'Create a sound, or a still image up to the size of a chest, for one minute.')],
            blocks=[
                dict(title='Spells',
                     pools=[('Spell slots', [('1st', 4), ('2nd', 2)],
                             'A spell spends one slot of its level. Targets resist on a save of 13 or higher.')],
                     rows=[
                         ('Healing Word', '1st, bonus action', 'A friend within 60 ft regains 1d4+3 HP.', 0),
                         ('Dissonant Whispers', '1st', 'A creature within 60 ft makes a Wisdom save: 3d6 psychic and it flees. Half on a success.', 0),
                         ('Faerie Fire', '1st', 'Creatures in a 20 ft square make a Dexterity save or glow. Attacks against them roll twice and keep the higher.', 0),
                         ('Charm Person', '1st', 'A person within 30 ft makes a Wisdom save or treats you as a friend for an hour.', 0),
                         ('Shatter', '2nd', 'A 10 ft burst within 60 ft. Each creature makes a Constitution save: 3d8 thunder, or half on a success.', 0),
                         ('Hold Person', '2nd', 'A person within 60 ft makes a Wisdom save or is frozen in place. It rolls again each turn.', 0),
                     ]),
                dict(title='Traits', rows=[
                    ('Bardic Inspiration', 'bonus action', 'A friend within 60 ft adds 1d6 to one attack, check, or save of their choice.', 3),
                    ('Jack of All Trades', '', 'Add +1 to any skill check outside your list.', 0),
                ]),
            ],
            skills=[('Persuasion', '+7'), ('Deception', '+7'), ('Performance', '+5'), ('Insight', '+3')],
            turn=['Bonus action first: inspire a friend or cast Healing Word.',
                  'Action: Vicious Mockery, or a bigger spell when it counts.',
                  'Outside a fight: you do the talking.'],
        ),
    ],
)
