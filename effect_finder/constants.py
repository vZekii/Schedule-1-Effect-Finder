from typing import List, Dict, Set, Tuple, NamedTuple, Optional, FrozenSet

import colorama
from colorama import Fore, Style, Back


# --- Colorama Initialization ---
colorama.init(autoreset=True)  # Automatically resets color after each print

# Define some color constants for readability
C_RESET = Style.RESET_ALL
C_GREEN = Fore.GREEN
C_YELLOW = Fore.YELLOW
C_CYAN = Fore.CYAN
C_MAGENTA = Fore.MAGENTA
C_RED = Fore.RED
C_BLUE = Fore.BLUE
C_DIM = Style.DIM


# --- Ingredient Effects Data Structure ---
# Define a structure for what an ingredient does
class IngredientAction(NamedTuple):
    effect_to_add: str
    effects_to_remove: List[str]


# Ingredient name -> List of actions it performs
IngredientLookup = Dict[str, List[IngredientAction]]

# --- Corrected Base Ingredient Effects ---
INGREDIENTS_DATA: Dict[str, List[str]] = {
    "Energy Drink": ["Athletic"],
    "Mouth Wash": ["Balding"],
    "Battery": ["Bright-Eyed"],
    "Donut": ["Calorie-Dense"],
    "Cuke": ["Energizing"],
    "Mega Bean": ["Foggy"],
    "Banana": ["Gingeritis"],
    "Iodine": ["Jennerising"],
    "Horse Semen": ["Long-Faced"],
    "Flu Medicine": ["Sedating"],
    "Motor Oil": ["Slippery"],
    "Paracetamol": ["Sneaky"],
    "Chili": ["Spicy"],
    "Addy": ["Thought-Provoking"],
    "Gasoline": ["Toxic"],
    "Viagra": ["Tropic Thunder"],
}

INGREDIENTS_PRICES: Dict[str, int] = {
    "Energy Drink": 6,
    "Mouth Wash": 4,
    "Battery": 8,
    "Donut": 3,
    "Cuke": 2,
    "Mega Bean": 7,
    "Banana": 2,
    "Iodine": 8,
    "Horse Semen": 9,
    "Flu Medicine": 5,
    "Motor Oil": 6,
    "Paracetamol": 3,
    "Chili": 7,
    "Addy": 9,
    "Gasoline": 5,
    "Viagra": 4,
}


# --- Corrected Transformation Rules ---
# (Insert the large corrected effects_data dictionary from above here)
#
effects_data_from_text = {}


def add_rule(target_effect, ingredient, replaced_effects):
    """Helper to add rules, creating dicts/lists as needed."""
    if target_effect not in effects_data_from_text:
        effects_data_from_text[target_effect] = {"replaces": {}}
    if ingredient not in effects_data_from_text[target_effect]["replaces"]:
        effects_data_from_text[target_effect]["replaces"][ingredient] = []

    # Add effects ensuring no duplicates in the list for a single rule
    current_list = effects_data_from_text[target_effect]["replaces"][ingredient]
    for eff in replaced_effects:
        if eff not in current_list:
            current_list.append(eff)
    # Sort for consistency (optional, but helps comparison)
    # effects_data_from_text[target_effect]["replaces"][ingredient].sort()


# --- Process Text List ---

# Cuke
add_rule("Euphoric", "Cuke", ["Toxic"])
add_rule("Munchies", "Cuke", ["Slippery"])  # Note: Cuke also -> Athletic if Slippery
add_rule("Paranoia", "Cuke", ["Sneaky"])
add_rule("Cyclopean", "Cuke", ["Foggy"])
add_rule("Thought-Provoking", "Cuke", ["Gingeritis"])
add_rule("Athletic", "Cuke", ["Munchies"])
add_rule("Laxative", "Cuke", ["Euphoric"])
add_rule("Athletic", "Cuke", ["Slippery"])  # Combine with Munchies rule for Athletic

# Flu Medicine
add_rule("Bright-Eyed", "Flu Medicine", ["Calming"])
add_rule("Munchies", "Flu Medicine", ["Athletic"])
add_rule("Gingeritis", "Flu Medicine", ["Thought-Provoking"])
add_rule("Foggy", "Flu Medicine", ["Cyclopean"])
add_rule("Slippery", "Flu Medicine", ["Munchies"])
add_rule("Euphoric", "Flu Medicine", ["Laxative"])
add_rule("Toxic", "Flu Medicine", ["Euphoric"])
add_rule("Calming", "Flu Medicine", ["Focused"])
add_rule("Refreshing", "Flu Medicine", ["Electrifying"])
add_rule("Paranoia", "Flu Medicine", ["Shrinking"])

# Gasoline
add_rule("Euphoric", "Gasoline", ["Energizing"])  # Note: Also -> Spicy if Energizing
add_rule("Smelly", "Gasoline", ["Gingeritis"])
add_rule("Sneaky", "Gasoline", ["Jennerising"])
add_rule("Tropic Thunder", "Gasoline", ["Sneaky"])
add_rule("Sedating", "Gasoline", ["Munchies"])
add_rule("Spicy", "Gasoline", ["Energizing"])  # Note: Also -> Euphoric if Energizing
add_rule("Foggy", "Gasoline", ["Laxative"])
add_rule("Glowing", "Gasoline", ["Disorienting"])
add_rule("Calming", "Gasoline", ["Paranoia"])
add_rule("Disorienting", "Gasoline", ["Electrifying"])
add_rule("Focused", "Gasoline", ["Shrinking"])
add_rule("Spicy", "Gasoline", ["Euphoric"])  # Combine with Energizing rule for Spicy

# Donut
add_rule(
    "Explosive", "Donut", ["Calorie-Dense"]
)  # Ignoring "(and no Explosive)" for now
add_rule("Sneaky", "Donut", ["Balding"])
add_rule("Slippery", "Donut", ["Anti-Gravity"])
add_rule(
    "Gingeritis", "Donut", ["Jennerising"]
)  # Corrected typo Jenerising -> Jennerising
add_rule("Euphoric", "Donut", ["Focused"])
add_rule("Energizing", "Donut", ["Shrinking"])

# Energy Drink
add_rule("Munchies", "Energy Drink", ["Sedating"])
add_rule("Euphoric", "Energy Drink", ["Spicy"])
add_rule("Sneaky", "Energy Drink", ["Tropic Thunder"])
add_rule("Disorienting", "Energy Drink", ["Glowing"])
add_rule("Laxative", "Energy Drink", ["Foggy"])
add_rule("Electrifying", "Energy Drink", ["Disorienting"])
add_rule(
    "Balding", "Energy Drink", ["Schizophrenic"]
)  # Corrected typo Schizophrenia -> Schizophrenic
add_rule("Shrinking", "Energy Drink", ["Focused"])

# Mouth Wash
add_rule("Anti-Gravity", "Mouth Wash", ["Calming"])
add_rule("Sneaky", "Mouth Wash", ["Calorie-Dense"])
add_rule("Sedating", "Mouth Wash", ["Explosive"])
add_rule("Jennerising", "Mouth Wash", ["Focused"])

# Motor Oil
add_rule(
    "Munchies", "Motor Oil", ["Energizing"]
)  # Note: Also -> Schizophrenic if Energizing
add_rule("Toxic", "Motor Oil", ["Foggy"])
add_rule(
    "Schizophrenic", "Motor Oil", ["Energizing"]
)  # Note: Also -> Munchies if Energizing
add_rule("Sedating", "Motor Oil", ["Euphoric"])
add_rule("Anti-Gravity", "Motor Oil", ["Paranoia"])
add_rule(
    "Schizophrenic", "Motor Oil", ["Munchies"]
)  # Combine with Energizing rule for Schizophrenic

# Banana
add_rule(
    "Thought-Provoking", "Banana", ["Energizing"]
)  # Ignoring "(and no Cyclopean)" Note: Also -> TP if Cyclopean
add_rule("Sneaky", "Banana", ["Calming"])
add_rule("Smelly", "Banana", ["Toxic"])
add_rule("Refreshing", "Banana", ["Long-Faced"])
add_rule(
    "Thought-Provoking", "Banana", ["Cyclopean"]
)  # Combine with Energizing rule for Thought-Provoking
add_rule("Focused", "Banana", ["Disorienting"])
add_rule("Seizure-Inducing", "Banana", ["Focused"])
add_rule("Jennerising", "Banana", ["Paranoia"])

# Chili
add_rule("Euphoric", "Chili", ["Athletic"])
add_rule("Tropic Thunder", "Chili", ["Anti-Gravity"])
add_rule("Bright-Eyed", "Chili", ["Sneaky"])
add_rule("Toxic", "Chili", ["Munchies"])
add_rule("Long-Faced", "Chili", ["Laxative"])
add_rule("Refreshing", "Chili", ["Shrinking"])

# Iodine
add_rule("Balding", "Iodine", ["Calming"])
add_rule("Sneaky", "Iodine", ["Toxic"])
add_rule("Paranoia", "Iodine", ["Foggy"])
add_rule("Gingeritis", "Iodine", ["Calorie-Dense"])
add_rule("Seizure-Inducing", "Iodine", ["Euphoric"])
add_rule("Thought-Provoking", "Iodine", ["Refreshing"])

# Paracetamol
add_rule("Paranoia", "Paracetamol", ["Energizing"])  # Ignoring "(and no Munchies)"
add_rule("Slippery", "Paracetamol", ["Calming"])
add_rule("Tropic Thunder", "Paracetamol", ["Toxic"])
add_rule("Bright-Eyed", "Paracetamol", ["Spicy"])
add_rule("Toxic", "Paracetamol", ["Glowing"])
add_rule("Calming", "Paracetamol", ["Foggy"])
add_rule("Anti-Gravity", "Paracetamol", ["Munchies"])
add_rule("Balding", "Paracetamol", ["Paranoia"])
add_rule("Athletic", "Paracetamol", ["Electrifying"])
add_rule("Paranoia", "Paracetamol", ["Balding"])

# Viagra
add_rule("Sneaky", "Viagra", ["Athletic"])
add_rule("Bright-Eyed", "Viagra", ["Euphoric"])
add_rule("Calming", "Viagra", ["Laxative"])
add_rule("Toxic", "Viagra", ["Disorienting"])

# Mega Bean
add_rule(
    "Cyclopean", "Mega Bean", ["Energizing"]
)  # Ignoring "(and no Thought-Provoking)" Note: Also -> Cyclopean if TP
add_rule("Glowing", "Mega Bean", ["Calming"])  # Note: Also -> Glowing if Sneaky
add_rule("Calming", "Mega Bean", ["Sneaky"])
add_rule("Paranoia", "Mega Bean", ["Jennerising"])
add_rule("Laxative", "Mega Bean", ["Athletic"])
add_rule("Toxic", "Mega Bean", ["Slippery"])
add_rule("Energizing", "Mega Bean", ["Thought-Provoking"])
add_rule("Focused", "Mega Bean", ["Seizure-Inducing"])
add_rule("Disorienting", "Mega Bean", ["Focused"])
add_rule("Glowing", "Mega Bean", ["Sneaky"])  # Combine with Calming rule for Glowing
add_rule(
    "Cyclopean", "Mega Bean", ["Thought-Provoking"]
)  # Combine with Energizing rule for Cyclopean
add_rule("Electrifying", "Mega Bean", ["Shrinking"])

# Addy
add_rule("Gingeritis", "Addy", ["Sedating"])
add_rule("Electrifying", "Addy", ["Long-Faced"])  # Corrected "Long Faced"
add_rule("Refreshing", "Addy", ["Glowing"])
add_rule("Energizing", "Addy", ["Foggy"])
add_rule("Euphoric", "Addy", ["Explosive"])

# Battery
add_rule("Tropic Thunder", "Battery", ["Munchies"])
add_rule("Zombifying", "Battery", ["Euphoric"])  # Ignoring "(and no Electrifying)"
add_rule("Euphoric", "Battery", ["Electrifying"])  # Ignoring "(and no Zombifying)"
add_rule("Calorie-Dense", "Battery", ["Laxative"])
# add_rule("Euphoric", "Battery", ["Electrifying"]) # Duplicate already handled
add_rule("Munchies", "Battery", ["Shrinking"])

# Horse Semen (Corrected "Horse Semen")
add_rule("Calming", "Horse Semen", ["Anti-Gravity"])
add_rule("Refreshing", "Horse Semen", ["Gingeritis"])
add_rule("Electrifying", "Horse Semen", ["Thought-Provoking"])

# --- Pricing Data ---
BASE_PRICES = {
    "Weed": 35,
    "Meth": 70,
    "Cocaine": 150,
}

# NOTE: Effects missing from the provided table are assigned 0.0 multiplier.
# Lethal is excluded as it's noted as cheat-only.
# 'Anti-Gravity', 'Balding', 'Cyclopean', 'Energizing', 'Foggy', 'Glowing'
# 0.54, 0.3, 0.56, 0.22, 0.36, 0.48
# 2.46
EFFECT_MULTIPLIERS = {
    "Anti-Gravity": 0.54,
    "Athletic": 0.32,
    "Balding": 0.30,
    "Bright-Eyed": 0.40,
    "Calming": 0.10,
    "Calorie-Dense": 0.28,
    "Cyclopean": 0.56,
    "Disorienting": 0.00,
    "Electrifying": 0.50,
    "Energizing": 0.22,
    "Euphoric": 0.18,
    "Explosive": 0.00,
    "Focused": 0.16,
    "Foggy": 0.36,
    "Gingeritis": 0.20,
    "Glowing": 0.48,
    "Jennerising": 0.42,
    "Laxative": 0.00,
    "Long-Faced": 0.52,
    "Munchies": 0.12,
    "Paranoia": 0.00,
    "Refreshing": 0.14,
    "Schizophrenic": 0.00,
    "Sedating": 0.26,
    "Seizure-Inducing": 0.00,
    "Shrinking": 0.60,
    "Slippery": 0.34,
    "Smelly": 0.00,
    "Sneaky": 0.24,
    "Spicy": 0.38,
    "Thought-Provoking": 0.44,
    "Toxic": 0.00,
    "Tropic Thunder": 0.46,
    "Zombifying": 0.58,
    # Effects confirmed present in rules but NOT in the provided multiplier table
    # will be handled by the validation step below (assigned 0.0).
}

effects_data = effects_data_from_text

# --- Generate Set of All Valid Effects ---
ALL_VALID_EFFECTS: Set[str] = set()

# 1. Add base effects
for base_effects_list in INGREDIENTS_DATA.values():
    ALL_VALID_EFFECTS.update(base_effects_list)

# 2. Add effects from transformation rules
for target_effect, data in effects_data.items():
    # Add the effect produced by the transformation
    ALL_VALID_EFFECTS.add(target_effect)
    # Add all effects that are replaced by this transformation
    for replaced_effects_list in data.get("replaces", {}).values():
        ALL_VALID_EFFECTS.update(replaced_effects_list)
