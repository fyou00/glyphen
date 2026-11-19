window.ProfileUI = (() => {
  const el = id => document.getElementById(id);
  const dialog = el('profile-dialog');
  let current = null, draftId = null, callback = null, working = false, rendering = false;
  const blobs = new Map();
  async function api(path, options={}) {
    const response = await fetch(path, options);
    const body = await response.json();
    if(response.status===404&&path==='/api/profiles')throw new Error('Server masih memakai versi lama. Hentikan dan jalankan ulang server setelah pembaruan.');
    if (!response.ok) throw new Error(body.detail || 'Permintaan profil belum berhasil.');
    return body;
  }
  const json = (method, data) => ({method, headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
  function showError(id, error) {el(id).textContent = error instanceof TypeError ? 'Koneksi terputus. Pastikan server lokal berjalan.' : error.message;el(id).hidden=false;}
  function controls() {
    el('profile-select').disabled = working || rendering || !current;
    for (const id of ['rename-profile','delete-profile']) el(id).disabled = working || rendering || !current;
    el('add-profile').disabled = working || rendering;
    el('review-profile').hidden = !current || current.ready;
    el('review-profile').disabled = working || rendering;
    dialog.querySelector('.close-dialog').disabled = working;
    document.querySelectorAll('#rename-dialog button,#delete-dialog button').forEach(b=>b.disabled=working);
    el('extract-profile').disabled = working;
    el('reject-crops').disabled = working;
  }
  function setWorking(value, message='') {
    working=value;el('profile-progress').textContent=message;
    document.dispatchEvent(new CustomEvent('profile-busy',{detail:value}));controls();allowUploads();
  }
  async function reload(selectedId=null, initial=false) {
    const data = await api('/api/profiles');
    const select=el('profile-select');select.replaceChildren();
    for(const profile of data.profiles) {
      const option=document.createElement('option');option.value=profile.user_id;
      option.textContent=profile.display_name+(profile.ready?'':' · Belum siap');select.append(option);
    }
    const id=data.profiles.some(p=>p.user_id===selectedId)?selectedId:data.default_user_id;
    current=id?await api(`/api/profiles/${encodeURIComponent(id)}`):null;
    if(current) select.value=current.user_id;
    else {const option=document.createElement('option');option.textContent='Belum ada profil';option.value='';select.append(option);}
    controls();await callback?.(current,initial);return current;
  }
  function stage(name) {
    el('profile-upload-form').hidden=name!=='upload';el('profile-review-form').hidden=name!=='review';el('profile-result').hidden=name!=='result';
  }
  function setRotation(page,angle) {
    const normalized=(angle+360)%360;
    el(`rotation-${page}`).value=String(normalized);
    el(`rotation-angle-${page}`).textContent=`${normalized}°`;
    el(`sample-preview-${page}`).className=`rotate-${normalized}`;
  }
  function clearFiles() {
    for(let n=1;n<=3;n++) {
      if(blobs.has(n)) URL.revokeObjectURL(blobs.get(n));blobs.delete(n);
      el(`sample-${n}`).value='';setRotation(n,0);
      el(`sample-preview-${n}`).hidden=true;el(`sample-preview-${n}`).className='';el(`sample-hint-${n}`).hidden=false;
    }
  }
  function allowUploads() {
    const enabled=el('owner-name').value.trim()&&el('owner-consent').checked;
    for(let n=1;n<=3;n++) el(`sample-${n}`).disabled=!enabled||working;
    for(let n=1;n<=3;n++) for(const direction of ['left','right'])
      el(`rotate-${direction}-${n}`).disabled=working||!enabled||!el(`sample-${n}`).files.length;
  }
  function uploadStage(existing=null) {
    stage('upload');clearFiles();draftId=existing?.user_id||null;
    el('profile-dialog-title').textContent=existing?'Unggah sampel profil':'Tambahkan tulisanmu';
    el('owner-name').value=existing?.display_name||'';el('owner-name').disabled=!!existing;
    el('owner-consent').checked=false;el('owner-consent').disabled=false;
    allowUploads();
  }
  function resultStage(profile) {
    stage('result');
    el('profile-result-title').textContent=profile.ready?'Profil siap dipakai':'Sampel perlu diperbaiki';
    el('profile-result-detail').textContent=profile.ready?'Semua huruf memiliki minimal 3 varian dan tinjauan potongan sudah lolos.':profile.detail;
    el('incomplete-labels').textContent=profile.incomplete_labels.length?'Huruf belum lengkap: '+profile.incomplete_labels.join(', '):'';
    el('retry-samples').hidden=profile.ready;el('use-profile').hidden=!profile.ready;
  }
  function reviewStage(profile) {
    draftId=profile.user_id;stage('review');el('profile-dialog-title').textContent='Periksa hasil ekstraksi';
    const c=profile.counts;el('extraction-counts').textContent=`${c.ok} OK · ${c.empty} kosong · ${c.touches_edge} menyentuh tepi`;
    const pages=el('debug-pages');pages.replaceChildren();
    for(const page of profile.pages) {
      const card=document.createElement('div');card.className='debug-card';
      const heading=document.createElement('h3');heading.textContent=`TPL-0${page.page}`;
      const link=document.createElement('a');link.href=page.url;link.target='_blank';link.rel='noopener';link.className='debug-link';
      const image=document.createElement('img');image.src=page.url;image.alt=`Hasil pemeriksaan kotak TPL-0${page.page}`;link.append(image);
      const full=document.createElement('a');full.href=page.url;full.target='_blank';full.rel='noopener';full.textContent='Buka gambar penuh';full.className='text-button';
      const label=document.createElement('label');label.className='consent-row';
      const checkbox=document.createElement('input');checkbox.type='checkbox';checkbox.className='page-reviewed';checkbox.value=page.page;
      const text=document.createElement('span');text.textContent='Saya sudah memeriksa semua kotak halaman ini; tinta utuh dan potongan sesuai.';label.append(checkbox,text);
      card.append(heading,link,full,label);pages.append(card);
    }
    const edges=el('edge-glyphs');edges.replaceChildren();el('edge-section').hidden=!profile.edges.length;
    for(const edge of profile.edges) {
      const label=document.createElement('label');label.className='edge-card';const image=document.createElement('img');image.src=edge.url;image.alt=`${edge.label}, varian ${edge.variant}`;
      const check=document.createElement('input');check.type='checkbox';check.className='edge-reviewed';check.dataset.label=edge.label;check.dataset.variant=edge.variant;
      const text=document.createElement('span');text.textContent=`${edge.label} ${edge.variant}: tinta masih utuh`;label.append(image,check,text);edges.append(label);
    }
    updateReview();
  }
  function updateReview() {
    const checks=[...el('profile-review-form').querySelectorAll('input[type=checkbox]')];
    el('accept-crops').disabled=working||el('debug-pages').children.length!==3||checks.some(c=>!c.checked);
  }
  async function openExisting() {
    if(!current)return;el('profile-error').hidden=true;el('profile-progress').textContent='';
    const profile=await api(`/api/profiles/${current.user_id}`);draftId=profile.user_id;
    if(profile.status==='awaiting_review')reviewStage(profile);
    else if(profile.status==='draft')uploadStage(profile);
    else resultStage(profile);
    dialog.showModal();
  }
  async function submitReview(correct) {
    if(working)return;
    const payload={crops_correct:correct,pages_checked:[...document.querySelectorAll('.page-reviewed:checked')].map(c=>Number(c.value)),accepted_edges:[...document.querySelectorAll('.edge-reviewed:checked')].map(c=>({label:c.dataset.label,variant:Number(c.dataset.variant)}))};
    setWorking(true,'Menyimpan tinjauan dan memeriksa coverage…');updateReview();el('profile-error').hidden=true;
    try {const profile=await api(`/api/profiles/${draftId}/review`,json('POST',payload));await reload(draftId);resultStage(profile);}
    catch(error){showError('profile-error',error);}finally{setWorking(false);updateReview();}
  }
  async function init(onChange) {
    callback=onChange;
    el('profile-select').addEventListener('change',async()=>{try{await reload(el('profile-select').value);}catch(error){showError('form-error',error);}});
    el('add-profile').addEventListener('click',()=>{el('profile-error').hidden=true;el('profile-progress').textContent='';uploadStage();dialog.showModal();});
    el('review-profile').addEventListener('click',()=>openExisting().catch(error=>showError('form-error',error)));
    el('owner-name').addEventListener('input',allowUploads);el('owner-consent').addEventListener('change',allowUploads);
    for(let n=1;n<=3;n++) {
      el(`sample-${n}`).addEventListener('change',()=>{
        if(blobs.has(n))URL.revokeObjectURL(blobs.get(n));const file=el(`sample-${n}`).files[0];
        const preview=el(`sample-preview-${n}`);preview.hidden=!file;el(`sample-hint-${n}`).hidden=!!file;
        if(file){const url=URL.createObjectURL(file);blobs.set(n,url);preview.src=url;}
        allowUploads();
      });
      for(const [direction,step] of [['left',-90],['right',90]])
        el(`rotate-${direction}-${n}`).addEventListener('click',()=>{
          if(!working&&!el(`rotate-${direction}-${n}`).disabled) setRotation(n,Number(el(`rotation-${n}`).value)+step);
        });
    }
    el('profile-upload-form').addEventListener('submit',async event=>{
      event.preventDefault();if(working)return;el('profile-error').hidden=true;
      const files=[1,2,3].map(n=>el(`sample-${n}`).files[0]);
      if(files.some(f=>!f||f.size>10*1024*1024)){showError('profile-error',new Error('Pilih tiga gambar, masing-masing maksimal 10 MiB.'));return;}
      setWorking(true,'Menyimpan persetujuan dan mengekstrak tiga halaman…');
      try {
        if(!draftId){const p=await api('/api/profiles',json('POST',{display_name:el('owner-name').value,consent:el('owner-consent').checked}));draftId=p.user_id;el('owner-name').disabled=true;}
        const data=new FormData();data.append('owner_confirmation',String(el('owner-consent').checked));files.forEach((f,i)=>{data.append(`tpl0${i+1}`,f);data.append(`rotation${i+1}`,el(`rotation-${i+1}`).value);});
        const profile=await api(`/api/profiles/${draftId}/samples`,{method:'POST',body:data});
        await reload(draftId);reviewStage(profile);
      } catch(error){showError('profile-error',error);if(draftId){try{await reload(draftId);}catch{ /* Pesan koneksi awal tetap terlihat. */ }}}
      finally{setWorking(false);allowUploads();updateReview();}
    });
    el('profile-review-form').addEventListener('change',updateReview);
    el('profile-review-form').addEventListener('submit',event=>{event.preventDefault();submitReview(true);});
    el('reject-crops').addEventListener('click',()=>submitReview(false));
    el('retry-samples').addEventListener('click',()=>{uploadStage(current);el('profile-error').hidden=true;});
    el('use-profile').addEventListener('click',()=>dialog.close());
    el('rename-profile').addEventListener('click',()=>{el('new-profile-name').value=current.display_name;el('rename-error').hidden=true;el('rename-dialog').showModal();});
    el('rename-form').addEventListener('submit',async event=>{
      event.preventDefault();if(working)return;setWorking(true);
      try{await api(`/api/profiles/${current.user_id}`,json('PATCH',{display_name:el('new-profile-name').value}));await reload(current.user_id);el('rename-dialog').close();}catch(error){showError('rename-error',error);}finally{setWorking(false);}
    });
    el('delete-profile').addEventListener('click',()=>{el('delete-profile-name').textContent=current.display_name;el('confirm-delete').checked=false;el('delete-error').hidden=true;el('delete-dialog').showModal();});
    el('delete-form').addEventListener('submit',async event=>{
      event.preventDefault();if(working)return;setWorking(true);
      try{await api(`/api/profiles/${current.user_id}`,json('DELETE',{confirm:el('confirm-delete').checked}));await reload();el('delete-dialog').close();}catch(error){showError('delete-error',error);}finally{setWorking(false);}
    });
    document.querySelectorAll('.close-dialog').forEach(button=>button.addEventListener('click',()=>{if(!working)button.closest('dialog').close();}));
    document.querySelectorAll('dialog').forEach(d=>d.addEventListener('cancel',event=>{if(working)event.preventDefault();}));
    dialog.addEventListener('close',clearFiles);
    await reload(null,true);
  }
  return {init,setRenderBusy(value){rendering=value;controls();}};
})();
