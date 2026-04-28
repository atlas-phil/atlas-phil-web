import type { MiddlewareHandler } from 'astro'

export const onRequest: MiddlewareHandler = async (context, next) => {
  const env = (context.locals as App.Locals).runtime?.env
  if (env) {
    const keys = [
      'KEYSTATIC_GITHUB_CLIENT_ID',
      'KEYSTATIC_GITHUB_CLIENT_SECRET',
      'KEYSTATIC_SECRET',
    ] as const
    for (const key of keys) {
      if (env[key]) process.env[key] = env[key]
    }
  }
  return next()
}
