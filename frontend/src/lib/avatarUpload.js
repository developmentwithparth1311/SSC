/** Resize and compress profile photo before upload (max 128px, JPEG). */

const MAX_BYTES = 480_000;
const MAX_DIM = 128;

export async function prepareAvatarFile(file) {
  if (!file?.type?.startsWith('image/')) {
    throw new Error('AVATAR_TYPE');
  }
  if (file.size > 8 * 1024 * 1024) {
    throw new Error('AVATAR_TOO_LARGE');
  }

  const bitmap = await createImageBitmap(file);
  const scale = Math.min(1, MAX_DIM / Math.max(bitmap.width, bitmap.height));
  const w = Math.max(1, Math.round(bitmap.width * scale));
  const h = Math.max(1, Math.round(bitmap.height * scale));

  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(bitmap, 0, 0, w, h);
  bitmap.close();

  let quality = 0.88;
  let blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', quality));
  while (blob && blob.size > MAX_BYTES && quality > 0.4) {
    quality -= 0.12;
    blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', quality));
  }
  if (!blob) throw new Error('AVATAR_ENCODE_FAIL');
  if (blob.size > MAX_BYTES) throw new Error('AVATAR_TOO_LARGE');

  return new File([blob], 'avatar.jpg', { type: 'image/jpeg' });
}