import { useEffect, useState } from 'react';
import { isNativeApp } from './platform';

/** True on Capacitor native or narrow viewports — drives single-pane chat UI. */
export function useMobileLayout() {
  const [narrow, setNarrow] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.innerWidth < 768;
  });

  useEffect(() => {
    const mq = window.matchMedia('(max-width: 767px)');
    const update = () => setNarrow(mq.matches);
    update();
    mq.addEventListener('change', update);
    return () => mq.removeEventListener('change', update);
  }, []);

  return isNativeApp() || narrow;
}