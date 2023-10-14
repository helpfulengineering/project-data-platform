const path = require("path");
const pkg = require("./package.json");

env = process.env;
const NODE_ENV = env.NODE_ENV;
const MIN = env.MIN;
const PROD = NODE_ENV === "production";

module.exports = {
	mode: "production", // Set the mode to 'production' for minification
	entry: "./src/ts/index.ts", // Entry point of your application
	output: {
		filename: `${pkg.name}.js`, // Output file name
		path: path.resolve(__dirname, "bin"), // Output directory path
		library: "projectdatavisualizations",
	},
	resolve: {
		extensions: [".ts", ".js"], // Add TypeScript and JavaScript as resolvable extensions
	},
	module: {
		rules: [
			{
				test: /\.ts$/, // Apply the following rules to TypeScript files
				use: "ts-loader", // Use ts-loader for transpiling TypeScript
				exclude: /(node_modules|\.spec\.ts)/, // Exclude node_modules and test files from processing
			},
		],
	},
	devServer: {
		static: {
			directory: __dirname,
		},
		compress: true,
		port: 8000,
	},
	optimization: {
		minimize: !!MIN,
	},
};
