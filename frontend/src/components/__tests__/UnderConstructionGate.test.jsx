import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import UnderConstructionGate from '../UnderConstructionGate';
import { LocaleProvider } from '../../context/LocaleContext';
import { t as translate } from '../../lib/i18n';
import * as siteGate from '../../lib/siteGate';

jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: null }),
}));

jest.mock('../LanguagePicker', () => function LanguagePicker() {
  return <div data-testid="language-picker" />;
});

describe('UnderConstructionGate', () => {
  beforeEach(() => {
    process.env.REACT_APP_SITE_PREVIEW_PASSWORD = 'test-invite-code';
    jest.spyOn(siteGate, 'verifySitePreviewPassword');
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders construction message and contact email', () => {
    render(
      <MemoryRouter>
        <LocaleProvider>
          <UnderConstructionGate onBypass={jest.fn()} />
        </LocaleProvider>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('under-construction-gate')).toBeInTheDocument();
    expect(screen.getByText(translate('constructionHeadline', 'en'))).toBeInTheDocument();
    expect(screen.getByTestId('construction-contact-email')).toHaveAttribute(
      'href',
      'mailto:contact@supersecurechat.com',
    );
    expect(screen.getByTestId('construction-access-trigger')).toBeInTheDocument();
  });

  it('requires correct password before bypass', () => {
    const onBypass = jest.fn();
    siteGate.verifySitePreviewPassword.mockReturnValue(false);
    render(
      <MemoryRouter>
        <LocaleProvider>
          <UnderConstructionGate onBypass={onBypass} />
        </LocaleProvider>
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByTestId('construction-access-trigger'));
    fireEvent.change(screen.getByTestId('construction-password-input'), { target: { value: 'nope' } });
    fireEvent.click(screen.getByTestId('construction-password-submit'));
    expect(onBypass).not.toHaveBeenCalled();
    expect(screen.getByTestId('construction-password-error')).toBeInTheDocument();

    siteGate.verifySitePreviewPassword.mockReturnValue(true);
    fireEvent.change(screen.getByTestId('construction-password-input'), { target: { value: 'secret' } });
    fireEvent.click(screen.getByTestId('construction-password-submit'));
    expect(onBypass).toHaveBeenCalledWith({ persist: false });
  });
});