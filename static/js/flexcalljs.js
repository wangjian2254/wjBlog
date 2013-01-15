/**
 * Created with PyCharm.
 * User: xp
 * Date: 12-11-14
 * Time: 下午4:22
 * To change this template use File | Settings | File Templates.
 */
function getPaperUpdateInfo(){
    //alert(location.href);
    var urlparm=location.href.split('?');
    if(urlparm.length==2){
        var parmarr=urlparm[1].split('=');
        if(parmarr[1].length>0){
            //alert(parmarr[1]);
            document.getElementById('swfupload').getImageList(parmarr[1]);
        }

    }
    //alert(urlparm);
}