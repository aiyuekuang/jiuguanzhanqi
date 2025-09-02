import 'dotenv/config';
import { getAccessToken } from './bnet_oauth';
import fs from 'node:fs/promises';
import path from 'node:path';

const API_HOSTS: Record<string, string> = {
  us: 'https://us.api.blizzard.com',
  eu: 'https://eu.api.blizzard.com',
  kr: 'https://kr.api.blizzard.com',
  tw: 'https://tw.api.blizzard.com',
  cn: 'https://gateway.battlenet.com.cn'
};

function getApiBase(): string {
  const region = String(process.env.BNET_REGION || 'us').toLowerCase();
  return API_HOSTS[region] || API_HOSTS.us;
}

async function fetchAllPages(url: URL, headers: Record<string, string>, pageSize = 100): Promise<any[]> {
  const results: any[] = [];
  let page = 1;
  // Simple pagination until empty
  while (true) {
    const u = new URL(url);
    u.searchParams.set('pageSize', String(pageSize));
    u.searchParams.set('page', String(page));

    const res = await fetch(u, { headers });
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`Fetch failed: ${res.status} ${res.statusText} ${text}`);
    }
    const data = (await res.json()) as { cards?: any[] };
    const cards = Array.isArray(data?.cards) ? data.cards : [];
    results.push(...cards);
    if (cards.length < pageSize) break;
    page += 1;
  }
  return results;
}

async function fetchCardDetail(baseApi: string, headers: Record<string, string>, id: number | string, locale: string): Promise<any | null> {
  const url = new URL(`${baseApi}/hearthstone/cards/${id}`);
  url.searchParams.set('locale', locale);
  const res = await fetch(url, { headers });
  if (!res.ok) {
    // swallow error, return null to keep progress
    return null;
  }
  return res.json();
}

async function enrichWithImages(baseApi: string, headers: Record<string, string>, cards: any[], locale: string, concurrency = 12): Promise<any[]> {
  const result: any[] = new Array(cards.length);
  let index = 0;

  async function worker() {
    while (true) {
      const i = index++;
      if (i >= cards.length) break;
      const c = cards[i];
      const id = c?.id ?? c?.cardId;
      if (id == null) {
        result[i] = c;
        continue;
      }
      const detail = await fetchCardDetail(baseApi, headers, id, locale).catch(() => null);
      if (detail && (detail.image || detail.imageGold)) {
        result[i] = { ...c, image: detail.image, imageGold: detail.imageGold };
      } else {
        result[i] = c;
      }
    }
  }

  const workers: Promise<void>[] = [];
  for (let w = 0; w < concurrency; w++) workers.push(worker());
  await Promise.all(workers);
  return result;
}

export async function run(): Promise<void> {
  const locale = process.env.BNET_LOCALE || 'zh_CN';
  const region = String(process.env.BNET_REGION || 'us').toLowerCase();

  const token = await getAccessToken();
  const base = getApiBase();

  const common = new URL(`${base}/hearthstone/cards`);
  common.searchParams.set('locale', locale);
  common.searchParams.set('gameMode', 'battlegrounds');

  const headers = { Authorization: `Bearer ${token}` };

  const heroesUrl = new URL(common);
  heroesUrl.searchParams.set('type', 'hero');

  const minionsUrl = new URL(common);
  minionsUrl.searchParams.set('type', 'minion');

  const [heroes, minions] = await Promise.all([
    fetchAllPages(heroesUrl, headers),
    fetchAllPages(minionsUrl, headers)
  ]);

  // Enrich with image fields by fetching individual card details
  const [heroesEnriched, minionsEnriched] = await Promise.all([
    enrichWithImages(base, headers, heroes, locale),
    enrichWithImages(base, headers, minions, locale)
  ]);

  const outDir = path.resolve('6aScript', 'output');
  await fs.mkdir(outDir, { recursive: true });
  await fs.writeFile(path.join(outDir, `bgs_heroes_${region}_${locale}.json`), JSON.stringify(heroesEnriched, null, 2), 'utf8');
  await fs.writeFile(path.join(outDir, `bgs_minions_${region}_${locale}.json`), JSON.stringify(minionsEnriched, null, 2), 'utf8');

  // unified data file
  const dataDir = path.resolve('data');
  await fs.mkdir(dataDir, { recursive: true });
  const unified = {
    region,
    locale,
    generatedAt: new Date().toISOString(),
    heroes: heroesEnriched,
    minions: minionsEnriched
  } as const;
  await fs.writeFile(path.join(dataDir, 'battlegrounds.json'), JSON.stringify(unified, null, 2), 'utf8');

  console.log(`Saved heroes: ${heroesEnriched.length}, minions: ${minionsEnriched.length} to ${outDir}`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  run().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}


