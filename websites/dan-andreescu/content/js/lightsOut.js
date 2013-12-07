function lightClicked(e){
	var light = Event.getTarget(e);
	if( light.id == 'lights' ) return;
	var x = light.id.substring(1,2);
	var y = light.id.substring(2,3);
	var xLeft = x-1;
	var xRight = x-0+1;
	var yUp = y-1;
	var yDown = y-0+1;
	
	var lightsAffected = new Array();
	lightsAffected[0] = light;
	lightsAffected[1] = Dom.get('c'+xLeft+y);
	lightsAffected[3] = Dom.get('c'+xRight+y);
	lightsAffected[2] = Dom.get('c'+x+yDown);
	lightsAffected[4] = Dom.get('c'+x+yUp);

	for( light in lightsAffected ) toggleLight(lightsAffected[light]);				
}
function toggleLight(light){
	if( Dom.hasClass(light, 'lightON') ){
		Dom.removeClass(light, 'lightON');
	}
	else{
		Dom.addClass(light, 'lightON');
	}
}

function saveSuccess(result){
	Dom.get('puzzlesContainer').innerHTML = result.responseText;
	Event.addListener('puzzles', 'change', loadPuzzle);
}
function failure(e){ alert(e); }
function buttonClicked(e){
	var params = new Object();
	var lightsOn = Dom.getElementsByClassName('lightON','div','lights');
	for( light in lightsOn ){
		lightsOn[light] = lightsOn[light].id;
	}
	params.lightsOn = lightsOn.join(',');
	params.name = Dom.get('puzzleName').value;
	if( params.name == '' ) params.name = 'Not named'

	var button = Event.getTarget(e);
	var operation = '/'+button.name;
	var callback = {success: saveSuccess};
	var body = YAHOO.lang.JSON.stringify(params);
	YAHOO.util.Connect.setDefaultPostHeader(false);
	YAHOO.util.Connect.initHeader('CONTENT-TYPE','application/json');
	var request = YAHOO.util.Connect.asyncRequest('POST', operation, callback, body);
}

function loadPuzzle(){
	var puzzles = Dom.get('puzzles');
	if( puzzles.value == '-1' ) return;
	var lights = puzzles.value.split(',');
	var lightLookup = new Array();
	for( light in lights ){
		lightLookup[lights[light]] = true;
	}
	var lightDivs = Dom.getElementsByClassName(
		'light',
		'div',
		'lights',
		function(n){
			if( lightLookup[n.id] ){
				Dom.addClass(n,'lightON');
			}
			else{
				Dom.removeClass(n,'lightON');
			}
		}
	);
}
Event.addListener(window, 'load', init);
function init(){
	Event.addListener('lights', 'click', lightClicked);	
	Event.addListener('save', 'click', buttonClicked);
	Event.addListener('puzzles', 'change', loadPuzzle);
	Event.addListener('restart', 'click', loadPuzzle);
}
