$(document).ready(function(){
	// general UI
	$('input.button, a.button').button();

	// search logic (load all recipes on startup because there aren't that many)
	$.get('/recipe/list', function(list){
		$('#search').autocomplete({
			source: list,
			focus: function (event, ui) {
				var showPicture = ui.item.picture != ''
				if (showPicture) {
					$('#imagePreview').attr('src', ui.item.picture);
				}
				$('#imagePreview').toggle(showPicture);
				return false;
			},
			close: function (event, ui) {
				$('#imagePreview').hide();
				return false;
			},
			select: function(event, ui) {
				location.href = ui.item.details;
				return false;
			}
		})
		.data('autocomplete')._renderItem = function(ul, item) {
			return $('<li></li>')
				.data('item.autocomplete', item)
				.append($('<a></a>').attr('href', item.details).text(item.label))
				.appendTo(ul);
		};
	})


	// edit recipe page handlers TODO: translate to knockout
	$(document).on('click', '#newLink', function(event){
		var newLinkToAdd = $('#newLinkUrl');
		var newLink = '<li><input type="hidden" value="###" name="links"/><a href="#" class="remove" title="remove">[x]</a> ###</li>'.replace(/\#\#\#/g, newLinkToAdd.val());
		$('#addedLinks').append(newLink);
		newLinkToAdd.val('');
	});
	$(document).on('click', '#addedLinks a.remove', function(event){
		event.preventDefault();
		$(this).parent().remove();
	});
});
