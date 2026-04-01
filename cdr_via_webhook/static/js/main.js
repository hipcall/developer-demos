let allCDRs = [];

async function fetchCDRs() {
    try {
        const response = await fetch('/api/cdrs');
        allCDRs = await response.json();

        renderTable(allCDRs);
        updateStats(allCDRs);

    } catch (err) {
        console.error('CDR fetch error:', err);
    }
}

function renderTable(cdrs) {
    const body = document.getElementById('cdr-body');
    body.innerHTML = '';

    if (cdrs.length === 0) {
        body.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 20px;">No records found.</td></tr>';
        return;
    }

    cdrs.forEach(cdr => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="direction-tag ${cdr.direction}">${cdr.direction === 'inbound' ? 'Inbound' : 'Outbound'}</span></td>
            <td>${cdr.caller_number || '-'}</td>
            <td>${cdr.callee_number || '-'}</td>
            <td>${formatDuration(cdr.duration)}</td>
            <td>${formatDate(cdr.started_at)}</td>
            <td><button class="btn-details" onclick="showDetails('${cdr.uuid}')">Details</button></td>
        `;
        body.appendChild(tr);
    });
}

function updateStats(cdrs) {
    let inbound = 0;
    let outbound = 0;
    let missed = 0;
    let totalDuration = 0;

    cdrs.forEach(cdr => {
        if (cdr.direction === 'inbound') inbound++;
        else outbound++;

        if (cdr.duration === 0) missed++;

        totalDuration += cdr.duration;
    });

    document.getElementById('total-inbound').innerText = inbound;
    document.getElementById('total-outbound').innerText = outbound;
    document.getElementById('total-missed').innerText = missed;
    document.getElementById('avg-duration').innerText = cdrs.length > 0 ? formatDuration(Math.round(totalDuration / cdrs.length)) : '0s';
}

async function showDetails(uuid) {
    try {
        const response = await fetch(`/api/cdrs/${uuid}`);
        const cdr = await response.json();

        document.getElementById('detail-uuid').innerText = cdr.uuid;
        document.getElementById('detail-caller').innerText = cdr.caller_number || '-';
        document.getElementById('detail-callee').innerText = cdr.callee_number || '-';
        document.getElementById('detail-direction').innerText = cdr.direction === 'inbound' ? 'Inbound' : 'Outbound';
        document.getElementById('detail-duration').innerText = formatDuration(cdr.duration);
        document.getElementById('detail-start').innerText = formatDate(cdr.started_at);
        document.getElementById('detail-end').innerText = formatDate(cdr.ended_at);
        document.getElementById('detail-hangup').innerText = cdr.hangup_by || '-';

        try {
            const raw = JSON.parse(cdr.raw_payload);
            document.getElementById('detail-raw').innerText = JSON.stringify(raw, null, 2);
        } catch (e) {
            document.getElementById('detail-raw').innerText = cdr.raw_payload;
        }

        const playerContainer = document.getElementById('record-player-container');
        const audio = document.getElementById('detail-audio');

        const audioSrc = cdr.local_record_path || cdr.record_url;
        if (audioSrc) {
            playerContainer.style.display = 'block';
            audio.src = audioSrc;
        } else {
            playerContainer.style.display = 'none';
        }

        document.getElementById('details-modal').style.display = 'block';
    } catch (err) {
        console.error('Detail fetch error:', err);
    }
}

function closeModal() {
    document.getElementById('details-modal').style.display = 'none';
    document.getElementById('detail-audio').pause();
}

function formatDuration(seconds) {
    if (!seconds) return '0s';
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return m > 0 ? `${m}dk ${s}sn` : `${s}sn`;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('tr-TR');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Modal close outside click
    window.onclick = function (event) {
        const modal = document.getElementById('details-modal');
        if (event.target == modal) {
            closeModal();
        }
    }

    // Initial fetch
    fetchCDRs();
    // Auto refresh every 20 seconds
    setInterval(fetchCDRs, 20000);
});
