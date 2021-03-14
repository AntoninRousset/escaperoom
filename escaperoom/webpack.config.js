const path = require('path')
const { VueLoaderPlugin } = require('vue-loader')
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const webpack = require('webpack');


module.exports = (env = {}) => {
	return {

		mode: env.prod ? 'production' : 'development',
		devtool: env.prod ? 'source-map' : 'cheap-module-source-map',
		context: __dirname,
		entry: {
			app: './escaperoom/frontend/app.ts',
		},
		output: {
			path: path.resolve(__dirname, 'dist'),
			publicPath: '/static/',
			filename: '[name]-[fullhash].js'
		},
		module: {
			rules: [
				{
					test: /\.s[ac]ss$/i,
					use: [
						'style-loader',
						'css-loader',
						'sass-loader',
					]
				}, {
					test: /\.(woff(2)?|ttf|eot)(\?v=\d+\.\d+\.\d+)?$/,
					use: 'file-loader'
				}, {
					test: /\.(png|jpe?g|gid|svg)$/i,
					use: 'file-loader'
				}, {
					test: /\.css$/,
					use: [
						'style-loader',
						'css-loader'
					]
				}, {
					test: /\.vue$/,
					use: 'vue-loader'
				}, {
					test: /\.ts$/,
					loader: 'ts-loader',
					options: {
						appendTsSuffixTo: [/\.vue$/],
					}
				},
			]
		},
		resolve: {
			extensions: ['.ts', '.js', '.vue', '.json'],
			alias: {
				'vue': '@vue/runtime-dom'
			}
		},
		plugins: [
			new webpack.DefinePlugin({
					"__VUE_OPTIONS_API__": true,
					"__VUE_PROD_DEVTOOLS__": false,
			}),
			new VueLoaderPlugin(),
			new BundleTracker({filename: './webpack-stats.json'})
		],
	};
}
