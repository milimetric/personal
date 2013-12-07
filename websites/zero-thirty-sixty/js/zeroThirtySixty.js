$(document).ready(function(){
	$('#addLearnableDialog').html($('#addLearnableDialogContents').html());
	$('input[type=submit]').button();
	$('#addLearnableDialog').dialog({ autoOpen: false, height: 130, width: 600 });
	$('#addLearnableButton').click(function(){
		$('#addLearnableDialog').dialog('open');
	});
	$('form.async').submit(function(event){
		event.preventDefault();
		var f = $(this);
		$.post(f.attr('action'), f.serialize(), function(data){
			$('input[name=imageUri]').val('').focus();
			viewModel.learnables.push(data);
		});
	});

	function MyViewModel() {
		this.learnables = ko.observableArray([]);
	}
	var viewModel = new MyViewModel();
	ko.applyBindings(viewModel);

	$.get('/main', function(data){
		viewModel.learnables(data.learnables);
		for (i in data.userLearneds) {
			var userLearned = data.userLearneds[i];
			var imgSelector = '#' + (userLearned.learnedAfterThirty === 'True' ? 'thirtySixty' : 'zeroThirty') + ' img.' + userLearned.learnableKey;
			$(imgSelector).parent('div').addClass('learned');
			$(imgSelector).parent('div').find('input[name=key]').val(userLearned.key);
		}
	});


	function learn(div, after30){
		var learnableKey = div.find('input[name=learnableKey]').val();
		var hidden = div.find('input[name=key]');
		$.post('/learn', {learnableKey: learnableKey, learnedAfterThirty: after30}, function(data){
			hidden.val(data.key);
			div.addClass('learned');
		});
	};

	$(document).on('click', '#zeroThirty div.learnables div:not(.learned)', function(event){
		event.stopPropagation();
		learn($(this), false);
	});
	$(document).on('click', '#thirtySixty div.learnables div:not(.learned)', function(event){
		event.stopPropagation();
		learn($(this), true);
	});

	$(document).on('click', 'div.learned', function(){
		var div = $(this);
		var key = div.find('input[name=key]').val();
		$.post('/unlearn', {key: key}, function(){
			div.removeClass('learned');
		});
	});
});
