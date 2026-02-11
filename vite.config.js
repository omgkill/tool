import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { copyFileSync, mkdirSync, existsSync } from 'fs'
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
  base: './'
})
