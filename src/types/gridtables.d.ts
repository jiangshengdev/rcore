// The Adobe packages do not ship declarations for these exported APIs.
declare module '@adobe/mdast-util-gridtables' {
  import type { Handler } from 'mdast-util-to-hast';

  export const TYPE_TABLE: 'gridTable';
  export function mdast2hastGridTablesHandler(): Handler;
}

declare module '@adobe/remark-gridtables' {
  import type { Plugin } from 'unified';
  import type { Root } from 'mdast';

  const remarkGridTable: Plugin<[], Root>;
  export default remarkGridTable;
}
