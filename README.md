# Schedule 1 Effect Finder

This is a simple script to find what order to mix ingredients for the desired effects. From my testing it is accurate, however please let me know as there may be some rare combinations that aren't implemented on this script

## Installation

NOTE: You will need Python 3.9 or above, which you can install here: https://www.python.org/downloads/

1. Download the repository. You can do this by clicking "Code" > Download zip. Or you can clone with git using

```
git clone https://github.com/vZekii/Schedule-1-Effect-Finder.git
```

2. Install the requirements.

```
pip install -r requirements.txt
```

3. Use the script

## Usage

The script features quite a few options. For details on how to use each, you can use --help on each feature

```
python main.py --help
python main.py effects --help
python main.py shortest --help
python main.py expensive --help
python main.py price --help
```

### Calculate effects

This can be used to calculate what effects the final product will have after applying them in order

```
python main.py effects "Mega Bean" "Energy Drink" Banana Chili --start-effects Calming --product-name "My product"
python main.py effects Gasoline Cuke Mouthwash Banana --start-effects Meth # Assuming 'Meth' isn't an effect, will be ignored
```

### Find shortest recipe

This can be used to find the shortest recipe for the desired effects. Some will be impossible, and raising the max ingredients will make the program execute for longer so keep that in mind

```
python main.py shortest Focused Long-Faced Spicy --start-effects Calming --max-ingredients 4
python main.py shortest Slippery Sneaky --max-ingredients 3
```

### Find most expensive

This can be used to find the most expensive possible combinations for each starting ingredient.

```
python main.py expensive Meth 4 --num-results 5
python main.py expensive Cocaine 3
```

### Calculate price

This can be used to determine the price of a product with the provided effects

```
python main.py price Meth Euphoric Thought-Provoking Balding Gingeritis
python main.py price Weed Athletic Spicy "Anti-Gravity"
```
