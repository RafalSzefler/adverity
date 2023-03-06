$(function() {
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
    const lock = AsyncLock();

    function clearTable()
    {
        $("#resultTable").html('');
    }

    async function internalLoadFiles()
    {
        const response = await fetch("/swapi/csv_files");
        const result = await response.json();
        const data = result.data;
        let html = "<thead><tr><th scope='col'>Index</th><th scope='col'>Filename</th><th scope='col'>Created At</th></tr></thead><tbody>";
        for (let i = 0; i < data.length; i++)
        {
            const entry = data[i];
            const filename = entry.filename;
            const datetime = (new Date(entry.created_at * 1000)).toUTCString();
            html += "<tr data-filename='" + filename + "'><th scope='row'>" + i + '</th><td>' + filename + '</td><td>' + datetime + '</td></tr>';
        }
        html += "</tbody>";
        $("#resultTable").html(html);
    }

    async function loadFiles()
    {
        await lock.acquire();
        loader.show();
        try
        {
            clearTable();
            await internalLoadFiles();
        }
        finally
        {
            loader.hide();
            lock.release();
        }
    }

    $("#fetchButton").on("click", async (ev) => {
        if (lock.locked)
        {
            return;
        }
        await lock.acquire();
        loader.show();
        try
        {
            clearTable();
            await fetch("/swapi/fetch", {method: "POST"});
            await internalLoadFiles();
        }
        finally
        {
            loader.hide();
            lock.release();
        }
    });

    $("#resultTable").on("click", "tbody tr", (ev) => {
        const filename = $(ev.currentTarget).attr("data-filename");
        if (filename)
        {
            window.location.href = "/static/file.html?filename=" + filename;
        }
    });

    loadFiles();
});