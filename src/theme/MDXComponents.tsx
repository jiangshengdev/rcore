import React from 'react';
import MDXComponents from '@theme-original/MDXComponents';
import Anchor from '@site/src/components/Anchor';
import TableViewport from '@site/src/components/TableViewport';
import Br from '@site/src/components/Br';

const TableWrapper = (props: React.HTMLAttributes<HTMLTableElement>) => (
  <TableViewport>
    <table {...props} />
  </TableViewport>
);

export default {
  // Re-use the default mapping
  ...MDXComponents,
  // Map the "<Anchor>" tag to our Anchor component
  // `Anchor` will receive all props that were passed to `<Anchor>` in MDX
  Anchor,
  // Map the "<Br>" tag to our line-break component for explicit breaks in MDX
  Br,
  table: TableWrapper,
  TableViewport,
};
