import { Outlet } from 'react-router-dom';
import TopNav from './TopNav';
import Sidebar from './Sidebar';
import styles from './MainLayout.module.css';

export default function MainLayout() {
  return (
    <div className={styles.root}>
      <TopNav />
      <div className={styles.body}>
        <Sidebar />
        <main className={styles.main}>
          <div className={`${styles.content} nom-animate-in`}>
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
