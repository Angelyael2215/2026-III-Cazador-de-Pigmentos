(function () {
    const form = document.querySelector(".level-builder");
    const kindField = document.getElementById("id_kind");
    const palette = document.querySelector("[data-color-palette]");
    const preview = document.querySelector("[data-level-json-preview]");
    const colorStatus = document.querySelector("[data-color-status]");
    const mixRecipe = document.querySelector("[data-mix-recipe]");
    const mixAnswerEntry = document.querySelector("[data-mix-answer-entry]");
    const mixIngredients = document.querySelector("[data-mix-ingredients]");
    const mixResultSwatch = document.querySelector("[data-mix-result-swatch]");
    const mixResultText = document.querySelector("[data-mix-result-text]");
    const mixAnswerErrors = document.querySelector("[data-mix-answer-errors]");

    if (!form || !kindField || !palette || !preview || !colorStatus) return;

    const quickColors = [
        "#F44336", "#E91E63", "#9C27B0", "#673AB7", "#3F51B5", "#2196F3",
        "#03A9F4", "#00BCD4", "#009688", "#4CAF50", "#8BC34A", "#CDDC39",
        "#FFEB3B", "#FFC107", "#FF9800", "#FF5722", "#795548", "#607D8B",
        "#263238", "#546E7A", "#B0BEC5", "#FFFFFF", "#1E88E5", "#E53935",
    ];
    const colorFieldNames = new Set([
        "colors",
        "answer_colors",
        "warm_colors",
        "cold_colors",
        "reference_color",
        "options_text",
    ]);
    const targetKeys = {
        hex: "target_hex",
        harmony: "target_color",
        contrast: "target_background",
        color_blindness: "target_color",
        albers: "target_color",
    };
    let activeColorField;
    const selectedMixColors = new Set();

    function field(name) {
        return form.elements.namedItem(name);
    }

    function colorsFrom(value) {
        return value
            .split(/[\n,]/)
            .map((color) => color.trim().toUpperCase())
            .filter(Boolean);
    }

    function optionsFromText(value, kind) {
        return value
            .split(/\r?\n/)
            .map((line) => line.trim())
            .filter(Boolean)
            .map((line, index) => {
                const separator = line.indexOf("|");
                const label = separator < 0
                    ? `Opción ${index + 1}`
                    : line.slice(0, separator).trim();
                const colors = colorsFrom(
                    separator < 0 ? "" : line.slice(separator + 1)
                );
                const option = {
                    id: String.fromCharCode(97 + index),
                    label: label || `Opción ${index + 1}`,
                };
                if (kind === "harmony" || kind === "atmosphere") {
                    option.colors = colors;
                } else if (colors.length) {
                    option.color = colors[0];
                    if (colors.length > 1) option.colors = colors.slice(1);
                }
                return option;
            });
    }

    function buildConfiguration() {
        const kind = kindField.value;
        const data = {};
        const solution = {};
        const colors = colorsFrom(field("colors").value);
        const answers = colorsFrom(field("answer_colors").value);
        const referenceColor = field("reference_color").value.trim().toUpperCase();
        const options = optionsFromText(field("options_text").value, kind);

        if (["mix", "temperature", "saturation", "gradient"].includes(kind)) {
            data.colors = colors;
        }

        if (kind === "mix") {
            solution.colors = answers;
        } else if (kind === "rgb") {
            data.reference_color = referenceColor;
            const match = /^#([0-9A-F]{6})$/.exec(referenceColor);
            solution.rgb = match
                ? [0, 2, 4].map((index) => parseInt(match[1].slice(index, index + 2), 16))
                : [0, 0, 0];
        } else if (kind === "temperature") {
            solution.warm = colorsFrom(field("warm_colors").value);
            solution.cold = colorsFrom(field("cold_colors").value);
        } else if (kind === "saturation") {
            solution.order = answers;
        } else {
            if (targetKeys[kind]) data[targetKeys[kind]] = referenceColor;
            if (kind === "branding") {
                data.brand_name = field("brand_name").value.trim();
            }
            if (kind === "harmony" || kind === "atmosphere") {
                data.palette_options = options;
            } else {
                data.options = options;
            }
            solution.option_id = field("correct_option").value;
        }

        return {data, solution};
    }

    function updatePreview() {
        preview.textContent = JSON.stringify(buildConfiguration(), null, 2);
    }

    function rgbFromHex(color) {
        return [1, 3, 5].map((index) => parseInt(color.slice(index, index + 2), 16));
    }

    function hexFromRgb(rgb) {
        return `#${rgb.map((channel) => Math.round(channel).toString(16).padStart(2, "0")).join("")}`
            .toUpperCase();
    }

    function colorName(color) {
        const [red, green, blue] = rgbFromHex(color);
        const max = Math.max(red, green, blue);
        const min = Math.min(red, green, blue);
        if (max - min < 28) {
            if (max < 45) return "Negro";
            if (min > 220) return "Blanco";
            return "Gris";
        }

        const delta = max - min;
        let hue;
        if (max === red) {
            hue = ((green - blue) / delta) % 6;
        } else if (max === green) {
            hue = (blue - red) / delta + 2;
        } else {
            hue = (red - green) / delta + 4;
        }
        hue = (hue * 60 + 360) % 360;
        if (hue < 15 || hue >= 345) return "Rojo";
        if (hue < 45) return "Naranja";
        if (hue < 70) return "Amarillo";
        if (hue < 165) return "Verde";
        if (hue < 195) return "Turquesa";
        if (hue < 255) return "Azul";
        if (hue < 290) return "Violeta";
        return "Rosa";
    }

    function mixColors(colors) {
        const channels = colors.map(rgbFromHex);
        return hexFromRgb([0, 1, 2].map((channel) => (
            channels.reduce((total, rgb) => total + rgb[channel], 0) / channels.length
        )));
    }

    function updateMixRecipe({initialize = false} = {}) {
        if (!mixRecipe || !mixIngredients || !mixResultSwatch || !mixResultText) return;

        const availableColors = [...new Set(colorsFrom(field("colors").value))];
        if (initialize) {
            selectedMixColors.clear();
            const answerColors = colorsFrom(field("answer_colors").value);
            availableColors
                .filter((color) => answerColors.includes(color))
                .forEach((color) => selectedMixColors.add(color));
        } else {
            [...selectedMixColors]
                .filter((color) => !availableColors.includes(color))
                .forEach((color) => selectedMixColors.delete(color));
            field("answer_colors").value = availableColors
                .filter((color) => selectedMixColors.has(color))
                .join("\n");
        }
        const answerColors = colorsFrom(field("answer_colors").value);

        mixIngredients.replaceChildren();
        if (!availableColors.length) {
            const emptyMessage = document.createElement("p");
            emptyMessage.textContent = "Agrega primero colores disponibles para elegir pigmentos.";
            mixIngredients.append(emptyMessage);
        }

        availableColors.forEach((color) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "level-builder__mix-ingredient";
            button.setAttribute("aria-pressed", String(selectedMixColors.has(color)));
            button.setAttribute("aria-label", `${colorName(color)} ${color}`);

            const swatch = document.createElement("span");
            swatch.className = "level-builder__mix-ingredient-swatch";
            swatch.style.setProperty("--mix-color", color);
            swatch.setAttribute("aria-hidden", "true");

            const label = document.createElement("span");
            label.className = "level-builder__mix-ingredient-label";
            label.textContent = colorName(color);

            const code = document.createElement("small");
            code.textContent = color;

            button.append(swatch, label, code);
            button.addEventListener("click", () => {
                if (selectedMixColors.has(color)) {
                    selectedMixColors.delete(color);
                } else {
                    selectedMixColors.add(color);
                }
                field("answer_colors").value = availableColors
                    .filter((item) => selectedMixColors.has(item))
                    .join("\n");
                if (mixAnswerErrors) mixAnswerErrors.hidden = true;
                updateMixRecipe();
                updatePreview();
            });
            mixIngredients.append(button);
        });

        const selectedColors = availableColors.filter((color) => selectedMixColors.has(color));
        if (!selectedColors.length) {
            mixResultSwatch.hidden = true;
            const invalidAnswer = answerColors.some((color) => !availableColors.includes(color));
            mixResultText.textContent = invalidAnswer
                ? "El color escrito no está entre los pigmentos. Selecciona aquí los colores que lo producen."
                : availableColors.length
                    ? "Elige los pigmentos que el jugador debe combinar."
                    : "Agrega colores disponibles para armar la combinación.";
            return;
        }

        const resultColor = mixColors(selectedColors);
        const resultName = colorName(resultColor);
        mixResultSwatch.hidden = false;
        mixResultSwatch.style.setProperty("--mix-result-color", resultColor);
        mixResultText.textContent = selectedColors.length === 1
            ? `Seleccionaste ${colorName(selectedColors[0])}. Elige otro pigmento para previsualizar la mezcla.`
            : `Vista previa aproximada: ${resultName}. La respuesta se guarda como ${selectedColors.map(colorName).join(" + ")}.`;
    }

    function updateGroups() {
        document.querySelectorAll("[data-level-kinds]").forEach((group) => {
            const kinds = group.dataset.levelKinds.split(/\s+/);
            group.hidden = !kinds.includes(kindField.value);
        });
        if (mixRecipe && mixAnswerEntry) {
            const isMix = kindField.value === "mix";
            mixRecipe.hidden = !isMix;
            mixAnswerEntry.hidden = isMix;
        }
    }

    function defaultColorField() {
        const kind = kindField.value;
        if (["mix", "temperature", "saturation", "gradient"].includes(kind)) {
            return field("colors");
        }
        if (kind === "branding" || kind === "atmosphere") {
            return field("options_text");
        }
        return field("reference_color");
    }

    function describeField(target) {
        const label = target.closest(".level-builder__field")?.querySelector("label");
        return label?.textContent.trim() || "el campo de color";
    }

    function updateColorStatus(message) {
        const target = activeColorField || defaultColorField();
        colorStatus.textContent = message || `Se agregará a ${describeField(target)}.`;
    }

    function updateCorrectOptionChoices() {
        const optionsField = field("options_text");
        const correctField = field("correct_option");
        const selected = correctField.value;
        const labels = optionsField.value
            .split(/\r?\n/)
            .map((line) => line.trim())
            .filter(Boolean)
            .map((line, index) => {
                const separator = line.indexOf("|");
                return separator < 0
                    ? `Opción ${index + 1}`
                    : line.slice(0, separator).trim() || `Opción ${index + 1}`;
            });

        correctField.replaceChildren(new Option("Selecciona la respuesta correcta", ""));
        labels.forEach((label, index) => {
            correctField.add(new Option(label, String.fromCharCode(97 + index)));
        });
        if (labels.some((_, index) => String.fromCharCode(97 + index) === selected)) {
            correctField.value = selected;
        }
    }

    function appendColor(color) {
        const target = activeColorField || defaultColorField();
        if (!target || target.closest("[hidden]")) {
            activeColorField = defaultColorField();
        }
        const destination = activeColorField || defaultColorField();
        if (!destination) return;

        if (destination.name === "reference_color") {
            destination.value = color;
        } else if (destination.name === "options_text") {
            const existing = destination.value.trimEnd();
            const optionNumber = destination.value
                .split(/\r?\n/)
                .filter((line) => line.trim()).length + 1;
            destination.value = `${existing}${existing ? "\n" : ""}Opción ${optionNumber} | ${color}`;
            updateCorrectOptionChoices();
        } else {
            const existing = destination.value.trimEnd();
            destination.value = `${existing}${existing ? "\n" : ""}${color}`;
        }

        destination.dispatchEvent(new Event("input", {bubbles: true}));
        destination.focus();
        updateColorStatus(`${color} agregado a ${describeField(destination)}.`);
        updatePreview();
    }

    quickColors.forEach((color) => {
        const swatch = document.createElement("button");
        swatch.type = "button";
        swatch.className = "level-builder__swatch";
        swatch.style.setProperty("--swatch-color", color);
        swatch.title = color;
        swatch.setAttribute("aria-label", `Agregar color ${color}`);
        swatch.addEventListener("click", () => appendColor(color));
        palette.append(swatch);
    });

    form.addEventListener("focusin", (event) => {
        if (colorFieldNames.has(event.target.name)) {
            activeColorField = event.target;
            updateColorStatus();
        }
    });
    form.addEventListener("input", (event) => {
        if (event.target.name === "options_text") updateCorrectOptionChoices();
        if (event.target.name === "colors" && kindField.value === "mix") {
            updateMixRecipe();
            field("answer_colors").value = [...selectedMixColors].join("\n");
        }
        updatePreview();
    });
    form.addEventListener("change", updatePreview);
    kindField.addEventListener("change", () => {
        updateGroups();
        activeColorField = defaultColorField();
        updateColorStatus();
        updateMixRecipe({initialize: true});
        updatePreview();
    });

    document.querySelector("[data-add-custom-color]")?.addEventListener("click", () => {
        appendColor(document.querySelector("[data-custom-level-color]").value.toUpperCase());
    });

    activeColorField = defaultColorField();
    updateGroups();
    updateMixRecipe({initialize: true});
    updateColorStatus();
    updatePreview();
}());
