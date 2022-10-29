

main_headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJEYW1pYW4ifQ.49JmaHCvE7bePDuEylskD344AAULyLAB9FPf8hRwHTM'
};


$('#editbtn1').click(function() {
    quantity = $('#move').val();
    item_id = $('#item_id').val();

    data = {
        "quantity":quantity,
        "item_id":item_id
    };

    fetch("/chemini-api/item-update-stack",{
    method: 'PUT',
    headers: main_headers,
    body: JSON.stringify(data)})
    .then(response => response.json())
    .then(result => {
        console.log(JSON.stringify(result))
        
        var server_code = JSON.stringify(result['code'])
        var server_response = JSON.stringify(result['response'])
        if (server_code == 200) {
            alert("SUKCES!\nPomyślnie zmieniono stan magazynowy!")}
        else if(server_code == 401) {
            alert("BŁĄD!\nKomunikat serwera:", server_response)}
        else if(server_code == 500) {
            alert("BŁĄD!\nKomunikat serwera:", server_response)}
        else {
            alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
    });
});

       

$('#editbtn2').click(function() {
    item_id = $('#item_id').val();

    data = {
        "item_id":item_id
    };

    fetch("/chemini-api/item-update-all",{
    method: 'PUT',
    headers: main_headers,
    body: JSON.stringify(data)})
    .then(response => response.json())
    .then(result => {
        console.log(JSON.stringify(result))
        
        var server_code = JSON.stringify(result['code'])
        var server_response = JSON.stringify(result['response'])
        if (server_code == 200) {
            alert("SUKCES!\nPomyślnie zmieniono stan magazynowy!")}
        else if(server_code == 401) {
            alert("BŁĄD!\nKomunikat serwera:", server_response)}
        else if(server_code == 500) {
            alert("BŁĄD!\nKomunikat serwera:", server_response)}
        else {
            alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
    });
})

$('#editbtn3').click(function() {
    item_id = $('#item_id').val();

    data = {
        "item_id":item_id
    };

    fetch("/chemini-api/item-delete",{
    method: 'POST',
    headers: main_headers,
    body: JSON.stringify(data)})
    .then(response => response.json())
    .then(result => {
        console.log(JSON.stringify(result))
        
        var server_code = JSON.stringify(result['code'])
        var server_response = JSON.stringify(result['response'])
        if (server_code == 200) {
            alert("SUKCES!\nPomyślnie zmieniono stan magazynowy!")}
        else if(server_code == 401) {
            alert("BŁĄD!\nKomunikat serwera:", server_response)}
        else if(server_code == 500) {
            alert("BŁĄD!\nKomunikat serwera:", server_response)}
        else {
            alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
    });
})