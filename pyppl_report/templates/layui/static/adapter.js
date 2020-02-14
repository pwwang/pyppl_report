// adjust doms, styles for the ui framework if necessary
(function($){
    var generate_toc = function(level) {

        var get_tocs = function() {
            // get tocs
            var heading_selector = 'h1'
            for (var i=2; i<=level; i++) {
                heading_selector += ', h' + i
            }
            /** tocs:
             *  { parents = [], nodes = []}
             **/
            var tocs = {parents: [], me: null, children: [], level: 0};
            var parent = tocs;
            $(heading_selector).each(function(index, heading) {
                heading = $(heading);
                if (heading.attr('data-toc')
                        && heading.attr('data-toc') == 'false') {
                    return;
                }
                var lvl = parseInt(heading.prop('tagName')[1]);
                if (parent.level != lvl - 1) {
                    try {
                        parent = parent.parents[lvl-1];
                    } catch (e) {
                        console.error(e);
                    }
                }
                var me = {parents: [].concat(parent.parents, [parent]),
                          me: heading,
                          level: lvl,
                          children: []};
                parent.children.push(me);
                parent = me;

            });
            return (tocs)
        };

        var tocs = get_tocs();

        var tocroot = $('<ul id="pyppl-report-toc" />').addClass(
            'layui-nav layui-nav-tree layui-nav-side'
        );

        var add_toc = function(node, dom) {
            var nodeid = node.me.prop('id');
            if (!nodeid && node.me.parent('section').length > 0) {
                // try to find section
                nodeid = 'pyppl-panel-' + node.me.parent('section').prop('id');
            }
            if (node.level == 1) {
                var menode = $('<li />')
                    .addClass('layui-nav-item')
                    .append('<a href="#'+ nodeid +'" title="'
                            + node.me.text() +'">'
                            + node.me.text() + '</a>');
                menode.appendTo(dom);
            } else {
                var menode = $('<dd />').append(
                    '<a href="#'+ nodeid
                    +'" title="'+ node.me.text() +'">'
                    + node.me.text() + '</a>'
                );

                menode.appendTo(dom);
            }
            if (node.children.length > 0) {
                var dnode = $('<dl />').addClass('layui-nav-child');
                dnode.appendTo(menode);
                for (var i in node.children) {
                    add_toc(node.children[i], dnode);
                }
            }
        };
        for (var i in tocs.children) {
            add_toc(tocs.children[i], tocroot);
        }

        $('#pyppl-report-main').prepend(tocroot);
        tocroot.find('li:first-child').addClass('layui-nav-itemed layui-this');
        $('#pyppl-report-main').addClass('with-toc');

    };

    // sidebar / toc
    if (window.metadata.toc > 0) {
        generate_toc(window.metadata.toc)

        $('#toc-controller').click(function() {
            $(this).toggleClass('layui-icon-left layui-icon-right');
            $("#pyppl-report-toc").toggle();
            $('#pyppl-report-main').toggleClass('with-toc without-toc');
        });
    }

    // links
    // add target="_blank" to all links unless the links have target specified
    $('a').each(function() {
        var link = $(this);
        if (link.is('.pyppl-report-reference')) {
            link.attr('href',
                      'https://scholar.google.com/scholar?q=' +
                      escape(link.text().split(/:\s*(.+)/)[1]));
        }
        var href = link.attr('href');
        // exclude anchor links as well
        if (!!link.attr('target')
                || !href
                || href[0] == '#'
                || href.indexOf('javascript:') == 0) {
            return;
        }

        link.attr('target', '_blank');
    });

    // admonition
    $('div.admon').each(function(){
        var $title = $('<p class="admon-title" />');
        var title = $(this).attr('data-head');
        var icon = 'layui-icon-speaker';
        switch(true) {
            case $(this).hasClass('note'):
                title = title || 'Note';
                break;
            case $(this).hasClass('warn') || $(this).hasClass('warning'):
                title = title || 'Warning';
                icon = 'layui-icon-notice';
                break;
            case $(this).hasClass('info') || $(this).hasClass('tip'):
                title = title || 'Tips';
                icon = 'layui-icon-tips';
                break;
            case $(this).hasClass('danger') || $(this).hasClass('error'):
                title = title || 'Error';
                icon = 'layui-icon-close';
                break;
            case $(this).hasClass('example'):
                title = title || 'Example';
                icon = 'layui-icon-list';
                break;
        };
        if (title != "false") {
            $title.text(title).prepend('<i class="layui-icon '+ icon +'"></i>');
            $(this).prepend($title);
        }
    });

    // panels
    var panelTab = function($wrapper) {
        $wrapper.children('.panel')
            .addClass('layui-tab-item')
            .first()
            .addClass('layui-show');
        $wrapper.addClass('layui-tab-content')
            .wrap('<div class="layui-tab layui-tab-card" />')
            .before('<ul class="layui-tab-title">' +
                    $wrapper.children('.panel')
                        .get()
                        .map(panel => '<li id="'+
                            ($(panel).prop('id') && 'pyppl-panel-' +
                            $(panel).prop('id')) +'">' +
                            ($(panel).attr('data-head') ||
                            $(panel).children('h1,h2,h3,h4,h5')
                            .first().detach().html()) +
                            '</li>')
                        .join('\n') +
                    '</ul>')
            .prev()
            .children('li:first')
            .addClass('layui-this')
            .end()
            .children('li')
            // force lazy loading images to show
            .click(() => $('#pyppl-report-main').scroll());
    };

    var panelAccordion = function($wrapper) {
        $wrapper.addClass('layui-collapse')
            .attr({'lay-accordion': '', 'lay-filter': 'accordion'})
            .children('.panel')
            .each(function(index) {
                var panelid = $(this).prop('id') &&
                    'pyppl-panel-' + $(this).prop('id');
                $(this).wrap('<div class="layui-colla-item"></div>')
                    .addClass('layui-colla-content')
                    .before('<div class="layui-colla-title" id="'+ panelid +'">' +
                        ($(this).attr('data-head') ||
                         $(this).children('h1,h2,h3,h4,h5')
                            .first().detach().html()) + '</div>');
                if (index === 0) {
                    $(this).addClass('layui-show');
                }
            })
            .click(() => $('#pyppl-report-main').scroll());
    };
    // has preceding siblings,      no leading siblings
    $(':not(.panel) + .panel, .panel:first-child').each(function(index){
        var panels = $(this).nextUntil(':not(.panel)')
               .addBack()
               .wrapAll('<div id="pyppl-report-panel-'+ (index+1) +'" />');

        var $panelWrapper = $('#pyppl-report-panel-' + (index + 1));
        if ($(this).hasClass('tab')) {
            panelTab($panelWrapper);
        } else if ($(this).hasClass('accordion')) {
            panelAccordion($panelWrapper);
        } else if (panels.length <= 4) {
            panelTab($panelWrapper);
        } else {
            panelAccordion($panelWrapper);
        }
    });

    // toggle layui-this for toc items
    $('li.layui-nav-item').click(function(e){
        e.stopImmediatePropagation();
        $(this).siblings()
            .removeClass('layui-this')
            .end()
            .addClass('layui-this');
    }).find('a').click(function(){
        // expand panels
        if ($(this).attr('href').substr(0, 13) == '#pyppl-panel-') {
            var panelid = $(this).attr('href').substr(1);
            var $target = $('[id="'+ panelid +'"]');
            if (!$target.hasClass('layui-this') &&
                !$target.next().hasClass('layui-show')) {

                $target.click();
            }
        }
    });


})(jQuery);
