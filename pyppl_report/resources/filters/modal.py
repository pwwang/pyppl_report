"""
Panflute filter to pop up a modal

Click [here](#detailinfo) for details.

```modal
id: detailinfo
title: Detailed information
closebtn: true
size: default # small, large, xlarge
---
content of the modal
```

into:

<div class="modal fade" id="exampleModalCenter" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered" role="document">
	<div class="modal-content">
	  <div class="modal-header">
		<h5 class="modal-title" id="exampleModalCenterTitle">Modal title</h5>
		<button type="button" class="close" data-dismiss="modal" aria-label="Close">
		  <span aria-hidden="true">&times;</span>
		</button>
	  </div>
	  <div class="modal-body">
		...
	  </div>
	  <div class="modal-footer">
		<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
	  </div>
	</div>
  </div>
</div>
"""

import panflute as pf

def fenced_action(options, data, element, doc):
	modalid  = options.get('id', 'modal1')
	title    = options.get('title')
	closebtn = options.get('closebtn', True)
	size     = options.get('size', 'default')
	size2class = {
		'default': None,
		'small'  : 'modal-sm',
		'sm'     : 'modal-sm',
		'large'  : 'modal-lg',
		'lg'     : 'modal-lg',
		'xlarge' : 'modal-xl',
		'xl'     : 'modal-xl',
	}

	components = []
	if title:
		modal_header1 = pf.Header(pf.Str(title), classes=['modal-title'], level=5, identifier=modalid + 'Title')
		modal_header2 = pf.Div(
			pf.Div(pf.Para(pf.Str('x')), attributes = {'aria-hidden': "true"}),
			classes = ['close', 'button'],
			attributes = {
				'type': 'button',
				'data-dismiss': 'modal',
				'aria-label': 'Close'
			})
		components.append(pf.Div(modal_header1, modal_header2, classes = ['modal-header']))
	components.append(pf.Div(*data, classes = ['modal-body']))
	if closebtn:
		components.append(pf.Div(
			pf.Div(pf.Para(pf.Str('Close')), classes = ['button', 'btn', 'btn-secondary'],
			attributes = {
				'type': 'button',
				'data-dismiss': 'modal',
			}),
			classes = ['modal-footer']
		))
	modal_content = pf.Div(*components, classes = ['modal-content'])
	mainclasses = ['modal-dialog', 'modal-dialog-centered', 'modal-dialog-scrollable']
	sizeclass = size2class.get(size)
	if sizeclass:
		mainclasses.append(sizeclass)
	model_dialog = pf.Div(modal_content, classes = mainclasses, attributes = {'role': 'document'})

	return pf.Div(model_dialog, classes = ['modal', 'fade'], identifier = modalid, attributes = {
		'tabindex'       : '-1',
		'role'           : 'dialog',
		'aria-labelledby': modalid + 'Title',
		'aria-hidden'    : "true"
	})

def action(elem, doc):
	"""
	Turn [link](modal#modal1) to:
	<a data-toggle="modal" data-target="#modal1">link</a>
	"""
	if isinstance(elem, pf.Link) and elem.url.startswith('modal'):
		modalid = elem.url.split('#')
		modalid = 'modal1' if len(modalid) == 1 else modalid[1]
		elem.attributes['data-toggle'] = 'modal'
		elem.attributes['data-target'] = '#' + modalid
	elif isinstance(elem, pf.Div) and 'modal' in elem.classes:
		return fenced_action(dict(id = elem.identifier, **elem.attributes), elem.content, elem, doc)

def main(doc=None):
	return pf.run_filter(action, doc=doc)

if __name__ == '__main__':
	main()
