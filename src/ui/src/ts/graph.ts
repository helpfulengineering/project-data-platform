import cytoscape from "cytoscape";
import { createMakerDataPanel } from "./html-utils";

const toggleVisibility = (n: cytoscape.NodeSingular) => {
	console.log(`Toggling the visibility of node ${n.id()}`);
	if (n.hidden()) {
		n.css({ visibility: "visible" });
		n.connectedEdges().forEach((edge) => {
			edge.css({ visibility: "visible" });
		});
	} else {
		n.css({ visibility: "hidden" });
		n.connectedEdges().forEach((edge) => {
			edge.css({ visibility: "hidden" });
		});
	}
};

/**
 * this method configures cytoscape to toggle the children of the nodes
 * whose class is contained in the input classes array.
 * @param cy  Cytoscape core instance
 * @param classes Classes of nodes whose children should hide on click.
 */
export const toggleDescendantsVisibilityOnClick = (
	cy: cytoscape.Core,
	classes: string[]
): void => {
	classes.forEach((className) => {
		const nodes = cy.$(`.${className}`);
		nodes.forEach((node) => {
			node.on("click", () => {
				const children = node.successors("node");
				children.forEach(toggleVisibility);
			});
		});
	});
};

const makerClickHandler = (
	cy: cytoscape.Core,
	maker: cytoscape.NodeSingular
) => {
	const subGraph = maker.successors();

	let dataPanel = document.getElementById("data-panel");
	if (!dataPanel) {
		subGraph.forEach((ele) => {
			ele.classes("highlighted");
		});
		maker.classes("highlighted");
		document.body.appendChild(createMakerDataPanel(maker));
	} else {
		subGraph.forEach((ele) => {
			ele.classes("");
			console.log(`setting ${ele.id()} classes to ${ele.classes()}`);
		});
		maker.classes("");
		dataPanel.parentElement?.removeChild(dataPanel);
	}
	// const highlightedNodes = cy.$(`node`)
	// console.log()
};

export const registerMakerClickHandler = (cy: cytoscape.Core): void => {
	const makers = cy.$("node[class='maker']");
	makers.forEach((maker) => {
		maker.on("click", () => {
			makerClickHandler(cy, maker);
		});
	});
};
