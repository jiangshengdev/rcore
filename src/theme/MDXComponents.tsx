import MDXComponents from '@theme-original/MDXComponents';
import Anchor from '@site/src/components/Anchor';

export default {
  // Re-use the default mapping
  ...MDXComponents,
  // Map the "<Anchor>" tag to our Anchor component
  // `Anchor` will receive all props that were passed to `<Anchor>` in MDX
  Anchor,
};
