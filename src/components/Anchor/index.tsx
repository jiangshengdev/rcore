import type { ReactNode } from 'react';
import styles from './styles.module.css';

interface AnchorProps {
  id: string;
}

/**
 * 锚点组件，用于在 Markdown 中创建可跳转的锚点位置
 * 自动处理顶部导航栏的偏移量
 */
export default function Anchor({ id }: AnchorProps): ReactNode {
  return <div id={id} className={styles.anchor} />;
}
