//const path = require('path');

var HtmlWebpackPlugin = require('html-webpack-plugin');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var CleanWebpackPlugin = require('clean-webpack-plugin');

module.exports = {
  entry: './src/index.js',
  output: {
    path: __dirname + '/dist',
    filename: '[hash].bundle.js'
  },
  module: {
    rules: [{
        test: /\.scss$/,
        use: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: ['css-loader', 'sass-loader'],
          publicPath: __dirname + '/dist'
        })
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: ['babel-loader', 'eslint-loader']
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      title: 'Finite Automata Sandbox',
      favicon: __dirname + '/src/img/favicon.ico',
      minify: {
        collapseWhitespace: true,
        removeComments: true,
        removeScriptTypeAttributes: true,
        removeAttributeQuotes: true,
        useShortDoctype: true,
        minifyCSS: true
      },
      template: './src/index.html'
    }),
    new ExtractTextPlugin({
      filename: '[contenthash].css',
      allChunks: true
    }),
    new CleanWebpackPlugin(['dist'], {
      root: __dirname,
      verbose: false,
      dry: false,
      watch: true,
      exclude: ['index.html']
    })


  ]
}
