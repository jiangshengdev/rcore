import React, { type PropsWithChildren } from 'react';
import styles from './styles.module.css';

export type TableViewportProps = PropsWithChildren<{}>;

/** 单层容器：限制最大宽度并在需要时滚动，用于承载表格等子内容。 */
export default function TableViewport({ children }: TableViewportProps) {
  return <div className={styles.container}>{children}</div>;
}
