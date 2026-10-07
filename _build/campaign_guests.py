"""
campaign_guests.py - the guest players' pages (guests/<slug>.html).

One page for someone sitting in for a session: their part in the story,
how the game works, and a tab per ready-made character. Everything on it
is static, and it carries none of the site's navigation.

Each one-shot gets a page of its own, named for its title, and the old
ones stay where they are as a record. GUEST_PAGES at the foot of this file
lists them. To add one, append `dict(GUESTS, slug=..., title=...,
subtitle=..., story=[...])` there: it takes the basics and the sheets
from GUESTS and brings its own story.

Voice: the page speaks to one reader ("you and your partner"), since
each guest reads it on their own. "Partner" is chosen to read as close
without saying how: the two may be a couple, friends or kin, as the guests like.

Player-known framing only, same as the rest of the site: the story below
says nothing a villager in Bracken Hollow could not tell a stranger.

Sheets follow the standard character sheet and are plain level 3
characters with the subclass left off (2014 rules, standard array with
+2/+1, average hit points). Each sheet carries one borrowed piece so a
guest has something to do outside a fight: the fighter's Know Your Enemy
(Battle Master), the sorcerer's Telepathic Speech (Aberrant Mind), the
artificer's Experimental Elixir (Alchemist, simplified to a choice of
three), and the bard's History and Medicine (College of Lore). The
ranger's is Primeval Awareness, which is the class's own. Ability modifiers, saving throws, the full
skill list and initiative are worked out by the build
from `scores`, `saves`, `skills`, `expertise` and `jack`. Attack and spell
numbers are entered by hand.
"""

GUESTS = dict(
    eyebrow='Guest Players',
    # The file is guests/<slug>.html, so the address says which one-shot it is.
    slug='the-road-through-bracken-hollow',
    title='The Road Through Bracken Hollow',
    subtitle='One evening of Dungeons & Dragons. Read the top of this page, choose a character, and you are ready.',

    # YouTube id of a short "how to play" video, shown at the top of the
    # How to Play section. None leaves the block off the page.
    video=None,

    # The errand is invented for the guests: they carry a letter from their
    # home village to Kalaman. The village is Barrowmere, invented for this
    # page and named for the old burial mounds (barrows) beside its lake. DM-side, for when the table asks: it lies in Hinterlund, the
    # Solamnic province west of Kalaman, about a week on foot, off the road
    # toward Maelgoth. Bracken Hollow and Tatina Rookledust's home lie the
    # same way. Only the name is on the page. It gives them a reason to be on the road, a
    # reason to leave for Kalaman with the party afterwards, and a thread to
    # pick up later.
    # What they know: people at home keep forgetting things, it had begun to
    # happen to them, and the village elder smuggled them out for help. A company of
    # mercenaries holds the village and watches the roads, which is why they left by
    # night; who pays the company and what it wants are not on the page. The story
    # puts the mercenaries' arrival before the forgetting, so the order is the hint.
    # "The three moons" is said as a known thing: Krynn has three, and the guests' characters
    # would know it. They know who they
    # are and where home is; only stretches of time are missing. That is all. Not
    # remembering is the clue, so the page gives them nothing more. Who is
    # doing it, how, and what they want from the village are DM-side and are
    # deliberately absent here. It is someone's doing, not a curse. The shape
    # of it: the missing time is time spent working, and the one who works and
    # the one who comes home do not share memories.
    # Where they were during Journey 011: in the second house, the one Boyd
    # carried food to, where the sick are tended. Boyd was still there when the
    # party left for the hill, so he is how they heard about the strangers.
    # They saw the monument fall. They do not know it can return.
    # They arrived under the red moon, with the battle in the streets. The
    # party arrived under the black, with the wolves.
    # "The Standing Stone" is the villagers' name for the monument, new on this page.
    story=[
        'You and your partner carry a letter from Barrowmere, your home village, to the city of Kalaman, '
        'asking for help. A company of mercenaries came to "keep the peace" and now watches every road. '
        'Soon after, people began losing an afternoon, then whole days, coming back with aching backs, '
        'dusty boots, and no memory of where they went. When the two of you began losing days of your '
        'own, the village elder slipped you past the mercenaries by night.',
        'A day short of the city, you stopped in Bracken Hollow, a quiet forest village. The sky turned '
        'red as you walked in, and fighting filled the lanes. An old soldier, Sergeant Boyd, pulled you '
        'through a doorway and gave you a place by his fire.',
        'He told you that here the three moons hang locked in a single eclipse and take turns, white, '
        'then red, then black, each with its own trouble. At the last hour the Standing Stone on the '
        'hill wakes and walks, someone vanishes, and no one can leave. You tried anyway. The road '
        'carried you straight back in. That was a week ago.',
        'Now a band of strangers has walked in, killed the wolves that met them, and climbed the hill '
        'at the eclipse. From a doorway, you watched them bring the Standing Stone down. Nothing else '
        'has changed here in a week. They may be your way out, and your way to help for home.',
    ],

    # The line under "Choose Your Character".
    choose='Each sheet lists everything that character can do. You and your partner may choose the '
           'same one. Your character\'s name, species (human, elf, or dwarf), and appearance are yours to decide. '
           'Species changes nothing on the sheet.',

    # A line of reassurance at the head of How to Play. None leaves it off.
    ease='You do not need to remember everything. The Dungeon Master will guide you and tell you '
         'what to do next, and you can ask anything at any time.',

    # Only what a first-time player needs to sit down. The DM calls for every
    # roll and explains the rest at the table, so checks, saves, advantage
    # and the action types are left for then.
    basics=[
        ('Say what you do.',
         'You can try anything. Describe what your character does, and the Dungeon Master (DM) tells '
         'you what happens.'),
        ('Roll when the DM asks.',
         'When it is unclear whether something works, the DM asks for a roll and tells you which number '
         'on your sheet to add. Roll the twenty-sided die (the d20), add that number, and say the total. '
         'Higher is better.'),
        ('Fights go in turns.',
         'When a fight starts, the DM has everyone roll to set the order. That roll is called '
         'initiative. On your turn you can move and do one thing, usually an attack or a spell.'),
        ('Armor Class and Hit Points.',
         'Armor Class (AC) is the number an attack must reach to hit you. Hit Points (HP) are how much '
         'harm you can take. At 0 HP you fall, and a friend can get you back up.'),
        ('Reading your sheet.',
         '"+5" is a number you add to a d20 roll. "1d8+3" means roll one eight-sided die and add 3. '
         'A box is a limited use: tick it when it is spent.'),
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
    sheets=[
        dict(
            slug='fighter', name='Fighter', role='Front-line warrior', complexity='Simple',
            quote='Stand behind me. This part is mine.',
            about='You are a trained warrior in heavy armor: the hardest person here to hurt, and your place '
                  'is between the danger and your friends. Key things: your longsword, Second Wind to heal '
                  'yourself, Action Surge to act twice in one turn, and Know Your Enemy to size up a threat '
                  'before a fight. This is the most straightforward character of the five.',
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
            features=[('Know Your Enemy',
                       'Spend 1 minute watching or talking with a creature outside a fight. The DM tells you '
                       'whether it is stronger or weaker than you in two things you choose, such as Strength, '
                       'Armor Class, or hit points, and anything a trained eye would notice about how it fights.'),
                      ('Fighting Style: Dueling',
                       '+2 damage with a one-handed melee weapon. Included in the longsword above.')],
        ),
        dict(
            slug='ranger', name='Ranger', role='Archer and tracker', complexity='Simple',
            quote='Everything leaves a trail. I only have to be patient.',
            about='You are a hunter and tracker, at home in the forest: deadly with a bow, quick to notice '
                  'trouble, and the one who finds the trail when everyone else is lost. Key things: your '
                  'longbow, Hunter\'s Mark for extra damage on one target, a healing spell, and Primeval '
                  'Awareness to sense unnatural creatures nearby.',
            scores=dict(STR=13, DEX=17, CON=13, INT=10, WIS=14, CHA=8),
            saves=('STR', 'DEX'),
            skills=('Stealth', 'Perception', 'Survival', 'Nature', 'Animal Handling'),
            ac='15', ac_note='Studded leather', hp='25', hit_dice='3d10', speed='30 ft.',
            attacks=[('Longbow', '+7', '1d8+3 piercing', 'Range 150/600 ft. Archery style included.'),
                     ('Shortsword', '+5', '1d6+3 piercing', 'Melee. Finesse, light.')],
            actions=[
                ('Actions', [
                    ('Primeval Awareness', '1 spell slot', 0,
                     'For 1 minute you sense whether any aberrations, celestials, dragons, elementals, fey, '
                     'fiends, or undead are within 1 mile, or 6 miles in forest. You learn which kinds, '
                     'not where or how many.'),
                ]),
            ],
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
        ),
        dict(
            slug='sorcerer', name='Sorcerer', role='Damage caster', complexity='Moderate',
            quote='There is a storm under my skin, and today it gets out.',
            about='Magic runs in your blood and answers when you call. You deal the most damage of the '
                  'five and you are the easiest to hurt, so keep your friends between you and the danger. '
                  'Key things: Fire Bolt as often as you like, Burning Hands for a group, Scorching Ray for '
                  'one tough enemy, Shield when you are hit, and Telepathic Speech for a private word.',
            scores=dict(STR=8, DEX=13, CON=15, INT=10, WIS=12, CHA=17),
            saves=('CON', 'CHA'),
            skills=('Persuasion', 'Deception', 'Insight', 'Arcana'),
            ac='14', ac_note='Mage Armor (active)', hp='20', hit_dice='3d6', speed='30 ft.',
            attacks=[('Fire Bolt', '+5', '1d10 fire', 'Cantrip. Range 120 ft.'),
                     ('Dagger', '+3', '1d4+1 piercing', 'Melee, or thrown at range 20/60 ft.')],
            actions=[
                ('Bonus Actions', [
                    ('Telepathic Speech', '', 0,
                     'Choose a creature within 30 ft. For the next 3 minutes the two of you can speak mind '
                     'to mind while within 3 miles of each other. You must share a language.'),
                ]),
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
        ),
        dict(
            slug='artificer', name='Artificer', role='Inventor and support', complexity='Moderate',
            quote='Give me an hour and a box of scrap, and you will have a better plan.',
            about='You are an inventor who works magic through devices of your own making. Your reinforced '
                  'gear keeps you sturdy while you solve problems and keep your friends on their feet. Key '
                  'things: Cure Wounds, Guidance to help a friend\'s roll, Faerie Fire to make enemies easier '
                  'to hit, Detect Magic for anything strange, and one elixir to hand out.',
            scores=dict(STR=8, DEX=13, CON=15, INT=17, WIS=12, CHA=10),
            saves=('CON', 'INT'),
            skills=('Investigation', 'Arcana', 'Perception', 'Sleight of Hand'),
            ac='18', ac_note='Scale mail, shield, infusion', hp='24', hit_dice='3d8', speed='30 ft.',
            attacks=[('Ray of Frost', '+6', '1d8 cold',
                      'Cantrip. Range 60 ft. The target\'s speed drops 10 ft. for a turn.'),
                     ('Light Crossbow', '+3', '1d8+1 piercing', 'Range 80/320 ft.')],
            actions=[
                ('Special', [
                    ('Experimental Elixir', '1 / Long Rest', 1,
                     'You carry one flask. Choose what it is when it is drunk: Healing (regain 2d4+3 hit '
                     'points), Swiftness (+10 ft. of speed for 1 hour), or Boldness (+1d4 to every attack '
                     'roll and saving throw for 1 minute). Drinking it, or giving it to someone, takes an action.'),
                ]),
            ],
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
        ),
        dict(
            slug='bard', name='Bard', role='Charmer and support', complexity='Most options',
            quote='A sharp word, a good song, and somehow everyone walks out alive.',
            about='You work magic through words, music, and nerve. You are the best talker at the table and '
                  'the best at making everyone around you better. Key things: Bardic Inspiration to boost a '
                  'friend\'s roll, Healing Word, Vicious Mockery to rattle an enemy, and knowing the old '
                  'stories. This sheet has the most options of the five, so it suits someone who enjoys choices.',
            scores=dict(STR=8, DEX=15, CON=13, INT=10, WIS=12, CHA=17),
            saves=('DEX', 'CHA'),
            skills=('Persuasion', 'Deception', 'Performance', 'Insight', 'Sleight of Hand', 'History', 'Medicine'),
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
                ('Bonus Proficiencies',
                 'History and Medicine: the old songs, and how to tell if someone is hurt. Included.'),
            ],
        ),
    ],
)


# Every guest page the site carries, oldest first. Each is built to
# guests/<slug>.html. Slugs must not repeat.
GUEST_PAGES = [GUESTS]
