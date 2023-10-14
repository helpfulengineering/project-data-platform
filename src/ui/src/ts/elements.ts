import cytoscape from "cytoscape";
import { Md5 } from "ts-md5";

type Product = {
	id: string;
	desc: string;
};

type SuppliedTree = {
	product: Product;
	type: "supplied";
	party: string;
};

type MissingTree = {
	product: Product;
	type: "missing";
};

type MadeTree = {
	product: Product;
	type: "made";
	party: string;
	design: string;
	bom: Array<Tree>;
};

// Union type for all trees
type Tree = SuppliedTree | MissingTree | MadeTree;

export const hash = (o: object): string => Md5.hashStr(JSON.stringify(o));

export const elementsEqual = (
	g1: cytoscape.ElementsDefinition,
	g2: cytoscape.ElementsDefinition
): boolean => {
	const g2NodesHashSet = new Set(g2.nodes.map((n) => hash(n)));
	const g2EdgesHashSet = new Set(g2.edges.map((e) => hash(e)));
	for (const node of g1.nodes) {
		if (!g2NodesHashSet.has(hash(node))) {
			return false;
		}
	}
	for (const edge of g1.edges) {
		if (!g2EdgesHashSet.has(hash(edge))) {
			return false;
		}
	}
	return true;
};

const createSuppliedElements = (
	st: SuppliedTree
): cytoscape.ElementsDefinition => {
	const atomId = st.product.id;
	const supplierId = `supplier-${st.party}-${atomId}`;
	return {
		nodes: [
			{
				data: {
					id: atomId,
					class: "atom",
					label: st.product.desc,
				},
			},
			{
				data: {
					id: supplierId,
					class: "supplier",
					label: st.party,
				},
			},
		],
		edges: [
			{
				data: {
					id: `edge-${supplierId}-->${atomId}`,
					target: atomId,
					source: supplierId,
				},
			},
		],
	};
};

const createMissingElements = (
	mt: MissingTree
): cytoscape.ElementsDefinition => {
	const missingId = `missing-${mt.product.id}`;
	return {
		nodes: [
			{
				data: {
					id: missingId,
					class: "atom",
					label: mt.product.desc,
					missing: true,
				},
			},
		],
		edges: [],
	};
};

const createMadeElements = (mt: MadeTree): cytoscape.ElementsDefinition => {
	const atomId = mt.product.id;
	const makerId = `maker-${mt.party}-${atomId}`;
	let madeElems: cytoscape.ElementsDefinition = {
		nodes: [
			{
				data: {
					id: atomId,
					class: "atom",
					label: mt.product.desc,
				},
			},
			{
				data: {
					id: makerId,
					class: "maker",
					label: mt.party,
				},
			},
		],
		edges: [
			{
				data: {
					id: `edge-${makerId}-->${atomId}`,
					source: makerId,
					target: atomId,
				},
			},
		],
	};

	for (const bt of mt.bom) {
		let treeElems: cytoscape.ElementsDefinition;
		switch (bt.type) {
			case "made":
				treeElems = createMadeElements(bt);
				break;
			case "missing":
				treeElems = createMissingElements(bt);
				break;
			case "supplied":
				treeElems = createSuppliedElements(bt);
				break;
		}
		madeElems = {
			nodes: madeElems.nodes.concat(treeElems.nodes),
			edges: madeElems.edges.concat(treeElems.edges),
		};
		const bomTreeRootNodeId = treeElems.nodes[0].data.id!;
		madeElems.edges.push({
			data: {
				id: `edge-${bomTreeRootNodeId}-->${makerId}`,
				source: bomTreeRootNodeId,
				target: makerId,
			},
		});
	}
	return madeElems;
};

export const createElements = (
	inputData: MadeTree
): cytoscape.ElementsDefinition => {
	const elems = createMadeElements(inputData);
	elems.nodes[0].data.root = true;
	return elems;
};
