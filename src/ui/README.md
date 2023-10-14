# Project Data Visualizations

This project aims to solve [Issue #13](https://github.com/helpfulengineering/project-data-platform/issues/13) of [Project Data](https://github.com/helpfulengineering/project-data-platform/tree/main), a CLI for supply-chain modeling. The goal is to visualize fulfillment plans, which defines the how and what in creating a thing. There are prototypes of these fulfillment plans written in python, it's now useful to visualize them with something more user-friendly than ascii art, as it's currently intended to be demo-able.

## Building the code

First build the JS that renders the graph using [cytoscape.js](https://js.cytoscape.org/):

```bash
yarn

# Set MIN=1 if you want a minified JS output
MIN=1 yarn build
```

This will compile the TS code to `./bin/project-data-visualizations.js`. This is then imported by the ipynb, and you're then free to go wild with python for computing the graphs, and rendering them with the full capability of cytoscape.js.

The python code interacts with javascript code using the [notebookjs](https://github.com/jorgehpo/notebookJS) python package. The `execute_js` function interfaces with the JS code. It allows for passing data from python to JS, and it sends JS code the div ID of the HTML element inside the Jupyter notebook where the graph will render.

The python code sends JS code a dictionary containing three essential ingredients to make a cytoscape graph. These are: [Elements](https://js.cytoscape.org/#notation/elements-json), [Layouts](https://js.cytoscape.org/#layouts) and [Style](https://js.cytoscape.org/#style). You can either modify the static JSON files directly that define these things, or create them purely in python.

## VS Code `.ipynb` Setup

Install the [Jupyter VS Code extensions](https://code.visualstudio.com/docs/datascience/jupyter-notebooks). Also you'll need [poetry](https://python-poetry.org/docs/).

1. Install poetry deps:

```bash
poetry shell
poetry install
```

2. Open the [`.ipynb`](src/py/project-data-visualizations.ipynb) in VS Code. The Jupyter extension should render something similar to Google Colab.
3. Select the python interpreter from poetry: `.venv/bin/python`. There should be an option at the top right to select the python interpreter.
4. Run the notebook.

## Google Colab Setup

Before starting, make sure you've first built the JS code. To run the `.ipynb` file in Google Colab, import the `src/py/project-data-visualizations.ipynb` file to Colab then copy over all of these files to the project:

- `./bin/project-data-visualizations.js`
- `./src/py/style.css`
- `./static/james-kitchen.json`
- `./static/roberts-dessert-kitchen.json`
- `./static/tims-tasty-treats-kitchen.json`
