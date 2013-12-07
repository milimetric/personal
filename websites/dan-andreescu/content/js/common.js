var Event = YAHOO.util.Event;
var Element = YAHOO.util.Element;
var Dom = YAHOO.util.Dom;

function getFormName( form ){
	return form.className.split(' ')[0];
}
function useNullForThisField(field){
    return Dom.hasClass(field, 'identifier') && field.value == '';
}
function toJSON( obj ){
	return YAHOO.lang.JSON.stringify(obj);
}

function buttonClicked(e, options){
	var buttonClicked = Event.getTarget(e);
	if( buttonClicked.type != 'button' ) return;

	if( !options ){
		var options = new Object();
	}
	if( !options.params ){
		options.params = new Object();
	}
	var requestForm = Dom.getAncestorByClassName( buttonClicked, 'saveParent' );
	var formName = getFormName( requestForm );

	var fields = Dom.getElementsByClassName( formName+'Field', '', requestForm );
	
	// Since this is a div and not a form, we must assign manually.
	//   If it were a form, the browser would do this automatically.
	for( var i=0; i<fields.length; i++ ){
		if (useNullForThisField(fields[i])){
			options.params[fields[i].name] = null;
		}
		else{
			options.params[fields[i].name] = fields[i].value;
		}
	}

	// if it exists, get the parent entity's identifier and
	//   set it as part of the request object
	var requestFormParent = Dom.getAncestorByClassName( requestForm, 'saveParent' );
	if( requestFormParent ){
		var saveParentName = getFormName( requestFormParent );

		var identifiers = Dom.getElementsByClassName( saveParentName+'Field', 'input', requestFormParent );
		if( identifiers ){
			for( var i=0; i<identifiers.length; i++ ){
				if( Dom.hasClass(identifiers[i], 'identifier') ){
					options.params[identifiers[i].name] = identifiers[i].value;
					break;
				}
			}
		}
	}

	var operation = '/ajax/'+buttonClicked.name;
	var callback = {success: options.saveSuccess};
	var body = YAHOO.lang.JSON.stringify(options.params);
	ajax( 'POST', operation, callback, body );
}


function ajax( method, operation, callback, body ){
	YAHOO.util.Connect.setDefaultPostHeader(false);
	YAHOO.util.Connect.initHeader('CONTENT-TYPE','application/json');
	var request = YAHOO.util.Connect.asyncRequest(method, operation, callback, body);
	return request;
}
