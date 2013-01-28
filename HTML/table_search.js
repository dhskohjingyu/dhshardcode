window.onload = function()
{
	// replace #search_table with the id of the table
	var $rows = $("#search_table tr");

	$rows.hide();
	
	// replace #search with the id of the search input
	$("#search").keyup(function()
	{
		var val = $.trim($(this).val()).replace(/ + /g, " ").toLowerCase();
		
		$rows.show().filter(function()
		{
			var text = $(this).text().replace(/\s+/g, " ").toLowerCase();
			return !~text.indexOf(val);
		}).hide();
		
		if(val == "")
		{
			$rows.hide();
		}
	});
}