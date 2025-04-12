from typing import List, Dict, Set, Tuple, NamedTuple, Optional, FrozenSet
import collections
from heapq import nlargest
import sys

import argparse
from colorama import Fore, Style, Back

import constants
from constants import C_RESET, C_GREEN, C_YELLOW, C_CYAN, C_MAGENTA, C_RED, C_BLUE, C_DIM


def calculate_product_price(base_product_name: str, final_effects: Set[str]) -> Optional[int]:
    """Calculates the final product price based on effects."""

    if base_product_name not in constants.BASE_PRICES:
        print(f"{C_RED}Error: Unknown base product '{base_product_name}'.")
        print(f"Valid options: {list(constants.BASE_PRICES.keys())}{C_RESET}")
        return None

    base_price = constants.BASE_PRICES[base_product_name]
    sum_of_multipliers = 0.0
    unknown_effects_found = []

    for effect in final_effects:
        multiplier = constants.EFFECT_MULTIPLIERS.get(effect)  # Safely get multiplier
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


def build_ingredient_lookup(data: Dict) -> constants.IngredientLookup:
    """Builds the lookup table from the structured effects_data."""
    lookup: constants.IngredientLookup = {}
    for effect_name, effect_data in data.items():
        # ingredients_list = effect_data.get("ingredients", []) # We don't strictly need this list if using replaces
        replaces_dict = effect_data.get("replaces", {})
        for ingredient, removes_list in replaces_dict.items():
            # Ensure removes_list is actually a list and not empty
            # (empty list means no transformation defined here)
            if removes_list:
                action = constants.IngredientAction(
                    effect_to_add=effect_name, effects_to_remove=removes_list
                )
                if ingredient not in lookup:
                    lookup[ingredient] = []
                # Avoid adding duplicate actions if data has redundancy
                if action not in lookup[ingredient]:
                    lookup[ingredient].append(action)
    return lookup


# Build the lookup table once
ingredient_lookup = build_ingredient_lookup(constants.effects_data)


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
    base_effects_to_add = constants.INGREDIENTS_DATA.get(ingredient, [])
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
    list(constants.INGREDIENTS_DATA.keys())
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
        if effect in constants.ALL_VALID_EFFECTS:
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
            if effect in constants.ALL_VALID_EFFECTS:
                valid_starting_effects.append(effect)
            else:
                invalid_starting.append(effect)
        if invalid_starting:
            print(
                f"{C_YELLOW}Warning:{C_RESET} Invalid starting effects provided and ignored: {C_RED}{invalid_starting}{C_RESET}"
            )
        initial_effects_set = set(valid_starting_effects)  # Use only valid starting effects

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
        print(f"    {C_DIM}Contains Effects: {sorted(list(initial_effects_set))}{C_RESET}")
    print(f"  Target Effects:  {C_YELLOW}{sorted(list(target_set))}{C_RESET}")

    # --- Initial Check ---
    if target_set.issubset(initial_effects_set):
        print(
            f"\n{C_GREEN}Starting product '{start_display_name}' already meets the target criteria.{C_RESET}"
        )
        print(f"  {C_GREEN}Solution Found!{C_RESET}")
        print(f"  Sequence ({C_CYAN}0{C_RESET} added ingredients): []")
        print(f"  Resulting Effects: {C_DIM}{sorted(list(initial_effects_set))}{C_RESET}")
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
            next_effects_set = apply_ingredient_optimized(current_effects_set, ingredient)
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
                    previous_path = visited_paths.get(next_effects_frozen, ["(Path not tracked?)"])
                    print(f"     !!! Visited via sequence: {previous_path} !!!{C_RESET}")

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
                    print(f"  Resulting Effects: {C_DIM}{sorted(list(next_effects_set))}{C_RESET}")
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
    valid_start_effects = {eff for eff in starting_effects if eff in constants.ALL_VALID_EFFECTS}
    valid_ingredients = [ing for ing in ingredients if ing in ALL_INGREDIENTS]

    current_set = valid_start_effects
    print(f"Initial Effects: {C_DIM}{sorted(list(current_set)) if current_set else '[]'}{C_RESET}")

    if not valid_ingredients:
        print(f"{C_YELLOW}Warning: No valid ingredients in the sequence to apply.{C_RESET}")
        return sorted(list(current_set))

    for i, ing in enumerate(valid_ingredients):
        print(f"\n{Style.BRIGHT}Step {i+1}: Applying ingredient: {C_CYAN}{ing}{C_RESET}")
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
                added_str = (
                    f"{', '.join(f'{C_GREEN}{eff}{C_RESET}' for eff in sorted(list(added)))}"
                )
                print(f"    {C_GREEN}Added:   {added_str}")
            if removed:
                removed_str = (
                    f"{', '.join(f'{C_RED}{eff}{C_RESET}' for eff in sorted(list(removed)))}"
                )
                print(f"    {C_RED}Removed: {removed_str}")

    final_sorted_list = sorted(list(current_set))
    print(f"\n--- {Style.BRIGHT}Final Effects after {len(valid_ingredients)} steps{C_RESET} ---")
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

    if base_product_name not in constants.BASE_PRICES:
        print(
            f"{C_RED}Error: Unknown base product '{base_product_name}'. Valid options: {list(constants.BASE_PRICES.keys())}{C_RESET}"
        )
        return []

    print(f"\n{Style.BRIGHT}Searching for Top {num_results} Most Expensive products{C_RESET}")
    print(
        f"  Base Product:    {C_YELLOW}{base_product_name}{C_RESET} (${constants.BASE_PRICES[base_product_name]})"
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
        if current_price is not None:  # Should always be not None if base product is valid
            total_cost = constants.BASE_PRICES[base_product_name] + sum(
                [constants.INGREDIENTS_PRICES[ing] for ing in current_sequence]
            )
            profit = current_price - total_cost
            profit_margin = round(profit / total_cost, 2)
            all_results.append(
                (
                    current_price,
                    current_sequence,
                    current_effects_set,
                    profit,
                    profit_margin,
                )
            )

        # --- Check Depth Limit ---
        if len(current_sequence) >= max_ingredients:
            continue  # Stop exploring further down this path

        # --- Explore Neighbors ---
        for ingredient in ALL_INGREDIENTS:
            # Calculate next state only once per ingredient transition
            next_effects_set = apply_ingredient_optimized(current_effects_set, ingredient)
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
    top_results = nlargest(num_results, all_results, key=lambda item: item[4])

    # --- Print Top Results ---
    print(f"\n{Style.BRIGHT}Top {len(top_results)} Results:{C_RESET}")
    if not top_results:
        print(f"  {C_YELLOW}No results found (check max_ingredients).{C_RESET}")
    else:
        for i, (price, sequence, effects, profit, profit_margin) in enumerate(top_results):
            seq_str = (
                f"[{', '.join(f'{C_CYAN}{ing}{C_RESET}' for ing in sequence)}]"
                if sequence
                else "[](Base)"
            )
            # total_cost = (BASE_PRICES[base_product_name] + sum([INGREDIENTS_PRICES[ing] for ing in sequence]))
            # profit = price - total_cost
            # profit_margin = round(profit / total_cost, 2)
            print(f"  {i+1}. Price: {C_GREEN}${price}{C_RESET}")
            print(f"     Sequence ({len(sequence)} ingredients): {seq_str}")
            print(f"     {C_DIM}Effects: {sorted(list(effects))}{C_RESET}")
            print(f"     Profit: {C_MAGENTA}${profit}{C_RESET}")
            print(f"     Profit margin: {C_RED}{profit_margin}{C_RESET}")

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


def run_effects_calculation(
    sequence: List[str], start_effects: Optional[List[str]], product_name: Optional[str]
):
    """Helper function to run and display effect sequence calculation."""
    # --- Input Validation ---
    valid_starting_effects = set()
    if start_effects:
        invalid_starting = []
        for effect in start_effects:
            if effect in constants.ALL_VALID_EFFECTS:
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
        print(f"    {C_DIM}Contains Effects: {sorted(list(valid_starting_effects))}{C_RESET}")
    # Use the internal function that prints step-by-step
    apply_ingredients_sequence_optimized(list(valid_starting_effects), valid_sequence)


def main():
    parser = argparse.ArgumentParser(
        description=f"{Style.BRIGHT}Product Calculator CLI{C_RESET}",
        formatter_class=argparse.RawTextHelpFormatter,  # Allows better formatting in help
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Action to perform")

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
    parser_expensive = subparsers.add_parser("expensive", help="Find the most expensive products.")
    parser_expensive.add_argument(
        "base_product",
        choices=list(constants.BASE_PRICES.keys()),
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
        choices=list(constants.BASE_PRICES.keys()),
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
            run_effects_calculation(args.ingredients, args.start_effects, args.product_name)

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
                if effect in constants.ALL_VALID_EFFECTS:
                    valid_effects.add(effect)
                else:
                    invalid_effects.append(effect)

            if invalid_effects:
                print(
                    f"{C_YELLOW}Warning:{C_RESET} Invalid effects provided and ignored for price calc: {C_RED}{invalid_effects}{C_RESET}"
                )

            if not valid_effects:
                print(f"{C_RED}Error: No valid effects provided for price calculation.{C_RESET}")
            else:
                final_price = calculate_product_price(args.base_product, valid_effects)
                if final_price is not None:
                    print(f"\nCalculating Price:")
                    print(f"  Base Product: {C_YELLOW}{args.base_product}{C_RESET}")
                    print(f"  Effects (valid): {C_DIM}{sorted(list(valid_effects))}{C_RESET}")
                    print(f"  {Style.BRIGHT}Calculated Price: {C_GREEN}${final_price}{C_RESET}")

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
