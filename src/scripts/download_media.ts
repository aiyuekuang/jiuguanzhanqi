import 'dotenv/config';
import fs from 'node:fs/promises';
import path from 'node:path';

type BgsUnified = {
  heroes: any[];
  minions: any[];
};

async function ensureDir(p: string): Promise<void> {
  await fs.mkdir(p, { recursive: true });
}

async function downloadToFile(url: string, filePath: string): Promise<void> {
  const res = await fetch(url, {
    headers: {
      'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36',
      Referer: 'https://playhearthstone.com/'
    }
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`download failed ${res.status} ${res.statusText} ${url} ${text}`);
  }
  const ab = await res.arrayBuffer();
  await fs.writeFile(filePath, Buffer.from(ab));
}

function sanitizeFilename(name: string): string {
  return name.replace(/[^a-zA-Z0-9-_\.]/g, '_');
}

export async function run(): Promise<void> {
  const jsonPath = path.resolve('data', 'battlegrounds.json');
  const raw = await fs.readFile(jsonPath, 'utf8');
  const data = JSON.parse(raw) as BgsUnified;

  const outDir = path.resolve('static', 'media');
  const heroesDir = path.join(outDir, 'heroes');
  const minionsDir = path.join(outDir, 'minions');
  await ensureDir(heroesDir);
  await ensureDir(minionsDir);

  type Job = { url: string; filePath: string };
  const jobs: Job[] = [];
  const heroMappings: Array<{ id: string; slug?: string; name?: string; image?: string; imageGold?: string }> = [];

  const handle = (item: any, dir: string, isHero = false) => {
    const id = String(item?.id || item?.cardId || 'unknown');
    const baseNameRaw = `${id}_${item?.slug || item?.name || ''}`;
    const baseName = sanitizeFilename(baseNameRaw || `card_${id}`);

    const makeFilePath = (u: string, suffix = '') => {
      try {
        const ext = path.extname(new URL(u).pathname) || '.png';
        return path.join(dir, `${baseName}${suffix}${ext}`);
      } catch {
        return path.join(dir, `${baseName}${suffix}.png`);
      }
    };

    let localImage: string | undefined;
    let localImageGold: string | undefined;
    if (typeof item?.image === 'string' && /^https?:\/\//.test(item.image)) {
      localImage = makeFilePath(item.image);
      jobs.push({ url: item.image, filePath: localImage });
    }
    if (typeof item?.imageGold === 'string' && /^https?:\/\//.test(item.imageGold)) {
      localImageGold = makeFilePath(item.imageGold, '_gold');
      jobs.push({ url: item.imageGold, filePath: localImageGold });
    }
    if (isHero) {
      heroMappings.push({
        id,
        slug: item?.slug,
        name: item?.name,
        image: localImage ? path.relative(outDir, localImage).replace(/\\/g, '/') : undefined,
        imageGold: localImageGold ? path.relative(outDir, localImageGold).replace(/\\/g, '/') : undefined
      });
    }
  };

  for (const h of data.heroes || []) handle(h, heroesDir, true);
  for (const m of data.minions || []) handle(m, minionsDir, false);

  const concurrency = Number(process.env.MEDIA_DL_CONCURRENCY || 12);
  let index = 0;
  async function worker() {
    while (true) {
      const i = index++;
      if (i >= jobs.length) break;
      const job = jobs[i];
      try {
        await downloadToFile(job.url, job.filePath);
      } catch (err: any) {
        console.warn(`skip ${job.url}: ${err?.message || err}`);
      }
    }
  }
  const workers: Promise<void>[] = [];
  for (let w = 0; w < concurrency; w++) workers.push(worker());
  await Promise.all(workers);

  await fs.writeFile(path.join(outDir, 'heroes.map.json'), JSON.stringify(heroMappings, null, 2), 'utf8');
  console.log(`media saved to ${outDir}. heroes.map.json generated with ${heroMappings.length} entries.`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  run().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}


