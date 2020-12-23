const path = require('path')
const { VueLoaderPlugin } = require('vue-loader')
const BundleTracker = require('webpack-bundle-tracker');

module.exports = (env = {}) => {
	return {

		mode: env.prod ? 'production' : 'development',
		devtool: env.prod ? 'source-map' : 'cheap-module-source-map',
		context: __dirname,
		entry: {
			app: './src/app.ts',
		},
		output: {
			path: path.resolve('../static/escaperoom/dist'),
			publicPath: "/static/escaperoom/dist/",
      filename: "[name]-[fullhash].js"
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
      new VueLoaderPlugin(),
      new BundleTracker({filename: './webpack-stats.json'})
    ],
  };
}
