const overlay = document.getElementById("meal-overlay");

overlay.addEventListener("click", function(e){
    if(e.target === overlay){
        overlay.classList.add("hidden");
    }
});


function closeMealOverlay() {
    const overlay = document.getElementById("meal-overlay");
    if (overlay) {
        overlay.classList.add("hidden");
        overlay.classList.remove("flex"); 
    }
}




let genderChart;

async function initCharts() {

    try {
        const response = await fetch('/count-male-and-female/');
        const stats = await response.json();

        if (genderChart) genderChart.destroy();

        const isDark = document.documentElement.classList.contains('dark');
        const ctx = document.getElementById('genderChart');
        if (!ctx) return;

        const total = stats.female + stats.male;

        const femalePercent = ((stats.female / total) * 100).toFixed(1);
        const malePercent = ((stats.male / total) * 100).toFixed(1);

        genderChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [
                    `Female (${femalePercent}%)`,
                    `Male (${malePercent}%)`
                ],
                datasets: [{
                    data: [stats.female, stats.male],
                    backgroundColor: [
                        '#f97316',
                        isDark ? '#334155' : '#cbd5e1'
                    ],
                    borderWidth: 0,
                    hoverOffset: 8
                }]
            },
            options: {
                cutout: '70%',
                maintainAspectRatio: false,
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            color: isDark ? '#e2e8f0' : '#334155',
                            font: {
                                size: 13,
                                weight: 'bold'
                            },
                            padding: 20
                        }
                    }
                }
            }
        });

        // compteur total
        document.getElementById('expertCounter').innerText = total;

    } catch (error) {
        console.error("Erreur lors de la récupération des stats:", error);
    }
}

async function initGlobe() {
    const isDark = document.documentElement.classList.contains('dark');

    // --- Tooltip ---
    let tooltip = d3.select("#globe-tip");
    if (tooltip.empty()) {
        tooltip = d3.select("body").append("div")
            .attr("id", "globe-tip")
            .attr("class", "globe-tooltip flex items-center gap-3 p-2 rounded-md shadow-lg text-xs")
            .style("position", "absolute")
            .style("pointer-events", "none")
            .style("opacity", 0)
            .style("background", isDark ? "#1e293b" : "#ffffff")
            .style("color", isDark ? "#f97316" : "#1e293b");
    }

    const globeContainer = document.getElementById('globe');
    let width = globeContainer.getBoundingClientRect().width || 300;
    let height = width;

    const svg = d3.select("#globe")
        .attr("width", width)
        .attr("height", height);
    svg.selectAll("*").remove();

    // --- Projection Orthographique ---
    const projection = d3.geoOrthographic()
        .scale(width / 2.1)
        .translate([width / 2, height / 2])
        .rotate([-40, -20]);

    const path = d3.geoPath().projection(projection);

    try {
        const [worldData, memberStats] = await Promise.all([
            d3.json("https://unpkg.com/world-atlas@2.0.2/countries-110m.json"),
            fetch('/count-members-of-countries/').then(res => res.json())
        ]);

        // Convert topojson en GeoJSON et filtrer les pays sans id
        const countries = topojson.feature(worldData, worldData.objects.countries).features
            .filter(d => d.id !== undefined);

        const g = svg.append("g");

        const worldPaths = g.selectAll("path")
            .data(countries)
            .enter()
            .append("path")
            .attr("d", path)
            .attr("fill", d => {
                const data = memberStats[d.id.toString().padStart(3,'0')];
                return data ? '#f97316' : (isDark ? '#1e293b' : '#e2e8f0');
            })
            .style("stroke", isDark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.1)")
            .on("mouseover", function(event, d) {
                const data = memberStats[d.id.toString().padStart(3,'0')];
                if (!data) return;

                d3.select(this).transition().duration(200).attr("fill", "#fb923c");
                tooltip.html(`
                    <img src="https://flagcdn.com/w20/${data.flag_code}.png" class="rounded-sm mr-1">
                    <div>
                        <div class="font-bold">${data.name}</div>
                        <div class="text-orange-400 text-[10px]">${data.total} membres</div>
                    </div>
                `).style("opacity", 1);
            })
            .on("mousemove", event => {
                tooltip.style("left", (event.pageX + 15) + "px")
                       .style("top", (event.pageY - 15) + "px");
            })
            .on("mouseleave", function(event, d) {
                const data = memberStats[d.id.toString().padStart(3,'0')];
                d3.select(this).transition().duration(200)
                    .attr("fill", data ? '#f97316' : (isDark ? '#1e293b' : '#e2e8f0'));
                tooltip.style("opacity", 0);
            });

        // --- Légende fixe ---
        let legendContainer = d3.select("#globe-legend");
        if (legendContainer.empty()) {
            legendContainer = d3.select("body").append("div")
                .attr("id", "globe-legend")
                .attr("class", "fixed right-6 top-32 bg-white dark:bg-slate-900/90 p-4 rounded-2xl shadow-lg text-sm max-h-[60vh] overflow-auto")
                .style("color", isDark ? "#f97316" : "#1e293b");
        } else {
            legendContainer.html(""); // reset
        }

        Object.keys(memberStats).forEach(id => {
            const data = memberStats[id];
            legendContainer.append("div")
                .html(`

                    <a href="/members-meal-afrique/${data.flag_code}/">
                    <img src="https://flagcdn.com/w20/${data.flag_code}.png" class="inline mr-2 rounded-sm">
                    <span class="font-bold">${data.name}</span>: ${data.total} membres
                    </a>
                `)
                .style("margin-bottom", "4px");
        });

        // --- Rotation continue ---
        const rotationSpeed = 0.5; // degrés par frame
        d3.timer(() => {
            const current = projection.rotate();
            projection.rotate([current[0] + rotationSpeed, current[1]]);
            worldPaths.attr("d", path);
        });

        // --- Resize responsive ---
        window.addEventListener('resize', () => {
            width = globeContainer.getBoundingClientRect().width || 300;
            height = width;
            svg.attr("width", width).attr("height", height);
            projection.scale(width / 2.1).translate([width / 2, height / 2]);
            worldPaths.attr("d", path);
        });

    } catch (error) {
        console.error("Erreur Globe:", error);
    }
}
    function previewImage(e) {
        if(e.target.files[0]) {
            const r = new FileReader();
            r.onload = () => document.getElementById('previewPhoto').src = r.result;
            r.readAsDataURL(e.target.files[0]);
        }
    }

    const themeToggle = document.getElementById('themeToggle');
    themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        initCharts();
        initGlobe();
    });

const signupForm = document.getElementById('signupForm');
const submitButton = signupForm.querySelector('button[type="submit"]');

// Créer un toast flottant
let toast = document.getElementById("meal-toast");
if (!toast) {
    toast = document.createElement("div");
    toast.id = "meal-toast";
    toast.className = "fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-orange-500 text-white px-6 py-3 rounded-2xl shadow-lg opacity-0 pointer-events-none transition-all duration-300";
    document.body.appendChild(toast);
}

signupForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);

    // --- Loader et indicatif ---
    submitButton.disabled = true;
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = `
        <span class="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
        Envoi...
    `;

    toast.innerText = "Envoi en cours...";
    toast.classList.remove("opacity-0");
    toast.classList.add("opacity-100");

    try {
        const response = await fetch('/synchronisation-data/', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.status === 'success') {
            // Overlay + confetti
            const overlay = document.getElementById('meal-overlay');
            if (overlay) overlay.classList.replace('hidden', 'flex');

            confetti({
                particleCount: 150,
                spread: 70,
                origin: { y: 0.6 },
                colors: ['#f97316', '#ffffff']
            });

            this.reset();
            toast.innerText = "Inscription réussie ! 🎉";
        } else {
            toast.innerText = data.message || "Une erreur est survenue";
        }
    } catch (err) {
        console.error(err);
        toast.innerText = "Impossible de contacter le serveur.";
    } finally {
        // --- Restaurer le bouton ---
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;

        // Masquer le toast après 3s
        setTimeout(() => {
            toast.classList.remove("opacity-100");
            toast.classList.add("opacity-0");
        }, 3000);
    }
});


    window.onload = () => {
        initCharts(); 
        initGlobe();
        window.intlTelInput(document.querySelector("#whatsapp"), { 
            initialCountry: "cm", 
            separateDialCode: true,
            utilsScript: "https://cdn.jsdelivr.net/npm/intl-tel-input@19.5.6/build/js/utils.js"
        });
    };

    window.addEventListener('resize', () => {
        clearTimeout(window.resizedFinished);
        window.resizedFinished = setTimeout(initGlobe, 250);
    });