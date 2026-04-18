import { createPortal } from 'react-dom';

export default function Overlay({ children, onClick }) {
  return createPortal(
    <div className="nom-overlay" onClick={onClick}>
      {children}
    </div>,
    document.body
  );
}
