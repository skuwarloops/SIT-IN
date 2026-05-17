// ── FILTER TABS ─────────────────────────────────────────
const ftabs    = document.querySelectorAll('.ftab');
const items    = document.querySelectorAll('#annList > [data-category]');
const emptyEl  = document.getElementById('emptyState');
const searchEl = document.getElementById('announcementSearch');

let currentFilter = 'all';
let currentSearch = '';

function applyFilters() {
  let visible = 0;
  items.forEach(item => {
    const catMatch    = currentFilter === 'all' || item.dataset.category === currentFilter;
    const searchText  = item.innerText.toLowerCase();
    const searchMatch = searchText.includes(currentSearch.toLowerCase());
    const show = catMatch && searchMatch;
    item.style.display = show ? '' : 'none';
    if (show) visible++;
  });
  if (emptyEl) emptyEl.classList.toggle('hidden', visible > 0);
}

ftabs.forEach(tab => {
  tab.addEventListener('click', () => {
    ftabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentFilter = tab.dataset.filter;
    applyFilters();
  });
});

if (searchEl) {
  searchEl.addEventListener('input', () => {
    currentSearch = searchEl.value;
    applyFilters();
  });
}

// ── VOTING ───────────────────────────────────────────────
document.querySelectorAll('.thread-votes').forEach(voteBox => {
  const upBtn    = voteBox.querySelector('.vote-btn:not(.down)');
  const downBtn  = voteBox.querySelector('.vote-btn.down');
  const countEl  = voteBox.querySelector('.vote-count');
  let count = parseInt(countEl.textContent);
  let voted = null; // 'up' | 'down' | null

  upBtn.addEventListener('click', () => {
    if (voted === 'up') {
      count--;
      voted = null;
      upBtn.classList.remove('voted');
    } else {
      if (voted === 'down') { count++; downBtn.classList.remove('voted'); }
      count++;
      voted = 'up';
      upBtn.classList.add('voted');
    }
    countEl.textContent = count;
  });

  downBtn.addEventListener('click', () => {
    if (voted === 'down') {
      count++;
      voted = null;
      downBtn.classList.remove('voted');
    } else {
      if (voted === 'up') { count--; upBtn.classList.remove('voted'); }
      count--;
      voted = 'down';
      downBtn.classList.add('voted');
    }
    countEl.textContent = count;
  });
});

// ── REPLY TOGGLE ─────────────────────────────────────────
document.querySelectorAll('.reply-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const form = btn.closest('.thread-body').querySelector('.reply-form');
    form.classList.toggle('hidden');
    if (!form.classList.contains('hidden')) form.querySelector('textarea').focus();
  });
});

document.querySelectorAll('.cancel-reply').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.closest('.reply-form').classList.add('hidden');
  });
});

document.querySelectorAll('.submit-reply').forEach(btn => {
  btn.addEventListener('click', () => {
    const form    = btn.closest('.reply-form');
    const ta      = form.querySelector('textarea');
    const text    = ta.value.trim();
    if (!text) return;
    const replies = form.closest('.thread-body').querySelector('.replies');

    const div = document.createElement('div');
    div.className = 'reply';
    div.innerHTML = `<span class="reply-author">👤 You</span><p>${text}</p>`;
    replies.appendChild(div);

    // Update reply count
    const countEl = form.closest('.thread-body').querySelector('.thread-replies');
    if (countEl) {
      const n = parseInt(countEl.textContent) || 0;
      countEl.textContent = `💬 ${n + 1} ${n + 1 === 1 ? 'reply' : 'replies'}`;
    }

    ta.value = '';
    form.classList.add('hidden');
  });
});

// ── NEW POST MODAL (Forums only) ─────────────────────────
const openModal   = document.getElementById('openModal');
const closeModal  = document.getElementById('closeModal');
const cancelPost  = document.getElementById('cancelPost');
const submitPost  = document.getElementById('submitPost');
const overlay     = document.getElementById('modalOverlay');
const list        = document.getElementById('annList');

function openModalFn() { overlay && overlay.classList.remove('hidden'); }
function closeModalFn() { overlay && overlay.classList.add('hidden'); }

openModal  && openModal.addEventListener('click', openModalFn);
closeModal && closeModal.addEventListener('click', closeModalFn);
cancelPost && cancelPost.addEventListener('click', closeModalFn);
overlay    && overlay.addEventListener('click', e => { if (e.target === overlay) closeModalFn(); });

submitPost && submitPost.addEventListener('click', () => {
  const title    = document.getElementById('postTitle').value.trim();
  const body     = document.getElementById('postBody').value.trim();
  const category = document.getElementById('postCategory').value;
  if (!title) { alert('Please enter a title.'); return; }

  const tagMap = { question: 'general', discussion: 'schedule', tip: 'important' };
  const labelMap = { question: 'Question', discussion: 'Discussion', tip: 'Tip' };

  const thread = document.createElement('div');
  thread.className = 'forum-thread';
  thread.dataset.category = category;
  thread.innerHTML = `
    <div class="thread-votes">
      <button class="vote-btn">▲</button>
      <span class="vote-count">0</span>
      <button class="vote-btn down">▼</button>
    </div>
    <div class="thread-body">
      <div class="ann-meta">
        <span class="ann-tag ${tagMap[category]}">${labelMap[category]}</span>
        <span class="ann-date">Just now</span>
      </div>
      <h3>${title}</h3>
      <p>${body || 'No details provided.'}</p>
      <div class="thread-footer">
        <span class="thread-author">👤 You</span>
        <span class="thread-replies">💬 0 replies</span>
        <button class="ann-read reply-btn">Reply</button>
      </div>
      <div class="replies"></div>
      <div class="reply-form hidden">
        <textarea placeholder="Write a reply…" rows="3"></textarea>
        <div style="display:flex;gap:8px;margin-top:8px;">
          <button class="ann-read submit-reply">Post Reply</button>
          <button class="ann-read cancel-reply" style="background:transparent;border:1px solid var(--card-border);color:var(--muted);">Cancel</button>
        </div>
      </div>
    </div>`;

  list.prepend(thread);

  // Wire up new thread buttons
  thread.querySelector('.reply-btn').addEventListener('click', () => {
    const form = thread.querySelector('.reply-form');
    form.classList.toggle('hidden');
  });
  thread.querySelector('.cancel-reply').addEventListener('click', () => {
    thread.querySelector('.reply-form').classList.add('hidden');
  });
  thread.querySelector('.submit-reply').addEventListener('click', () => {
    const ta = thread.querySelector('textarea');
    const txt = ta.value.trim();
    if (!txt) return;
    const rep = document.createElement('div');
    rep.className = 'reply';
    rep.innerHTML = `<span class="reply-author">👤 You</span><p>${txt}</p>`;
    thread.querySelector('.replies').appendChild(rep);
    ta.value = '';
    thread.querySelector('.reply-form').classList.add('hidden');
    const rc = thread.querySelector('.thread-replies');
    const n = parseInt(rc.textContent) || 0;
    rc.textContent = `💬 ${n+1} ${n+1===1?'reply':'replies'}`;
  });

  // Wire voting
  const vb = thread.querySelectorAll('.vote-btn');
  const vc = thread.querySelector('.vote-count');
  let cnt = 0, vt = null;
  vb[0].addEventListener('click', () => {
    if (vt==='up'){cnt--;vt=null;vb[0].classList.remove('voted');}
    else{if(vt==='down'){cnt++;vb[1].classList.remove('voted');}cnt++;vt='up';vb[0].classList.add('voted');}
    vc.textContent=cnt;
  });
  vb[1].addEventListener('click', () => {
    if(vt==='down'){cnt++;vt=null;vb[1].classList.remove('voted');}
    else{if(vt==='up'){cnt--;vb[0].classList.remove('voted');}cnt--;vt='down';vb[1].classList.add('voted');}
    vc.textContent=cnt;
  });

  // Clear & close
  document.getElementById('postTitle').value = '';
  document.getElementById('postBody').value  = '';
  closeModalFn();
  applyFilters();
});
