# Default settings
framerate = 60

# Load colors
Colors = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 150, 0),
    "pink": (255, 0, 150),
    "purple": (150, 0, 255),
    "cyan": (0, 255, 255),
    "teal": (0, 150, 255),
    "lime": (150, 255, 0),
    "seafoam": (0, 255, 150),
    "magenta": (255, 0, 255),
    "gold": (255, 215, 0),
    "black": (0, 0, 0),
    "silver": (240, 240, 240),
    "grey": (150, 150, 150),
}

# initialize variables
# strings
fuse_type = "self"
game_state = "main_menu"
# boolean
LeftHold = LeftClick = strike = strike_hold = False
encounter = victory = enemy_attack = False
enemy_done = attack_state = False
buttoncheck = RightClick = False
RightHold = MiddleClick = False
show_band = info_button = False
pause = attack_setup = band_sort = False
y_neg = band_init = fuse_complete = fuse_setup = False
swap_ready = selection_made = claimed = False
build_pixite = build_voxite = False
build_doxite = build_tyxite = False

# numeric variables
win_count = 0
energy = 100
experience = 0
next_class = 100
HoldStart = 0
death_time = 0
y_walk = 0
y_btn = 65  # build button
dB = 1.0
pixite = 12
voxite = 7
doxite = 1
tyxite = 0
num_display = num_total = results_timer = 0
fuse_counter = fuse_num = fuse_timer = 0
swap_x = swap_y = scroll = x = y = xx = 0
journey_timer = num_fights = fail_time = 0
victory_time = enemy_xp = overkill = 0
queue = 0
attack_counter = 0
attack_timer = 0
dt = 0
true_counter = 0
realtime = 0
frame_counter = 0
space = 180
bx = 100
by = 220

# lists and tuples
name_fuse = ["Fodder", "Ikuppi", "Banunu", "Sirsir"]
stash_names = ["pixite", "voxite", "doxite", "tyxite"]
stash_rgb = [Colors["orange"], Colors["silver"], Colors["yellow"], Colors["red"]]
cat = ["", "HP ", "ATK", "DEF", "WIS", "AGI", "LV ", "SEF", ""]
pull = fuse_dict = reserves = {}
barracks = {}
attack_order = {}
check_fuse = fuse_list = prize = odds = []
frontline = []
swipe_order = []
xyz = []
og_health = []
damage = [0, 0, 0]
dmg_color = [Colors["orange"],] * 3

class Fighter:
    def __init__(self, name, keyname):
        self.name = name
        self.keyname = keyname
        self.HP = 0
        self.ATK = 0
        self.DEF = 0
        self.WIS = 0
        self.AGI = 0
        self.LV = 1
        self.SEF = 0
        self.XP = 0
        self.rarity = "Common"
        self.tribe = "null"
        self.sign = "null"
        self.type = "null"

empty = Fighter("-", "empty")
selection = empty

