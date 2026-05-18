/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly RAPIDMARK_WORKER_NAME: string
  readonly RAPIDMARK_ADMIN_MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
