
// main_headers = {
//     'Content-Type': 'application/json',
//     'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJEYW1pYW4ifQ.49JmaHCvE7bePDuEylskD344AAULyLAB9FPf8hRwHTM'
// };

// let my_cookie = document.cookie;
// alert(my_cookie)


$('#editbtn1').click(function() {
    quantity = $('#move').val();
    item_id = $('#item_id').val();

    data = {
        "quantity":quantity,
        "item_id":item_id
    };

    fetch("/warehouse/item-update-stack",{
    method: 'PUT',
    // headers: main_headers,
    body: JSON.stringify(data)})
    .then(response => response.json())
    .then(result => {
        console.log(JSON.stringify(result))
        
        var server_response = result['response']
        var server_msg = result['msg']
        if (server_response == "success") {
            alert(server_msg)
            location.replace("/warehouse");}
        else if(server_response == "error") {
            resp = server_msg.replace(/\n/g, "<br />")
            document.getElementById('moveError').innerHTML = resp;}
        else {
            alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
    });
});

       

// $('#editbtn2').click(function() {
//     item_id = $('#item_id').val();
//     item_name = $('#name').val();
//     manufacturer = $('#manufacturer').val();
//     reference = $('#reference').val();
//     stack_min = $('#stack_min').val();
//     buy = $('#buy').val();
//     sell = $('#sell').val();
//     description = $('#description').val();
//     code = $('#code').val();
//     used = document.getElementById("isused").checked;

//     data = {
//         "item_id": item_id,
//         "item_name": item_name,
//         "manufacturer": manufacturer,
//         "reference": reference,
//         "stack_min": stack_min,
//         "buy": buy,
//         "sell": sell,
//         "description": description = description.replace(/\n/g, "_g_nl_"),
//         "code": code,
//         "used": used
//     };

//     console.log(data)

//     fetch("/warehouse/item-update-all",{
//     method: 'PUT',
//     // headers: main_headers,
//     body: JSON.stringify(data)})
//     .then(response => response.json())
//     .then(result => {
//         console.log(JSON.stringify(result))
        
//         var server_response = result['response']
//         var server_msg = result['msg']
//         if (server_response == "success") {
//             alert(server_msg)
//             location.replace("/warehouse");}
//         else if(server_response == "error") {
//             resp = server_msg.replace(/\n/g, "<br />")
//             document.getElementById('editError').innerHTML = resp;}
//         else {
//             alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
//     });
// });

// $('#editbtn3').click(function() {
//     item_id = $('#item_id').val();

//     data = {
//         "item_id": item_id
//     };

//     fetch("/warehouse/item-delete-row",{
//     method: 'DELETE',
//     // headers: main_headers,
//     body: JSON.stringify(data)})
//     .then(response => response.json())
//     .then(result => {
//         console.log(JSON.stringify(result))
        
//         var server_response = result['response']
//         var server_msg = result['msg']
//         if (server_response == "success") {
//             alert(server_msg)
//             location.replace("/warehouse");}
//         else if(server_response == "error") {
//             resp = server_msg.replace(/\n/g, "<br />")
//             document.getElementById('deleteError').innerHTML = resp;}
//         else {
//             alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
//     });
// });