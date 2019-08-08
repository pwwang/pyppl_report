
var Tab = function(index, wrap) {
	wrapid    = 'report_tab_' + (index + 1)
	tabwrap  = $('<div class="tabwrap tab"><nav><div class="nav nav-tabs" id="'+ wrapid +'" role="tablist"></div></nav><div class="tab-content" id="'+ wrapid +'Content"></div></div>')
	$(wrap).children('div.tab').each(function(i) {
		tabtitle = $(this).children('h3:first')
		tabtitle.replaceWith('')
		if (tabtitle.length == 0) {
			tabtitle = $(this).children('h4:first')
			tabtitle.replaceWith('')
		}
		if (tabtitle.length == 0) {
			tabtitle = $(this).children('h5:first')
			tabtitle.replaceWith('')
		}
		if (tabtitle.length == 0) {
			tabtitle = $('<h5>Tab '+ (i+1) +'</h5>')
		}

		tabid = wrapid + '_' + (i + 1)
		tabid_tab = tabid + '-tab'
		nav = $('<a class="nav-item nav-link" id="'+ tabid_tab + '" data-toggle="tab" href="#'+ tabid +'" role="tab" aria-controls="'+ tabid +'" aria-selected="true"></a>').append(tabtitle).appendTo(tabwrap.find('#' + wrapid))

		content = $('<div class="tab-pane fade show" id="'+ tabid +'" role="tabpanel" aria-labelledby="'+ tabid_tab +'"></div>').append($(this).children()).appendTo(tabwrap.find('#' + wrapid + 'Content'))

		if (i == 0) {
			nav.addClass('active')
			content.addClass('active')
		}
	})
	$(wrap).replaceWith(tabwrap)
};

var Collapse = function(index, wrap) {
	wrapid    = 'report_collapse_' + (index + 1)
	tabwrap  = $('<div id="'+ wrapid +'" class="collapsewrap tab"></div>')
	$(wrap).children('div.tab').each(function(i) {
		tabtitle = $(this).children('h3:first')
		tabtitle.replaceWith('')
		if (tabtitle.length == 0) {
			tabtitle = $(this).children('h4:first')
			tabtitle.replaceWith('')
		}
		if (tabtitle.length == 0) {
			tabtitle = $(this).children('h5:first')
			tabtitle.replaceWith('')
		}
		if (tabtitle.length == 0) {
			tabtitle = $('<h5>Tab '+ (i+1) +'</h5>')
		}

		tabid = wrapid + '_' + (i + 1)
		tabid_content = tabid + '-content'

		card = $('<div class="card"><div class="card-header" id="'+ tabid +'"></div><div id="'+ tabid_content +'" class="collapse" aria-labelledby="'+ tabid +'" data-parent="#'+ wrapid +'"></div></div>').appendTo(tabwrap)

		tabtitle.addClass('mb-0').html($('<button class="btn btn-link" data-toggle="collapse" data-target="#'+ tabid_content +'" aria-expanded="true" aria-controls="'+ tabid_content +'">'+ tabtitle.text() +'</button>')).appendTo(card.find('#' + tabid))

		$('<div class="card-body" />').append($(this).children()).appendTo(card.find('#' + tabid_content))

		if (i == 0) {
			card.find('#' + tabid_content).addClass('show')
		} else {
			card.find('div.card-header button').addClass('collapsed')
		}
	})
	$(wrap).replaceWith(tabwrap)
};

var TabType = function(index) {
	tabs = $(this).children('div.tab');
	if (tabs.length <= 1)
		return;

	if ((tabs.length <= 3 && !tabs.hasClass('force-collapse')) || tabs.hasClass('force-tab')) {
		Tab(index, this)
	} else {
		Collapse(index, this)
	}
};

var TabWrap = function(selector) {
	wraps = $(selector + ':first-of-type')
	wraps.each(function(){
		$(this).nextUntil(':not('+ selector +')').
			addBack().
			wrapAll('<div class="tab-wrapper" />')
	})
	$("div.tab-wrapper").each(TabType)
};

var adjustImage = function() {
	$('div.tab :has(img)').on('display', function(){
		$(this).find('img').each(function(){
			// squared images, too large
			if ($(this).height() == $(this).width() && $(this).height() > 200) {
				$(this).css('max-width', '50%')
			}
		})
	})
	$('div.tab :has(img)').trigger('display')
};

var correctModal = function() {
	$('.modal div.button').each(function(){
		$(this).find('p').each(function(){
			$(this).replaceWith($(this).html())
		})
		var outer = this.outerHTML
		// replace <div and div>
		outer = '<button' + outer.substring(4, outer.length - 4) + 'button>'
		$(this).replaceWith(outer)
	})
};

var createDataTables = function(){
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
	$('table > caption').each(function(i){
		$(this).html('<strong>Table ' + (i+1) + '.</strong> ' + $(this).html())
	})
	$('.tablewrapper > table').addClass("table table-sm table-striped table-bordered")
	$('.datatablewrapper').each(function(){
		table = $(this).find('table.table')
		$(this).attr('style', table.attr('style'))
		table.removeAttr('style')
		config = JSON.parse($(this).attr('data-datatable'))
		table.addClass('dataTable').dataTable(config)
	})
	$('div.dt-buttons').addClass('btn-group-sm')
};

(function() {
	var ev = new $.Event('display'),
		orig = $.fn.css;
	$.fn.css = function() {
		ret = orig.apply(this, arguments);
		if ($(this).is('div')) {
			$(this).trigger(ev);
		}
		return ret; // keep chaining
	}
})();

$(document).ready(function () {
	$("a.reference[name^=REF_]").each(function() {
		$(this).attr({
			'target': 'blank',
			'href': 'https://scholar.google.com/scholar?q=' + $(this).text()
		})
	})

	TabWrap("div.tab")

	adjustImage()

	correctModal()

	createDataTables()
});