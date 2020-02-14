// Initialize layui components
;(function(){
    /**
     * Rewrite the sort function to
     * 1. support scientific notation of floats
     * 2. not clone deeply to save memory
     * 3. keep the previous order of ties objects in the array
     *
     *    var data = [{"rowname":"C","PMET":1,"PNoMET":1},
     *                {"rowname":"B","PMET":1,"PNoMET":1},
     *                {"rowname":"A","PMET":1,"PNoMET":0},
     *                {"rowname":"E","PMET":0,"PNoMET":0},
     *                {"rowname":"D","PMET":0,"PNoMET":1}]
     *
     *    Previously, sort(data, 'PNoMET', true) yields
     *    var data = [{"rowname":"D","PMET":0,"PNoMET":1},
     *                {"rowname":"B","PMET":1,"PNoMET":1},
     *                {"rowname":"C","PMET":1,"PNoMET":1},
     *                {"rowname":"E","PMET":0,"PNoMET":0},
     *                {"rowname":"A","PMET":1,"PNoMET":0}]
     *
     *    Now it yields:
     *    var data = [{"rowname":"C","PMET":1,"PNoMET":1},
     *                {"rowname":"B","PMET":1,"PNoMET":1},
     *                {"rowname":"D","PMET":0,"PNoMET":1},
     *                {"rowname":"E","PMET":0,"PNoMET":0},
     *                {"rowname":"A","PMET":1,"PNoMET":0}]
     *
     */
    layui.sort = function(obj, key, desc){
        var clone = (obj || []).slice(0);

        if(!key) return clone;

        // detect numbers
        clone.sort(function(o1, o2){
            var isNum = /^-?[\d.]+(?:[eE]-?\d+)?$/
            ,v1 = o1[key]
            ,v2 = o2[key];

            if(isNum.test(v1)) v1 = parseFloat(v1);
            if(isNum.test(v2)) v2 = parseFloat(v2);

            if(v1 && !v2){
                return 1;
            } else if(!v1 && v2){
                return -1;
            }

            if(v1 > v2){
                return 1;
            } else if (v1 < v2) {
                return -1;
            } else {
                var ret = obj.indexOf(o1) < obj.indexOf(o2) ? -1 : 1;
                return desc ? -ret : ret;
            }
        });

        desc && clone.reverse(); //倒序
        return clone;
    };

    var element = layui.element;
    var table = layui.table;
    var flow = layui.flow;
    var layer = layui.layer;

    var $ = layui.jquery;

    /***
     * Handling tables
     */
    var formatCell = function(cell) {
        if (!cell) {
            return '';
        }
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
            sort: true, field: header, title: header
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

        // render table
        data = data.map(function(row) {
            var ret = {};
            for (var i in headers) {
                ret[headers[i]] = formatCell(row[i]);
            }
            return ret;
        });
        table.render({
            elem: $table[0],
            page: true,
            cols: [cols],
            limit: pagesize,
            title: caption,
            initSort: sort,
            cellMinWidth: 80,
            defaultToolbar: defaultToolbar,
            toolbar: true,
            skin: {size: 'sm', even: true},
            limits: [25, 50, 75, 100],
            data: data
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

        table.on('sort('+ tableid +')', function(obj) {
            var newdata = data;
            if (obj.type === 'desc') {
                newdata = layui.sort(data, obj.field, true);
            } else if (obj.type === 'asc') {
                newdata = layui.sort(data, obj.field);
            }
            table.reload(tableid, {
                initSort: obj,
                data: newdata
            });

            $("div[lay-id="+ tableid +"] .layui-table-tool-temp")
            .html('<strong>Table '+ (index + 1) +'. </strong>' +
                  '<span class="pyppl-table-caption">'+ caption +'</span>');
        });
    });

    /***
     * Handling images
     */
    var previewimg = 'static/image-preview.jpg'
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
                         '     style="max-width: 100%;"' +
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
