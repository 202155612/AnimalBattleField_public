console.log("replay.js loaded");
const script = document.currentScript;

const replay = JSON.parse(script.dataset.replay);

const moveDuration = 300;
const stayDuration = 0;


document.addEventListener('DOMContentLoaded', () => {
    const control_bar = document.getElementById("control-bar")
    const log_p = document.getElementById("log_p");
    
    const cardImages = [];
    const cardDivs = [];

    let is_playing = false;

    for (let row = 1; row <= 2; row++) {
        const rowCards = document.querySelectorAll(`.card[id^='card_${row}_']`);
        const rowCardsImages = document.querySelectorAll(`[id^='card_${row}_'] card-image`);
        cardDivs.push(Array.from(rowCards));
        cardImages.push(Array.from(rowCardsImages));
    }

    const allTimeouts = [];
    const animatingCards = new Set();

    function createLogs(){
        const actions = replay.actions;
        const battleLogs = [];

        const cardNames = [[], []];

        for (const card of replay.player1_cards) {
            cardNames[0].push(card.card_with_last_patch.card.name);
        }
        
        for (const card of replay.player2_cards) {
            cardNames[1].push(card.card_with_last_patch.card.name);
        }

        for (const action of actions) {
            const cardStates = [[], []];
            for (const cardState of action.before_state.player1_cards){
                cardStates[0].push(cardState);
            }

            for (const cardState of action.before_state.player2_cards){
                cardStates[1].push(cardState);
            }

            const attack_side = action.attack_side - 1;
            const attack_slot = action.attack_slot;
            const target_side = 1 - attack_side;
            const target_slot = action.target_slot;

            const battleLog = [];

            const attackerName = cardNames[attack_side][attack_slot];
            const attackState = cardStates[attack_side][attack_slot];
            const targetName = cardNames[target_side][target_slot];
            const targetState = cardStates[target_side][target_slot];

            battleLog.push(
                `${attackerName}(${attackState.health})가 `+
                `${targetName}(${targetState.health})를 ` +
                `공격해 ${action.attacker_damage} 데미지를 입고 ${action.target_damage} 데미지를 주었습니다.`
            );

            if (action.is_attacker_dead == true){
                battleLog.push(
                    `${attackerName}(이)가 사망했습니다.`
                );
            }

            if (action.is_target_dead == true){
                battleLog.push(
                    `${targetName}(이)가 사망했습니다.`
                );
            }

            battleLogs.push(battleLog.join("<br>"));
        }

        

        if (replay.winner_player_side == 1){
            battleLogs[battleLogs.length - 1] += `<br>플레이어 ${replay.player1_nickname}(이)가 승리했습니다!`
        }
        else if (replay.winner_player_side == 2){
            battleLogs[battleLogs.length - 1] += `<br>플레이어 ${replay.player2_nickname}(이)가 승리했습니다!`
        }
        else {
            battleLogs[battleLogs.length - 1] += `<br>결과는 무승부입니다!`
        }

        return battleLogs;
    }

    const battleLogs = createLogs();

    function printLogs(action_num) {
        const end_index = Number(action_num) + 1;
        return battleLogs.slice(0, end_index).join("<br>");
    }

    function resetCards(action_num) {
        const state = replay.actions[action_num].before_state;
        if (!state) {
            console.error("before_state is null for action", action.action_num);
            return;
        }

        const p1 = state.player1_cards;
        const p2 = state.player2_cards;

        for (let col = 0; col < 4; col++) {
            if (p1[col]) {
                cardImages[0][col].setHealth(p1[col].health, p1[col].is_dead);
            }
            if (p2[col]) {
                cardImages[1][col].setHealth(p2[col].health, p2[col].is_dead);
            }
        }

        log_p.innerHTML = printLogs(action_num);
    }

    function resetAnimations(){

        allTimeouts.forEach(id => clearTimeout(id));
        allTimeouts.length = 0;

        cardImages.forEach (row => { 
            row.forEach(el => {
                el.style.transition = 'none';
                el.style.transform = 'translate(0, 0)';
                el.style.zIndex = 0;
                void el.offsetWidth;
            });
        });
        animatingCards.clear();
    }

    function playAction(action_num) {
        const action = replay.actions[action_num]
        const attack_side = action.attack_side - 1;
        const target_side = 2 - action.attack_side;
        const attack_slot = action.attack_slot;
        const target_slot = action.target_slot;
        const from = cardDivs[attack_side][attack_slot];
        const fromImage = cardImages[attack_side][attack_slot];
        const to = cardDivs[target_side][target_slot];
        const toImage = cardImages[target_side][target_slot];

        resetCards(action_num);

        let attack_card, target_card;
        if (attack_side == 0){
            attack_card = action.after_state.player1_cards[attack_slot]
            target_card = action.after_state.player2_cards[target_slot]
        }
        else {
            attack_card = action.after_state.player2_cards[attack_slot]
            target_card = action.after_state.player1_cards[target_slot]
        }

        if (!from || !to) return;

        from.style.zIndex = 999;
        to.style.zIndex = 0;

        const fromRect = from.getBoundingClientRect();
        const toRect   = to.getBoundingClientRect();

        const dx = toRect.left - fromRect.left;
        const dy = toRect.top  - fromRect.top;

        from.style.transition = `transform ${moveDuration}ms ease`;

        animatingCards.add(from);

        requestAnimationFrame(() => {
            from.style.transform = `translate(${dx}px, ${dy}px)`;
        });

        const backTimeoutId = setTimeout(() => {
            from.style.transform = 'translate(0, 0)';
            fromImage.setHealth(attack_card.health, attack_card.is_dead);
            toImage.setHealth(target_card.health, target_card.is_dead);
        }, moveDuration + stayDuration);

        const endTimeoutId = setTimeout(() => {
            from.style.transition = '';
            from.style.zIndex = 0;
            animatingCards.delete(from);
        }, moveDuration * 2 + stayDuration);

        allTimeouts.push(backTimeoutId, endTimeoutId);
    }

    function startAutoPlay(startIndex = 0) {
        control_play.innerHTML = "■";
        const maxIndex = replay.actions.length - 1;
        if (maxIndex < 0) return;

        is_playing = true;

        let idx = Math.max(0, Math.min(startIndex, maxIndex));

        if (idx == maxIndex){
            idx = 0;
        }

        resetCards(idx);

        const stepDelay = moveDuration * 2 + stayDuration + 50;

        function step() {
            if (idx > maxIndex) {
                is_playing = false;
                return;
            }

            control_bar.value = idx;
            playAction(idx);

            idx++;

            if (idx <= maxIndex) {
                const id = setTimeout(step, stepDelay);
                allTimeouts.push(id);
            }
        }

        step();
    }

    function stopAutoPlay() {
        control_play.innerHTML = "▶";
        is_playing = false;
        allTimeouts.forEach(id => clearTimeout(id));
        allTimeouts.length = 0;
        animatingCards.forEach(el => {
            el.style.transition = 'none';
            el.style.transform = 'translate(0, 0)';
            el.style.zIndex = 0;
            void el.offsetWidth;
        });
        animatingCards.clear();
    }

    const control_left = document.getElementById("control-left");
    const control_right = document.getElementById("control-right");
    const control_play = document.getElementById("control-play");

    control_left.addEventListener("click", (e) => {
        stopAutoPlay();
        let current_idx = control_bar.value;
        if (current_idx > 0){
            current_idx -= 1;
        }
        control_bar.value = current_idx;
        playAction(current_idx);
    })

    control_right.addEventListener("click", (e) => {
        stopAutoPlay();
        let current_idx = Number(control_bar.value);
        if (current_idx < replay.actions.length - 1){
            current_idx += 1;
        }
        control_bar.value = current_idx;
        playAction(current_idx);
    })

    control_play.addEventListener("click", (e) => {
        if (is_playing == true){
            stopAutoPlay()
        }
        else {
            startAutoPlay(control_bar.value);
        }
    })

    control_bar.addEventListener("input", (e) => {
        console.log(e.target.value);
        resetCards(e.target.value);
        resetAnimations();
        playAction(e.target.value);
    });



    startAutoPlay();
})

