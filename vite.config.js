import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { copyFileSync, existsSync } from 'fs'
import { join } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'copy-preload-deps',
      closeBundle() {
        // 打包后，把 preload 需要的依赖拷贝到 dist/preload/node_modules
        const distPreload = join(__dirname, 'dist/preload')
        const preloadPkg = join(__dirname, 'public/preload/package.json')
        
        // 拷贝 package.json
        if (existsSync(preloadPkg)) {
          copyFileSync(preloadPkg, join(distPreload, 'package.json'))
        }
        
        console.log('\n📦 请在 dist/preload 目录执行: npm install')
      }
    }
  ],
  base: './',
  build: {
    sourcemap: false, // 禁用 source map，避免生成 .map 文件
    minify: 'esbuild', // 默认就是 esbuild，也可以用 'terser'
    reportCompressedSize: false, // 禁用 gzip 压缩大小报告（不会禁用压缩，但能稍微加快构建）
    rollupOptions: {
      output: {
        // 确保没有 .gz 等压缩文件生成（Vite 默认不会生成 .gz，除非用了 compression 插件）
      }
    }
  }
})
