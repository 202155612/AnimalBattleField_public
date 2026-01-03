document.addEventListener('DOMContentLoaded', () => {
    const filters = document.querySelectorAll('#statFilters .filter');

    filters.forEach(filter => {
        const key   = filter.getAttribute('filter-name');
        const label = filter.getAttribute('label');
        const min   = filter.getAttribute('min');
        const max   = filter.getAttribute('max');

        filter.innerHTML = `
            <style>
                .search-bar {
                    padding: 5px;
                    margin: 5px;
                }

                .stat-filter .row {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }

                .singleRange,
                .doubleRange {
                    display: flex;
                    gap: 5px;
                }

                .stat-name {
                    width: 50px;
                }
            </style>
            <div class="stat-filter">
                <div class="row">
                    <input type="checkbox" class="enableFilter" name="${key}Enabled">

                    <div class="stat-name"><strong>${label}</strong></div>

                    <label>
                        <input type="radio" name="${key}Mode" value="single" checked>
                        선택
                    </label>
                    <label>
                        <input type="radio" name="${key}Mode" value="range">
                        범위
                    </label>

                    <div class="singleRange">
                        <input type="range" name="${key}" min="${min}" max="${max}">
                        <input type="number" name="${key}Value" min="${min}" max="${max}" style="width: 50px;">
                    </div>

                    <div class="doubleRange" style="display:none;">
                        <input type="range" name="${key}Min" value="${min}" min="${min}" max="${max}">
                        <input type="number" name="${key}MinValue" min="${min}" max="${max}" style="width: 50px;">
                        <input type="range" name="${key}Max" value="${max}" min="${min}" max="${max}">
                        <input type="number" name="${key}MaxValue" min="${min}" max="${max}" style="width: 50px;">
                    </div>
                </div>
            </div>
        `;
    });

    document.querySelectorAll('.stat-filter').forEach(group => {
        const singleBox = group.querySelector('.singleRange');
        const doubleBox = group.querySelector('.doubleRange');
        const radios = group.querySelectorAll('input[type="radio"]');

        radios.forEach(radio => {
            radio.addEventListener('change', () => {
                if (radio.value === 'single') {
                    singleBox.style.display = 'block';
                    doubleBox.style.display = 'none';
                } else {
                    singleBox.style.display = 'none';
                    doubleBox.style.display = 'block';
                }
            });
        });

        const singleRange = group.querySelector('.singleRange input[type="range"]');
        const singleNumber = group.querySelector('.singleRange input[type="number"]');

        if (singleRange && singleNumber) {
            singleRange.value = singleRange.min;
            singleNumber.value = singleRange.min;

            singleRange.addEventListener('input', () => {
                singleNumber.value = singleRange.value;
            });

            singleNumber.addEventListener('input', () => {
                let v = Number(singleNumber.value);
                if (Number.isNaN(v)) return;
                const min = Number(singleRange.min);
                const max = Number(singleRange.max);
                if (v < min) v = min;
                if (v > max) v = max;
                singleNumber.value = v;
                singleRange.value = v;
            });
        }

        const doubleInputs = group.querySelectorAll('.doubleRange input');
        if (doubleInputs.length === 4) {
            const [minRange, minNumber, maxRange, maxNumber] = doubleInputs;

            minNumber.value = minRange.value;
            maxNumber.value = maxRange.value;

            minRange.addEventListener('input', () => {
                let v = Number(minRange.value);
                const maxV = Number(maxRange.value);
                if (v > maxV) {
                    v = maxV;
                    minRange.value = v;
                }
                minNumber.value = v;
            });

            maxRange.addEventListener('input', () => {
                let v = Number(maxRange.value);
                const minV = Number(minRange.value);
                if (v < minV) {
                    v = minV;
                    maxRange.value = v;
                }
                maxNumber.value = v;
            });

            minNumber.addEventListener('input', () => {
                let v = Number(minNumber.value);
                if (Number.isNaN(v)) return;
                const min = Number(minRange.min);
                const max = Number(maxRange.max);
                if (v < min) v = min;
                if (v > Number(maxRange.value)) v = Number(maxRange.value);
                minNumber.value = v;
                minRange.value = v;
            });

            maxNumber.addEventListener('input', () => {
                let v = Number(maxNumber.value);
                if (Number.isNaN(v)) return;
                const min = Number(minRange.min);
                const max = Number(maxRange.max);
                if (v > max) v = max;
                if (v < Number(minRange.value)) v = Number(minRange.value);
                maxNumber.value = v;
                maxRange.value = v;
            });
        }
    });
});
