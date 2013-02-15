window.onload=function(){
  var divs=document.getElementsByTagName('div');
	for(var i=0; i<divs.length; i++){
		if(divs[i].className!='jsdemo') continue;
		var title=divs[i].previousSibling;
		if(title.nodeType!=1){
			title=title.previousSibling;
		}
		title.next=divs[i];
		title.onclick=function(){
			var curStyle=this.next.style.display;
			var newStyle;
			var ico=title.getElementsByTagName('span')[0];
			if(curStyle=='none'){
				newStyle='block';
				ico.innerHTML='-';
			}else{
				newStyle='none';
				ico.innerHTML='+';
			};
			title.next.style.display=newStyle;
		}
	}
}
$(function(){
    var $title=$('div.jqdemo');
    $title.each(  
        function()
        {            
            var $titleDiv = $(this);
            $titleDiv.prev().toggle(function(){
                $titleDiv.show().prev().find('span').text('-');
            },function(){
				$titleDiv.hide().prev().find('span').text('+');
            });
        }    
    );
    $title.hide(); 
     
});
