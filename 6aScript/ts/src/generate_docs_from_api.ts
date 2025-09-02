import 'dotenv/config';
import fs from 'node:fs/promises';
import path from 'node:path';

function byName(a: any, b: any): number {
  return String(a.name || a.text || '').localeCompare(String(b.name || b.text || ''), 'zh');
}

function ensure<T, K extends keyof T>(obj: T | undefined | null, key: K, fallback: any) {
  if (obj && obj[key] != null) return (obj as any)[key];
  return fallback;
}

function renderHeroLine(c: any): string {
  const name = ensure(c, 'name', '');
  const text = String(ensure(c, 'text', '')).replace(/\n/g, ' ');
  const armor = ensure(c?.battlegrounds, 'armor', undefined);
  const tier = ensure(c?.battlegrounds, 'tier', undefined);
  const armorStr = armor != null ? ` 护甲:${armor}` : '';
  const tierStr = tier != null ? ` 等级:${tier}` : '';
  return `- ${name}${armorStr}${tierStr} — ${text}`;
}

function renderMinionLine(c: any): string {
  const name = ensure(c, 'name', '');
  const at = ensure(c, 'attack', '');
  const hp = ensure(c, 'health', '');
  const tribe = ensure(c, 'minionType', '') || ensure(c, 'races', '') || '';
  const text = String(ensure(c, 'text', '')).replace(/\n/g, ' ');
  return `- ${name} (${at}/${hp}) [${tribe}] — ${text}`;
}

async function backupFile(filePath: string): Promise<void> {
  try {
    const stat = await (fs as any).stat(filePath);
    if (stat.isFile()) {
      const dir = path.dirname(filePath);
      const base = path.basename(filePath);
      const ts = new Date().toISOString().replace(/[:.]/g, '-');
      const backupPath = path.join(dir, `${base}.bak.${ts}`);
      const content = await fs.readFile(filePath, 'utf8');
      await fs.writeFile(backupPath, content, 'utf8');
    }
  } catch (_) {
    // ignore if not exists
  }
}

async function writeFileSafe(filePath: string, content: string): Promise<void> {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await backupFile(filePath);
  await fs.writeFile(filePath, content, 'utf8');
}

function groupMinionsByTier(minions: any[]): Map<number, any[]> {
  const map = new Map<number, any[]>();
  for (const m of minions) {
    const tier = ensure(m?.battlegrounds, 'tier', 0);
    if (!map.has(tier)) map.set(tier, []);
    map.get(tier)!.push(m);
  }
  return map;
}

function renderHeroesMd(heroes: any[]): string {
  const lines: string[] = [];
  lines.push('# 英雄数据');
  lines.push('');
  heroes.sort(byName).forEach((h) => lines.push(renderHeroLine(h)));
  lines.push('');
  return lines.join('\n');
}

function renderTierMd(tier: number, minions: any[]): string {
  const lines: string[] = [];
  lines.push(`# ${tier}级随从`);
  lines.push('');
  minions.sort(byName).forEach((m) => lines.push(renderMinionLine(m)));
  lines.push('');
  return lines.join('\n');
}

export async function run(): Promise<void> {
  const region = String(process.env.BNET_REGION || 'us').toLowerCase();
  const locale = process.env.BNET_LOCALE || 'zh_CN';

  const unifiedPath = path.resolve('data', 'battlegrounds.json');
  let heroes: any[] = [];
  let minions: any[] = [];
  try {
    const unified = JSON.parse(await fs.readFile(unifiedPath, 'utf8'));
    heroes = unified.heroes || [];
    minions = unified.minions || [];
  } catch (_) {
    const outDir = path.resolve('6aScript', 'output');
    const heroesPath = path.join(outDir, `bgs_heroes_${region}_${locale}.json`);
    const minionsPath = path.join(outDir, `bgs_minions_${region}_${locale}.json`);
    heroes = JSON.parse(await fs.readFile(heroesPath, 'utf8'));
    minions = JSON.parse(await fs.readFile(minionsPath, 'utf8'));
  }

  const heroesMd = renderHeroesMd(heroes);
  await writeFileSafe(path.resolve('docs', 'heroes', 'heroes_data.md'), heroesMd);

  const grouped = groupMinionsByTier(minions);
  for (const tier of Array.from(grouped.keys()).sort((a, b) => a - b)) {
    const md = renderTierMd(tier, grouped.get(tier)!);
    await writeFileSafe(path.resolve('docs', 'minions', `tier${tier}_minions.md`), md);
  }

  console.log('Docs generated from API output (TS).');
}

if (import.meta.url === `file://${process.argv[1]}`) {
  run().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}


