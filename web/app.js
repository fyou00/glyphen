const $ = (id) => document.getElementById(id);
const form = $('editor');
const text = $('text');
let profileReady = false;
let busy = false;
let result = null;
let currentPage = 0;
let renderedInput = '';

function inputSignature() {
  return JSON.stringify({text:text.value, doc_type:form.elements.doc_type.value,
    seed:$('seed').value === '' ? null : Number($('seed').value), guidelines:$('guidelines').checked});
}
function setDownload(link, url) {
  link.setAttribute('aria-disabled', url ? 'false' : 'true');
  if (url) {link.href = `${url}?download=true`;link.setAttribute('download','');}
  else {link.removeAttribute('href');link.removeAttribute('download');}
}
function updateInputs() {
  $('character-count').textContent = `${Array.from(text.value).length.toLocaleString('id-ID')} / 12.000`;
  $('render').disabled = busy || !profileReady || !text.value.trim();
  const stale = result && inputSignature() !== renderedInput;
  if (stale && !busy) {
    $('result-status').textContent = 'Ada perubahan pada catatan';
    $('result-detail').textContent = 'Buat ulang tulisan untuk memperbarui pratinjau.';
  } else if (result && !busy) {
    $('result-status').textContent = 'Tulisanmu sudah siap';
    $('result-detail').textContent = `${result.pages} halaman · ${result.elapsed_seconds.toFixed(2).replace('.',',')} detik`;
  }
  setDownload($('download-pdf'), result && !stale && !busy ? result.pdf_url : null);
  setDownload($('download-png'), result && !stale && !busy ? result.png_urls[currentPage] : null);
  $('guidelines').disabled = form.elements.doc_type.value !== 'catatan';
}
function showPage(page) {
  if (!result) return;
  currentPage = Math.max(0, Math.min(result.pages - 1, page));
  $('preview-image').src = result.png_urls[currentPage];
  $('preview-image').alt = `Pratinjau halaman ${currentPage + 1} dari ${result.pages}, dengan watermark tidak resmi`;
  $('preview-image').hidden = false;
  $('preview-placeholder').hidden = true;
  $('page-counter').textContent = `${currentPage + 1} / ${result.pages}`;
  $('download-png').setAttribute('aria-label', `Unduh PNG halaman ${currentPage + 1}`);
  $('previous').disabled = busy || currentPage === 0;
  $('next').disabled = busy || currentPage === result.pages - 1;
  updateInputs();
}
function setBusy(value) {
  busy = value;
  $('loading').hidden = !value;
  $('preview-panel').setAttribute('aria-busy', String(value));
  $('render-label').textContent = value ? 'Menyusun tulisan…' : 'Buat tulisan tangan';
  $('previous').disabled = value || !result || currentPage === 0;
  $('next').disabled = value || !result || currentPage === result.pages - 1;
  if (value) $('result-status').textContent = 'Sedang membuat dokumen';
  updateInputs();
}
async function generate(event) {
  event?.preventDefault();
  if (busy || !profileReady || !text.value.trim() || !form.reportValidity()) return;
  $('form-error').hidden = true;
  const signature = inputSignature();
  setBusy(true);
  try {
    const response = await fetch('/api/render', {method:'POST', headers:{'Content-Type':'application/json'}, body:signature});
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Dokumen belum bisa dibuat. Coba kembali.');
    result = data;
    renderedInput = signature;
    const warnings = [];
    if (data.missing_characters.length) warnings.push(`Karakter belum tersedia: ${data.missing_characters.map(c => JSON.stringify(c)).join(', ')}. Kotak pengganti ditampilkan pada posisinya.`);
    if (data.below_ideal_labels.length) warnings.push('Sebagian huruf memiliki kurang dari 5 varian. Minimum coverage sudah terpenuhi.');
    $('missing-warning').textContent = warnings.join(' ');
    $('missing-warning').hidden = warnings.length === 0;
    showPage(0);
  } catch (error) {
    $('form-error').textContent = error instanceof TypeError ? 'Koneksi ke aplikasi terputus. Pastikan server lokal masih berjalan.' : error.message || 'Dokumen belum bisa dibuat. Coba kembali.';
    $('form-error').hidden = false;
    if (!result) {
      $('preview-placeholder').querySelector('p').textContent = 'Pratinjau akan muncul setelah dokumen berhasil dibuat.';
      $('result-status').textContent = 'Pratinjau belum tersedia';
    }
  } finally {setBusy(false);}
}
form.addEventListener('submit', generate);
form.addEventListener('input', updateInputs);
form.addEventListener('change', updateInputs);
$('clear').addEventListener('click', () => {text.value='';updateInputs();text.focus();});
$('previous').addEventListener('click', () => showPage(currentPage - 1));
$('next').addEventListener('click', () => showPage(currentPage + 1));
$('zoom').addEventListener('click', () => {
  const zoomed = $('paper-stage').classList.toggle('zoomed');
  $('zoom').setAttribute('aria-pressed', String(zoomed));
  $('zoom').setAttribute('aria-label', zoomed ? 'Pas halaman' : 'Perbesar pratinjau');
  $('zoom').textContent = zoomed ? '−' : '＋';
});
document.addEventListener('keydown', (event) => {if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {event.preventDefault();generate();}});
for (const id of ['download-pdf','download-png']) $(id).addEventListener('click', event => {if ($(id).getAttribute('aria-disabled') === 'true') event.preventDefault();});
$('preview-image').addEventListener('error', () => {$('form-error').textContent='Gambar pratinjau belum bisa dimuat. Coba buat ulang dokumen.';$('form-error').hidden=false;});
async function boot() {
  updateInputs();
  try {
    const response = await fetch('/api/profile');
    if (!response.ok) throw new Error('Profil belum bisa dimuat. Pastikan aplikasi lokal masih berjalan.');
    const profile = await response.json();
    $('profile-id').textContent = profile.user_id;
    profileReady = profile.ready;
    $('profile-state').textContent = profile.ready ? 'Siap dipakai' : 'Perlu diperiksa';
    $('profile-state').classList.toggle('unready',!profile.ready);
    if (!profile.ready) throw new Error(profile.detail);
    await generate();
  } catch (error) {
    $('form-error').textContent = error instanceof TypeError ? 'Profil belum bisa dimuat. Pastikan aplikasi lokal masih berjalan.' : error.message;
    $('form-error').hidden = false;
    $('result-status').textContent = 'Pratinjau belum tersedia';
    $('preview-placeholder').querySelector('p').textContent = 'Siapkan profil tulisan untuk mulai membuat catatan.';
    if (!profileReady) {
      $('profile-state').textContent = 'Belum siap';
      $('profile-state').classList.add('unready');
    }
  }
  updateInputs();
}
boot();
