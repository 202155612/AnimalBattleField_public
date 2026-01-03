const script = document.currentScript;
const cardStats = JSON.parse(script.dataset.cardStats);

const style = document.createElement('style');
style.textContent = `
    table {
        width: 100%;
        border-collapse: collapse;
        border: 2px solid #000;
    }

    thead {
        background: #eaeaea;
    }

    th {
        padding: 10px 6px;
        border-bottom: 2px solid #000;
        text-align: center;
        position: relative;
        transition: background 0.2s;
        white-space: nowrap;
    }

    th[data-head] {
        cursor: pointer;
        user-select: none;
    }

    th[data-head]:hover {
        background: #f0f0f0;
    }

    tbody tr {
        transition: background 0.2s;
        cursor: pointer;
    }

    tbody tr:nth-child(even) {
        background: #fafafa;
    }

    tbody tr:hover {
        background: #f1f7ff;
    }

    td {
        padding: 8px 6px;
        border-bottom: 1px solid #e0e0e0;
        text-align: right;
        
    }

    .card_image {
        text-align: center;
        width: 40px;
    }

    .card_image img {
        width: 24px;
        height: 24px;
        object-fit: contain;
    }

    .number_column {
        width: 90px;
        text-align: right;
    }

    td.card_name_cell {
        text-align: left;
    }

    th[data-head].sort-asc::after {
        content: "▲";
        font-size: 10px;
        margin-left: 5px;
        
    }

    th[data-head].sort-desc::after {
        content: "▼";
        font-size: 10px;
        margin-left: 5px;
    }
`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('card_stat_container');

    const headers = [
        { key: 'card_name',         label: '이름' },
        { key: 'matches_played',    label: '픽 횟수' },
        { key: 'win_rate',          label: '승률' },
        { key: 'avg_kills',         label: '킬 비율' },
        { key: 'avg_deaths',        label: '데스 비율' },
        { key: 'avg_given_damage',  label: '준 피해량' },
        { key: 'avg_taken_damage',  label: '받은 피해량' },
    ];

    const numberColumns = [
        "matches_played",
        "win_rate",
        "avg_kills",
        "avg_deaths",
        "avg_given_damage",
        "avg_taken_damage"
    ];

    const intColumns = ["matches_played"];

    const table = document.createElement('table');

    const thead = document.createElement('thead');
    const headTr = document.createElement('tr');
    headTr.classList.add('card_stat_list_head');

    let currentSortKey = null;
    let currentSortAsc = true;

    const thImage = document.createElement('th');
    thImage.textContent = " ";
    headTr.appendChild(thImage);

    headers.forEach(h => {
        const th = document.createElement('th');
        th.dataset.head = h.key;
        th.textContent = h.label;

        if (numberColumns.includes(h.key)) {
            th.classList.add("number_column");
        }

        th.addEventListener('click', () => {
            if (currentSortKey === h.key) {
                currentSortAsc = !currentSortAsc;
            } else {
                currentSortKey = h.key;
                currentSortAsc = true;
            }
            sortAndRender(currentSortKey, currentSortAsc);
        });

        headTr.appendChild(th);
    });

    thead.appendChild(headTr);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    tbody.id = 'card_stat_list_body';

    const currentCardStats = [...cardStats];

    function renderRows(data) {
        tbody.innerHTML = '';

        for (const card_stat of data) {
            const tr = document.createElement('tr');

            const tdImage = document.createElement('td');
            tdImage.className = "card_image";

            const imgValue = card_stat["card_image"];
            if (imgValue) {
                const img = document.createElement('img');
                img.src = `static/images/cards/${imgValue}`;
                img.alt = "";
                tdImage.appendChild(img);
            } else {
                tdImage.textContent = "";
            }
            tr.appendChild(tdImage);

            headers.forEach(h => {
                let value = card_stat[h.key];

                if (value !== null && value !== "" && !isNaN(value)) {
                    if (intColumns.includes(h.key)) {
                        value = parseInt(value);
                    } else {
                        value = parseFloat(value).toFixed(2);
                    }
                }

                const td = document.createElement('td');
                td.textContent = value ?? "";

                if (h.key === 'card_name') {
                    td.classList.add('card_name_cell');
                }

                tr.appendChild(td);
            });

            tr.addEventListener('click', () => {
                window.location.href = `/card_stat?card_id=${card_stat["card_id"]}`;
            });

            tbody.appendChild(tr);
        }
    }

    function updateSortIndicators(key, asc) {
        const headerCells = thead.querySelectorAll('th[data-head]');
        headerCells.forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
            if (th.dataset.head === key) {
                th.classList.add(asc ? 'sort-asc' : 'sort-desc');
            }
        });
    }

    function sortAndRender(key, asc) {
        updateSortIndicators(key, asc);

        currentCardStats.sort((a, b) => {
            let va = a[key];
            let vb = b[key];

            if (va == null && vb == null) return 0;
            if (va == null) return asc ? 1 : -1;
            if (vb == null) return asc ? -1 : 1;

            const na = parseFloat(va);
            const nb = parseFloat(vb);
            const numeric = !isNaN(na) && !isNaN(nb);

            if (numeric) {
                return asc ? (na - nb) : (nb - na);
            } else {
                const sa = String(va);
                const sb = String(vb);
                return asc
                    ? sa.localeCompare(sb, 'ko')
                    : sb.localeCompare(sa, 'ko');
            }
        });

        renderRows(currentCardStats);
    }

    renderRows(currentCardStats);

    table.appendChild(tbody);
    container.appendChild(table);
});
