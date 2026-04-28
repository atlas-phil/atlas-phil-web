/// <reference path="../.astro/types.d.ts" />
/// <reference types="@astrojs/cloudflare" />

interface Env {
  KEYSTATIC_GITHUB_CLIENT_ID: string
  KEYSTATIC_GITHUB_CLIENT_SECRET: string
  KEYSTATIC_SECRET: string
}

type Runtime = import('@astrojs/cloudflare').Runtime<Env>

declare namespace App {
  interface Locals extends Runtime {}
}