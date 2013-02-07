$(function() {

    var $cols = $('colgroup');

    $('td').live('mouseover', function()
	{
        var i = $(this).prevAll('td').length;
        $(this).parent().addClass('hover')
        $($cols[i]).addClass('hover');
    }).live('mouseout', function()
	{
        var i = $(this).prevAll('td').length;
        $(this).parent().removeClass('hover');
        $($cols[i]).removeClass('hover');
    })
    
    $('table').mouseleave(function()
	{
        $cols.removeClass('hover');
    })

    $('table').mousedown(function()
	{
		/* Replace with whatever you want the click to do */
    })
});
