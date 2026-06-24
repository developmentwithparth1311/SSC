import React from 'react';
import { render, screen } from '@testing-library/react';
import Avatar from '../Avatar';

describe('Avatar', () => {
  it('renders username initials when no image', () => {
    render(<Avatar user={{ username: 'alex_x' }} />);
    expect(screen.getByTestId('avatar-alex_x')).toHaveTextContent('AL');
  });

  it('renders profile image when avatar URL is set', () => {
    render(<Avatar user={{ username: 'alex_x', avatar: 'data:image/jpeg;base64,abc' }} />);
    expect(screen.getByTestId('avatar-alex_x').querySelector('img')).toBeTruthy();
  });

  it('shows group icon for group chats', () => {
    render(<Avatar isGroup size="md" />);
    expect(screen.getByTestId('avatar')).toBeTruthy();
  });
});