"""
campaign_guests.py - the guest players' page (guests/index.html).

One page for someone sitting in for a session: their part in the story,
how the game works, and a tab per ready-made character. Everything on it
is static, and it carries none of the site's navigation. To reuse it for
another session, rewrite `story`, `title` and `subtitle`; the sheets can
stay as they are.

Voice: the page speaks to one reader ("you and your companion"), since
each guest reads it on their own.

Player-known framing only, same as the rest of the site: the story below
says nothing a villager in Bracken Hollow could not tell a stranger.

Sheets follow the standard character sheet and are plain level 3
characters with the subclass left off (2014 rules, standard array with
+2/+1, average hit points). Ability modifiers, saving throws, the full
skill list and initiative are worked out by the build
from `scores`, `saves`, `skills`, `expertise` and `jack`. Attack and spell
numbers are entered by hand.
"""

GUESTS = dict(
    eyebrow='Guest Players',
    title='Welcome to Bracken Hollow',
    subtitle='One evening of Dungeons & Dragons. Read the top of this page, choose a character, and you are ready.',

    # YouTube id of a short "how to play" video, shown at the top of the
    # How to Play section. None leaves the block off the page.
    video=None,

    # The errand is invented for the guests: they carry a letter from their
    # home village to Kalaman. It gives them a reason to be on the road, a
    # reason to leave for Kalaman with the party afterwards, and a thread to
    # pick up later. What is fouling the brook upstream is left open on purpose;
    # the villagers do not know.
    # Where they were during Journey 011: in the second house, the one Boyd
    # carried food to, where the sick are tended. They saw the monument fall.
    # They do not know it can return.
    story=[
        'The brook that turns the mill in your home village has run low and rust-red since the end of '
        'summer. The wheel stands idle, the fish are gone, and the wells have begun to taste of iron. '
        'The elders wrote a letter to Kalaman explaining it and asking for help, and handed it to you '
        'and your traveling companion to carry. About a week ago, with the city a day ahead, the two '
        'of you turned off the road to rest for a night in Bracken Hollow, a quiet forest village with '
        'no wall and no guard at its gate.',
        'The light failed as you walked in. Three moons stood over the rooftops in a single eclipse, '
        'and they have stood there since. When you shouldered your packs and walked out, the road '
        'carried you straight back in on the far side of the village.',
        'You have watched the moons take their turns several times now: white, then red, then black, '
        'each with its own danger in the streets. Then comes the hour of the eclipse, when the stone '
        'monument on the hill wakes and someone vanishes. The village has lived this way for about a '
        'month. An old soldier, Sergeant Boyd, keeps people fed and indoors. The farms give food only '
        'under the black moon, when the wolves are out, and the two of you have taken your turns '
        'carrying sacks back through the dark.',
        'This last time you stayed behind at the house where the sick are tended, and Boyd brought the '
        'food over himself. From its doorway you watched a band of strangers climb the hill to meet the '
        'monument, and you watched it fall. It is the first time anyone in the Hollow has seen that. '
        'The letter is still in your coat, and Kalaman is still a day away. You and your companion mean '
        'to find those strangers and help.',
    ],

    # The line under "Choose Your Character".
    choose='Each sheet lists everything that character can do. You and your companion may choose the '
           'same one. Your character\'s name, species, and appearance are yours to decide.',

    basics=[
        ('Say what you do.',
         'You can try anything. Describe what your character does, and the Dungeon Master (DM) tells '
         'you what happens or what to roll.'),
        ('The d20 decides.',
         'When the outcome is uncertain, roll the twenty-sided die, add the number from your sheet, '
         'and say the total. Higher is better.'),
        ('Armor Class and Hit Points.',
         'Armor Class (AC) is the number an attack must reach to hit you. Hit Points (HP) are how much '
         'harm you can take. At 0 HP you fall, and a friend can get you back up.'),
        ('Your turn in a fight.',
         'Initiative, rolled when a fight starts, sets the turn order. On your turn, move up to your '
         'speed and take one action, usually an attack or a spell. Some abilities use a bonus action '
         'on your turn, or a reaction on someone else\'s.'),
        ('Checks and saves.',
         'A check is you attempting something: d20 plus the number beside that skill. A saving throw '
         'is you resisting something: d20 plus the number beside that ability under Saving Throws.'),
        ('Advantage and disadvantage.',
         'With advantage, roll two d20s and keep the higher. With disadvantage, keep the lower.'),
        ('Reading your sheet.',
         '"Hit +5" is d20 + 5 against the target\'s Armor Class. "1d8+3" is one eight-sided die plus 3. '
         '"DEX 13" means the target makes a Dexterity save and needs 13 or higher. A box is a '
         'limited use: tick it when it is spent.'),
    ],

    # scores:   the six ability scores
    # saves:    abilities with saving throw proficiency
    # skills:   proficient skills; expertise: the ones that count double
    # jack:     True adds half proficiency to everything else (the bard)
    # attacks:  (name, hit, damage/type, notes)
    # actions:  [(group, [(name, uses label, boxes, text)])]
    # spells:   ability, dc, attack, groups [(label, slots, slots already spent,
    #           [(name, time, range, save/attack, effect)])], optional note
    # features: [(name, text)]
    # turn:     a dependable turn, listed under How to Play
    sheets=[
        dict(
            slug='fighter', name='Fighter', role='Front-line warrior', complexity='Simple',
            quote='Stand behind me. This part is mine.',
            about='You are a trained warrior in heavy armor. You are the hardest person here to hurt, and '
                  'you land a solid blow almost every turn. Your place is between the danger and your '
                  'friends. This is the most straightforward character of the five.',
            scores=dict(STR=17, DEX=13, CON=15, INT=8, WIS=12, CHA=10),
            saves=('STR', 'CON'),
            skills=('Athletics', 'Perception', 'Survival', 'Intimidation'),
            ac='18', ac_note='Chain mail, shield', hp='28', hit_dice='3d10', speed='30 ft.',
            attacks=[('Longsword', '+5', '1d8+5 slashing', 'Melee. Dueling style included.'),
                     ('Javelin', '+5', '1d6+3 piercing', 'Thrown, range 30/120 ft. You carry four.')],
            actions=[
                ('Bonus Actions', [('Second Wind', '1 / Short Rest', 1, 'Regain 1d10+3 hit points.')]),
                ('Special', [('Action Surge', '1 / Short Rest', 1, 'On your turn, take one additional action.')]),
            ],
            features=[('Fighting Style: Dueling',
                       '+2 damage with a one-handed melee weapon. Included in the longsword above.')],
            turn=['Move next to the biggest threat.',
                  'Attack with your longsword.',
                  'Badly hurt: Second Wind. Decisive moment: Action Surge and attack again.'],
        ),
        dict(
            slug='ranger', name='Ranger', role='Archer and tracker', complexity='Simple',
            quote='Everything leaves a trail. I only have to be patient.',
            about='You are a hunter and tracker, at home in the forest. You are deadly with a bow, quick '
                  'to notice trouble, and the one who finds the trail when everyone else is lost. You '
                  'also carry a few spells drawn from the wild.',
            scores=dict(STR=13, DEX=17, CON=13, INT=10, WIS=14, CHA=8),
            saves=('STR', 'DEX'),
            skills=('Stealth', 'Perception', 'Survival', 'Nature', 'Animal Handling'),
            ac='15', ac_note='Studded leather', hp='25', hit_dice='3d10', speed='30 ft.',
            attacks=[('Longbow', '+7', '1d8+3 piercing', 'Range 150/600 ft. Archery style included.'),
                     ('Shortsword', '+5', '1d6+3 piercing', 'Melee. Finesse, light.')],
            actions=[],
            spells=dict(ability='Wisdom', dc='12', attack='+4', groups=[
                ('1st Level', 3, 0, [
                    ('Hunter\'s Mark', 'Bonus', '90 ft.', '',
                     'Concentration. Your weapon hits on the marked creature deal an extra 1d6 damage.'),
                    ('Ensnaring Strike', 'Bonus', 'Self', 'STR 12',
                     'Concentration. Your next weapon hit wraps the target in vines: restrained on a failed save.'),
                    ('Cure Wounds', 'Action', 'Touch', '', 'A creature regains 1d8+2 hit points.'),
                ]),
            ]),
            features=[
                ('Favored Enemy: Beasts',
                 'Advantage on Survival checks to track beasts and on Intelligence checks to recall information about them.'),
                ('Natural Explorer: Forest',
                 'In forest your group travels at full pace over difficult terrain, you keep your bearings, '
                 'and you forage twice as much food.'),
                ('Fighting Style: Archery', '+2 to attack rolls with ranged weapons. Included in the longbow above.'),
            ],
            turn=['Stay back where you have a clear shot.',
                  'First turn: Hunter\'s Mark on the main threat, then shoot.',
                  'Every turn after: shoot the marked target.'],
        ),
        dict(
            slug='sorcerer', name='Sorcerer', role='Damage caster', complexity='Moderate',
            quote='There is a storm under my skin, and today it gets out.',
            about='Magic runs in your blood and answers when you call. You deal the most damage of the '
                  'five and you are the easiest to hurt, so keep your friends between you and the danger. '
                  'A small pool of Sorcery Points lets you bend your spells.',
            scores=dict(STR=8, DEX=13, CON=15, INT=10, WIS=12, CHA=17),
            saves=('CON', 'CHA'),
            skills=('Persuasion', 'Deception', 'Insight', 'Arcana'),
            ac='14', ac_note='Mage Armor (active)', hp='20', hit_dice='3d6', speed='30 ft.',
            attacks=[('Fire Bolt', '+5', '1d10 fire', 'Cantrip. Range 120 ft.'),
                     ('Dagger', '+3', '1d4+1 piercing', 'Melee, or thrown at range 20/60 ft.')],
            actions=[
                ('Special', [
                    ('Sorcery Points', '3 / Long Rest', 3, 'Spend them on Metamagic as you cast a spell.'),
                    ('Empowered Spell', '1 point', 0,
                     'Reroll up to three of the spell\'s damage dice. You must use the new rolls.'),
                    ('Careful Spell', '1 point', 0,
                     'Choose up to three creatures. They automatically succeed on the spell\'s saving throw.'),
                ]),
            ],
            spells=dict(ability='Charisma', dc='13', attack='+5', groups=[
                ('Cantrips', 0, 0, [
                    ('Mage Hand', 'Action', '30 ft.', '', 'A spectral hand moves or carries small objects for 1 minute.'),
                    ('Light', 'Action', 'Touch', '', 'An object sheds bright light for 1 hour.'),
                    ('Prestidigitation', 'Action', '10 ft.', '', 'A minor trick: sparks, a breeze, a clean cloak, a warmed drink.'),
                ]),
                ('1st Level', 4, 0, [
                    ('Mage Armor', 'Action', 'Touch', '', 'Already active when play begins, at no cost. Your Armor Class of 14 includes it.'),
                    ('Burning Hands', 'Action', '15 ft. cone', 'DEX 13',
                     '3d6 fire to each creature in the cone, or half on a successful save.'),
                    ('Shield', 'Reaction', 'Self', '',
                     'When you are hit: +5 AC until the start of your next turn, which can turn the hit into a miss.'),
                ]),
                ('2nd Level', 2, 0, [
                    ('Scorching Ray', 'Action', '120 ft.', '+5',
                     'Three rays, at one target or several. Each hit deals 2d6 fire.'),
                ]),
            ]),
            features=[],
            turn=['Most turns: Fire Bolt from behind your friends.',
                  'Enemies bunched together: Burning Hands.',
                  'One tough enemy: Scorching Ray.',
                  'An attack hits you: Shield.'],
        ),
        dict(
            slug='artificer', name='Artificer', role='Inventor and support', complexity='Moderate',
            quote='Give me an hour and a box of scrap, and you will have a better plan.',
            about='You are an inventor who works magic through devices of your own making. Your reinforced '
                  'gear keeps you sturdy while you solve problems: mend the wounded, light up hidden '
                  'enemies, sharpen a friend\'s roll.',
            scores=dict(STR=8, DEX=13, CON=15, INT=17, WIS=12, CHA=10),
            saves=('CON', 'INT'),
            skills=('Investigation', 'Arcana', 'Perception', 'Sleight of Hand'),
            ac='18', ac_note='Scale mail, shield, infusion', hp='24', hit_dice='3d8', speed='30 ft.',
            attacks=[('Ray of Frost', '+6', '1d8 cold',
                      'Cantrip. Range 60 ft. The target\'s speed drops 10 ft. for a turn.'),
                     ('Light Crossbow', '+3', '1d8+1 piercing', 'Range 80/320 ft.')],
            actions=[],
            spells=dict(ability='Intelligence', dc='13', attack='+6', groups=[
                ('Cantrips', 0, 0, [
                    ('Guidance', 'Action', 'Touch', '',
                     'Concentration. The target adds 1d4 to one ability check within 1 minute.'),
                ]),
                ('1st Level', 3, 0, [
                    ('Cure Wounds', 'Action', 'Touch', '', 'A creature regains 1d8+3 hit points.'),
                    ('Faerie Fire', 'Action', '60 ft.', 'DEX 13',
                     'Concentration. Creatures in a 20 ft. cube are outlined on a failed save, and attacks '
                     'against them have advantage.'),
                    ('Thunderwave', 'Action', '15 ft. cube', 'CON 13',
                     '2d8 thunder and pushed 10 ft., or half damage and no push on a successful save.'),
                    ('Detect Magic', 'Action', 'Self', '', 'Concentration. You sense magic within 30 ft. for up to 10 minutes.'),
                ]),
            ]),
            features=[
                ('Magical Tinkering',
                 'Touch a tiny object to make it shed light, play a recorded message, or display a short line of text.'),
                ('Infusions',
                 'Enhanced Defense (+1 AC) and Enhanced Arcane Focus (+1 to spell attacks). Both are included in the numbers on this sheet.'),
                ('Tools', 'Thieves\' tools +3.'),
            ],
            turn=['Most turns: Ray of Frost.',
                  'A friend is hurt: Cure Wounds.',
                  'Several enemies: Faerie Fire, so every attack against them has advantage.',
                  'Before a friend\'s skill check: Guidance.'],
        ),
        dict(
            slug='bard', name='Bard', role='Charmer and support', complexity='Most options',
            quote='A sharp word, a good song, and somehow everyone walks out alive.',
            about='You work magic through words, music, and nerve. You are the best talker at the table and '
                  'the best at making everyone around you better. This sheet has the most options of the '
                  'five, so it suits someone who enjoys choices.',
            scores=dict(STR=8, DEX=15, CON=13, INT=10, WIS=12, CHA=17),
            saves=('DEX', 'CHA'),
            skills=('Persuasion', 'Deception', 'Performance', 'Insight', 'Sleight of Hand'),
            expertise=('Persuasion', 'Deception'), jack=True,
            ac='13', ac_note='Leather armor', hp='21', hit_dice='3d8', speed='30 ft.',
            attacks=[('Rapier', '+4', '1d8+2 piercing', 'Melee. Finesse.'),
                     ('Vicious Mockery', 'WIS 13', '1d4 psychic',
                      'Cantrip. Range 60 ft. On a failed save, the target has disadvantage on its next attack roll.')],
            actions=[
                ('Bonus Actions', [
                    ('Bardic Inspiration', '3 / Long Rest', 3,
                     'A creature within 60 ft. gains a d6. Within 10 minutes it can add the die to one '
                     'ability check, attack roll, or saving throw.'),
                ]),
            ],
            spells=dict(ability='Charisma', dc='13', attack='+5', groups=[
                ('Cantrips', 0, 0, [
                    ('Minor Illusion', 'Action', '30 ft.', '', 'A sound, or a still image up to a 5 ft. cube, for 1 minute.'),
                ]),
                ('1st Level', 4, 0, [
                    ('Healing Word', 'Bonus', '60 ft.', '', 'A creature regains 1d4+3 hit points.'),
                    ('Dissonant Whispers', 'Action', '60 ft.', 'WIS 13',
                     '3d6 psychic, and the target uses its reaction to move away. Half damage on a successful save.'),
                    ('Faerie Fire', 'Action', '60 ft.', 'DEX 13',
                     'Concentration. Creatures in a 20 ft. cube are outlined on a failed save, and attacks '
                     'against them have advantage.'),
                    ('Charm Person', 'Action', '30 ft.', 'WIS 13', 'A humanoid is charmed by you for 1 hour on a failed save.'),
                ]),
                ('2nd Level', 2, 0, [
                    ('Shatter', 'Action', '60 ft.', 'CON 13',
                     '3d8 thunder to each creature in a 10 ft. radius, or half on a successful save.'),
                    ('Hold Person', 'Action', '60 ft.', 'WIS 13',
                     'Concentration. A humanoid is paralyzed on a failed save. It repeats the save at the end of each of its turns.'),
                ]),
            ]),
            features=[
                ('Jack of All Trades', '+1 on ability checks you lack proficiency in. Included in the skills on this sheet.'),
                ('Expertise', 'Double proficiency in Persuasion and Deception. Included.'),
            ],
            turn=['Bonus action first: Bardic Inspiration or Healing Word.',
                  'Action: Vicious Mockery, or a levelled spell when it counts.',
                  'Outside a fight: you do the talking.'],
        ),
    ],
)
