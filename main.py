from typing import List, Dict, Set, Tuple, NamedTuple, Optional, FrozenSet
import collections
import colorama
from colorama import Fore, Style, Back
from heapq import nlargest
import sys
import argparse

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

# print(
#     f"{Style.BRIGHT}Discovered {len(ALL_VALID_EFFECTS)} unique valid effects.{C_RESET}"
# )


# # --- Validate Multiplier Data ---
# print(f"\n{Style.BRIGHT}Validating Effect Multipliers...{C_RESET}")
# missing_multipliers = []
# invalid_multiplier_keys = []
# for effect in ALL_VALID_EFFECTS:
#     if effect not in EFFECT_MULTIPLIERS:
#         missing_multipliers.append(effect)
#         EFFECT_MULTIPLIERS[effect] = 0.0  # Assign default 0.0

# for effect_key in EFFECT_MULTIPLIERS.keys():
#     if effect_key not in ALL_VALID_EFFECTS:
#         invalid_multiplier_keys.append(effect_key)

# if missing_multipliers:
#     print(
#         f"{C_YELLOW}Warning:{C_RESET} Effects missing from multiplier list (assigned 0.0): {C_YELLOW}{sorted(missing_multipliers)}{C_RESET}"
#     )
# else:
#     print(f"{C_GREEN}✓ All valid effects have multiplier entries.{C_RESET}")

# if invalid_multiplier_keys:
#     print(
#         f"{C_RED}Error:{C_RESET} Invalid effect names found as keys in EFFECT_MULTIPLIERS: {C_RED}{sorted(invalid_multiplier_keys)}{C_RESET}"
#     )
#     raise ValueError("Invalid keys found in EFFECT_MULTIPLIERS.")
# else:
#     print(f"{C_GREEN}✓ EFFECT_MULTIPLIERS keys are valid effect names.{C_RESET}")


def calculate_product_price(
    base_product_name: str, final_effects: Set[str]
) -> Optional[int]:
    """Calculates the final product price based on effects."""

    if base_product_name not in BASE_PRICES:
        print(
            f"{C_RED}Error: Unknown base product '{base_product_name}'. Valid options: {list(BASE_PRICES.keys())}{C_RESET}"
        )
        return None

    base_price = BASE_PRICES[base_product_name]
    sum_of_multipliers = 0.0
    unknown_effects_found = []

    for effect in final_effects:
        multiplier = EFFECT_MULTIPLIERS.get(effect)  # Safely get multiplier
        if multiplier is None:
            # This case should be prevented by the validation step, but good practice
            if effect not in unknown_effects_found:  # Avoid duplicate warnings per run
                print(
                    f"{C_YELLOW}Warning:{C_RESET} Unknown effect '{effect}' found during price calculation (multiplier treated as 0.0)."
                )
                unknown_effects_found.append(effect)
            multiplier = 0.0
        sum_of_multipliers += multiplier

    final_price = round(base_price * (1.0 + sum_of_multipliers))
    return final_price


def build_ingredient_lookup(data: Dict) -> IngredientLookup:
    """Builds the lookup table from the structured effects_data."""
    lookup: IngredientLookup = {}
    for effect_name, effect_data in data.items():
        # ingredients_list = effect_data.get("ingredients", []) # We don't strictly need this list if using replaces
        replaces_dict = effect_data.get("replaces", {})
        for ingredient, removes_list in replaces_dict.items():
            # Ensure removes_list is actually a list and not empty
            # (empty list means no transformation defined here)
            if removes_list:
                action = IngredientAction(
                    effect_to_add=effect_name, effects_to_remove=removes_list
                )
                if ingredient not in lookup:
                    lookup[ingredient] = []
                # Avoid adding duplicate actions if data has redundancy
                if action not in lookup[ingredient]:
                    lookup[ingredient].append(action)
    return lookup


# --- Data Validation Step ---
def validate_data_effects(data_dict, context_name, valid_set):
    """Checks effects within INGREDIENTS_DATA or effects_data."""
    errors_found = []
    if context_name == "INGREDIENTS_DATA":
        for ingredient, effects in data_dict.items():
            for effect in effects:
                if effect not in valid_set:
                    errors_found.append(
                        f"Invalid base effect '{C_RED}{effect}{C_RESET}' for ingredient '{C_YELLOW}{ingredient}{C_RESET}' in {context_name}."
                    )
    elif context_name == "effects_data":
        for target_effect, data in data_dict.items():
            if target_effect not in valid_set:
                errors_found.append(
                    f"Invalid target effect '{C_RED}{target_effect}{C_RESET}' used as key in {context_name}."
                )
            for ingredient, replaced_effects in data.get("replaces", {}).items():
                for effect in replaced_effects:
                    if effect not in valid_set:
                        errors_found.append(
                            f"Invalid replaced effect '{C_RED}{effect}{C_RESET}' for target '{C_MAGENTA}{target_effect}{C_RESET}' / ingredient '{C_YELLOW}{ingredient}{C_RESET}' in {context_name}."
                        )
    else:
        raise ValueError(f"Unknown context for validation: {context_name}")

    if errors_found:
        print(
            f"\n{Back.RED}{Style.BRIGHT}!--- Validation Errors in Core Data ({context_name}) ---!{C_RESET}"
        )
        for error in errors_found:
            print(f"  - {error}")
        raise ValueError(
            f"Invalid effect names found in {context_name}. Please correct the data definitions."
        )
    else:
        print(
            f"{C_GREEN}✓ Effect names in {context_name} validated successfully.{C_RESET}"
        )


# Perform validation immediately after defining data and ALL_VALID_EFFECTS
# validate_data_effects(INGREDIENTS_DATA, "INGREDIENTS_DATA", ALL_VALID_EFFECTS)
# validate_data_effects(effects_data, "effects_data", ALL_VALID_EFFECTS)

# Build the lookup table once
ingredient_lookup = build_ingredient_lookup(effects_data)


# --- Optimized Application Logic ---


def apply_ingredient_optimized(current_effects: Set[str], ingredient: str) -> Set[str]:
    """
    Applies ingredient effects based on the corrected logic using sets.
    1. Stores the initial state (before adding base effects).
    2. Adds base effects from INGREDIENTS_DATA.
    3. Determines transformations based on the *initial* state and the ingredient_lookup.
    4. Applies transformations (removals first, then additions).
    """
    initial_effects_set = current_effects.copy()  # State before this ingredient
    final_effects_set = current_effects.copy()  # Working set, starts same as initial

    # 1. Generation Step
    base_effects_to_add = INGREDIENTS_DATA.get(ingredient, [])
    final_effects_set.update(base_effects_to_add)

    # 2. Transformation Step - Identify based on initial state
    possible_actions = ingredient_lookup.get(ingredient, [])
    effects_to_add_via_transform: Set[str] = set()
    effects_to_remove_via_transform: Set[str] = set()

    if possible_actions:
        for action in possible_actions:
            target_effect = action.effect_to_add
            potential_removals = action.effects_to_remove

            # Check if any effect to be replaced was present in the *initial* set
            made_replacement = False
            for eff_to_replace in potential_removals:
                if eff_to_replace in initial_effects_set:  # Check ORIGINAL effects
                    effects_to_remove_via_transform.add(eff_to_replace)
                    made_replacement = True

            # If a replacement was triggered by this action, queue the target effect
            if made_replacement:
                effects_to_add_via_transform.add(target_effect)

    # 3. Apply Transformations to the working set
    final_effects_set.difference_update(effects_to_remove_via_transform)
    final_effects_set.update(effects_to_add_via_transform)

    return final_effects_set


ALL_INGREDIENTS = sorted(
    list(INGREDIENTS_DATA.keys())
)  # Get all possible ingredients once


def find_shortest_product_sequence(
    target_effects: List[str],
    starting_effects: Optional[List[str]] = None,
    product_name: Optional[str] = None,
    max_ingredients: int = 8,
    debug_specific_sequence: Optional[List[str]] = None,
) -> Optional[List[str]]:
    """
    Finds the shortest sequence of additional ingredients (up to max_ingredients)
    starting from a given initial state (or named product), that results
    in a state including all target_effects. Uses Breadth-First Search.
    Outputs results with terminal colors.

    Args:
        target_effects: A list of effect names that must be present.
        starting_effects: An optional list of effects already present.
        product_name: An optional name for the starting product state.
        max_ingredients: The maximum number of *additional* ingredients allowed.
        debug_specific_sequence: If provided, prints detailed info only for
                                 steps along this exact sequence path.

    Returns:
        The shortest list of additional ingredients if a solution is found
        within the limit, otherwise None. Returns [] if starting_effects
        already meet the target.
    """
    # --- Input Validation ---
    valid_target_effects = []
    invalid_targets = []
    for effect in target_effects:
        if effect in ALL_VALID_EFFECTS:
            valid_target_effects.append(effect)
        else:
            invalid_targets.append(effect)

    if invalid_targets:
        print(
            f"{C_YELLOW}Warning:{C_RESET} Invalid target effects provided and ignored: {C_RED}{invalid_targets}{C_RESET}"
        )

    target_set: Set[str] = set(valid_target_effects)  # Use only valid targets
    if not target_set:
        print(
            f"{C_YELLOW}Target effects list is empty or contained only invalid effects. Cannot search. Solution is [].{C_RESET}"
        )
        return []

    # Validate Starting Effects
    initial_effects_set = set()
    if starting_effects is not None:
        valid_starting_effects = []
        invalid_starting = []
        for effect in starting_effects:
            if effect in ALL_VALID_EFFECTS:
                valid_starting_effects.append(effect)
            else:
                invalid_starting.append(effect)
        if invalid_starting:
            print(
                f"{C_YELLOW}Warning:{C_RESET} Invalid starting effects provided and ignored: {C_RED}{invalid_starting}{C_RESET}"
            )
        initial_effects_set = set(
            valid_starting_effects
        )  # Use only valid starting effects

    initial_effects_frozen = frozenset(initial_effects_set)

    # --- Determine Starting product Display Name ---
    start_display_name = (
        product_name
        if product_name
        else ("Empty product" if not initial_effects_set else "Unnamed product")
    )

    print(
        f"\n{Style.BRIGHT}Searching for shortest sequence{C_RESET} (max {max_ingredients} added ingredients)"
    )
    print(f"  Starting product: {C_YELLOW}{start_display_name}{C_RESET}")
    if initial_effects_set:  # Only show effects if they exist
        print(
            f"    {C_DIM}Contains Effects: {sorted(list(initial_effects_set))}{C_RESET}"
        )
    print(f"  Target Effects:  {C_YELLOW}{sorted(list(target_set))}{C_RESET}")

    # --- Initial Check ---
    if target_set.issubset(initial_effects_set):
        print(
            f"\n{C_GREEN}Starting product '{start_display_name}' already meets the target criteria.{C_RESET}"
        )
        print(f"  {C_GREEN}Solution Found!{C_RESET}")
        print(f"  Sequence ({C_CYAN}0{C_RESET} added ingredients): []")
        print(
            f"  Resulting Effects: {C_DIM}{sorted(list(initial_effects_set))}{C_RESET}"
        )
        return []

    # --- Initialize BFS ---
    queue = collections.deque([(initial_effects_frozen, [])])
    visited: Set[FrozenSet[str]] = {initial_effects_frozen}
    visited_paths: Dict[FrozenSet[str], List[str]] = {initial_effects_frozen: []}

    while queue:
        current_effects_frozen, added_sequence = queue.popleft()
        current_effects_set = set(current_effects_frozen)

        # --- Targeted Debug Output (Dequeue) ---
        on_debug_path_prefix = False
        if (
            debug_specific_sequence
            and added_sequence == debug_specific_sequence[: len(added_sequence)]
        ):
            on_debug_path_prefix = True
            print(
                f"{C_BLUE}{Style.DIM}"
                + "-" * 10
                + f" DEBUG: Dequeued state for sequence prefix: {added_sequence} "
                + "-" * 10
            )
            print(f"  State: {sorted(list(current_effects_set))}{C_RESET}")

        # --- Check Depth Limit ---
        if len(added_sequence) >= max_ingredients:
            continue

        # --- Explore Neighbors ---
        for ingredient in ALL_INGREDIENTS:
            next_effects_set = apply_ingredient_optimized(
                current_effects_set, ingredient
            )
            next_effects_frozen = frozenset(next_effects_set)
            next_sequence = added_sequence + [ingredient]

            # --- Targeted Debug Output (Transition) ---
            is_next_debug_step = False
            if (
                on_debug_path_prefix
                and debug_specific_sequence
                and len(next_sequence) <= len(debug_specific_sequence)
                and next_sequence == debug_specific_sequence[: len(next_sequence)]
            ):
                is_next_debug_step = True
                print(
                    f"\n{C_BLUE}{Style.DIM}  DEBUG: -> Applying '{C_CYAN}{ingredient}{C_BLUE}{Style.DIM}' (Expected next step in debug sequence)"
                )
                print(f"     Result State: {sorted(list(next_effects_set))}")
                print(f"     Is Solution?: {target_set.issubset(next_effects_set)}")
                print(f"     Already Visited?: {next_effects_frozen in visited}")
                if next_effects_frozen in visited:
                    previous_path = visited_paths.get(
                        next_effects_frozen, ["(Path not tracked?)"]
                    )
                    print(
                        f"     !!! Visited via sequence: {previous_path} !!!{C_RESET}"
                    )

            if next_effects_frozen not in visited:
                visited.add(next_effects_frozen)
                visited_paths[next_effects_frozen] = next_sequence  # Store path

                if target_set.issubset(next_effects_set):
                    # Format ingredient list with color
                    seq_str = f"[{', '.join(f'{C_CYAN}{ing}{C_RESET}' for ing in next_sequence)}]"

                    if is_next_debug_step:
                        print(
                            f"{C_BLUE}{Style.DIM}     DEBUG: Solution found on this path step!{C_RESET}"
                        )
                    print(f"\n{C_GREEN}Solution Found!{C_RESET}")
                    print(
                        f"  Sequence ({C_MAGENTA}{len(next_sequence)}{C_RESET} added ingredients): {seq_str}"
                    )
                    print(
                        f"  Resulting Effects: {C_DIM}{sorted(list(next_effects_set))}{C_RESET}"
                    )
                    return next_sequence

                queue.append((next_effects_frozen, next_sequence))

            elif is_next_debug_step and target_set.issubset(next_effects_set):
                print(
                    f"{C_BLUE}{Style.DIM}  DEBUG: State is solution BUT was already visited.{C_RESET}"
                )

    # If queue becomes empty and no solution was found
    print(
        f"\n{C_RED}No solution found{C_RESET} adding up to {max_ingredients} ingredients for target: {C_YELLOW}{sorted(list(target_set))}{C_RESET}"
    )
    return None


def apply_ingredients_sequence_optimized(
    starting_effects: List[str], ingredients: List[str]
) -> List[str]:
    """
    Applies a sequence of ingredients, printing the state after each step.
    Uses the optimized set-based logic for applying individual ingredients.

    Args:
        starting_effects: A list of effects present before starting.
        ingredients: A list of ingredient names to apply in order.

    Returns:
        A sorted list of the final effects present after applying all ingredients.
    """
    # Assume inputs might contain invalid effects/ingredients if called directly
    # Filter them out for robustness
    valid_start_effects = {eff for eff in starting_effects if eff in ALL_VALID_EFFECTS}
    valid_ingredients = [ing for ing in ingredients if ing in ALL_INGREDIENTS]

    current_set = valid_start_effects
    print(
        f"Initial Effects: {C_DIM}{sorted(list(current_set)) if current_set else '[]'}{C_RESET}"
    )

    if not valid_ingredients:
        print(
            f"{C_YELLOW}Warning: No valid ingredients in the sequence to apply.{C_RESET}"
        )
        return sorted(list(current_set))

    for i, ing in enumerate(valid_ingredients):
        print(
            f"\n{Style.BRIGHT}Step {i+1}: Applying ingredient: {C_CYAN}{ing}{C_RESET}"
        )
        previous_set = current_set.copy()  # Keep track to see if changes occurred
        current_set = apply_ingredient_optimized(current_set, ing)
        changed_effects = current_set != previous_set
        added = current_set - previous_set
        removed = previous_set - current_set

        if not changed_effects:
            print(f"  Result: {C_DIM}(No change){C_RESET}")
            print(f"  Current Effects: {C_DIM}{sorted(list(current_set))}{C_RESET}")

        else:
            print(f"  Result: {sorted(list(current_set))}")
            if added:
                added_str = f"{', '.join(f'{C_GREEN}{eff}{C_RESET}' for eff in sorted(list(added)))}"
                print(f"    {C_GREEN}Added:   {added_str}")
            if removed:
                removed_str = f"{', '.join(f'{C_RED}{eff}{C_RESET}' for eff in sorted(list(removed)))}"
                print(f"    {C_RED}Removed: {removed_str}")

    final_sorted_list = sorted(list(current_set))
    print(
        f"\n--- {Style.BRIGHT}Final Effects after {len(valid_ingredients)} steps{C_RESET} ---"
    )
    print(f"{C_DIM}{final_sorted_list}{C_RESET}")
    return final_sorted_list


def find_most_expensive_products(
    base_product_name: str,
    max_ingredients: int,
    num_results: int = 10,  # How many top results to display
) -> List[Tuple[int, List[str], Set[str]]]:
    """
    Finds product sequences resulting in the highest prices using BFS.

    Args:
        base_product_name: Name of the starting product ("Weed", "Meth", "Cocaine").
        max_ingredients: The maximum number of ingredients in the sequence.
        num_results: The number of top-priced results to return.

    Returns:
        A list of tuples, sorted by price descending:
        [(price, sequence_list, final_effects_set), ...]
    """

    if base_product_name not in BASE_PRICES:
        print(
            f"{C_RED}Error: Unknown base product '{base_product_name}'. Valid options: {list(BASE_PRICES.keys())}{C_RESET}"
        )
        return []

    print(
        f"\n{Style.BRIGHT}Searching for Top {num_results} Most Expensive products{C_RESET}"
    )
    print(
        f"  Base Product:    {C_YELLOW}{base_product_name}{C_RESET} (${BASE_PRICES[base_product_name]})"
    )
    print(f"  Max Ingredients: {C_MAGENTA}{max_ingredients}{C_RESET}")

    # --- Initialize BFS ---
    initial_effects_frozen = frozenset()
    queue = collections.deque([(initial_effects_frozen, [])])
    # Visited stores frozensets of *states* to avoid redundant exploration
    # We still process sequences leading to already visited states if the sequence is new/shorter
    visited_states: Set[FrozenSet[str]] = {initial_effects_frozen}

    # Store results: (price, sequence, effects_set)
    # Using a list and then sorting/heapq is easier than managing a complex sorted structure during BFS
    all_results = []

    processed_count = 0
    while queue:
        current_effects_frozen, current_sequence = queue.popleft()
        current_effects_set = set(current_effects_frozen)
        processed_count += 1

        # --- Calculate and store price for the *current* state/sequence ---
        # We calculate price for every state reached within the limit
        current_price = calculate_product_price(base_product_name, current_effects_set)
        if (
            current_price is not None
        ):  # Should always be not None if base product is valid
            all_results.append((current_price, current_sequence, current_effects_set))

        # --- Check Depth Limit ---
        if len(current_sequence) >= max_ingredients:
            continue  # Stop exploring further down this path

        # --- Explore Neighbors ---
        for ingredient in ALL_INGREDIENTS:
            # Calculate next state only once per ingredient transition
            next_effects_set = apply_ingredient_optimized(
                current_effects_set, ingredient
            )
            next_effects_frozen = frozenset(next_effects_set)

            # We only add to the queue if the *state* hasn't been visited
            # by *any* path yet, to avoid cycles and redundant BFS branches.
            # However, we calculate the price for *every* path terminus above.
            if next_effects_frozen not in visited_states:
                visited_states.add(next_effects_frozen)
                next_sequence = current_sequence + [ingredient]
                queue.append((next_effects_frozen, next_sequence))

    print(f"{C_DIM}Processed {processed_count} states/sequences.{C_RESET}")

    # --- Find Top Results ---
    # Use heapq.nlargest for efficiency, especially if all_results is huge
    # Sort key is the price (first element of the tuple)
    top_results = nlargest(num_results, all_results, key=lambda item: item[0])

    # --- Print Top Results ---
    print(f"\n{Style.BRIGHT}Top {len(top_results)} Results:{C_RESET}")
    if not top_results:
        print(f"  {C_YELLOW}No results found (check max_ingredients).{C_RESET}")
    else:
        for i, (price, sequence, effects) in enumerate(top_results):
            seq_str = (
                f"[{', '.join(f'{C_CYAN}{ing}{C_RESET}' for ing in sequence)}]"
                if sequence
                else "[](Base)"
            )
            print(f"  {i+1}. Price: {C_GREEN}${price}{C_RESET}")
            print(f"     Sequence ({len(sequence)} ingredients): {seq_str}")
            print(f"     {C_DIM}Effects: {sorted(list(effects))}{C_RESET}")

    return top_results


def try_all_ingredients(sequence):
    """
    Test all ingredients in the system to see if they produce the expected base effects.
    This is a sanity check to ensure that the base effects are correctly defined.
    """
    find_shortest_product_sequence(
        sequence, max_ingredients=8, starting_effects=[], product_name="Meth"
    )

    find_shortest_product_sequence(
        sequence,
        max_ingredients=8,
        starting_effects=["Calming"],
        product_name="Og Kush",
    )

    find_shortest_product_sequence(
        sequence,
        max_ingredients=8,
        starting_effects=["Refreshing"],
        product_name="Sour Diesel",
    )

    find_shortest_product_sequence(
        sequence,
        max_ingredients=8,
        starting_effects=["Energizing"],
        product_name="Green Crack",
    )

    find_shortest_product_sequence(
        sequence,
        max_ingredients=8,
        starting_effects=["Sedating"],
        product_name="Granddaddy Purple",
    )


# if __name__ == "__main__":
#     try_all_ingredients(
#         ["Shrinking", "Zombifying", "Cyclopean", "Anti-Gravity", "Long-Faced"]
#     )
#     find_most_expensive_products("Meth", 8, num_results=10)


def run_effects_calculation(
    sequence: List[str], start_effects: Optional[List[str]], product_name: Optional[str]
):
    """Helper function to run and display effect sequence calculation."""
    # --- Input Validation ---
    valid_starting_effects = set()
    if start_effects:
        invalid_starting = []
        for effect in start_effects:
            if effect in ALL_VALID_EFFECTS:
                valid_starting_effects.add(effect)
            else:
                invalid_starting.append(effect)
        if invalid_starting:
            print(
                f"{C_YELLOW}Warning:{C_RESET} Invalid starting effects provided and ignored: {C_RED}{invalid_starting}{C_RESET}"
            )

    valid_sequence = []
    invalid_ingredients = []
    for ingredient in sequence:
        if ingredient in ALL_INGREDIENTS:
            valid_sequence.append(ingredient)
        else:
            invalid_ingredients.append(ingredient)
    if invalid_ingredients:
        print(
            f"{C_YELLOW}Warning:{C_RESET} Invalid ingredients provided and ignored: {C_RED}{invalid_ingredients}{C_RESET}"
        )

    if not valid_sequence:
        print(f"{C_RED}Error: No valid ingredients provided in the sequence.{C_RESET}")
        return

    start_display_name = (
        product_name
        if product_name
        else ("Empty product" if not valid_starting_effects else "Unnamed product")
    )

    print(f"\n{Style.BRIGHT}Calculating Effects{C_RESET}")
    print(f"  Starting product: {C_YELLOW}{start_display_name}{C_RESET}")
    if valid_starting_effects:
        print(
            f"    {C_DIM}Contains Effects: {sorted(list(valid_starting_effects))}{C_RESET}"
        )
    # Use the internal function that prints step-by-step
    apply_ingredients_sequence_optimized(list(valid_starting_effects), valid_sequence)


def main():
    parser = argparse.ArgumentParser(
        description=f"{Style.BRIGHT}Product Calculator CLI{C_RESET}",
        formatter_class=argparse.RawTextHelpFormatter,  # Allows better formatting in help
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Action to perform"
    )

    # --- Subparser: effects ---
    parser_effects = subparsers.add_parser(
        "effects", help="Calculate the final effects of an ingredient sequence."
    )
    parser_effects.add_argument(
        "ingredients",
        metavar="INGREDIENT",
        nargs="+",  # one or more ingredients
        help=f'Sequence of ingredients to add (e.g., "Mega Bean" "Energy Drink"). Valid: {sorted(ALL_INGREDIENTS)}',
    )
    parser_effects.add_argument(
        "--start-effects",
        metavar="EFFECT",
        nargs="*",  # zero or more
        default=[],
        help="Optional list of effects present before adding ingredients.",
    )
    parser_effects.add_argument(
        "--product-name",
        help="Optional name for the starting product if --start-effects are provided.",
    )

    # --- Subparser: shortest ---
    parser_shortest = subparsers.add_parser(
        "shortest", help="Find the shortest sequence to achieve target effects."
    )
    parser_shortest.add_argument(
        "target_effects",
        metavar="EFFECT",
        nargs="+",
        help="List of desired effects that must be present.",
    )
    parser_shortest.add_argument(
        "--start-effects",
        metavar="EFFECT",
        nargs="*",
        default=None,  # Pass None if not provided
        help="Optional list of effects present before adding ingredients.",
    )
    parser_shortest.add_argument(
        "--product-name",
        help="Optional name for the starting product if --start-effects are provided.",
    )
    parser_shortest.add_argument(
        "--max-ingredients",
        type=int,
        default=8,
        help="Maximum number of *additional* ingredients to try (default: 8).",
    )

    # --- Subparser: expensive ---
    parser_expensive = subparsers.add_parser(
        "expensive", help="Find the most expensive products."
    )
    parser_expensive.add_argument(
        "base_product",
        choices=list(BASE_PRICES.keys()),
        help="The starting base product.",
    )
    parser_expensive.add_argument(
        "max_ingredients", type=int, help="Maximum number of ingredients to mix."
    )
    parser_expensive.add_argument(
        "--num-results",
        type=int,
        default=10,
        help="Number of top results to display (default: 10).",
    )

    # --- Subparser: price ---
    parser_price = subparsers.add_parser(
        "price", help="Calculate the price for a given base product and effect list."
    )
    parser_price.add_argument(
        "base_product",
        choices=list(BASE_PRICES.keys()),
        help="The starting base product.",
    )
    parser_price.add_argument(
        "effects",
        metavar="EFFECT",
        nargs="+",
        help="List of final effects present in the product.",
    )

    # --- Parse Arguments ---
    if len(sys.argv) == 1:  # If run with no arguments, print help
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    # --- Execute Command ---
    try:  # Wrap in try block to catch validation errors during data loading if not caught earlier
        if args.command == "effects":
            # Need apply_ingredients_sequence_optimized or a wrapper
            run_effects_calculation(
                args.ingredients, args.start_effects, args.product_name
            )

        elif args.command == "shortest":
            find_shortest_product_sequence(
                target_effects=args.target_effects,
                starting_effects=args.start_effects,
                product_name=args.product_name,
                max_ingredients=args.max_ingredients,
                # debug_specific_sequence could be added as another arg if needed
            )

        elif args.command == "expensive":
            find_most_expensive_products(
                base_product_name=args.base_product,
                max_ingredients=args.max_ingredients,
                num_results=args.num_results,
            )

        elif args.command == "price":
            # Validate input effects for price calculation
            valid_effects = set()
            invalid_effects = []
            for effect in args.effects:
                if effect in ALL_VALID_EFFECTS:
                    valid_effects.add(effect)
                else:
                    invalid_effects.append(effect)

            if invalid_effects:
                print(
                    f"{C_YELLOW}Warning:{C_RESET} Invalid effects provided and ignored for price calc: {C_RED}{invalid_effects}{C_RESET}"
                )

            if not valid_effects:
                print(
                    f"{C_RED}Error: No valid effects provided for price calculation.{C_RESET}"
                )
            else:
                final_price = calculate_product_price(args.base_product, valid_effects)
                if final_price is not None:
                    print(f"\nCalculating Price:")
                    print(f"  Base Product: {C_YELLOW}{args.base_product}{C_RESET}")
                    print(
                        f"  Effects (valid): {C_DIM}{sorted(list(valid_effects))}{C_RESET}"
                    )
                    print(
                        f"  {Style.BRIGHT}Calculated Price: {C_GREEN}${final_price}{C_RESET}"
                    )

    except ValueError as e:
        print(f"\n{Back.RED}{Style.BRIGHT}Runtime Error:{C_RESET} {C_RED}{e}{C_RESET}")
        sys.exit(1)
    except Exception as e:
        print(
            f"\n{Back.RED}{Style.BRIGHT}An unexpected error occurred:{C_RESET} {C_RED}{e}{C_RESET}"
        )

        sys.exit(1)


if __name__ == "__main__":
    # Any setup that needs to run once can go here (like colorama init)

    # Run the main command-line handler
    main()
