const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  transpileDependencies: true,
  devServer: {
    proxy: {
      "/extensions": {
        target: "http://10.25.20.17:8200",
        //开启跨域
        changeOrigin: true, 
        // 路径重写
        pathRewrite: {
          "^/extensions": ""
        }
      }
    }
  }
})
