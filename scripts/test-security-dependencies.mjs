import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { test } from 'node:test';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const requireFromCore = createRequire(
  require.resolve('@docusaurus/core/package.json'),
);
const { default: Tinypool } = await import(
  pathToFileURL(requireFromCore.resolve('tinypool')).href
);
const requireFromTerser = createRequire(
  require.resolve('terser-webpack-plugin/package.json'),
);
const serialize = requireFromTerser('serialize-javascript');
const requireFromSockjs = createRequire(require.resolve('sockjs/package.json'));
const uuid = requireFromSockjs('uuid');
const requireFromServe = createRequire(
  requireFromCore.resolve('serve-handler/package.json'),
);

const directory = await mkdtemp(path.join(tmpdir(), 'rcore-dependency-test-'));
const filename = path.join(directory, 'worker.mjs');
await writeFile(
  filename,
  `export default (value) => ({
  value: value * 2,
  execArgv: process.execArgv,
  inheritedEnv: process.env.RCORE_INHERITED_ENV,
});\n`,
);

try {
  await test(
    'tinypool ignores inherited worker options',
    { timeout: 15000 },
    async () => {
      let pool;
      let result;
      try {
        // Benign markers only: no injected code or external process is executed.
        Object.prototype.execArgv = ['--no-warnings'];
        Object.prototype.env = {
          ...process.env,
          RCORE_INHERITED_ENV: 'unexpected',
        };
        pool = new Tinypool({ filename, minThreads: 1, maxThreads: 1 });
        result = await pool.run(21);
      } finally {
        delete Object.prototype.execArgv;
        delete Object.prototype.env;
        await pool?.destroy();
      }
      assert.equal(result.value, 42);
      assert.equal(result.inheritedEnv, undefined);
      assert.ok(!result.execArgv.includes('--no-warnings'));
    },
  );

  await test(
    'tinypool ignores inherited run filename',
    { timeout: 15000 },
    async () => {
      const pool = new Tinypool({ filename, minThreads: 1, maxThreads: 1 });
      let result;
      try {
        Object.prototype.filename = path.join(directory, 'does-not-exist.mjs');
        result = await pool.run(21, {});
      } finally {
        delete Object.prototype.filename;
        await pool.destroy();
      }
      assert.equal(result.value, 42);
    },
  );

  await test('serializer preserves build options and escapes script terminators', () => {
    const input = {
      transform: function (value) {
        return value + 1;
      },
      pattern: /test/gi,
      date: new Date('2026-01-01T00:00:00Z'),
      text: '</script><p>text</p>',
    };
    const output = serialize(input);
    assert.ok(!output.toLowerCase().includes('</script'));
    // Only evaluate the locally defined test fixture, as the minifier does.
    const roundTrip = Function(`return (${output})`)();
    assert.equal(roundTrip.transform(2), 3);
    assert.equal(roundTrip.pattern.flags, 'gi');
    assert.equal(roundTrip.date.toISOString(), input.date.toISOString());
    assert.equal(roundTrip.text, input.text);

    function withClosingTag() {
      return '</script>';
    }
    assert.ok(!serialize(withClosingTag).toLowerCase().includes('</script'));

    const arrayLike = Object.create(Array.prototype);
    arrayLike.length = 100;
    assert.deepEqual(JSON.parse(serialize(arrayLike)), { length: 100 });
  });

  await test('SockJS can use UUID v4 and invalid UUID buffers are rejected', () => {
    assert.equal(uuid.version(uuid.v4()), 4);
    assert.equal(uuid.validate(uuid.v4()), true);
    assert.throws(
      () => uuid.v5('test', uuid.v5.DNS, new Uint8Array(8), 4),
      RangeError,
    );
    assert.throws(
      () => uuid.v3('test', uuid.v3.DNS, new Uint8Array(8), 4),
      RangeError,
    );
    assert.doesNotThrow(() => require('sockjs/lib/transport'));
  });

  await test('serve-handler retains the callable minimatch API', () => {
    const minimatch = requireFromServe('minimatch');
    assert.equal(typeof minimatch, 'function');
    assert.equal(
      minimatch('/docs/chapter/index.html', '/docs/**/*.html'),
      true,
    );
    assert.equal(minimatch('/blog/index.html', '/docs/**/*.html'), false);
  });
} finally {
  await rm(directory, { recursive: true, force: true });
}
