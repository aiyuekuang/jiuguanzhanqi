import 'dotenv/config';

const requiredEnv = ['BNET_CLIENT_ID', 'BNET_CLIENT_SECRET', 'BNET_REGION'] as const;

for (const key of requiredEnv) {
  if (!process.env[key]) {
    throw new Error(`Missing required env ${key}. Please set it in .env`);
  }
}

const regionToHost: Record<string, string> = {
  us: 'https://us.battle.net',
  eu: 'https://eu.battle.net',
  kr: 'https://kr.battle.net',
  tw: 'https://tw.battle.net',
  cn: 'https://www.battlenet.com.cn'
};

export async function getAccessToken(): Promise<string> {
  const region = String(process.env.BNET_REGION || 'us').toLowerCase();
  const host = regionToHost[region] || regionToHost.us;
  const url = `${host}/oauth/token`;
  const body = new URLSearchParams();
  body.set('grant_type', 'client_credentials');

  const clientId = String(process.env.BNET_CLIENT_ID);
  const clientSecret = String(process.env.BNET_CLIENT_SECRET);
  const auth = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${auth}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Failed to obtain token: ${res.status} ${res.statusText} ${text}`);
  }

  const json = (await res.json()) as { access_token?: string };
  if (!json.access_token) {
    throw new Error('No access_token in response');
  }
  return json.access_token;
}


