import { getStoredUiLang, normalizeLang, setStoredUiLang, t } from '../i18n';

describe('i18n', () => {
  it('normalizes language codes to supported UI locales', () => {
    expect(normalizeLang('EN')).toBe('en');
    expect(normalizeLang('es-ES')).toBe('es');
    expect(normalizeLang('xx')).toBe('en');
  });

  it('persists and reads UI language from localStorage', () => {
    setStoredUiLang('ro');
    expect(getStoredUiLang()).toBe('ro');
  });

  it('returns English strings by default', () => {
    expect(t('landingLogin', 'en')).toBe('Login');
  });

  it('returns Romanian strings when locale is ro', () => {
    expect(t('landingLogin', 'ro')).toBe('Autentificare');
  });

  it('interpolates variables in translated strings', () => {
    expect(t('inviteFrom', 'en', { user: 'alice' })).toBe('@alice wants to connect');
  });
});