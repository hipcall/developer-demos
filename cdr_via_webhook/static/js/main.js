const translations = {
    en: {
        subtitle: 'Online call logs',
        pageTitle: 'Call Detail Reports (CDR)', pageDesc: 'All terminated call records via Hipcall.',
        hipcallAccount: 'Hipcall Account', selectAccount: '— Select an account to play recordings —',
        inboundCalls: 'Inbound Calls', outboundCalls: 'Outbound Calls',
        missedCalls: 'Missed Calls', avgDuration: 'Avg. Duration',
        recentCalls: 'Recent Calls', refresh: 'Refresh', clearHistory: 'Clear History',
        direction: 'Direction', caller: 'Caller', callee: 'Callee',
        duration: 'Duration', date: 'Date', action: 'Action',
        inbound: 'Inbound', outbound: 'Outbound', noRecords: 'No records found.',
        details: 'Details', callDetails: 'Call Details', callUuid: 'Call UUID:',
        callerLabel: 'Caller:', calleeLabel: 'Callee:', directionLabel: 'Direction:',
        durationLabel: 'Duration:', startLabel: 'Start:', endLabel: 'End:',
        hangupLabel: 'Hangup Cause:', recording: 'Recording', rawData: 'Raw Data (Webhook Payload)',
        selectAccountToPlay: 'Please select a Hipcall account above to play this recording.',
        confirmClear: 'Are you sure you want to delete all call records? This cannot be undone.',
        successClear: 'All records deleted.', errClear: 'Failed to delete records.'
    },
    tr: {
        subtitle: 'Çevrimiçi arama kayıtları',
        pageTitle: 'Arama Detay Raporları (CDR)', pageDesc: 'Hipcall üzerinden gerçekleşen tüm tamamlanan aramalar.',
        hipcallAccount: 'Hipcall Hesabı', selectAccount: '— Kayıt dinlemek için hesap seçin —',
        inboundCalls: 'Gelen Aramalar', outboundCalls: 'Giden Aramalar',
        missedCalls: 'Cevapsız Aramalar', avgDuration: 'Ort. Süre',
        recentCalls: 'Son Aramalar', refresh: 'Yenile', clearHistory: 'Geçmişi Temizle',
        direction: 'Yön', caller: 'Arayan', callee: 'Aranan',
        duration: 'Süre', date: 'Tarih', action: 'İşlem',
        inbound: 'Gelen', outbound: 'Giden', noRecords: 'Kayıt bulunamadı.',
        details: 'Detaylar', callDetails: 'Arama Detayları', callUuid: 'Arama UUID:',
        callerLabel: 'Arayan:', calleeLabel: 'Aranan:', directionLabel: 'Yön:',
        durationLabel: 'Süre:', startLabel: 'Başlangıç:', endLabel: 'Bitiş:',
        hangupLabel: 'Kapatma Nedeni:', recording: 'Ses Kaydı', rawData: 'Ham Veri (Webhook Payload)',
        selectAccountToPlay: 'Bu kaydı dinlemek için lütfen yukarıdan bir Hipcall hesabı seçin.',
        confirmClear: 'Tüm arama kayıtlarını silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.',
        successClear: 'Tüm kayıtlar silindi.', errClear: 'Kayıtlar silinemedi.'
    },
    nl: {
        subtitle: 'Online gesprekslogboek',
        pageTitle: 'Gespreksdetailrapporten (CDR)', pageDesc: 'Alle beëindigde gesprekken via Hipcall.',
        hipcallAccount: 'Hipcall Account', selectAccount: '— Selecteer een account om opnames te beluisteren —',
        inboundCalls: 'Inkomende gesprekken', outboundCalls: 'Uitgaande gesprekken',
        missedCalls: 'Gemiste gesprekken', avgDuration: 'Gem. Duur',
        recentCalls: 'Recente gesprekken', refresh: 'Vernieuwen', clearHistory: 'Geschiedenis wissen',
        direction: 'Richting', caller: 'Beller', callee: 'Gebelde',
        duration: 'Duur', date: 'Datum', action: 'Actie',
        inbound: 'Inkomend', outbound: 'Uitgaand', noRecords: 'Geen records gevonden.',
        details: 'Details', callDetails: 'Gespreksdetails', callUuid: 'Gesprek UUID:',
        callerLabel: 'Beller:', calleeLabel: 'Gebelde:', directionLabel: 'Richting:',
        durationLabel: 'Duur:', startLabel: 'Start:', endLabel: 'Einde:',
        hangupLabel: 'Ophaagreden:', recording: 'Opname', rawData: 'Ruwe data (Webhook Payload)',
        selectAccountToPlay: 'Selecteer een Hipcall-account hierboven om deze opname te beluisteren.',
        confirmClear: 'Weet u zeker dat u alle gespreksrecords wilt verwijderen? Dit kan niet ongedaan worden gemaakt.',
        successClear: 'Alle records verwijderd.', errClear: 'Records verwijderen mislukt.'
    },
    it: {
        subtitle: 'Registro chiamate online',
        pageTitle: 'Rapporti Dettaglio Chiamate (CDR)', pageDesc: 'Tutti i record di chiamate terminate via Hipcall.',
        hipcallAccount: 'Account Hipcall', selectAccount: '— Seleziona un account per ascoltare le registrazioni —',
        inboundCalls: 'Chiamate in entrata', outboundCalls: 'Chiamate in uscita',
        missedCalls: 'Chiamate perse', avgDuration: 'Durata media',
        recentCalls: 'Chiamate recenti', refresh: 'Aggiorna', clearHistory: 'Cancella cronologia',
        direction: 'Direzione', caller: 'Chiamante', callee: 'Destinatario',
        duration: 'Durata', date: 'Data', action: 'Azione',
        inbound: 'In entrata', outbound: 'In uscita', noRecords: 'Nessun record trovato.',
        details: 'Dettagli', callDetails: 'Dettagli chiamata', callUuid: 'UUID chiamata:',
        callerLabel: 'Chiamante:', calleeLabel: 'Destinatario:', directionLabel: 'Direzione:',
        durationLabel: 'Durata:', startLabel: 'Inizio:', endLabel: 'Fine:',
        hangupLabel: 'Causa chiusura:', recording: 'Registrazione', rawData: 'Dati grezzi (Webhook Payload)',
        selectAccountToPlay: 'Seleziona un account Hipcall sopra per ascoltare questa registrazione.',
        confirmClear: 'Sei sicuro di voler eliminare tutti i record delle chiamate? Questa azione non può essere annullata.',
        successClear: 'Tutti i record eliminati.', errClear: 'Eliminazione record fallita.'
    },
    fr: {
        subtitle: 'Journal d\'appels en ligne',
        pageTitle: 'Rapports de détail des appels (CDR)', pageDesc: 'Tous les enregistrements d\'appels terminés via Hipcall.',
        hipcallAccount: 'Compte Hipcall', selectAccount: '— Sélectionner un compte pour écouter les enregistrements —',
        inboundCalls: 'Appels entrants', outboundCalls: 'Appels sortants',
        missedCalls: 'Appels manqués', avgDuration: 'Durée moy.',
        recentCalls: 'Appels récents', refresh: 'Actualiser', clearHistory: 'Effacer l\'historique',
        direction: 'Direction', caller: 'Appelant', callee: 'Appelé',
        duration: 'Durée', date: 'Date', action: 'Action',
        inbound: 'Entrant', outbound: 'Sortant', noRecords: 'Aucun enregistrement trouvé.',
        details: 'Détails', callDetails: 'Détails de l\'appel', callUuid: 'UUID de l\'appel:',
        callerLabel: 'Appelant:', calleeLabel: 'Appelé:', directionLabel: 'Direction:',
        durationLabel: 'Durée:', startLabel: 'Début:', endLabel: 'Fin:',
        hangupLabel: 'Cause de fin:', recording: 'Enregistrement', rawData: 'Données brutes (Webhook Payload)',
        selectAccountToPlay: 'Veuillez sélectionner un compte Hipcall ci-dessus pour écouter cet enregistrement.',
        confirmClear: 'Êtes-vous sûr de vouloir supprimer tous les enregistrements d\'appels ? Cette action est irréversible.',
        successClear: 'Tous les enregistrements supprimés.', errClear: 'Échec de la suppression des enregistrements.'
    },
    es: {
        subtitle: 'Registro de llamadas en línea',
        pageTitle: 'Informes de Detalle de Llamadas (CDR)', pageDesc: 'Todos los registros de llamadas terminadas vía Hipcall.',
        hipcallAccount: 'Cuenta Hipcall', selectAccount: '— Seleccionar una cuenta para reproducir grabaciones —',
        inboundCalls: 'Llamadas entrantes', outboundCalls: 'Llamadas salientes',
        missedCalls: 'Llamadas perdidas', avgDuration: 'Duración prom.',
        recentCalls: 'Llamadas recientes', refresh: 'Actualizar', clearHistory: 'Borrar historial',
        direction: 'Dirección', caller: 'Llamante', callee: 'Destinatario',
        duration: 'Duración', date: 'Fecha', action: 'Acción',
        inbound: 'Entrante', outbound: 'Saliente', noRecords: 'No se encontraron registros.',
        details: 'Detalles', callDetails: 'Detalles de la llamada', callUuid: 'UUID de llamada:',
        callerLabel: 'Llamante:', calleeLabel: 'Destinatario:', directionLabel: 'Dirección:',
        durationLabel: 'Duración:', startLabel: 'Inicio:', endLabel: 'Fin:',
        hangupLabel: 'Causa de cierre:', recording: 'Grabación', rawData: 'Datos brutos (Webhook Payload)',
        selectAccountToPlay: 'Selecciona una cuenta Hipcall arriba para escuchar esta grabación.',
        confirmClear: '¿Estás seguro de que deseas eliminar todos los registros de llamadas? Esta acción no se puede deshacer.',
        successClear: 'Todos los registros eliminados.', errClear: 'Error al eliminar los registros.'
    },
    de: {
        subtitle: 'Online-Anrufprotokoll',
        pageTitle: 'Anrufdetailberichte (CDR)', pageDesc: 'Alle beendeten Anrufaufzeichnungen über Hipcall.',
        hipcallAccount: 'Hipcall-Konto', selectAccount: '— Konto zum Abspielen von Aufnahmen auswählen —',
        inboundCalls: 'Eingehende Anrufe', outboundCalls: 'Ausgehende Anrufe',
        missedCalls: 'Verpasste Anrufe', avgDuration: 'Durchschn. Dauer',
        recentCalls: 'Letzte Anrufe', refresh: 'Aktualisieren', clearHistory: 'Verlauf löschen',
        direction: 'Richtung', caller: 'Anrufer', callee: 'Angerufener',
        duration: 'Dauer', date: 'Datum', action: 'Aktion',
        inbound: 'Eingehend', outbound: 'Ausgehend', noRecords: 'Keine Einträge gefunden.',
        details: 'Details', callDetails: 'Anrufdetails', callUuid: 'Anruf-UUID:',
        callerLabel: 'Anrufer:', calleeLabel: 'Angerufener:', directionLabel: 'Richtung:',
        durationLabel: 'Dauer:', startLabel: 'Start:', endLabel: 'Ende:',
        hangupLabel: 'Trennungsgrund:', recording: 'Aufnahme', rawData: 'Rohdaten (Webhook Payload)',
        selectAccountToPlay: 'Bitte wählen Sie oben ein Hipcall-Konto aus, um diese Aufnahme abzuspielen.',
        confirmClear: 'Sind Sie sicher, dass Sie alle Anrufdatensätze löschen möchten? Dies kann nicht rückgängig gemacht werden.',
        successClear: 'Alle Einträge gelöscht.', errClear: 'Einträge konnten nicht gelöscht werden.'
    }
};

function t(key) {
    const lang = document.getElementById('langSwitcher').value;
    return (translations[lang] && translations[lang][key]) || translations['en'][key] || key;
}

function changeLanguage() {
    const lang = document.getElementById('langSwitcher').value;
    localStorage.setItem('cdr_lang', lang);
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.textContent = t(el.getAttribute('data-i18n'));
    });
    const selectOpt = document.querySelector('[data-i18n-opt="selectAccount"]');
    if (selectOpt) selectOpt.textContent = t('selectAccount');
    renderTable(allCDRs);
}

function showAlert(message, type) {
    const container = document.getElementById('alert-container');
    container.innerHTML = `
        <div class="alert alert-${type}" style="padding:12px 16px; border-radius:8px; margin-bottom:16px; background:${type === 'success' ? '#d1fae5' : '#fee2e2'}; color:${type === 'success' ? '#065f46' : '#991b1b'};">
            ${message}
        </div>
    `;
    setTimeout(() => { container.innerHTML = ''; }, 4000);
}

let allCDRs = [];

async function fetchCDRs() {
    try {
        const response = await fetch('api/cdrs');
        allCDRs = await response.json();
        renderTable(allCDRs);
        updateStats(allCDRs);
    } catch (err) {
        console.error('CDR fetch error:', err);
    }
}

async function clearHistory() {
    if (!confirm(t('confirmClear'))) return;
    try {
        const res = await fetch('api/cdrs', { method: 'DELETE' });
        if (res.ok) {
            allCDRs = [];
            renderTable([]);
            updateStats([]);
            showAlert(t('successClear'), 'success');
        } else {
            showAlert(t('errClear'), 'danger');
        }
    } catch (err) {
        console.error(err);
        showAlert(t('errClear'), 'danger');
    }
}

function renderTable(cdrs) {
    const body = document.getElementById('cdr-body');
    body.innerHTML = '';

    if (cdrs.length === 0) {
        body.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px;">${t('noRecords')}</td></tr>`;
        return;
    }

    cdrs.forEach(cdr => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="direction-tag ${cdr.direction}">${cdr.direction === 'inbound' ? t('inbound') : t('outbound')}</span></td>
            <td>${cdr.caller_number || '-'}</td>
            <td>${cdr.callee_number || '-'}</td>
            <td>${formatDuration(cdr.duration)}</td>
            <td>${formatDate(cdr.started_at)}</td>
            <td><button class="btn-details" onclick="showDetails('${cdr.uuid}')">${t('details')}</button></td>
        `;
        body.appendChild(tr);
    });
}

function updateStats(cdrs) {
    let inbound = 0, outbound = 0, missed = 0, totalDuration = 0;
    cdrs.forEach(cdr => {
        if (cdr.direction === 'inbound') inbound++;
        else outbound++;
        if (cdr.duration === 0) missed++;
        totalDuration += cdr.duration;
    });
    document.getElementById('total-inbound').innerText = inbound;
    document.getElementById('total-outbound').innerText = outbound;
    document.getElementById('total-missed').innerText = missed;
    document.getElementById('avg-duration').innerText = cdrs.length > 0
        ? formatDuration(Math.round(totalDuration / cdrs.length))
        : '0s';
}

async function showDetails(uuid) {
    try {
        const response = await fetch(`api/cdrs/${uuid}`);
        const cdr = await response.json();

        document.getElementById('detail-uuid').innerText = cdr.uuid;
        document.getElementById('detail-caller').innerText = cdr.caller_number || '-';
        document.getElementById('detail-callee').innerText = cdr.callee_number || '-';
        document.getElementById('detail-direction').innerText = cdr.direction === 'inbound' ? t('inbound') : t('outbound');
        document.getElementById('detail-duration').innerText = formatDuration(cdr.duration);
        document.getElementById('detail-start').innerText = formatDate(cdr.started_at);
        document.getElementById('detail-end').innerText = formatDate(cdr.ended_at);
        document.getElementById('detail-hangup').innerText = cdr.hangup_by || '-';

        try {
            document.getElementById('detail-raw').innerText = JSON.stringify(JSON.parse(cdr.raw_payload), null, 2);
        } catch (e) {
            document.getElementById('detail-raw').innerText = cdr.raw_payload;
        }

        const playerContainer = document.getElementById('record-player-container');
        const audio = document.getElementById('detail-audio');
        const msg = document.getElementById('record-player-msg');

        if (cdr.record_url) {
            playerContainer.style.display = 'block';
            const accountId = document.getElementById('account-selector').value;
            if (accountId) {
                msg.style.display = 'none';
                audio.src = `api/records/${cdr.uuid}?account_id=${encodeURIComponent(accountId)}`;
                audio.load();
            } else {
                audio.src = '';
                msg.style.display = 'block';
                msg.innerText = t('selectAccountToPlay');
            }
        } else {
            playerContainer.style.display = 'none';
            audio.src = '';
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
    return new Date(dateStr).toLocaleString('tr-TR');
}

document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('cdr_lang') || 'en';
    document.getElementById('langSwitcher').value = saved;
    changeLanguage();

    window.onclick = function (event) {
        const modal = document.getElementById('details-modal');
        if (event.target == modal) closeModal();
    };

    fetchCDRs();
    setInterval(fetchCDRs, 20000);
});
