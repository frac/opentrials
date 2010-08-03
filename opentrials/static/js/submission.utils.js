/**
 * Clone form elements in Django forms. JQuery
 * is required by this function.
 */
function cloneMore(selector, type, visitor) {
    var newElement = $(selector).clone(true);

    if( typeof visitor == "function"){
        visitor(newElement);
    }

    var classname = newElement.attr('class');
    if( classname.search('even') > -1 ){
        newElement.attr('class', classname.replace('even','odd'))
    } else if( classname.search('odd') > -1 ){
        newElement.attr('class', classname.replace('odd','even'))
    }

    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    newElement.find(':input').each(function() {
        this.name = this.name.replace(/-[0-9]+-/g,'-' + (total) + '-');
        this.id = 'id_' + this.name;

        if($(this).attr('type')!='hidden')$(this).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });

    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    newElement.hide();
    $(selector).after(newElement);
    newElement.show("fast",function(){this.style.display='';});
}

function handle_decs_div(node){
    var decs_div = $(node).find(".decstool");
    if(decs_div.length === 1){
        if($.browser.msie){
            decs_div.remove();
        } else {
            var match = decs_div.attr('name').match(/-([0-9]+)-/);
            if(match.length > 1){
                var next = parseInt(match[1]) + 1;
                var nome = decs_div.attr('name').replace(/[0-9]+/,next);
                decs_div.attr('name', nome);
                decs_div.attr('id', 'id_'+nome);
            }
        }
    }
    $(node).find(".showdecs").removeAttr("class");
    $(node).find(":input").removeAttr("readonly");
}

/**
 * Try to be a temp
 */
if( window.decsdata == undefined ){
    window.decsdata = {};
}

/**
 * A utility to name and create form elements
 */
function make_decs_for(node,lang){
    var set = node.id.match(/[a-z]+-\d+/)[0]; // get django formset prefix
    return {'lang':lang,
            'select':set+"-combodecs",
            'div':set+'-decstools',
            'input':set+'-searchfield',
            'button':set+'-searchbutton',
            'id':function(e){return 'id_'+ this[e];},
            'create':function(e){return $('<'+e+'>').attr('id',this.id(e)).attr('name',this[e]);},
            'set':set};
}

/**
 * This is the callback for decsclient app
 */
function make_decstool_callback(decs){
    return function(data){
        var lang = decs.lang.substring(0,2);
        for(var i=0; i<data.length;i++){
            var option = $("<option>").attr("value",data[i].fields.label)
                .html(data[i].fields.description[lang])
                .appendTo('#'+decs.id('select'));
            window.decsdata[ data[i].fields.label ]=data[i].fields.description;
        }
        
        $('#'+decs.id('select')).change(function(evt){
            decs = make_decs_for(evt.target,decs.lang);
            $("input#id_"+decs.set+"-code")
                .attr("value",this.value)
                .attr("readonly","readonly");
            $("input[name="+decs.set+"-text]")
                .attr("value",window.decsdata[this.value].en)
                .attr("readonly","readonly");
            $("input[name="+decs.set+"-text|es]")
                .attr("value",window.decsdata[this.value].es)
                .attr("readonly","readonly");
            $("input[name="+decs.set+"-text|pt-br]")
                .attr("value",window.decsdata[this.value].pt)
                .attr("readonly","readonly");
        });

        if( data.length === 1){
            $('#'+decs.id('select') + " option").attr("selected","selected");
            $('#'+decs.id('select')).change();
        }

        if($("input#id_"+decs.set+"-code").val().match(/^[A-Z](\d{2,2}(\.\d{3,3})*)?$/)){
            var code=$("input#id_"+decs.set+"-code").val();
            $('#'+decs.id('select'))
                .find('option[value='+code+']')
                .attr('selected','selected');
        }
    }
}

/**
 * Extend the django form and insert decs elements
 */
function getterm_event(decsclient_url,lang) {
    return function(){
        this.parentNode.className = "";
        if(this.value === 'DeCS'){
            this.parentNode.className = "showdecs";
            var decs = make_decs_for(this,lang);
            $(this).parents('table').find(":input[type=text]").attr("readonly","readonly");
            if($('#'+decs.id('select')).length === 0){
                decs.create('div')
                    .attr('class','decstool')
                    .appendTo(this.parentNode)
                    .append(decs.create('select'));

                $.get(decsclient_url,'',
                    make_decstool_callback(decs),"json");
            }
            $(this.parentNode).find('.decstool :input[type=text]').removeAttr("readonly");
        }else{
            $(this).parents('table').find(":input[type=text]").removeAttr("readonly");
        }
    }
};

/**
 * Extend the django form and insert decs elements
 */
function search_event(decsclient_url,label,lang) {
    return function(){
        this.parentNode.className = "";
        if(this.value === 'DeCS'){
            this.parentNode.className = "showdecs";
            var decs = make_decs_for(this,lang);

            $(this).parents('table').find(":input[type=text]").attr("readonly","readonly");

            if($(this.parentNode).find('.decstool').length === 0){
                decs.create('div')
                   .attr('class','decstool')
                   .appendTo(this.parentNode)
                   .append(decs.create('input').bind("keypress", function(e) {
                            if(e.keyCode === 13){
                                $('#'+decs.id('button')).click();
                                return false;
                            }
                        }))
                   .append(decs.create('button').html(label));

                $('#'+decs.id('button'))
                    .click(function(evt){
                        var decs = make_decs_for(evt.target,lang);
                        if($('#'+decs.id('select')).length === 0){
                            decs.create('select')
                                .insertAfter(this);
                        }
                        $('#'+decs.id('select')).html('');

                        $.get(decsclient_url+$('#'+decs.id('input')).val(),'',
                            make_decstool_callback(decs),
                            'json');
                        return false;
                    });
            }
            $(this.parentNode).find('.decstool :input[type=text]').removeAttr("readonly");
        }else{
            $(this).parents('table').find(":input[type=text]").removeAttr("readonly");
        }
    }
};

function ack_remark(remark_id){

    $.get('/remark/change/'+remark_id+'/acknowledged', function(data, textStatus){

        if (textStatus == "success"){
            $("#remark_"+remark_id).toggleClass('ack');
            $("#remark_"+remark_id).hide('slow',function(){
                if( $("div.warning li.ack").length == $("div.warning li").length) {
                    $("div.warning").hide('fast');
                }
            });
        }
    });
}
