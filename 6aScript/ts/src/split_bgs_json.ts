import 'dotenv/config'
import { promises as fs } from 'fs'
import * as path from 'path'

type BattlegroundsData = {
  region?: string
  locale?: string
  generatedAt?: string
  heroes?: unknown[]
  minions?: unknown[]
  [key: string]: any
}

async function ensureDir(dirPath: string) {
  await fs.mkdir(dirPath, { recursive: true })
}

async function readJson<T>(filePath: string): Promise<T> {
  const content = await fs.readFile(filePath, 'utf8')
  return JSON.parse(content) as T
}

async function writeJson(filePath: string, data: unknown) {
  const content = JSON.stringify(data, null, 2)
  await fs.writeFile(filePath, content, 'utf8')
}

async function main() {
  const root = process.cwd()
  const inputFile = path.join(root, 'data', 'battlegrounds.json')
  const outDir = path.join(root, 'data', 'bgs')

  const exists = await fs
    .access(inputFile)
    .then(() => true)
    .catch(() => false)
  if (!exists) {
    throw new Error(`Input file not found: ${inputFile}`)
  }

  await ensureDir(outDir)

  const all = await readJson<BattlegroundsData>(inputFile)

  const { heroes = [], minions = [], ...meta } = all || {}

  await Promise.all([
    writeJson(path.join(outDir, 'heroes.json'), heroes),
    writeJson(path.join(outDir, 'minions.json'), minions),
    writeJson(path.join(outDir, 'meta.json'), meta)
  ])

  console.log(
    `Split completed: heroes=${(heroes as any[]).length}, minions=${(minions as any[]).length}`
  )
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})


