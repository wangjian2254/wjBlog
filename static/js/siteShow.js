/**
 * Created with PyCharm.
 * User: xp
 * Date: 12-11-21
 * Time: 下午3:17
 * To change this template use File | Settings | File Templates.
 */
function createHttpRequest(){
   if(window.XMLHttpRequest){
        this.xmlHttp=new XMLHttpRequest();
    }
    else if(window.ActiveXObject){
       try{
           this.xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
       }
       catch(e){
          try{
            this.xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
           }
          catch(e){}
      }
   }
}
function sendRequest(url,method,data,flag){
   url= url ? url : "";
   if(url==""){
   	return;
   }
   flag= flag===false ? false : true;
   method= method ? method : "get";
   data= data ? data : null;
   var xmlHttp=new createHttpRequest();
   var handleResponse= function(){
   	if(xmlHttp.xmlHttp.readyState==4){
	    if(xmlHttp.xmlHttp.status==200){
	    	//alert(xmlHttp.xmlHttp.responseText);
	    	try{
	    		//var o=eval("("+xmlHttp.xmlHttp.responseText+")");
	    	}catch(e){
	    		//alert(url);
	    	}
	    	//alert(o.message.message);
	    	//handle(xmlHttp.xmlHttp);
	    	//document.getElementById("rightDiv").innerHTML=xmlHttp.xmlHttp.responseText;
	    }
	    else{
	       //alert("您的页面有异常");
	    }
  	}
   };
   xmlHttp.xmlHttp.onreadystatechange=handleResponse;
   xmlHttp.xmlHttp.open(method,url,flag);
   xmlHttp.xmlHttp.setRequestHeader('Content-Type','application/application/json');
   xmlHttp.xmlHttp.setRequestHeader('X-Requested-With','XMLHttpRequest');
   xmlHttp.xmlHttp.send(null);
}
sendRequest('/blog/websiteNum',null,null,false);