// Initialize layui components
;(function(){
    var element = layui.element;
    var table = layui.table;
    var flow = layui.flow;
    var layer = layui.layer;

    var $ = layui.jquery;

    /***
     * Handling tables
     */
    var formatCell = function(cell) {
        if (cell.length > 10 && !isNaN(parseFloat(cell))) {
            var index_e = Math.max(cell.indexOf('e'), cell.indexOf('E'));
            if (index_e == -1) {
                return parseFloat(cell).toFixed(3);
            }
            return parseFloat(cell.substr(0, index_e)).toFixed(3) + cell.substr(index_e)
        }
        cell = cell.replace(/<([^:]+)\s*:\s*([^>]+)>/,
            (m, p1, p2) => '<a href="'+ p2 +'" target="_blank">'+ p1 +'</a>'
        );

        return cell;
    };

    var decodeHTML = function(html) {
        var txt = document.createElement("textarea");
        txt.innerHTML = html;
        return txt.value;
    };

    $('.pyppl-report-table').each(function(index) {
        var $elem = $(this);
        var headers = $elem.attr('data-prtable-header');
        var sort = $elem.attr('data-prtable-sort');
        var pagesize = $elem.attr('data-prtable-pagesize');
        var caption = $elem.attr('data-prtable-caption');
        var download = $elem.attr('data-prtable-download');
        var file = $elem.attr('data-prtable-file');
        pagesize = parseInt(pagesize || 25);

        var data = $.parseJSON(decodeHTML($elem.attr('data-prtable-data')));
        if (headers) {
            headers = $.parseJSON(decodeHTML(headers));
        } else {
            headers = [...Array(len(data[0]))].keys().map(i => "V" + (i+1));
        }
        if (sort) {
            sort = {field: headers[
                $.parseJSON(decodeHTML(sort))[0]
            ]};
        } else {
            sort = null
        }
        var cols = headers.map(header => ({
            sort: true, field: header, title: header, width: 'auto'
        }));

        // add download
        var defaultToolbar = ['filter', 'print', 'exports'];
        if (download == 'true') {
            defaultToolbar.push({
                title: 'Download the whole dataset',
                layEvent: 'DownloadWhole',
                icon: 'layui-icon-download-circle'
            });
        }

        // replace div to table
        var tableid = 'pyppl-table-' + (index + 1);
        var $table = $('<table id="'+ tableid +'" ' +
                       'lay-filter="'+ tableid +'"></table>');
        $elem.replaceWith($table);

        // render tab le
        table.render({
            elem: $table[0],
            page: true,
            cols: [cols],
            limit: pagesize,
            title: caption,
            initSort: sort,
            defaultToolbar: defaultToolbar,
            toolbar: true,
            skin: {size: 'sm', even: true},
            limits: [25, 50, 75, 100],
            data: data.map(function(row) {
                var ret = {};
                for (var i in headers) {
                    ret[headers[i]] = formatCell(row[i]);
                }
                return ret;
            })
        });

        // add caption
        $("div[lay-id="+ tableid +"] .layui-table-tool-temp")
            .html('<strong>Table '+ (index + 1) +'. </strong>' +
                  '<span class="pyppl-table-caption">'+ caption +'</span>');

        // add download event
        table.on('toolbar('+ tableid +')', function(obj) {
            if (obj.event == 'DownloadWhole') {
                var link = document.createElement("a");
                link.href = file;
                link.target = "_blank";
                link.click();
            }
        });
    });

    /***
     * Handling images
     */
    var previewimg = 'data:image/jpeg;base64,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'
    $('img[src="data:null"]').each(function(){
        var $img = $(this);
        $img.attr('lay-src', $img.attr('data-src'));
        $img.removeAttr('data-src');
        $img.attr('src', previewimg);
    }).on('load', function(){
        $(this).css({
            'max-width': '420px',
            'max-height': '500px'
        })
        .attr('title', 'Click to zoom in.')
        .click(function() {
            layer.open({
                type: 1,
                offset: 'auto',
                shadeClose: true,
                area: '960px',
                title: this.alt,
                id: 'pyppl-report-imagepopup-' + $(this).index(),
                content: '<img src="' + this.src + '" '+
                         '     onclick="javascript:var a = document.createElement(\'a\');' +
                         '                         a.href=\''+ this.src +'\';' +
                         '                         a.target=\'_blank\';' +
                         '                         a.click();" />',
                shade: 0.5,
                yes: function(){
                    layer.closeAll();
                }
            });
        });
    });

    // image grids
    $('p:has(img)').each(function(index, elem){
        var $figure = $('<figure />');
        var legend = '';
        $(this).find('img').each(function(idx) {
            var namedidx = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[idx] + ')'
            var $tag = $('<span class="img-tag" />').text(namedidx);
            legend += '<strong>' + namedidx + '</strong> ' +
                $(this).attr('alt') + ' ';
            $figure.append(this).append($tag);
        });
        $figure.append('<figcaption>'+ legend +'</figcaption>')
        $(this).replaceWith($figure);
    });

    // add index for figures
    $('figcaption').each(function(index) {
        $(this).prepend('<strong>Figure '+(index+1)+'. </strong>');
    });

    flow.lazyimg({
        scrollElem: '#pyppl-report-main'
    });

    // scroll according
    element.on('collapse(accordion)', function(data){
        var $container = $('#pyppl-report-main');
        if (data.show) {
            $container.scrollTop(
                $(data.title).offset().top -
                $container.offset().top +
                $container.scrollTop()
            );
        }
    });

})();
