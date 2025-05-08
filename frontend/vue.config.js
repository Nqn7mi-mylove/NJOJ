module.exports = {
  // Disable source maps in production to save memory
  productionSourceMap: false,
  
  // Configure webpack to use less memory
  configureWebpack: {
    performance: {
      hints: false
    },
    optimization: {
      splitChunks: {
        minSize: 10000,
        maxSize: 250000,
      }
    }
  },
  
  // Disable lint on save to reduce memory usage during development
  lintOnSave: false,
  
  // Disable hot reload to save memory (uncomment if needed)
  // devServer: {
  //   hot: false
  // }
}
