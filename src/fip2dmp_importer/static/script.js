const importer = new DSWImporter()

let selected = null;
let fips = [];
let timer = null;
let searchValue = '';

function compareItems(a, b) {
    if (a.name < b.name) {
        return -1;
    }
    if (a.name > b.name) {
        return 1;
    }
    return 0;
}

function searchItems() {
    if (searchValue === '') {
        fips = []
        renderItems()
    } else {
        jQuery.ajax({
            url: `/api/fips?q=${searchValue}`,
            success: function (result) {
                fips = result._embedded.questionnaires
                fips.sort(compareItems)
                renderItems()
            },
            error: function (result) {
                console.log(result)
                renderItemsError()
            }
        })
    }
}

function renderItemsError() {
    clearTimeout(timer)
    timer = null
    const items = jQuery('#fip-items')
    items.empty()
    items.append(`<div class="fip-item fip-error-item">Unable to retrieve FIPs</div>`)
    if (searchValue === '') {
        items.addClass('hide')
    } else {
        items.removeClass('hide')
    }
}

function renderItems() {
    clearTimeout(timer)
    timer = null
    const items = jQuery('#fip-items')
    items.empty()
    fips.forEach((fip, index) => {
        let description = ""
        if (fip.description !== null && fip.description.trim() !== "") {
            description = `<div class="fip-item-description">${fip.description}</div>`
        }
        items.append(`
            <div class="fip-item fip-selectable-item" data-uuid="${fip.uuid}" data-index="${index}">
                <span class="fip-item-title">${fip.name}</span>
                <span class="fip-item-package">${fip.package.id}</span>
                ${description}
            </div>
        `)
    })
    if (fips.length === 0 && searchValue !== '') {
        items.append(`
            <div class="fip-item fip-no-item">No FIPs available for this search query</div>
        `)
    }
    if (searchValue === '') {
        items.addClass('hide')
    } else {
        items.removeClass('hide')
    }
}

function initImport() {
    jQuery('#fip2dmp-select').addClass('hide')
    jQuery('#fip2dmp-importing').removeClass('hide')

    jQuery.ajax({
        url: `/api/fips/${selected}`,
        success: function (result) {
            doImport(result)
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus)
            console.log(errorThrown)
            jQuery('#fip2dmp-importing').addClass('hide')
            jQuery('#fip2dmp-error').removeClass('hide')
        }
    })
}

function doImport(data) {
    const actions = data.actions
    const replacements = new Map()
    const debug = $('#debug-checkbox').is(':checked')

    const replacePath = (path) => {
        let newPath = [];
        path.forEach((pathItem) => {
            if (replacements.has(pathItem)) {
                newPath.push(replacements.get(pathItem))
            } else {
                newPath.push(pathItem)
            }
        })
        return newPath
    }

    actions.forEach((item) => {
        if (item.type === 'debug') {
            console.log('DEBUG:', item.message)
        } else if (item.type === 'setReply') {
            const path = replacePath(item.path)
            console.log(`SET REPLY: ${path} = "${item.value}"`)
            importer.setReply(path, item.value)
        } else if (item.type === 'setIntegrationReply') {
            const path = replacePath(item.path)
            console.log(`SET INTEGRATION REPLY: ${path} = "${item.value}" [${item.itemId}]`)
            importer.setIntegrationReply(path, item.value, item.itemId)
        } else if (item.type === 'addItem') {
            const path = replacePath(item.path)
            const itemUuid = importer.addItem(path)
            console.log(`ADD ITEM: ${path} = ${itemUuid} [${item.var}]`)
            replacements.set(item.var, itemUuid)
        }
    })

    if (debug) {
        alert("Stop (debug enabled)")
    }

    importer.send()
}

importer
    .init({
        useWizardStyles: true,
        windowSize: {
            width: 300,
            height: 500,
        },
    })
    .then(() => {
        jQuery('#fip-input').on('input', function () {
            const field = jQuery(this)
            searchValue = field.val()

            if (timer) {
                clearTimeout(timer)
            } else {
                const items = jQuery('#fip-items')
                items.removeClass('hide')
                items.empty()
                items.append(`
                    <div class="fip-item fip-loading-item">
                        <div class="fip-loader spinner-grow text-primary spinner-grow-sm" role="status">
                          <span class="sr-only">Loading...</span>
                        </div>
                        <span>Loading FIPs for your query...</span>
                    </div>
                `)
            }
            timer = setTimeout(searchItems, 600)
        })

        jQuery('#fip-items').on('click', '.fip-selectable-item', function () {
            const item = jQuery(this)
            selected = item.data('uuid')
            initImport()
        })

        jQuery('#btn-reset').on('click', function () {
            selected = null;
            fips = [];
            timer = null;
            searchValue = '';
            jQuery('#fip2dmp-importing').addClass('hide')
            jQuery('#fip2dmp-error').addClass('hide')
            jQuery('#fip2dmp-select').removeClass('hide')
        })
    })
    .catch(error => {
        console.error(error)
    })
