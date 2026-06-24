import React from 'react';

export const MemoryRouter = ({ children }) => <div data-testid="memory-router">{children}</div>;

export const Link = ({ children, to, ...props }) => (
  <a href={to} {...props}>{children}</a>
);

export const Navigate = () => null;
export const useNavigate = () => jest.fn();
export const useLocation = () => ({ pathname: '/', search: '', hash: '' });
export const useParams = () => ({});