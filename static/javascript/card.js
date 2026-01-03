const cardTemplate = document.createElement("template");

cardTemplate.innerHTML = `
        <style>
            .card {
            position: relative;
            width: 160px;
            height: 240px;
            font-family: system-ui, sans-serif;
            transform: scale(1);
            }

            .card .layer {
            position: absolute;
            top: 0;
            left: 0;
            display: block;
            }

            .card-base {
            z-index: 1;
            }

            .card-image-frame {
            margin-top: 20px;
            margin-left: 14px;
            z-index: 2;
            }

            .card-art {
            margin-top: 24px;
            margin-left: 18px;
            width: 124px;
            height: 124px;
            object-fit: cover;
            z-index: 2;
            }

            .card-name-frame {
            margin-top: 140px;
            margin-left: 14px;
            z-index: 2;
            }

            .card-cost {
            margin-top: 0;
            margin-left: 0;
            z-index: 3;
            }

            .card-attack {
            margin-top: 204px;
            margin-left: 0;
            z-index: 3;
            }

            .card-health {
            margin-top: 204px;
            margin-left: 124px;
            z-index: 3;
            }

            .card-abilities{
                margin-top: 180px;
                margin-left: 14px;
                z-index: 4;
                width: 132px;
                height: 24px;
            }

            .card-ability-icon{
                width: 24px;
                height: 24px;
            }

            .card-text {
            position: absolute;
            text-align: center;
            font-weight: bold;
            z-index: 4;
            }

            .cost-text {
            top: 6px;
            left: 0;
            width: 36px;
            font-size: 18px;
            }

            .attack-text {
            bottom: 6px;
            left: 0;
            width: 36px;
            font-size: 18px;
            }

            .health-text {
            bottom: 6px;
            right: 0;
            width: 36px;
            font-size: 18px;
            }

            .name-text {
            top: 146px;
            left: 14px;
            width: 132px;
            font-size: 14px;
            }

            .desc-text {
            left: 36px;
            right: 36px;
            bottom: 8px;
            font-size: 12px;
            }

            .ability-wrapper {
                position: absolute;
                width: 24px;
                height: 24px;
            }

            .ability-wrapper .card-ability-icon {
                width: 100%;
                height: 100%;
            }

            .tooltip {
                position: absolute;
                bottom: 28px;
                left: 0;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.9);
                color: #fff;
                padding: 4px 6px;
                font-size: 10px;
                border-radius: 3px;
                white-space: nowrap;
                width: auto;
                max-width: none; 
                display: none;
                pointer-events: none;
                z-index: 10;
                text-align: left;
                line-height: 1.3;
            }

            .tooltip .name {
                font-weight: bold;
                margin-bottom: 2px;
            }

            .tooltip .desc {
                opacity: 0.9;
            }
        </style>

        <div class="card">
            <img src="static/images/templates/card_template.png" class="layer card-base">

            <img src="static/images/templates/cost_template.png"   class="layer card-cost">
            <img src="static/images/templates/attack_template.png" class="layer card-attack">
            <img src="static/images/templates/health_template.png" class="layer card-health">

            <img src="static/images/templates/card_image_template.png" class="layer card-image-frame">

            <img src="static/images/cards/placeholder.png" class="layer card-art">

            <img src="static/images/templates/name_template.png" class="layer card-name-frame">

            <div class="card-text cost-text">?</div>
            <div class="card-text attack-text">?</div>
            <div class="card-text health-text">?</div>
            <div class="card-text name-text">?</div>

            <div class="layer card-abilities">
                <div class="ability-wrapper" style="top:0; left:0;">
                    <img class="card-ability-icon" src="static/images/abilities/placeholder.png">
                </div>
                <div class="ability-wrapper" style="top:0; left:28px;">
                    <img class="card-ability-icon" src="static/images/abilities/placeholder.png">
                </div>
                <div class="ability-wrapper" style="top:0; left:56px;">
                    <img class="card-ability-icon" src="static/images/abilities/placeholder.png">
                </div>
                <div class="ability-wrapper" style="top:0; left:84px;">
                    <img class="card-ability-icon" src="static/images/abilities/placeholder.png">
                </div>

                <div class="tooltip">
                    <div class="name"></div>
                    <div class="desc"></div>
                </div>
            </div>
        </div>
    `;

class CardImage extends HTMLElement {
  constructor() {
    super();
    const shadow = this.attachShadow({ mode: "open" });
    shadow.appendChild(cardTemplate.content.cloneNode(true));
    this._tooltipInitialized = false;
  }

  static get observedAttributes() {
    return ["card", "size"];
  }

  connectedCallback() {
    this.update();
    this.initTooltip();
  }

  attributeChangedCallback() {
    this.update();
  }

  setHealth(health, is_dead) {
    this.shadowRoot.querySelector(".health-text").textContent = health ?? "";
    const card = this.shadowRoot.querySelector(".card");
    card.style.opacity = is_dead ? "0.5" : "1";
  }

  initTooltip() {
    if (this._tooltipInitialized) return;
    this._tooltipInitialized = true;

    const shadow = this.shadowRoot;
    const abilitiesFrame = shadow.querySelector(".card-abilities");
    const tooltip = abilitiesFrame.querySelector(".tooltip");
    const nameBox = tooltip.querySelector(".name");
    const descBox = tooltip.querySelector(".desc");
    const wrappers = abilitiesFrame.querySelectorAll(".ability-wrapper");

    wrappers.forEach((wrapper) => {
      wrapper.addEventListener("mouseenter", () => {
        const abilityName = wrapper.dataset.abilityName || "";
        const abilityDesc = wrapper.dataset.abilityDesc || "";
        if (!abilityName && !abilityDesc) {
          tooltip.style.display = "none";
          return;
        }
        nameBox.textContent = abilityName;
        descBox.textContent = abilityDesc;

        const centerX = wrapper.offsetLeft + wrapper.offsetWidth / 2;
        tooltip.style.left = centerX + "px";
        tooltip.style.display = "block";
      });

      wrapper.addEventListener("mouseleave", () => {
        tooltip.style.display = "none";
      });
    });
  }

  update() {
    const shadow = this.shadowRoot;
    if (!shadow) return;

    const sizeAttr = this.getAttribute("size");
    const card = shadow.querySelector(".card");
    if (sizeAttr) {
      const value = parseFloat(sizeAttr);
      if (!isNaN(value)) card.style.transform = `scale(${value})`;
    }

    let cardData;
    try {
      cardData = JSON.parse(this.getAttribute("card") ?? "{}");
    } catch {
      cardData = {};
    }

    card.style.opacity = cardData.is_active === false ? "0.5" : "1";

    shadow.querySelector(".cost-text").textContent = cardData.cost ?? "";
    shadow.querySelector(".name-text").textContent = cardData.name ?? "";
    shadow.querySelector(".attack-text").textContent = cardData.attack ?? "";
    shadow.querySelector(".health-text").textContent = cardData.health ?? "";

    const img = shadow.querySelector(".layer.card-art");
    if (cardData.image_file) img.src = "static/images/cards/" + cardData.image_file;

    const abilities = cardData.abilities || [];
    const abilitiesFrame = shadow.querySelector(".layer.card-abilities");
    const wrappers = abilitiesFrame.querySelectorAll(".ability-wrapper");

    for (let i = 0; i < wrappers.length; i++) {
      const wrapper = wrappers[i];
      const icon = wrapper.querySelector(".card-ability-icon");

      if (i < abilities.length) {
        const ability = abilities[i] || {};
        wrapper.style.display = "block";
        if (ability.image_file) icon.src = "static/images/abilities/" + ability.image_file;
        const name = ability.name ?? "";
        const desc = ability.desc ?? "";
        icon.alt = name;
        wrapper.dataset.abilityName = name;
        wrapper.dataset.abilityDesc = desc;
      } else {
        wrapper.style.display = "none";
        icon.alt = "";
        wrapper.dataset.abilityName = "";
        wrapper.dataset.abilityDesc = "";
      }
    }
  }
}

customElements.define("card-image", CardImage);
