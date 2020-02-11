$(function() {

    // toc
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

        var tocroot = $('<div class="ui dividing left rail"> \
                            <div id="pyppl-report-toc" class="ui sticky fixed top"> \
                                <div class="ui vertical following fluid accordion text menu"><div> \
                            </div> \
                        </div>');

        var add_toc = function(node, dom) {
            if (node.level == 1) {
                var menode = $('<div class="item" />')
                    .append('<a href="#'+ node.me.prop('id') +'" class="title"></a>')
                    .appendTo(dom);
                if (node.children.length > 0) {
                    menode.find('a')
                        .append('<i class="dropdown icon"></i><b>'+ node.me.html() +'</b>');
                } else {
                    menode.find('a').html(node.me.html());
                }
            }  else {
                var menode = $('<div class="menu content" />')
                    .append('<a href="#'+ node.me.prop('id') +'" class="item">'
                            + node.me.text() + '</a>')
                    .appendTo(dom);
            }
            if (node.children.length > 0) {
                var dnode = $('<div />').addClass('content menu');
                dnode.appendTo(menode);
                for (var i in node.children) {
                    add_toc(node.children[i], dnode);
                }
            }
        };
        for (var i in tocs.children) {
            add_toc(tocs.children[i], tocroot.find('#pyppl-report-toc > div:first'), i==0);
        }

        $('#pyppl-report-container').prepend(tocroot);
        $('#pyppl-report-main').addClass('with-toc');
    };

    // sidebar / toc
    if (window.metadata.toc > 0) {
        generate_toc(window.metadata.toc)
        $('<div id="toc-controller"><i title="Toggle sidebar" class="arrow alternate circle left outline icon"></i></div>')
            .prependTo('body')
            .click(function(){
                $('#pyppl-report-toc').toggle();
                $('#pyppl-report-main').toggleClass('with-toc without-toc');
                $(this).children('i').toggleClass('left right');
            });

    }

    // admonition
    $('div.admon').each(function(){
        var $title = $('<div class="header" />');
        var title = $(this).attr('data-head');
        var klass = 'positive';
        switch(true) {
            case $(this).hasClass('note'):
                title = title || 'Note';
                break;
            case $(this).hasClass('warn') || $(this).hasClass('warning'):
                title = title || 'Warning';
                klass = 'warning'
                break;
            case $(this).hasClass('info') || $(this).hasClass('tip'):
                title = title || 'Warning';
                klass = 'info';
                break;
            case $(this).hasClass('danger') || $(this).hasClass('error'):
                title = title || 'Error';
                klass = 'negative';
                break;
            case $(this).hasClass('example'):
                title = title || 'Example';
                klass = 'violet';
                break;
        };
        $(this).addClass('ui message ' + klass);
        if (title != "false") {
            $title.text(title);
            $(this).prepend($title);
        }
    });


    // links
    // add target="_blank" to all links unless the links have target specified
    $('a').each(function() {
        var link = $(this);
        if (link.is('.pyppl-report-reference')) {
            link.attr('href',
                      'https://scholar.google.com/scholar?q=' +
                        escape(link.text()));
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

    // images
    var previewimg = 'data:image/jpeg;base64,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'
    $('img[src="data:null"]').each(function(){
        $(this)
            .attr('src', previewimg)
            .attr('data-echo', $(this).attr('data-src'))
            .removeAttr('data-src');
    }).on('load', function(){
        $(this).css({
            'max-width': '420px',
            'max-height': '500px'
        })
        .attr('title', 'Click to zoom in.')
        .click(function() {
            // popups
            $('#figurePreviewer-image').attr('src', $(this).attr('src'));
            $('#figurePreviewer').html($(this).next().text());
            $('#figurePreviewer-modal').modal('show');
        });
    });

    // panels
    var panelTab = function($wrapper) {
        var panelid = $wrapper.prop('id');
        $wrapper
            .children('.panel')
            .addClass('ui tab attached segment')
            .end()
            .prepend('<div class="ui menu top attached tabular">' +
                    $wrapper.children('.panel')
                        .get()
                        .map((panel, index) => '<a class="item '+ (index==0 ? 'active' : '') +'" ' +
                            '                      data-tab="'+ panelid + '-' + index + '">'+
                            $(panel).attr('data-head') +
                            '</a>')
                        .join('\n') +
                    '</div>')
            .children('.panel')
            .each(function(index) {
                $(this).attr('data-tab', panelid + '-' + index);
                if (index==0) {
                    $(this).addClass('active');
                }
            });
    };

    var panelAccordion = function($wrapper) {
        var panelid = $wrapper.prop('id');
        $wrapper
            .addClass('ui styled fluid accordion')
            .children('.panel')
            .addClass('content')
            .each(function(index){
                $(this)
                    .before('<div class="title">'+
                            '   <i class="dropdown icon"></i>' +
                            $(this).attr('data-head') +
                            '</div>');
            });
    };
    // has preceding siblings,      no leading siblings
    $(':not(div.panel) + div.panel, div.panel:first-child').each(function(index){
        var panels = $(this).nextUntil(':not(div.panel)')
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
    $('.accordion').on('shown.bs.collapse', function(event){
        $(document).scrollTop(
            $(this).find('.collapse:visible').prev().offset().top -
            $('#pyppl-report-header').outerHeight()
        );
    });

    // image previewer
    $('body').append('<div class="ui longer modal" id="figurePreviewer-modal"> \
        <div class="header" id="figurePreviewer"></div> \
		<div class="image content"> \
            <div class="ui image"> \
			    <img class="image" src="" style="cursor: pointer;" id="figurePreviewer-image" style="width:100%;"> \
			</div> \
		</div> \
		</div> \
    </div>');

    $('#figurePreviewer-image').click(function(){
        var a = document.createElement('a');
        a.href = this.src;
        a.target = '_blank';
        a.click();
    });
});
