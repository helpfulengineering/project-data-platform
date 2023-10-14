import cytoscape from "cytoscape";

export const createMakerDataPanel = (
	maker: cytoscape.NodeSingular
): HTMLElement => {
	var dataPanel = document.createElement("div") as HTMLElement;
	dataPanel.className = "data-panel";
	dataPanel.id = "data-panel";

	var title = document.createElement("span") as HTMLElement;
	title.textContent = maker.data("label");
	dataPanel.appendChild(title);

	var tableDiv = document.createElement("div") as HTMLElement;
	var table = document.createElement("table");
	var productTR = document.createElement("tr");
	var productTD = document.createElement("td");
	productTD.textContent = "Product";
	var productTDAtomID = document.createElement("td");
	var productSpan = document.createElement("span");
	productSpan.className = "limited";
	productSpan.textContent = maker.data("product");
	productTDAtomID.appendChild(productSpan);

	productTR.appendChild(productTD);
	productTR.appendChild(productTDAtomID);
	table.appendChild(productTR);
	tableDiv.appendChild(table);
	dataPanel.appendChild(tableDiv);

	return dataPanel;
};
