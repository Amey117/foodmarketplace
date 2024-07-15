
$(document).ready(function(){


    // maps api

    var placeOptions=
    {
    location:[28.61, 77.23]/*,
    geolocation:true,
    pod:'City',
    bridge:true,
    tokenizeAddress:true,*
    filter:'cop:9QGXAM',
    hyperLocal:true, Default is false. Location parameter is mandatory to use this parameter.
    distance:true,
    width:300,
    height:300,
    clearButton:false, //to hide cross button, which is right side of search input
    blank_callback:function(){console.log("called when click on cross button or input value become blank");}
    */
    };
    function callback(data){
        console.log("********* inside callback function ==> data is ",data)
    }

    $('#autoaddress').on('keyup',function(e){
        console.log("******* inside audo address")
        query_text = $(this).val()
        console.log($(this).val())
        // response = new mappls.search(text,placeOptions,callback);
        $.ajax({
            url: 'https://atlas.mappls.com/api/places/search/json', // Your API endpoint
            type: 'GET', // Specify the request type
            headers: {
                'Authorization': 'Bearer 0d3134e8-4ee4-4869-8e8c-d76c84d6c661', // Replace YOUR_TOKEN_HERE with your actual token
                'accept': 'application/json', // Optional: Specify the content type you expect
                'Access-Control-Allow-Origin':"*"
            },
            data: {
                query: query_text,
            },
            dataType: 'json', // Specify the expected data type
            success: function(data) {
                console.log('Success:', data);
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
        //console.log("response is ***** ==> ",response)
    })
    



    $('.add-to-cart').on('click',function(e){
        e.preventDefault()
        food_id = $(this).attr('data-id')
        url = $(this).attr('data-url')
        data = {
            food_id:food_id
        }
        $.ajax({
            type:'GET',
            url:url,
            success:function(response){
                if(response.status=="login_required"){
                    Swal.fire({
                        title: "Login required!",
                        icon: "error"
                      }).then(function(){
                        window.location = '/login'
                      })
                }else{
                    $('#cart-counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty_counter)
                    console.log(response)
                    console.log("response.cart_amount['taxes_list']",response.cart_amount['taxes_list'])
                }
                
                
                // handling sub total ,tax,grandtotal
                applyCartAmount(response.cart_amount['sub_total'],response.cart_amount['taxes_list'],response.cart_amount['grand_total'])
                

            }
        })
    })

    //decrease_cart

    $('.remove-from-cart').on('click',function(e){
        e.preventDefault()
        food_id = $(this).attr('data-id')
        url = $(this).attr('data-url')
        cart_id = $(this).attr('data-cartid')
        data = {
            food_id:food_id
        }
        $.ajax({
            type:'GET',
            url:url,
            success:function(response){
                // sweet alert
                if(response.status=='login_required'){
                    Swal.fire({
                        title: "Login required!",
                        icon: "error"
                      }).then(function(){
                        window.location = '/login'
                      })
                }else{
                    $('#cart-counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty_counter)
                    if(window.location.pathname=='/cart/'){
                        removeCartItem(response.qty_counter,cart_id)
                        isCartEmpty()
                        applyCartAmount(response.cart_amount['sub_total'],response.cart_amount['taxes_list'],response.cart_amount['grand_total'])
                    }
                }
                console.log(response)
            }
        })
    })

    // to display cart for initial view
    $('.item-qty').each(function(){
        // to display for first time
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        $("#"+the_id).html(qty)
    })


    
    // delete cart
    $('.delete-cart').on('click',function(e){
        e.preventDefault()
        cart_id = $(this).attr('data-id')
        url = $(this).attr('data-url')
        $.ajax({
            type:'GET',
            url:url,
            success:function(response){
                if(response.status=="login_required"){
                    Swal.fire({
                        title: "Login required!",
                        icon: "error"
                      }).then(function(){
                        window.location = '/login'
                      })
                }else{
                    $('#cart-counter').html(response.cart_counter['cart_count'])
                    removeCartItem(0,cart_id)
                    isCartEmpty()
                    applyCartAmount(response.cart_amount['sub_total'],response.cart_amount['taxes_list'],response.cart_amount['grand_total'])
                    console.log(response)
                }
            }
        })
    })

       // remove opening hrs


    

    // add opening hrs for vendor restaurant

    $('#add-opening-hrs').on('click',function(e){
        e.preventDefault()
        var day = document.getElementById('id_day').value
        var from_hour = document.getElementById('id_from_hour').value
        var to_hour = document.getElementById('id_to_hour').value
        var is_closed = document.getElementById('id_is_closed').checked
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
        var url = document.getElementById('add-url').value

        // from hour < to hour validation 
        const date1 = new Date(`1970-01-01T${from_hour}`);
        const date2 = new Date(`1970-01-01T${to_hour}`);
        console.log(date1,date2)
        if(date1 > date2){
            Swal.fire({
                title: "Incorrect input",
                text: "Cannot put value for to hour less than from hour"
              });
              return
        }


        console.log(day,from_hour,to_hour,is_closed,csrf_token)

        if(is_closed){
            is_closed=true
            from_hour =''
            to_hour =''
            condition = day!=''
        }else{
            is_closed = false
            condition = day!='' && from_hour!='' && to_hour!=''
        }

        if(condition){
            $.ajax({
                type:'POST',
                url:url,
                data:{
                    'day':day,
                    'from_hour':from_hour,
                    'to_hour':to_hour,
                    'is_closed':eval(is_closed),
                    'csrfmiddlewaretoken':csrf_token
                },
                success:function(response){
                    console.log("response success",response)
                    if(response.status == 'success'){
                        if(response.is_closed){
                            html = `<tr id='hour-${response.id}'>
                                     <td><b>${response.day}</b></td>
                                    <td>
                                        <b style="color: red;">Closed</b> 
                                    </td>
                                        <td><a class="remove_hour" data-url=${response.remove_url} href="#">Remove</a></td>
                                </tr>`
                        }else{
                            html = `<tr id='hour-${response.id}'>
                                     <td><b>${response.day}</b></td>
                                    <td>
                                        ${response.from_hour} - ${response.to_hour} 
                                    </td>
                                        <td><a class="remove_hour" data-url=${response.remove_url} href="#">Remove</a></td>
                                </tr>`
                        }
                        console.log(html)
                        $('.openinghour').append(html)
                        document.getElementById('openinghour').reset()
                    }else{
                        Swal.fire({
                            icon: "error",
                            title: "error",
                            text: response.msg
                          });
                    }
                }
            })
        }else{
            Swal.fire("Please fill required fields!");
        }
        
    })

    $(document).on('click','.remove_hour',function(e){
        e.preventDefault()
        url = $(this).attr('data-url')
        
        $.ajax({
            type:'GET',
            url:url,
            success:function(response){
                console.log(response)
                if(response.status == "success"){
                    element = document.getElementById(`hour-${response.id}`).remove()
                }
            }
        })
    })

 



    // delete the cart element if the quantity is zero or cart item is removed
    // only run if the use is on cart page
    function removeCartItem(cartItemQty,cartId){
        if (cartItemQty<=0){
            // delete the cart item
            document.getElementById('cart-item-'+cartId).remove()
        }
    }

    function isCartEmpty(){
        var cartCounter = document.getElementById('cart-counter').innerHTML
        if (cartCounter==0){
            document.getElementById("empty-cart").style.display = 'block'
        }
    }

    function applyCartAmount(subtotal,taxes,grandtotal){
        if(window.location.pathname=='/cart/'){
            $('#subtotal').html(subtotal)
            // for displaying taxes for particular tax category
            for(var i in taxes){
                $('#tax-' + taxes[i].type).html(taxes[i].tax_amount)
            }
            $('#total').html(grandtotal)

        }
    }

})