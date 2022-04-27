$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#wishlist_id").val(res.id);
        $("#wishlist_name").val(res.name);
        $("#wishlist_type").val(res.type);
        $("#wishlist_user_id").val(res.user_id);
        $("#wishlist_created_date").val(res.created_date);
    }

    // Updates the form with data from the response
    function update_item_form_data(res) {
        $("#wishlist_item_id").val(res.id);
        $("#wishlist_item_name").val(res.name);
        $("#wishlist_item_purchased").val(res.purchased);
    }
    /// Clears all form fields
    function clear_form_data() {
        $("#wishlist_id").val("");
        $("#wishlist_name").val("");
        $("#wishlist_type").val("");
        $("#wishlist_user_id").val("");
        $("#wishlist_created_id").val("");
        $("#wishlist_items").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Wishlist
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#wishlist_name").val();
        let type = $("#wishlist_type").val();
        let user_id = $("#wishlist_user_id").val();
        let created_date = $("#wishlist_created_date").val();
        let items = $("#wishlist_items").val();; // Note: items data in

        let data = {
            "name": name,
            "type": type,
            "user_id": user_id,
            "created_date": created_date,
            "items": items
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Wishlist
    // ****************************************

    $("#update-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();
        let name = $("#wishlist_name").val();
        let type = $("#wishlist_type").val();
        let user_id = $("#wishlist_user_id").val();
        let created_date = $("#wishlist_created_date").val();
        let items = $("#wishlist_items").val();

        let data = {
            "name": name,
            "type": type,
            "user_id": user_id,
            "created_date": created_date,
            "items": []
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/wishlists/${wishlist_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Add Item to a Wishlist
    // ****************************************

    $("#item-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val(); //need to specify a wishlist id first
        let name = $("#wishlist_item_name").val();
        let category = $("#wishlist_item_category").val();
        let price = $("#wishlist_item_price").val();
        //let in_stock = $("#item_in_stock").val();
        //let purchased = $("#item_purchased").val();

        let data = {
            "wishlist_id": wishlist_id,
            "name": name,
            "category": category,
            "price": price
            // "in_stock": in_stock,
            // "purchased": purchased
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "POST",
                url: `/wishlists/${wishlist_id}/items`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_item_form_data(res)
            flash_message("Success: Item added to Wishlist")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Wishlist
    // ****************************************

    $("#retrieve-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Wishlist
    // ****************************************

    $("#delete-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Wishlist has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#wishlist_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Wishlist
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#wishlist_name").val();
        let type = $("#wishlist_type").val();
        // let available = $("#pet_available").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (type) {
            if (queryString.length > 0) {
                queryString += '&type=' + type
            } else {
                queryString += 'type=' + type
            }
        }
        // if (available) {
        //     if (queryString.length > 0) {
        //         queryString += '&available=' + available
        //     } else {
        //         queryString += 'available=' + available
        //     }
        // }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/wishlists?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Type</th>'
            table += '<th class="col-md-2">User ID</th>'
            table += '<th class="col-md-2">Created Date</th>'
            table += '<th class="col-md-2">Items</th>'
            table += '</tr></thead><tbody>'
            let firstWishlist = "";
            for(let i = 0; i < res.length; i++) {
                let wishlist = res[i];
                table +=  `<tr id="row_${i}"><td>${wishlist.id}</td><td>${wishlist.name}</td><td>${wishlist.type}</td><td>${wishlist.user_id}</td><td>${wishlist.created_date}</td><td>${wishlist.items[0]}</td></tr>`;
                if (i == 0) {
                    firstWishlist = wishlist;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstWishlist != "") {
                update_form_data(firstWishlist)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Action: Purchase an Item in a Wishlist
    // ****************************************

    $("#purchase-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();
        let item_id = $("#wishlist_item_id").val();
        //let name = $("#wishlist_name").val();
        //let type = $("#wishlist_type").val();
        //let user_id = $("#wishlist_user_id").val();
        //let created_date = $("#wishlist_created_date").val();
        //let items = $("#wishlist_items").val();

        // let data = {
        //     "name": name,
        //     "type": type,
        //     "user_id": user_id,
        //     "created_date": created_date,
        //     "items": [] // TODO - update items
        // };

        $("#flash_message").empty();
        // @app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>/purchase", methods=["PUT"])
        let ajax = $.ajax({
                type: "PUT",
                url: `/wishlists/${wishlist_id}/items/${item_id}/purchase`,
                contentType: "application/json",
                // data: JSON.stringify(data)
                data: ''
            })

        ajax.done(function(res){
            update_item_form_data(res)
            flash_message("Success: Item Purchased!")
        });

        ajax.fail(function(res){
            flash_message("Failed to Purchase Item")
        });

    });

})
