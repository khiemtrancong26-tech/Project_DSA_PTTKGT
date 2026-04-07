const state = {
    datasetSize: '1',
    scenarioType: '2A',
    isLoaded: false
};

const dom = {
    term: document.getElementById('terminal-output'),
    btnLoadDb: document.getElementById('btn-load-dataset'),
    dsRadios: document.querySelectorAll('input[name="dataset"]'),
    dbStatus: document.getElementById('dataset-status'),
    secScenario: document.getElementById('scenario-section'),
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    algoBtns: document.querySelectorAll('.btn-algo'),
    s2RadioLabels: document.querySelectorAll('input[name="s2_type"]'),
    s2DeptGroup: document.getElementById('dept-group'),
    clearBtn: document.getElementById('clear-output')
};

// --- Terminal Logger ---
function log(msg, type = '') {
    const line = document.createElement('div');
    line.className = 'term-line';

    let time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3 });

    let content = `<span class="time">[${time}]</span> `;
    if (type) content += `<span class="${type}">${msg}</span>`;
    else content += msg;

    line.innerHTML = content;
    dom.term.appendChild(line);
    dom.term.scrollTop = dom.term.scrollHeight;
}

dom.clearBtn.addEventListener('click', () => {
    dom.term.innerHTML = '';
});

// --- Dataset Selection ---
dom.dsRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        state.datasetSize = e.target.value;
    });
});

dom.btnLoadDb.addEventListener('click', async () => {
    const icon = dom.btnLoadDb.querySelector('i');
    icon.className = 'fa-solid fa-spinner fa-spin';
    dom.btnLoadDb.disabled = true;

    log(`[Hệ thống] Đang khởi tạo bộ nhớ, tải tập dữ liệu mẫu (Kích thước: ${state.datasetSize})...`, 'info');

    try {
        const res = await fetch('/api/dataset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ size: state.datasetSize })
        });

        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();

        log(`[Thành công] Đã đưa <span class="match">${data.count.toLocaleString()}</span> bản ghi vào bộ nhớ.`, 'success');

        document.getElementById('s1-target-id').value = data.suggested_id;

        state.isLoaded = true;
        dom.secScenario.classList.remove('disabled');
        dom.dbStatus.innerHTML = `<span class="text-success"><i class="fa-solid fa-check"></i> Tải thành công ${data.count.toLocaleString()} dòng</span>`;

        // Ẩn kết quả cũ khi load dataset mới
        document.getElementById('ui-result-area').style.display = 'none';

    } catch (err) {
        log(`[Lỗi] Không thể tải dữ liệu: ${err.message}`, 'err');
        dom.dbStatus.innerHTML = `<span class="text-danger"><i class="fa-solid fa-xmark"></i> Lỗi: ${err.message}</span>`;
    } finally {
        icon.className = 'fa-solid fa-database';
        dom.btnLoadDb.disabled = false;
    }
});

// --- Scenario Tabs ---
dom.tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const target = btn.dataset.target;

        dom.tabBtns.forEach(b => b.classList.remove('active'));
        dom.tabPanes.forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(target).classList.add('active');
    });
});

// --- S2 Type Selector ---
dom.s2RadioLabels.forEach(radio => {
    radio.addEventListener('change', (e) => {
        state.scenarioType = e.target.value;
        if (state.scenarioType === '2A') {
            dom.s2DeptGroup.style.display = 'flex';
            document.querySelector('#s2 .btn-algo[data-algo="hash"] .algo-name').textContent = 'Composite Hash';
        } else {
            dom.s2DeptGroup.style.display = 'none';
            document.querySelector('#s2 .btn-algo[data-algo="hash"] .algo-name').textContent = 'Hash (Không hỗ trợ)';
        }
    });
});

// --- Run Algorithms ---
async function formatMs(ms) {
    if (ms === null || ms === undefined) return '--';
    if (ms < 0.001) return '<0.001 ms';
    return ms.toFixed(4) + ' ms';
}

// --- Render full results table ---
function buildMatchesTable(matches) {
    let html = `<div class="results-scroll-wrapper">`;
    html += `<table class="results-full-table">`;
    html += `<thead><tr>
        <th>MSSV</th>
        <th>Họ và Tên</th>
        <th>Khoa</th>
        <th>GPA</th>
        <th>Tỉnh thành</th>
    </tr></thead><tbody>`;

    for (const r of matches) {
        html += `<tr>
            <td class="cell-id">${r.student_id ?? ''}</td>
            <td class="cell-name">${r.name ?? r.full_name ?? ''}</td>
            <td>${r.department_code ?? ''}</td>
            <td class="cell-gpa">${r.gpa ?? ''}</td>
            <td>${r.province_name ?? ''}</td>
        </tr>`;
    }

    html += `</tbody></table></div>`;
    return html;
}

dom.algoBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
        if (!state.isLoaded) return log('[Hệ thống] Vui lòng tải dữ liệu trước khi chạy phân tích.', 'err');
        if (btn.classList.contains('disabled-algo')) return log('[Hệ thống] Thuật toán hiện tại không hỗ trợ kịch bản này.', 'err');

        const algo = btn.dataset.algo;
        const sPane = btn.closest('.tab-pane').id;

        const resultSpan = btn.querySelector('.algo-result');
        resultSpan.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xử lý...';
        resultSpan.className = 'algo-result';

        let endpoint = '';
        let payload = {};
        let algoName = btn.querySelector('.algo-name').textContent;

        try {
            if (sPane === 's1') {
                endpoint = '/api/scenario1';
                const targetId = document.getElementById('s1-target-id').value;
                if (!targetId) return log('[Lỗi] Không được để trống MSSV.', 'err');
                payload = { algo, target_id: targetId };
                log(`[Kịch Bản 1] Đang thực thi ${algoName} với MSSV: "${targetId}"...`, 'info');
            }
            else if (sPane === 's2') {
                endpoint = '/api/scenario2';
                const dept = document.getElementById('s2-dept').value;
                const minGpa = parseFloat(document.getElementById('s2-min-gpa').value);
                const maxGpa = parseFloat(document.getElementById('s2-max-gpa').value);
                payload = { algo, scenario: state.scenarioType, department: dept, min_gpa: minGpa, max_gpa: maxGpa };
                log(`[Kịch Bản 2] Phân loại ${state.scenarioType} chạy ${algoName} (Khoảng GPA: [${minGpa} - ${maxGpa}]${state.scenarioType === '2A' ? ', Khoa ' + dept : ''})...`, 'info');
            }
            else if (sPane === 's3') {
                endpoint = '/api/scenario3';
                const query = document.getElementById('s3-query').value;
                if (!query) return log('[Lỗi] Không được để trống tên truy vấn.', 'err');
                payload = { algo, query };
                log(`[Kịch Bản 3] Chạy ${algoName} để tìm mờ chuỗi: "${query}"...`, 'info');
            }

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error(await res.text());
            const data = await res.json();

            if (data.failed) {
                resultSpan.textContent = 'THẤT BẠI';
                resultSpan.classList.add('failed');
                log(`${algoName} <span class="err">THẤT BẠI</span>. Thuật toán không có cấu trúc hỗ trợ kịch bản này.`, 'err');
            } else {
                resultSpan.textContent = await formatMs(data.ms);
                resultSpan.classList.add('success');

                let sortInfo = data.sort_ms ? ` (Thời gian Sort: ${await formatMs(data.sort_ms)})` : '';
                let msg = `[Kết quả] ${algoName} hoàn tất trong <span class="match">${await formatMs(data.ms)}</span>${sortInfo}. `;

                let uiHtml = `<div class="result-algo-header">
                    <strong>${algoName}</strong>
                    <span class="result-badge-time">${await formatMs(data.ms)}</span>
                    <span class="result-sort-note">${sortInfo.replace('Thời gian Sort', 'Sort')}</span>
                </div>`;

                if (sPane === 's1') {
                    if (data.found) {
                        msg += `Tên: <span class="match">${data.found.name}</span> | Khoa: <span class="info">${data.found.department_code}</span> | GPA: <span class="sys">${data.found.gpa}</span>`;
                        uiHtml += `<table class="results-full-table">
                            <thead><tr><th>Họ và Tên</th><th>Khoa</th><th>GPA</th><th>Tỉnh thành</th></tr></thead>
                            <tbody><tr>
                                <td class="cell-name">${data.found.name ?? data.found.full_name ?? ''}</td>
                                <td>${data.found.department_code ?? ''}</td>
                                <td class="cell-gpa">${data.found.gpa ?? ''}</td>
                                <td>${data.found.province_name ?? ''}</td>
                            </tr></tbody>
                        </table>`;
                    } else {
                        msg += `Không tìm thấy sinh viên nào tương ứng.`;
                        uiHtml += `<div class="result-not-found"><i class="fa-solid fa-circle-exclamation"></i> Không tìm thấy sinh viên với MSSV yêu cầu.</div>`;
                    }
                } else {
                    msg += `Lọc được <span class="match">${data.match_count}</span> sinh viên.`;
                    uiHtml += `<div class="result-count-note">📝 Tìm thấy <strong>${data.match_count.toLocaleString()}</strong> kết quả phù hợp.</div>`;

                    if (data.matches && data.matches.length > 0) {
                        uiHtml += buildMatchesTable(data.matches);
                    }
                }

                log(msg);

                const resultArea = document.getElementById('ui-result-area');
                const resultContent = document.getElementById('ui-result-content');
                resultContent.innerHTML = uiHtml;
                resultArea.style.display = 'block';
                resultArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }

        } catch (err) {
            resultSpan.textContent = 'LỖI';
            resultSpan.classList.add('failed');
            log(`[Lỗi thực thi]: ${err.message}`, 'err');
        }
    });
});