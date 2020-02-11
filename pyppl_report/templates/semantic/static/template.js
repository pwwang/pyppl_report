$(function() {


    // datatables
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

    $.extend(true, $.fn.dataTable.defaults, {
		"searching": true,
		"ordering" : true,
		"pageLength": 25,
		"dom": " <'row'<'col-4 text-left'B><'col-4'f><'col-4 text-right'l>>" +
				"<'row'<'col-12'tr>>" +
				"<'row'<'col-6'i><'col-6'p>>",
		"buttons": [ 'copy', 'csv', 'excel', 'print'],
		"colReorder": true
    });

    $('div.pyppl-report-table').each(function(index) {
        var $table = $('<table class="ui very compact table celled" style="width:100%" />');
        var $elem = $(this);
        var headers = $elem.attr('data-prtable-header');
        var sort = $elem.attr('data-prtable-sort');
        var pagesize = $elem.attr('data-prtable-pagesize');
        var caption = $elem.attr('data-prtable-caption');
        var download = $elem.attr('data-prtable-download');
        var file = $elem.attr('data-prtable-file');
        pagesize = parseInt(pagesize || 25);
        if (headers) {
            headers = $.parseJSON(decodeHTML(headers));
        } else {
            headers = [...Array(len(data[0]))].keys().map(i => "V" + (i+1));
        }
        $table.prepend('<caption><b>Table ' + (index+1) + '. </b>' + caption +'</caption>');

        $(this).replaceWith($table);
        var data = $.parseJSON(decodeHTML($elem.attr('data-prtable-data')));
        try {
            $table.dataTable({
                data: data.map(row => row.map(formatCell)),
                columns: headers.map(header => ({title: header}))
            });
        } catch(e){
            console.log(e);
        }
    });
    $('div.dt-buttons').addClass('ui small basic buttons')
        .children('button')
        .addClass('ui button');
    $('.dataTables_filter').addClass('ui form');

	// image lazy loading
	echo.init();

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

    $('.top.menu .item').tab();
    $('.ui.accordion').accordion().not('.menu').click(function(e){
        // I don't find any callbacks for animation done
        // visibility does not work well
        // I only want it to be triggered when clicking
        setTimeout(function(){
            $(document).scrollTop(
                $(e.target).offset().top
            );
        }, 500);
    });

    (function() {
        // scrollspy
        // selector cache
        var $container = $('.main.container'),
            $sectionHeaders = $container.find('h1').not('[data-toc=false]'),
            $followMenu = $container.find('.following.menu'),
            $footer = $('.page > .footer'),

            // alias
            handler;

        // event handlers
        handler = {
            createWaypoints: function() {
                $sectionHeaders
                    .visibility({
                        observeChanges: false,
                        once: false,
                        onTopPassed: handler.activate.section,
                        onTopPassedReverse: handler.activate.previous
                    });

                $footer
                    .visibility({
                        observeChanges: false,
                        once: false,
                        onBottomVisible: function(calculations) {
                        var
                            $title = $followMenu.find('> .item > .title').last()
                        ;
                        $followMenu
                            .accordion('open', $title)
                        ;
                        }
                    });
            },

            activate: {
                previous: function() {
                    var $menuItems  = $followMenu.children('.item'),
                        $section    = $menuItems.filter('.active'),
                        index       = $menuItems.index($section);
                    if($section.prev().length > 0) {
                        $section
                            .removeClass('active')
                            .prev('.item')
                            .addClass('active');
                        $followMenu
                            .accordion('open', index - 1);
                    }
                },

                section: function() {
                    var $section       = $(this),
                        index          = $sectionHeaders.index($section),
                        $followSection = $followMenu.children('div.item'),
                        $activeSection = $followSection.eq(index),
                        isActive       = $activeSection.hasClass('active');
                    if(!isActive) {
                        $followSection.filter('.active')
                            .removeClass('active');
                        $activeSection
                            .addClass('active');
                        $followMenu.accordion('open', index);
                    }
                }
            }
        };

        handler.createWaypoints();
        $followMenu.accordion('open', 0);
    })();
});
