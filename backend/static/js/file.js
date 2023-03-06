$(function() {
    const params = new Proxy(new URLSearchParams(window.location.search), {
        get: (searchParams, prop) => searchParams.get(prop),
    });
    const filename = params.filename;

    $("#file").html("<h3>" + filename + "</h3>");

    function AsyncLock()
    {
        const lock = {};
        lock._resolvers = [];
        lock.locked = false;
        lock.acquire = function()
        {
            if (!lock.locked)
            {
                lock.locked = true;
                return Promise.resolve();
            }
            return new Promise((resolve, reject) => {
                lock._resolvers.push(resolve);
            });
        };

        lock.release = async function()
        {
            const resolver = lock._resolvers.pop();
            if (resolver)
            {
                resolver();
                return;
            }
            lock.locked = false;
        };

        return lock;
    }

    const loader = $("#loader");
    const fieldsHolder = $("#fields");
    const lock = AsyncLock();

    function clearTable()
    {
        $("#resultTable").html('');
        $("#tableContainer button").remove();
    }

    async function internalInitialLoad(count, offset)
    {
        let url = "/swapi/csv_file/" + filename + "?count=" + count + "&offset=" + offset;

        let currentFields = [];
        fieldsHolder.children(".btn-success").each(function(el) { currentFields.push($(this).text()); });
        if (currentFields.length > 0)
        {
            url += "&fields=" + currentFields.join(',');
        }
        const response = await fetch(url);
        const result = await response.json();
        const headers = result.headers;
        const data = result.data;
        const tableContainer = $("#tableContainer");
        const resultTableEl = $("#resultTable");
        const headersEl = resultTableEl.children("thead");
        if (!headersEl.length)
        {
            let html = "<thead><tr>";
            for (let i = 0; i < headers.length; i++)
            {
                html += "<th scope='col'>" + headers[i] + "</th>";
            }
            html += "</tr></thead>";
            resultTableEl.append(html);
        }

        if (!fieldsHolder.data("initialized"))
        {
            let queryHtml = "";
            for (let i = 0; i < headers.length; i++)
            {
                queryHtml += "<button type='button' class='btn btn-secondary'>" + headers[i] + "</button>";
            }
            fieldsHolder.html(queryHtml);
            fieldsHolder.data("initialized", true);
        }

        let tableBody = resultTableEl.children("tbody");
        if (!tableBody.length)
        {
            resultTableEl.append("<tbody></tbody>");
            tableBody = resultTableEl.children("tbody");
        }

        html = "";
        for (let i = 0; i < data.length; i++)
        {
            const entry = data[i];

            html += "<tr>";
            for (let j = 0; j < headers.length; j++)
            {
                html += "<td>" + entry[j] + "</td>";
            }
            html += "</tr>";
        }
        tableBody.append(html);

        if (currentFields.length == 0)
        {
            if (!($("#tableContainer #loadMore").length))
            {
                $("#tableContainer").append('<button type="button" class="btn btn-primary" id="loadMore">Load more</button>');
            }
        }

        if (data.length == 0)
        {
            tableContainer.children("button").remove();
        }
    }

    async function initialLoad(count, offset)
    {
        await lock.acquire();
        loader.show();
        try
        {
            clearTable();
            await internalInitialLoad(count, offset);
        }
        finally
        {
            loader.hide();
            lock.release();
        }
    }

    const count = 10;
    let currentOffset = 0;

    initialLoad(count, currentOffset);

    $("#fields").on("click", "button", (ev) => {
        const bt = $(ev.currentTarget);
        if (bt.hasClass("btn-success"))
        {
            bt.removeClass("btn-success");
            bt.addClass("btn-secondary");
        }
        else
        {
            bt.removeClass("btn-secondary");
            bt.addClass("btn-success");
        }
        currentOffset = 0;
        initialLoad(count, currentOffset);
    });

    $("#tableContainer").on("click", "#loadMore", async (ev) => {
        await lock.acquire();
        loader.show();
        try
        {
            currentOffset += count;
            await internalInitialLoad(count, currentOffset);
        }
        finally
        {
            loader.hide();
            lock.release();
        }
    });
});
