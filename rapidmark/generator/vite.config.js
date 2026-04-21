import { defineConfig } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'path'

export default defineConfig(({ command, mode }) => {
  const taskFile = process.env.RAPIDMARK_TASK_FILE
  let taskConfig = null

  if (taskFile && fs.existsSync(taskFile)) {
    console.log(`📋 Loading task configuration: ${taskFile}`)
    taskConfig = JSON.parse(fs.readFileSync(taskFile, 'utf8'))
  } else {
    console.log('🔧 Using development configuration')
    taskConfig = {
      definition: {
        id: 'dev_ner',
        name: 'Development NER Task',
        type: 'ner',
        description: 'Development environment',
        labels: [
          { id: 'PERSON', name: 'Person', parentId: null },
          { id: 'LOCATION', name: 'Location', parentId: null },
          { id: 'ORGANIZATION', name: 'Organization', parentId: null }
        ]
      },
      texts: [
        {
          id: 'text1',
          content: 'Apple CEO Tim Cook announced the new iPhone at the company headquarters in Cupertino. Tim Cook joined Apple in 1998.',
          attributes: {}
        }
      ]
    }
  }

  const resultFile = process.env.RAPIDMARK_RESULT_FILE
  let resultConfig = null

  if (resultFile && fs.existsSync(resultFile)) {
    console.log(`📊 Loading result data: ${resultFile}`)
    resultConfig = JSON.parse(fs.readFileSync(resultFile, 'utf8'))
  }

  return {
    plugins: [vue(), viteSingleFile()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    build: {
      target: 'es2015',
      assetsInlineLimit: 100000000,
      chunkSizeWarningLimit: 100000000,
      cssCodeSplit: false,
      outDir: 'dist',
      rollupOptions: {
        input: path.resolve(__dirname, 'index.html'),
        output: {
          inlineDynamicImports: true,
        }
      }
    },
    base: './',
    define: {
      __TASK_CONFIG__: JSON.stringify(taskConfig),
      __RESULT_CONFIG__: JSON.stringify(resultConfig),
      'import.meta.env.RAPIDMARK_ADMIN_MODE': JSON.stringify(process.env.RAPIDMARK_ADMIN_MODE),
      'import.meta.env.RAPIDMARK_WORKER_NAME': JSON.stringify(process.env.RAPIDMARK_WORKER_NAME)
    }
  }
})