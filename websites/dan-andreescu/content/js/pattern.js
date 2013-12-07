Event.addListener('pattern', 'click', buttonClicked, {saveSuccess: renderNewPatternList});

function renderNewPatternList(result){
	var patternList = Dom.get('patternList');
	patternList.innerHTML = result.responseText;
}


function getPattern(key){

	var params = new Object();
	params.key = key;
	
	ajax( 'POST', '/ajax/GetPattern', {success: renderPattern}, toJSON(params) );
}

function renderPattern(result){
	Dom.get('patternDetail').innerHTML = result.responseText;
	Event.addListener('fact', 'click', buttonClicked, {saveSuccess: renderPattern});
	Event.addListener('occurrence', 'click', buttonClicked, {saveSuccess: renderPattern});
}
