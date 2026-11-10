import 'mdast';
import type { Parent } from 'unist';

declare module 'mdast' {
  interface RootContentMap {
    gridTable: Parent & { type: 'gridTable' };
  }
}
