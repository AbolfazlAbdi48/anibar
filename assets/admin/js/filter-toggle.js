document.addEventListener("DOMContentLoaded", function () {
    const changelist = document.getElementById("changelist");

    if (!changelist) {
        return;
    }

    const filterPanel = document.getElementById("changelist-filter");
    const searchToolbar = document.getElementById("toolbar");
    const searchInput = document.getElementById("searchbar");

    if (!filterPanel && !searchToolbar) {
        return;
    }

    const controls = document.createElement("div");
    controls.className = "admin-list-tools";
    controls.setAttribute("role", "toolbar");
    controls.setAttribute("aria-label", "List tools");

    changelist.parentNode.insertBefore(controls, changelist);

    const urlParams = new URLSearchParams(window.location.search);

    if (filterPanel) {
        const overlay = document.createElement("div");
        overlay.className = "filter-overlay";
        document.body.appendChild(overlay);

        const closeButton = document.createElement("button");
        closeButton.type = "button";
        closeButton.className = "filter-close-btn";
        closeButton.innerHTML = "&times;";
        closeButton.title = "Close filters";
        closeButton.setAttribute("aria-label", "Close filters");
        filterPanel.prepend(closeButton);

        const filterButton = document.createElement("button");
        filterButton.type = "button";
        filterButton.className = "toggle-filter-btn";
        filterButton.innerHTML = "<span aria-hidden=\"true\">☷</span> Filters";
        filterButton.setAttribute("aria-expanded", "false");
        filterButton.setAttribute("aria-controls", "changelist-filter");

        const ignoredParameters = new Set([
            "p",
            "q",
            "o",
            "all",
            "e",
            "_facets",
        ]);

        const activeFilterKeys = new Set();

        for (const [key, value] of urlParams.entries()) {
            if (!ignoredParameters.has(key) && value !== "") {
                activeFilterKeys.add(key);
            }
        }

        if (activeFilterKeys.size > 0) {
            filterButton.innerHTML =
                `<span aria-hidden="true">☷</span> Filters (${activeFilterKeys.size})`;
            filterButton.classList.add("has-filters");
        }

        controls.appendChild(filterButton);

        function openFilters() {
            filterPanel.classList.add("filter-drawer-open");
            overlay.classList.add("active");
            filterButton.classList.add("is-open");
            filterButton.setAttribute("aria-expanded", "true");
            document.body.style.overflow = "hidden";
        }

        function closeFilters() {
            filterPanel.classList.remove("filter-drawer-open");
            overlay.classList.remove("active");
            filterButton.classList.remove("is-open");
            filterButton.setAttribute("aria-expanded", "false");
            document.body.style.overflow = "";
            filterButton.focus();
        }

        filterButton.addEventListener("click", function () {
            if (filterPanel.classList.contains("filter-drawer-open")) {
                closeFilters();
            } else {
                openFilters();
            }
        });

        closeButton.addEventListener("click", closeFilters);
        overlay.addEventListener("click", closeFilters);

        document.addEventListener("keydown", function (event) {
            if (
                event.key === "Escape" &&
                filterPanel.classList.contains("filter-drawer-open")
            ) {
                closeFilters();
            }
        });
    }

    if (searchToolbar) {
        changelist.classList.add("search-toggle-enabled");

        const searchButton = document.createElement("button");
        searchButton.type = "button";
        searchButton.className = "toggle-search-btn";
        searchButton.innerHTML = "<span aria-hidden=\"true\">⌕</span> Search";
        searchButton.setAttribute("aria-expanded", "false");
        searchButton.setAttribute("aria-controls", "toolbar");

        const searchQuery = urlParams.get("q");

        if (searchQuery) {
            searchButton.classList.add("has-search");
            searchButton.innerHTML = "<span aria-hidden=\"true\">⌕</span> Search active";
        }

        controls.appendChild(searchButton);

        function openSearch() {
            searchToolbar.classList.add("search-panel-open");
            searchButton.classList.add("is-open");
            searchButton.setAttribute("aria-expanded", "true");

            if (searchInput) {
                window.requestAnimationFrame(function () {
                    searchInput.focus();
                    searchInput.select();
                });
            }
        }

        function closeSearch() {
            searchToolbar.classList.remove("search-panel-open");
            searchButton.classList.remove("is-open");
            searchButton.setAttribute("aria-expanded", "false");
            searchButton.focus();
        }

        searchButton.addEventListener("click", function () {
            if (searchToolbar.classList.contains("search-panel-open")) {
                closeSearch();
            } else {
                openSearch();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (
                event.key === "Escape" &&
                searchToolbar.classList.contains("search-panel-open")
            ) {
                closeSearch();
            }
        });
    }
});
