/**
 * Validierungs-Utilities für Formulare
 */

// E-Mail Validierung
export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) {
    return { valid: false, message: 'E-Mail-Adresse ist erforderlich' };
  }
  if (!re.test(email)) {
    return { valid: false, message: 'Bitte geben Sie eine gültige E-Mail-Adresse ein' };
  }
  return { valid: true, message: '' };
};

// Passwort Validierung
export const validatePassword = (password) => {
  if (!password) {
    return { valid: false, message: 'Passwort ist erforderlich' };
  }
  if (password.length < 8) {
    return { valid: false, message: 'Passwort muss mindestens 8 Zeichen lang sein' };
  }
  if (!/[A-Z]/.test(password)) {
    return { valid: false, message: 'Passwort muss mindestens einen Großbuchstaben enthalten' };
  }
  if (!/[a-z]/.test(password)) {
    return { valid: false, message: 'Passwort muss mindestens einen Kleinbuchstaben enthalten' };
  }
  if (!/[0-9]/.test(password)) {
    return { valid: false, message: 'Passwort muss mindestens eine Zahl enthalten' };
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return { valid: false, message: 'Passwort muss mindestens ein Sonderzeichen enthalten (!@#$%^&*...)' };
  }
  return { valid: true, message: 'Passwort ist stark' };
};

// Passwort-Übereinstimmung
export const validatePasswordMatch = (password, confirmPassword) => {
  if (!confirmPassword) {
    return { valid: false, message: 'Bitte bestätigen Sie Ihr Passwort' };
  }
  if (password !== confirmPassword) {
    return { valid: false, message: 'Passwörter stimmen nicht überein' };
  }
  return { valid: true, message: 'Passwörter stimmen überein' };
};

// Name Validierung
export const validateName = (name) => {
  if (!name || name.trim().length === 0) {
    return { valid: false, message: 'Name ist erforderlich' };
  }
  if (name.trim().length < 2) {
    return { valid: false, message: 'Name muss mindestens 2 Zeichen lang sein' };
  }
  return { valid: true, message: '' };
};

// Telefon Validierung
export const validatePhone = (phone) => {
  if (!phone) {
    return { valid: true, message: '' }; // Optional field
  }
  const re = /^[+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$/;
  if (!re.test(phone.replace(/\s/g, ''))) {
    return { valid: false, message: 'Bitte geben Sie eine gültige Telefonnummer ein' };
  }
  return { valid: true, message: '' };
};

// URL Validierung
export const validateURL = (url) => {
  if (!url) {
    return { valid: true, message: '' }; // Optional field
  }
  try {
    new URL(url);
    return { valid: true, message: '' };
  } catch (e) {
    return { valid: false, message: 'Bitte geben Sie eine gültige URL ein (z.B. https://beispiel.de)' };
  }
};

// Firma Validierung
export const validateCompanyName = (name) => {
  if (!name || name.trim().length === 0) {
    return { valid: false, message: 'Firmenname ist erforderlich' };
  }
  if (name.trim().length < 2) {
    return { valid: false, message: 'Firmenname muss mindestens 2 Zeichen lang sein' };
  }
  return { valid: true, message: '' };
};

// Passwort-Stärke berechnen
export const calculatePasswordStrength = (password) => {
  let strength = 0;
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
  
  if (strength <= 2) return { level: 'weak', label: 'Schwach', color: 'red' };
  if (strength <= 4) return { level: 'medium', label: 'Mittel', color: 'yellow' };
  return { level: 'strong', label: 'Stark', color: 'green' };
};
