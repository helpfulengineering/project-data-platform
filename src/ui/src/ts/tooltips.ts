import cytoscape from "cytoscape";
import popper from "cytoscape-popper";
import tippy from "tippy.js";

cytoscape.use(popper);

const _makeTippy = (node: cytoscape.NodeSingular, text: string) => {
	var ref = node.popperRef();
	var dummyDomEle = document.createElement("div");

	var tip = tippy(dummyDomEle, {
		getReferenceClientRect: ref.getBoundingClientRect,
		trigger: "manual",
		content: function () {
			var div = document.createElement("div");

			div.innerHTML = text;

			return div;
		},
		arrow: true,
		placement: "bottom",
		hideOnClick: false,
		sticky: "reference",

		interactive: true,
		appendTo: document.body,
	});

	node.on("mouseover", () => tip.show());
	node.on("mouseout", () => tip.hide());

	return tip;
};

export const registerTooltips = (cy: cytoscape.Core) => {
	cy.nodes().forEach((node) => {
		const nodeClass = node.data("class");
		if (nodeClass === "maker" || nodeClass === "supplier") {
			const tooltipStr = node.data("label");
			_makeTippy(node, tooltipStr);
		}
	});
};
