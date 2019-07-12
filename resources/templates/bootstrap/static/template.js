
var Tab = function(index, wrap) {
	wrapid    = 'report_tab_' + (index + 1)
	tabwrap  = $('<div><nav><div class="nav nav-tabs" id="'+ wrapid +'" role="tablist"></div></nav><div class="tab-content" id="'+ wrapid +'Content"></div></div>')
	$(wrap).children('div.tab').each(function(i) {
		tabtitle = $(this).children('h3:first')
		tabtitle.replaceWith('')
		if (tabtitle.length == 0) {
			tabtitle = $(this).children('h4:first')
			tabtitle.replaceWith('')
		}
		if (tabtitle.length == 0) {
			tabtitle = $('<h4>Tab '+ (i+1) +'</h4>')
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
	tabwrap  = $('<div id="'+ wrapid +'"></div>')
	$(wrap).children('div.tab').each(function(i) {
		tabtitle = $(this).children('h3:first')
		tabtitle.replaceWith('')
		if (tabtitle.length == 0) {
			tabtitle = $(this).children('h4:first')
			tabtitle.replaceWith('')
		}
		if (tabtitle.length == 0) {
			tabtitle = $('<h4>Tab '+ (i+1) +'</h4>')
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
	ntabs = $(this).children('div.tab').length;
	if (ntabs <= 1)
		return;

	if (ntabs <= 3) {
		Tab(index, this)
	} else {
		Collapse(index, this)
	}
}

var TabWrap = function(selector) {
	wraps = $(selector + ':first-of-type')
	wraps.each(function(){
		$(this).nextUntil(':not('+ selector +')').
			addBack().
			wrapAll('<div class="tab-wrapper" />')
	})
	$("div.tab-wrapper").each(TabType)
};

$(document).ready(function () {

	$("table").addClass("table table-striped table-sm")

	$("a.reference[name^=REF_]").each(function() {
		$(this).attr({
			'target': 'blank',
			'href': 'https://scholar.google.com/scholar?q=' + $(this).text()
		})
	})
	TabWrap("div.tab")
});