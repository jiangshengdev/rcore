import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(path.resolve('package.json'));

if (existsSync('node_modules/gray-matter')) {
  execFileSync(
    process.execPath,
    [require.resolve('patch-package'), '--error-on-fail'],
    {
      stdio: 'inherit',
    },
  );
} else {
  // Docusaurus 3.10 uses the maintained fork, which already has the YAML fix.
  // Retain the old patch for dependency graphs that still install gray-matter.
  // Any additional patch needs explicit handling; never silently skip it.
  assert.deepEqual(readdirSync('patches').sort(), ['gray-matter+4.0.3.patch']);
  const requireFromUtils = createRequire(
    require.resolve('@docusaurus/utils/package.json'),
  );
  const matter = requireFromUtils('@11ty/gray-matter');
  const sample = { title: 'rCore', tags: ['安全', 'YAML'] };
  assert.deepEqual(matter(matter.stringify('Body', sample)).data, sample);
  assert.throws(() =>
    matter('---\nvalue: !!js/function "function () {}"\n---\nBody'),
  );
  console.log(
    '@11ty/gray-matter YAML checks passed; legacy gray-matter patch retained (package absent).',
  );
}
